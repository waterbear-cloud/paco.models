"""
All things Application Engine.
"""

from paco.models import loader
from paco.models import schemas
from paco.models.base import Parent, Named, Deployable, Enablable, Regionalized, Resource, ApplicationResource, \
    AccountRef, DNSEnablable, CFNExport, md5sum, ImportFrom
from paco.models.exceptions import InvalidPacoBucket, InvalidModelObject, InvalidPacoProjectFile
from paco.models.formatter import get_formatted_model_context, smart_join
from paco.models.locations import get_parent_by_interface
from paco.models.metrics import Monitorable, AlarmNotifications, MonitorConfig
from paco.models.vocabulary import application_group_types
from paco.models.logging import CloudWatchLogRetention
from paco.models.iam import Role
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
import troposphere
import troposphere.autoscaling
import troposphere.dynamodb
import troposphere.ecs
import troposphere.elasticache
import troposphere.elasticloadbalancingv2
import troposphere.elasticsearch
import troposphere.cognito
import troposphere.pinpoint
import troposphere.rds
import troposphere.s3
import troposphere.secretsmanager


@implementer(schemas.IApplicationEngines)
class ApplicationEngines(Named, dict):
    pass

@implementer(schemas.IApplicationEngine)
class ApplicationEngine(Named, Deployable, Regionalized, Monitorable):
    groups = FieldProperty(schemas.IApplicationEngine['groups'])
    order = FieldProperty(schemas.IApplicationEngine['order'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.groups = ResourceGroups('groups', self)
        self.notifications = AlarmNotifications('notifications', self)

    # Returns a list of groups sorted by 'order'
    def groups_ordered(self):
        group_config_list = []
        for item_group_id, item_group_config in self.groups.items():
            new_group_config = [item_group_id, item_group_config]
            insert_idx = 0
            for group_config in group_config_list:
                if item_group_config.order < group_config[1].order:
                    group_config_list.insert(insert_idx, new_group_config)
                    break
                insert_idx += 1
            else:
                group_config_list.append(new_group_config)

        return group_config_list

@implementer(schemas.IApplication)
class Application(ApplicationEngine, Regionalized):
    type = "App"

    def get_resource_by_name(self, resource_name):
        """
        Iterate through resource groups and find resource
        of the given name.
        """
        resource = None
        for group in self.groups.values():
            if resource_name in group.resources.keys():
                return group.resources[resource_name]
        return resource

    def get_all_group_types(self):
        """
        Iterate through all groups and return a list of all types in use.
        Results are always sorted in a fixed order.
        """
        types = {}
        results = []
        for group in self.groups.values():
            if group.type not in types:
                types[group.type] = True
        for sorted_type in application_group_types:
            if sorted_type in types:
                results.append(sorted_type)
        return results

    def list_alarm_info(self, group_name=None):
        """
        Return a list of dicts of Alarms for the Application. The dict contains
        the group and resource that the Alarm belongs to for context:

            {
                'alarm': CloudWatchAlarm,
                'group': ResourceGroup,
                'resource': Resource
            }

        The `group_name` will limit results to a specifc ResourceGroup.
        """
        alarm_info = []
        for group in self.groups.values():
            if group_name and group.__name__ != group_name:
                continue
            for resource in group.resources.values():
                if hasattr(resource, 'monitoring'):
                    if hasattr(resource.monitoring, 'alarm_sets'):
                        for alarm_set in resource.monitoring.alarm_sets.values():
                            for alarm in alarm_set.values():
                                alarm_info.append({
                                    'alarm': alarm,
                                    'resource': resource,
                                    'group': group
                                })
        return alarm_info

    def resolve_ref(self, ref):
        pass

@implementer(schemas.IServiceEnvironment)
class ServiceEnvironment(AccountRef, Named):
    applications = FieldProperty(schemas.IServiceEnvironment['applications'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.applications = ApplicationEngines('applications', self)

@implementer(schemas.IResourceGroups)
class ResourceGroups(Named, dict):
    "ResourceGroups"

    def all_groups_by_type(self, group_type):
        "Return all ResourceGroups contained of a specific type"
        results = []
        for group in self.values():
            if group.type == group_type:
                results.append(group)
        return results


@implementer(schemas.IResourceGroup)
class ResourceGroup(Named, Deployable, DNSEnablable, ImportFrom):
    resources = FieldProperty(schemas.IResourceGroup['resources'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.resources = Resources('resources', self)

    def resources_ordered(self):
        "Returns a list of a group's resources sorted by 'order'"
        res_config_list = []
        for item_res_id, item_res_config in self.resources.items():
            new_res_config = [item_res_id, item_res_config]
            insert_idx = 0
            for res_config in res_config_list:
                if item_res_config.order < res_config[1].order:
                    res_config_list.insert(insert_idx, new_res_config)
                    break
                insert_idx+=1
            else:
                res_config_list.append(new_res_config)

        return res_config_list

    def list_alarm_info(self):
        app = get_parent_by_interface(self, schemas.IApplication)
        return app.list_alarm_info(group_name=self.__name__)

@implementer(schemas.IResources)
class Resources(Named, dict):
    "Resources"

    def deployments(self):
        # Loop through resources and return list of deployment
        # resources only
        pass


@implementer(schemas.IS3BucketPolicy)
class S3BucketPolicy(Parent):
    action = FieldProperty(schemas.IS3BucketPolicy['action'])
    aws = FieldProperty(schemas.IS3BucketPolicy['aws'])
    condition = FieldProperty(schemas.IS3BucketPolicy['condition'])
    effect = FieldProperty(schemas.IS3BucketPolicy['effect'])
    principal = FieldProperty(schemas.IS3BucketPolicy['principal'])
    resource_suffix = FieldProperty(schemas.IS3BucketPolicy['resource_suffix'])
    sid = FieldProperty(schemas.IS3BucketPolicy['sid'])

    def __init__(self, __parent__=None):
        super().__init__(__parent__)
        self.processed = False

@implementer(schemas.IS3LambdaConfiguration)
class S3LambdaConfiguration(Parent):
    event = FieldProperty(schemas.IS3LambdaConfiguration['event'])
    function = FieldProperty(schemas.IS3LambdaConfiguration['function'])

@implementer(schemas.IS3NotificationConfiguration)
class S3NotificationConfiguration(Parent):
    lambdas = FieldProperty(schemas.IS3NotificationConfiguration['lambdas'])

@implementer(schemas.IS3StaticWebsiteHostingRedirectRequests)
class S3StaticWebsiteHostingRedirectRequests(Parent):
    target = FieldProperty(schemas.IS3StaticWebsiteHostingRedirectRequests['target'])
    protocol = FieldProperty(schemas.IS3StaticWebsiteHostingRedirectRequests['protocol'])

@implementer(schemas.IS3StaticWebsiteHosting)
class S3StaticWebsiteHosting(Parent, Deployable):
    redirect_requests = FieldProperty(schemas.IS3StaticWebsiteHosting['redirect_requests'])

@implementer(schemas.IS3Bucket)
class S3Bucket(Resource, Deployable):
    add_paco_suffix = FieldProperty(schemas.IS3Bucket['add_paco_suffix'])
    bucket_name = FieldProperty(schemas.IS3Bucket['bucket_name'])
    account = FieldProperty(schemas.IS3Bucket['account'])
    deletion_policy = FieldProperty(schemas.IS3Bucket['deletion_policy'])
    policy = FieldProperty(schemas.IS3Bucket['policy'])
    region = FieldProperty(schemas.IS3Bucket['region'])
    cloudfront_origin = FieldProperty(schemas.IS3Bucket['cloudfront_origin'])
    external_resource = FieldProperty(schemas.IS3Bucket['external_resource'])
    versioning = FieldProperty(schemas.IS3Bucket['versioning'])
    notifications = FieldProperty(schemas.IS3Bucket['notifications'])
    bucket_name_prefix = None
    bucket_name_suffix = None

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.policy = []

    def add_policy(self, policy_dict):
        policy_obj = S3BucketPolicy()
        loader.apply_attributes_from_config(policy_obj, policy_dict)
        self.policy.append(policy_obj)
        return policy_obj

    def set_account(self, account_ref):
        setattr(self, 'account', account_ref)

    def update(self, config_dict):
        loader.apply_attributes_from_config(self, config_dict)

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

    @property
    def versioning_cfn(self):
        if not hasattr(self, 'versioning'):
            return {}
        if self.versioning:
            status = 'Enabled'
        else:
            status = 'Suspended'

        return { "Status": status }

    def get_aws_name(self):
        "Name of the S3 Bucket in AWS"
        return self.get_bucket_name()

    def get_bucket_name(self):
        "Returns the complete computed bucket name"
        # external_resource buckets are simply the name of the bucket
        if self.external_resource == True:
            return self.bucket_name

        bucket_name_suffix = self.bucket_name_suffix
        if self.add_paco_suffix == True:
            project = get_parent_by_interface(self, schemas.IProject)
            if project.s3bucket_hash == None:
                raise InvalidPacoProjectFile(
                    f"Bucket {self.paco_ref_parts} declares 'add_paco_suffix: true' but 's3bucket_hash' is not set in project.yaml."
                )
            bucket_name_suffix = project.s3bucket_hash

        ne = get_parent_by_interface(self, schemas.INetworkEnvironment)
        service = get_parent_by_interface(self, schemas.IService)
        app = get_parent_by_interface(self, schemas.IApplication)

        bucket_name_list_standard = [
                self.bucket_name_prefix,
                self.bucket_name,
                bucket_name_suffix,
                self.region_short_name
            ]
        if schemas.IResource.providedBy(self.__parent__):
            bucket_name_list_standard.insert(0, self.__parent__.name)
            bucket_name_list_standard.insert(4, self.name)
        else:
            bucket_name_list_standard.insert(0, self.name)

        bucket_name_list = []
        # Bucket in a NetworkEnvironment contained Application
        if ne != None and app != None:
            # NetworkEnvironment Application buckets are in the format:
            # ne-<netenv>-<env>-app-<app>-<resourcegroup>-<resource>-<bucket_name_prefix>-<bucketname>-<bucket_name_suffix>-<shortregionname>
            bucket_name_list.extend([
                'ne',
                ne.name,
                get_parent_by_interface(self, schemas.IEnvironment).name,
                'app',
                app.name,
                get_parent_by_interface(self, schemas.IResourceGroup).name,
            ])
            bucket_name_list.extend(bucket_name_list_standard)
        elif service != None and app != None:
            # Service Application buckets are in the format:
            # service-<app>-<resourcegroup>-<resource>-<bucket_name_prefix>-<bucketname>-<bucket_name_suffix>-<shortregionname>
            bucket_name_list.extend([
                'service',
                app.name,
                get_parent_by_interface(self, schemas.IResourceGroup).name,
            ])
            bucket_name_list.extend(bucket_name_list_standard)
        # Bucket as a global Resource
        elif get_parent_by_interface(self, schemas.IS3Resource):
            # Global buckets have the format:
            # paco-s3-<resourcename>-<bucket_name_prefix>-<bucketname>-<bucket_name_suffix>-<shortregionname>
            bucket_name_list.append('paco-s3')
            bucket_name_list.extend(bucket_name_list_standard)

        # Custom buckets are created with internal API calls e.g. EC2 LaunchMangaer, CloudTrail
        # They rely on bucket_name_prefix and bucket_name_suffix attributes being set on the S3Bucket object
        else:
            if self.bucket_name_prefix == None or bucket_name_suffix == None:
                raise InvalidPacoBucket("""Custom named bucket requires a bucket_name_prefix and bucket_name_suffix attributes to be set.

{}""".format(get_formatted_model_context(self)))
            bucket_name_list.extend([
                self.bucket_name_prefix,
                self.name,
                self.bucket_name,
                bucket_name_suffix
            ])

        bucket_name = smart_join('-', bucket_name_list)
        bucket_name = bucket_name.replace('_', '-').lower()

        # If the generated bucket name is > 63 chars, then prefix a hash of the bucket
        if len(bucket_name) > 63:
            bucket_hash = md5sum(str_data=bucket_name)[:8]
            bucket_copy_size = -(63-9)
            if bucket_name[bucket_copy_size] != '-':
                bucket_hash += '-'
            bucket_name = bucket_hash+bucket_name[bucket_copy_size:]

        return bucket_name

    troposphere_props = troposphere.s3.Bucket.props
    cfn_mapping = {
        #'AccessControl': (basestring, False),
        #'AccelerateConfiguration': (AccelerateConfiguration, False),
        #'AnalyticsConfigurations': ([AnalyticsConfiguration], False),
        #'BucketEncryption': (BucketEncryption, False),
        #'CorsConfiguration': (CorsConfiguration, False),
        #'InventoryConfigurations': ([InventoryConfiguration], False),
        #'LifecycleConfiguration': (LifecycleConfiguration, False),
        #'LoggingConfiguration': (LoggingConfiguration, False),
        #'MetricsConfigurations': ([MetricsConfiguration], False),
        #'ObjectLockConfiguration': (ObjectLockConfiguration, False),
        #'ObjectLockEnabled': (boolean, False),
        #'PublicAccessBlockConfiguration': (PublicAccessBlockConfiguration, False),
        #'ReplicationConfiguration': (ReplicationConfiguration, False),
        #'Tags': (Tags, False),
        #'WebsiteConfiguration': (WebsiteConfiguration, False),
        #'NotificationConfiguration': computed in template for ARNs
        'BucketName': 'bucket_name',
        'VersioningConfiguration': 'versioning_cfn',
    }

@implementer(schemas.IApplicationS3Bucket)
class ApplicationS3Bucket(ApplicationResource, S3Bucket):
    "S3 Bucket to support an application"

@implementer(schemas.IASGLifecycleHooks)
class ASGLifecycleHooks(Named, dict):
    pass

@implementer(schemas.IASGLifecycleHook)
class ASGLifecycleHook(Named, Deployable):
    lifecycle_transition = FieldProperty(schemas.IASGLifecycleHook['lifecycle_transition'])
    notification_target_arn = FieldProperty(schemas.IASGLifecycleHook['notification_target_arn'])
    role_arn = FieldProperty(schemas.IASGLifecycleHook['role_arn'])
    default_result = FieldProperty(schemas.IASGLifecycleHook['default_result'])

@implementer(schemas.IASGScalingPolicies)
class ASGScalingPolicies(Named, dict):
    pass


@implementer(schemas.IASGScalingPolicy)
class ASGScalingPolicy(Named, Deployable):
    policy_type = FieldProperty(schemas.IASGScalingPolicy['policy_type'])
    adjustment_type = FieldProperty(schemas.IASGScalingPolicy['adjustment_type'])
    scaling_adjustment = FieldProperty(schemas.IASGScalingPolicy['scaling_adjustment'])
    cooldown = FieldProperty(schemas.IASGScalingPolicy['cooldown'])
    alarms = FieldProperty(schemas.IASGScalingPolicy['alarms'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.alarms = []

@implementer(schemas.IEIP)
class EIP(ApplicationResource):
    dns = FieldProperty(schemas.IEIP['dns'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dns = []

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IEBSVolumeMount)
class EBSVolumeMount(Parent, Deployable):
    folder = FieldProperty(schemas.IEBSVolumeMount['folder'])
    volume = FieldProperty(schemas.IEBSVolumeMount['volume'])
    device = FieldProperty(schemas.IEBSVolumeMount['device'])
    filesystem = FieldProperty(schemas.IEBSVolumeMount['filesystem'])

@implementer(schemas.IEBS)
class EBS(ApplicationResource):
    size_gib = FieldProperty(schemas.IEBS['size_gib'])
    snapshot_id = FieldProperty(schemas.IEBS['snapshot_id'])
    availability_zone = FieldProperty(schemas.IEBS['availability_zone'])
    volume_type = FieldProperty(schemas.IEBS['volume_type'])

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IEC2LaunchOptions)
class EC2LaunchOptions(Named):
    ssm_agent = FieldProperty(schemas.IEC2LaunchOptions['ssm_agent'])
    codedeploy_agent = FieldProperty(schemas.IEC2LaunchOptions['codedeploy_agent'])
    ssm_expire_events_after_days = FieldProperty(schemas.IEC2LaunchOptions['ssm_expire_events_after_days'])
    update_packages = FieldProperty(schemas.IEC2LaunchOptions['update_packages'])
    cfn_init_config_sets = FieldProperty(schemas.IEC2LaunchOptions['cfn_init_config_sets'])

@implementer(schemas.IBlockDevice)
class BlockDevice(Parent):
    delete_on_termination = FieldProperty(schemas.IBlockDevice['delete_on_termination'])
    encrypted = FieldProperty(schemas.IBlockDevice['encrypted'])
    iops = FieldProperty(schemas.IBlockDevice['iops'])
    snapshot_id = FieldProperty(schemas.IBlockDevice['snapshot_id'])
    size_gib = FieldProperty(schemas.IBlockDevice['size_gib'])
    volume_type = FieldProperty(schemas.IBlockDevice['volume_type'])

    troposphere_props = troposphere.autoscaling.EBSBlockDevice.props
    cfn_mapping = {
        'DeleteOnTermination': 'delete_on_termination',
        'Encrypted': 'encrypted',
        'Iops': 'iops',
        'SnapshotId': 'snapshot_id',
        'VolumeSize': 'size_gib',
        'VolumeType': 'volume_type',
    }

@implementer(schemas.IBlockDeviceMapping)
class BlockDeviceMapping(Parent):
    device_name = FieldProperty(schemas.IBlockDeviceMapping['device_name'])
    ebs = FieldProperty(schemas.IBlockDeviceMapping['ebs'])
    virtual_name = FieldProperty(schemas.IBlockDeviceMapping['virtual_name'])

    @property
    def ebs_cfn(self):
        if self.ebs != None:
            return self.ebs.cfn_export_dict

    troposphere_props = troposphere.autoscaling.BlockDeviceMapping.props
    cfn_mapping = {
        'DeviceName': 'device_name',
        'Ebs': 'ebs_cfn',
        'VirtualName': 'virtual_name',
    }

@implementer(schemas.IASGRollingUpdatePolicy)
class ASGRollingUpdatePolicy(Named):
    enabled = FieldProperty(schemas.IASGRollingUpdatePolicy['enabled'])
    max_batch_size = FieldProperty(schemas.IASGRollingUpdatePolicy['max_batch_size'])
    min_instances_in_service = FieldProperty(schemas.IASGRollingUpdatePolicy['min_instances_in_service'])
    pause_time = FieldProperty(schemas.IASGRollingUpdatePolicy['pause_time'])
    wait_on_resource_signals = FieldProperty(schemas.IASGRollingUpdatePolicy['wait_on_resource_signals'])

@implementer(schemas.IECSCapacityProvider)
class ECSCapacityProvider(Named, Deployable):
    target_capacity = FieldProperty(schemas.IECSCapacityProvider['target_capacity'])
    minimum_scaling_step_size = FieldProperty(schemas.IECSCapacityProvider['minimum_scaling_step_size'])
    managed_instance_protection = FieldProperty(schemas.IECSCapacityProvider['managed_instance_protection'])
    maximum_scaling_step_size = FieldProperty(schemas.IECSCapacityProvider['maximum_scaling_step_size'])

    def get_aws_name(self):
        asg = self.__parent__.__parent__
        return f"{asg.netenv_name}-{asg.env_name}-{asg.app_name}-{asg.group_name}-{asg.name}"

@implementer(schemas.IECSASGConfiguration)
class ECSASGConfiguration(Named):
    cluster = FieldProperty(schemas.IECSASGConfiguration['cluster'])
    log_level = FieldProperty(schemas.IECSASGConfiguration['log_level'])
    capacity_provider = FieldProperty(schemas.IECSASGConfiguration['capacity_provider'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.capacity_provider = ECSCapacityProvider('capacity_provider', self)

@implementer(schemas.IECSCapacityProviderStrategyItem)
class ECSCapacityProviderStrategyItem(Parent):
    base = FieldProperty(schemas.IECSCapacityProviderStrategyItem['base'])
    provider = FieldProperty(schemas.IECSCapacityProviderStrategyItem['provider'])
    weight = FieldProperty(schemas.IECSCapacityProviderStrategyItem['weight'])

@implementer(schemas.ISSHAccess)
class SSHAccess(Named):
    users = FieldProperty(schemas.ISSHAccess['users'])
    groups = FieldProperty(schemas.ISSHAccess['groups'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.users = []
        self.groups = []

@implementer(schemas.IScriptManagerECRDeployRepositories)
class ScriptManagerECRDeployRepositories(Parent):
    source_repo = FieldProperty(schemas.IScriptManagerECRDeployRepositories['source_repo'])
    source_tag = FieldProperty(schemas.IScriptManagerECRDeployRepositories['source_tag'])
    dest_repo = FieldProperty(schemas.IScriptManagerECRDeployRepositories['dest_repo'])
    dest_tag = FieldProperty(schemas.IScriptManagerECRDeployRepositories['dest_tag'])
    release_phase = FieldProperty(schemas.IScriptManagerECRDeployRepositories['release_phase'])

@implementer(schemas.IScriptManagerEcrDeploy)
class ScriptManagerEcrDeploy(Named):
    repositories = FieldProperty(schemas.IScriptManagerEcrDeploy['repositories'])
    release_phase = FieldProperty(schemas.IScriptManagerEcrDeploy['release_phase'])

@implementer(schemas.IScriptManagerEcrDeploys)
class ScriptManagerEcrDeploys(Named, dict):
    pass

@implementer(schemas.IScriptManagerEcs)
class ScriptManagerEcs(Named):
    cluster = FieldProperty(schemas.IScriptManagerEcs['cluster'])

@implementer(schemas.IScriptManagerEcsGroup)
class ScriptManagerEcsGroup(Named, dict):
    pass

@implementer(schemas.IScriptManager)
class ScriptManager(Named):
    ecr_deploy = FieldProperty(schemas.IScriptManager['ecr_deploy'])
    ecs = FieldProperty(schemas.IScriptManager['ecs'])

@implementer(schemas.IASG)
class ASG(ApplicationResource, Monitorable):
    cfn_init = FieldProperty(schemas.IASG['cfn_init'])
    desired_capacity = FieldProperty(schemas.IASG['desired_capacity'])
    desired_capacity_ignore_changes = FieldProperty(schemas.IASG['desired_capacity_ignore_changes'])
    dns = FieldProperty(schemas.IASG['dns'])
    min_instances = FieldProperty(schemas.IASG['min_instances'])
    max_instances = FieldProperty(schemas.IASG['max_instances'])
    associate_public_ip_address = FieldProperty(schemas.IASG['associate_public_ip_address'])
    cooldown_secs = FieldProperty(schemas.IASG['cooldown_secs'])
    ebs_optimized = FieldProperty(schemas.IASG['ebs_optimized'])
    health_check_type = FieldProperty(schemas.IASG['health_check_type'])
    health_check_grace_period_secs = FieldProperty(schemas.IASG['health_check_grace_period_secs'])
    eip = FieldProperty(schemas.IASG['eip'])
    ecs = FieldProperty(schemas.IASG['ecs'])
    instance_iam_role = FieldProperty(schemas.IASG['instance_iam_role'])
    instance_ami = FieldProperty(schemas.IASG['instance_ami'])
    instance_ami_ignore_changes = FieldProperty(schemas.IASG['instance_ami_ignore_changes'])
    instance_ami_type = FieldProperty(schemas.IASG['instance_ami_type'])
    instance_key_pair = FieldProperty(schemas.IASG['instance_key_pair'])
    instance_type = FieldProperty(schemas.IASG['instance_type'])
    segment = FieldProperty(schemas.IASG['segment'])
    termination_policies = FieldProperty(schemas.IASG['termination_policies'])
    security_groups = FieldProperty(schemas.IASG['security_groups'])
    target_groups = FieldProperty(schemas.IASG['target_groups'])
    load_balancers = FieldProperty(schemas.IASG['load_balancers'])
    termination_policies = FieldProperty(schemas.IASG['termination_policies'])
    user_data_script = FieldProperty(schemas.IASG['user_data_script'])
    user_data_pre_script = FieldProperty(schemas.IASG['user_data_pre_script'])
    instance_monitoring = FieldProperty(schemas.IASG['instance_monitoring'])
    scaling_policy_cpu_average = FieldProperty(schemas.IASG['scaling_policy_cpu_average'])
    efs_mounts = FieldProperty(schemas.IASG['efs_mounts'])
    ebs_volume_mounts = FieldProperty(schemas.IASG['ebs_volume_mounts'])
    scaling_policies = FieldProperty(schemas.IASG['scaling_policies'])
    lifecycle_hooks = FieldProperty(schemas.IASG['lifecycle_hooks'])
    availability_zone = FieldProperty(schemas.IASG['availability_zone'])
    secrets = FieldProperty(schemas.IASG['secrets'])
    launch_options = FieldProperty(schemas.IASG['launch_options'])
    block_device_mappings = FieldProperty(schemas.IASG['block_device_mappings'])
    rolling_update_policy = FieldProperty(schemas.IASG['rolling_update_policy'])
    script_manager = FieldProperty(schemas.IASG['script_manager'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.secrets = []
        self.target_groups = []
        self.load_balancers = []
        self.efs_mounts = []
        self.ebs_volume_mounts = []
        self.rolling_update_policy = ASGRollingUpdatePolicy('rolling_update_policy', self)
        self.launch_options = EC2LaunchOptions('launch_options', self)
        self.instance_iam_role = Role('role', self)
        self.ssh_access = SSHAccess('ssh_access', self)

    @property
    def instance_ami_type_family(self):
        """AMI Type family. Either redhat, debian or microsoft"""
        if self.instance_ami_type_generic in ('ubuntu', 'debian'):
            return 'debian'
        elif self.instance_ami_type_generic in ('amazon','centos','redhat','suse'):
            return 'redhat'
        elif self.instance_ami_type_generic in ('microsoft'):
            return 'microsoft'
        # undectected type?
        raise AttributeError(f'Can not determine instance_ami_type_family for {self.name} with type {self.instance_ami_type}')

    @property
    def instance_ami_type_generic(self):
        """AMI Type without version information. e.g. ubuntu_14 is ubuntu."""
        return self.instance_ami_type.split('_')[0]

    def get_aws_name(self):
        "AutoScalingGroup Name for AWS"
        name_list = []

        # NetworkEnvironment or Service name
        netenv = get_parent_by_interface(self, schemas.INetworkEnvironment)
        if netenv == None:
            service = get_parent_by_interface(self, schemas.IService)
            if service == None:
                raise InvalidModelObject("""Unable to find an INetworkEnvironment or IService model object.""")
            name_list.append('Service')
        else:
            name_list.append(netenv.name)

        # Environment name or Blank if one does not exist
        env = get_parent_by_interface(self, schemas.IEnvironment)
        if env != None:
            name_list.append(env.name)

        # Application Name
        app = get_parent_by_interface(self, schemas.IApplication)
        resource_group = get_parent_by_interface(self, schemas.IResourceGroup)
        name_list.extend([
            app.name,
            resource_group.name,
            self.name
        ])
        aws_name = self.create_resource_name_join(
                name_list=name_list,
                separator='-',
                camel_case=True
        )
        return aws_name

    def resolve_ref(self, ref):
        if ref.resource_ref == 'name':
            return self.resolve_ref_obj.resolve_ref(ref)
        elif ref.resource_ref == 'instance_iam_role':
            return self.instance_iam_role
        elif ref.resource_ref == 'instance_ami':
            return self.instance_ami
        elif ref.parts[-2] == 'resources':
            return self
        elif ref.resource_ref.startswith('instance_id'):
            self.resolve_ref_obj.resolve_ref(ref)
        elif ref.last_part == 'resource_name':
            return self.resource_name
        return None

# ECS

@implementer(schemas.IPortMapping)
class PortMapping(Parent):
    container_port = FieldProperty(schemas.IPortMapping['container_port'])
    host_port = FieldProperty(schemas.IPortMapping['host_port'])
    protocol = FieldProperty(schemas.IPortMapping['protocol'])

    troposphere_props = troposphere.ecs.PortMapping.props
    cfn_mapping = {
        'ContainerPort': 'container_port',
        'HostPort': 'host_port',
        'Protocol': 'protocol',
    }

@implementer(schemas.IECSMountPoint)
class ECSMountPoint(Parent):
    "ECS TaskDefinition Mount Point"
    container_path = FieldProperty(schemas.IECSMountPoint['container_path'])
    read_only = FieldProperty(schemas.IECSMountPoint['read_only'])
    source_volume = FieldProperty(schemas.IECSMountPoint['source_volume'])

    troposphere_props = troposphere.ecs.MountPoint.props
    cfn_mapping = {
        'ContainerPath': 'container_path',
        'SourceVolume': 'source_volume',
        'ReadOnly': 'read_only',
    }

@implementer(schemas.IECSVolumesFrom)
class ECSVolumesFrom(Parent):
    "ECS VolumesFrom"
    read_only = FieldProperty(schemas.IECSVolumesFrom['read_only'])
    source_container = FieldProperty(schemas.IECSVolumesFrom['source_container'])

    troposphere_props = troposphere.ecs.VolumesFrom.props
    cfn_mapping = {
        'SourceContainer': 'source_container',
        'ReadOnly': 'read_only',
    }

@implementer(schemas.IECSLogging)
class ECSLogging(Named, CloudWatchLogRetention):
    driver = FieldProperty(schemas.IECSLogging['driver'])

@implementer(schemas.IECSTaskDefinitionSecret)
class ECSTaskDefinitionSecret(Parent, CFNExport):
    name = FieldProperty(schemas.IECSTaskDefinitionSecret['name'])
    value_from = FieldProperty(schemas.IECSTaskDefinitionSecret['value_from'])

    troposphere_props = troposphere.ecs.Secret.props
    cfn_mapping = {
        'Name': 'name',
        'ValueFrom': 'value_from'
    }

@implementer(schemas.IECSContainerDependency)
class ECSContainerDependency(Parent):
    container_name = FieldProperty(schemas.IECSContainerDependency['container_name'])
    condition = FieldProperty(schemas.IECSContainerDependency['condition'])

    troposphere_props = troposphere.ecs.ContainerDependency.props
    cfn_mapping = {
        'ContainerName': 'container_name',
        'Condition': 'condition',
    }

@implementer(schemas.IDockerLabels)
class DockerLabels(Named, dict):
    pass

@implementer(schemas.IECSHostEntry)
class ECSHostEntry(Parent):
    hostname = FieldProperty(schemas.IECSHostEntry['hostname'])
    ip_address = FieldProperty(schemas.IECSHostEntry['ip_address'])

@implementer(schemas.IECSHealthCheck)
class ECSHealthCheck(Named):
    command = FieldProperty(schemas.IECSHealthCheck['command'])
    retries = FieldProperty(schemas.IECSHealthCheck['retries'])
    timeout = FieldProperty(schemas.IECSHealthCheck['timeout'])
    interval = FieldProperty(schemas.IECSHealthCheck['interval'])
    start_period = FieldProperty(schemas.IECSHealthCheck['start_period'])

    troposphere_props = troposphere.ecs.HealthCheck.props
    cfn_mapping = {
        'Command': 'command',
        'Interval': 'interval',
        'Retries': 'retries',
        'StartPeriod': 'start_period',
        'Timeout': 'timeout',
    }

@implementer(schemas.IECSUlimit)
class ECSUlimit(Parent):
    name = FieldProperty(schemas.IECSUlimit['name'])
    hard_limit = FieldProperty(schemas.IECSUlimit['hard_limit'])
    soft_limit = FieldProperty(schemas.IECSUlimit['soft_limit'])

@implementer(schemas.IECSContainerDefinition)
class ECSContainerDefinition(Named):
    cpu = FieldProperty(schemas.IECSContainerDefinition['cpu'])
    command = FieldProperty(schemas.IECSContainerDefinition['command'])
    depends_on = FieldProperty(schemas.IECSContainerDefinition['depends_on'])
    disable_networking = FieldProperty(schemas.IECSContainerDefinition['disable_networking'])
    dns_search_domains = FieldProperty(schemas.IECSContainerDefinition['dns_search_domains'])
    dns_servers = FieldProperty(schemas.IECSContainerDefinition['dns_servers'])
    docker_labels = FieldProperty(schemas.IECSContainerDefinition['docker_labels'])
    docker_security_options = FieldProperty(schemas.IECSContainerDefinition['docker_security_options'])
    entry_point = FieldProperty(schemas.IECSContainerDefinition['entry_point'])
    environment = FieldProperty(schemas.IECSContainerDefinition['environment'])
    essential = FieldProperty(schemas.IECSContainerDefinition['essential'])
    extra_hosts = FieldProperty(schemas.IECSContainerDefinition['extra_hosts'])
    health_check = FieldProperty(schemas.IECSContainerDefinition['health_check'])
    hostname = FieldProperty(schemas.IECSContainerDefinition['hostname'])
    image = FieldProperty(schemas.IECSContainerDefinition['image'])
    image_tag = FieldProperty(schemas.IECSContainerDefinition['image_tag'])
    interactive = FieldProperty(schemas.IECSContainerDefinition['interactive'])
    logging = FieldProperty(schemas.IECSContainerDefinition['logging'])
    memory = FieldProperty(schemas.IECSContainerDefinition['memory'])
    memory_reservation = FieldProperty(schemas.IECSContainerDefinition['memory_reservation'])
    mount_points = FieldProperty(schemas.IECSContainerDefinition['mount_points'])
    port_mappings = FieldProperty(schemas.IECSContainerDefinition['port_mappings'])
    privileged = FieldProperty(schemas.IECSContainerDefinition['privileged'])
    pseudo_terminal = FieldProperty(schemas.IECSContainerDefinition['pseudo_terminal'])
    readonly_root_filesystem = FieldProperty(schemas.IECSContainerDefinition['readonly_root_filesystem'])
    start_timeout = FieldProperty(schemas.IECSContainerDefinition['start_timeout'])
    stop_timeout = FieldProperty(schemas.IECSContainerDefinition['stop_timeout'])
    secrets = FieldProperty(schemas.IECSContainerDefinition['secrets'])
    setting_groups = FieldProperty(schemas.IECSContainerDefinition['setting_groups'])
    ulimits = FieldProperty(schemas.IECSContainerDefinition['ulimits'])
    user = FieldProperty(schemas.IECSContainerDefinition['user'])
    volumes_from = FieldProperty(schemas.IECSContainerDefinition['volumes_from'])
    working_directory = FieldProperty(schemas.IECSContainerDefinition['working_directory'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.port_mappings = []
        self.volumes_from = []
        self.mount_points = []
        self.environment = []
        self.secrets = []
        self.setting_groups = []
        self.depends_on = []
        self.dns_search_domains = []
        self.dns_servers = []
        self.DockerLabels = DockerLabels('docker_labels', self)
        self.ulimits = []

    @property
    def secrets_mappings_cfn(self):
        return [
            sm.cfn_export_dict for sm in self.secrets
        ]

    @property
    def port_mappings_cfn(self):
        return [
            pm.cfn_export_dict for pm in self.port_mappings
        ]

    @property
    def mount_points_cfn(self):
        return [
            mp.cfn_export_dict for mp in self.mount_points
        ]

    @property
    def volumes_from_cfn(self):
        return [
            vf.cfn_export_dict for vf in self.volumes_from
        ]

    @property
    def depends_on_cfn(self):
        return [
            dep.cfn_export_dict for dep in self.depends_on
        ]

    @property
    def ulimits_cfn(self):
        return [
            ulimit.cfn_export_dict for ulimit in self.ulimits
        ]

    @property
    def health_check_cfn(self):
        if self.health_check != None:
            return self.health_check.cfn_export_dict

    @property
    def ebsoptions_cfn(self):
        if self.ebs_volumes != None:
            return self.ebs_volumes.cfn_export_dict

    troposphere_props = troposphere.ecs.ContainerDefinition.props
    cfn_mapping = {
        'Command': 'command',
        'Cpu': 'cpu',
        'DependsOn': 'depends_on_cfn',
        'DisableNetworking': 'disable_networking',
        'DnsSearchDomains': 'dns_search_domains',
        'DnsServers': 'dns_servers',
        'DockerLabels': 'docker_labels',
        'DockerSecurityOptions': 'docker_security_options',
        'EntryPoint': 'entry_point',
        # 'Environment':  computed in template
        'Essential': 'essential',
        'ExtraHosts': 'extra_hosts',
        # 'FirelensConfiguration': (FirelensConfiguration, False),
        'HealthCheck': 'health_check_cfn',
        'Hostname': 'hostname',
        # 'Image': computed in the template
        'Interactive': 'interactive',
        # 'Links': ([basestring], False),
        # 'LinuxParameters': (LinuxParameters, False),
        # 'LogConfiguration': computed in template
        'Memory': 'memory',
        'MemoryReservation': 'memory_reservation',
        'MountPoints': 'mount_points_cfn',
        'Name': 'name',
        'PortMappings': 'port_mappings_cfn',
        'Privileged': 'privileged',
        'PseudoTerminal': 'pseudo_terminal',
        'ReadonlyRootFilesystem': 'readonly_root_filesystem',
        # 'RepositoryCredentials': (RepositoryCredentials, False),
        # 'ResourceRequirements': ([ResourceRequirement], False),
        # 'ServiceRegistries': ([ServiceRegistry], False)
        # 'Secrets': computed in the template
        'StartTimeout': 'start_timeout',
        'StopTimeout': 'stop_timeout',
        # 'SystemControls': ([SystemControl], False),
        'Ulimits': 'ulimits_cfn',
        'User': 'user',
        'VolumesFrom': 'volumes_from_cfn',
        'WorkingDirectory': 'working_directory',
    }

@implementer(schemas.IECSContainerDefinitions)
class ECSContainerDefinitions(Named, dict):
    pass

@implementer(schemas.IECSTaskDefinitions)
class ECSTaskDefinitions(Named, dict):
    pass

@implementer(schemas.IECSVolume)
class ECSVolume(Parent):
    "ECS Volume"
    name = FieldProperty(schemas.IECSVolume['name'])

    troposphere_props = troposphere.ecs.Volume.props
    cfn_mapping = {
        # 'DockerVolumeConfiguration': (DockerVolumeConfiguration, False),
        'Name': 'name',
        # 'Host': (Host, False),
    }

@implementer(schemas.IECSTaskDefinition)
class ECSTaskDefinition(Named):
    container_definitions = FieldProperty(schemas.IECSTaskDefinition['container_definitions'])
    cpu_units = FieldProperty(schemas.IECSTaskDefinition['cpu_units'])
    fargate_compatibile = FieldProperty(schemas.IECSTaskDefinition['fargate_compatibile'])
    memory_in_mb = FieldProperty(schemas.IECSTaskDefinition['memory_in_mb'])
    network_mode = FieldProperty(schemas.IECSTaskDefinition['network_mode'])
    volumes = FieldProperty(schemas.IECSTaskDefinition['volumes'])

    @property
    def container_definitions_cfn(self):
        return [
            cd.cfn_export_dict for cd in self.container_definitions.values()
        ]

    @property
    def volumes_cfn(self):
        return [
            v.cfn_export_dict for v in self.volumes
        ]

    @property
    def cpu_cfn(self):
        if self.fargate_compatibile:
            return str(self.cpu_units)
        return None

    @property
    def memory_cfn(self):
        if self.fargate_compatibile:
            return str(self.memory_in_mb)
        return None

    @property
    def requires_compabilities_cfn(self):
        if self.fargate_compatibile:
            return ["FARGATE"]
        return None

    troposphere_props = troposphere.ecs.TaskDefinition.props
    cfn_mapping = {
        'ContainerDefinitions': 'container_definitions_cfn',
        'Cpu': 'cpu_cfn',
        # 'ExecutionRoleArn': created in the reseng
        # 'Family': (basestring, False),
        # 'InferenceAccelerators': ([InferenceAccelerator], False),
        # 'IpcMode': (basestring, False),
        'Memory': 'memory_cfn',
        'NetworkMode': 'network_mode',
        # 'PidMode': (basestring, False),
        # 'PlacementConstraints': ([PlacementConstraint], False),
        # 'ProxyConfiguration': (ProxyConfiguration, False),
        'RequiresCompatibilities': 'requires_compabilities_cfn',
        # 'Tags': (Tags, False),
        # 'TaskRoleArn': (basestring, False),
        'Volumes': 'volumes_cfn',
    }

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.volumes = []
        self.container_definitions = ECSContainerDefinitions('container_definitions', self)

@implementer(schemas.IECSLoadBalancer)
class ECSLoadBalancer(Named):
    container_name = FieldProperty(schemas.IECSLoadBalancer['container_name'])
    container_port = FieldProperty(schemas.IECSLoadBalancer['container_port'])
    target_group = FieldProperty(schemas.IECSLoadBalancer['target_group'])

    troposphere_props = troposphere.ecs.LoadBalancer.props
    cfn_mapping = {
        'ContainerName': 'container_name',
        'ContainerPort': 'container_port',
        # 'LoadBalancerName': (basestring, False),
        'TargetGroupArn': 'target_group',
    }

@implementer(schemas.IECSServicesContainer)
class ECSServicesContainer(Named, dict):
    pass

@implementer(schemas.IECSTargetTrackingScalingPolicy)
class ECSTargetTrackingScalingPolicy(Named, Enablable):
    disable_scale_in = FieldProperty(schemas.IECSTargetTrackingScalingPolicy['disable_scale_in'])
    scale_in_cooldown = FieldProperty(schemas.IECSTargetTrackingScalingPolicy['scale_in_cooldown'])
    scale_out_cooldown = FieldProperty(schemas.IECSTargetTrackingScalingPolicy['scale_out_cooldown'])
    predefined_metric = FieldProperty(schemas.IECSTargetTrackingScalingPolicy['predefined_metric'])
    target = FieldProperty(schemas.IECSTargetTrackingScalingPolicy['target'])

@implementer(schemas.IECSTargetTrackingScalingPolicies)
class ECSTargetTrackingScalingPolicies(Named, dict):
    pass

@implementer(schemas.IServiceVPCConfiguration)
class ServiceVPCConfiguration(Named):
    assign_public_ip = FieldProperty(schemas.IServiceVPCConfiguration['assign_public_ip'])
    segments = FieldProperty(schemas.IServiceVPCConfiguration['segments'])
    security_groups = FieldProperty(schemas.IServiceVPCConfiguration['security_groups'])

@implementer(schemas.IECSService)
class ECSService(Named, Monitorable):
    type = 'ECSService'
    deployment_controller = FieldProperty(schemas.IECSService['deployment_controller'])
    deployment_minimum_healthy_percent = FieldProperty(schemas.IECSService['deployment_minimum_healthy_percent'])
    deployment_maximum_percent = FieldProperty(schemas.IECSService['deployment_maximum_percent'])
    desired_count = FieldProperty(schemas.IECSService['desired_count'])
    minimum_tasks = FieldProperty(schemas.IECSService['minimum_tasks'])
    maximum_tasks = FieldProperty(schemas.IECSService['maximum_tasks'])
    suspend_scaling = FieldProperty(schemas.IECSService['suspend_scaling'])
    target_tracking_scaling_policies = FieldProperty(schemas.IECSService['target_tracking_scaling_policies'])
    health_check_grace_period_seconds = FieldProperty(schemas.IECSService['health_check_grace_period_seconds'])
    task_definition = FieldProperty(schemas.IECSService['task_definition'])
    launch_type = FieldProperty(schemas.IECSService['launch_type'])
    load_balancers = FieldProperty(schemas.IECSService['load_balancers'])
    hostname = FieldProperty(schemas.IECSService['hostname'])
    vpc_config = FieldProperty(schemas.IECSService['vpc_config'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.load_balancers = []
        self.target_tracking_scaling_policies = ECSTargetTrackingScalingPolicies('target_tracking_scaling_policies', self)

    def resolve_ref(self, ref):
        services = get_parent_by_interface(self, schemas.IECSServices)
        return services.stack

    @property
    def load_balancers_cfn(self):
        return [
            lb.cfn_export_dict for lb in self.load_balancers
        ]

    @property
    def deployment_configuration_cfn(self):
        return {
            "MaximumPercent": self.deployment_maximum_percent,
            "MinimumHealthyPercent": self.deployment_minimum_healthy_percent
        }

    @property
    def launch_type_cfn(self):
        if self.launch_type == 'Fargate':
            return 'FARGATE'
        else:
            return 'EC2'

    @property
    def deployment_controller_cfn(self):
        return {"Type": self.deployment_controller.upper()}

    troposphere_props = troposphere.ecs.Service.props
    cfn_mapping = {
        # 'Cluster': set in template
        'DeploymentConfiguration': 'deployment_configuration_cfn',
        'DeploymentController': 'deployment_controller_cfn',
        # 'DesiredCount': set in the template as Parameter
        # 'EnableECSManagedTags': (boolean, False),
        'HealthCheckGracePeriodSeconds': 'health_check_grace_period_seconds',
        'LaunchType': 'launch_type_cfn',
        'LoadBalancers': 'load_balancers_cfn',
        # 'NetworkConfiguration': set in template
        # 'Role': (basestring, False),
        # 'PlacementConstraints': ([PlacementConstraint], False),
        # 'PlacementStrategies': ([PlacementStrategy], False),
        # 'PlatformVersion': (basestring, False), # only for Fargate
        # 'PropagateTags': (basestring, False),
        # 'SchedulingStrategy': (basestring, False),
        # 'ServiceName': provided by CloudFormation
        # 'ServiceRegistries': ([ServiceRegistry], False),
        # 'Tags': (Tags, False),
        'TaskDefinition': 'task_definition',
    }

class ServicesMonitorConfig(MonitorConfig):
    "MonitorConfig with enabled based on any Service in the Services"
    # _enabled = True

    def __get_enabled(self):
        # if getattr(self, '_enabled', False):
        #     return False
        for service in self.__parent__.services.values():
            if getattr(service, 'monitoring', None) != None:
                if service.monitoring.enabled == True:
                    return True
        return False

    def __set_enabled(self, value):
        self._enabled = value

    enabled = property(__get_enabled, __set_enabled)

@implementer(schemas.IECSSettingsGroup)
class ECSSettingsGroup(Named):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.secrets = []
        self.environment = []

    secrets = FieldProperty(schemas.IECSSettingsGroup['secrets'])
    environment = FieldProperty(schemas.IECSSettingsGroup['environment'])

@implementer(schemas.IECSSettingsGroups)
class ECSSettingsGroups(Named, dict):
    pass

@implementer(schemas.IECSServices)
class ECSServices(Resource, Monitorable):
    cluster = FieldProperty(schemas.IECSServices['cluster'])
    setting_groups = FieldProperty(schemas.IECSServices['setting_groups'])
    services = FieldProperty(schemas.IECSServices['services'])
    service_discovery_namespace_name = FieldProperty(schemas.IECSServices['service_discovery_namespace_name'])
    secrets_manager_access = FieldProperty(schemas.IECSServices['secrets_manager_access'])
    task_definitions = FieldProperty(schemas.IECSServices['task_definitions'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.task_definitions = ECSTaskDefinitions('task_definitions', self)
        self.services = ECSServicesContainer('services', self)

@implementer(schemas.IECSCluster)
class ECSCluster(Resource, Monitorable):
    capacity_providers = FieldProperty(schemas.IECSCluster['capacity_providers'])

    def resolve_ref(self, ref):
        return self.stack

# ECR: Elastic Container Repository
@implementer(schemas.IECRRepository)
class ECRRepository(Resource):
    cross_account_access = FieldProperty(schemas.IECRRepository['cross_account_access'])
    lifecycle_policy_registry_id = FieldProperty(schemas.IECRRepository['lifecycle_policy_registry_id'])
    lifecycle_policy_text = FieldProperty(schemas.IECRRepository['lifecycle_policy_text'])
    repository_name = FieldProperty(schemas.IECRRepository['repository_name'])
    repository_policy = FieldProperty(schemas.IECRRepository['repository_policy'])
    account = FieldProperty(schemas.IECRRepository['account'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.cross_account_access = []

    def resolve_ref(self, ref):
        if ref.last_part == 'name':
            return self.repository_name
        return self.stack

# EC2

@implementer(schemas.IEC2)
class EC2(ApplicationResource):
    "EC2"


@implementer(schemas.IPortProtocol)
class PortProtocol():
    port = FieldProperty(schemas.IPortProtocol['port'])
    protocol = FieldProperty(schemas.IPortProtocol['protocol'])

@implementer(schemas.ITargetGroups)
class TargetGroups(Named, dict):
    pass

@implementer(schemas.ITargetGroup)
class TargetGroup(Resource, PortProtocol):
    type = 'TargetGroup'
    connection_drain_timeout = FieldProperty(schemas.ITargetGroup['connection_drain_timeout'])
    healthy_threshold = FieldProperty(schemas.ITargetGroup['healthy_threshold'])
    health_check_http_code = FieldProperty(schemas.ITargetGroup['health_check_http_code'])
    health_check_interval = FieldProperty(schemas.ITargetGroup['health_check_interval'])
    health_check_path = FieldProperty(schemas.ITargetGroup['health_check_path'])
    health_check_protocol = FieldProperty(schemas.ITargetGroup['health_check_protocol'])
    health_check_timeout = FieldProperty(schemas.ITargetGroup['health_check_timeout'])
    target_type = FieldProperty(schemas.ITargetGroup['target_type'])
    unhealthy_threshold = FieldProperty(schemas.ITargetGroup['unhealthy_threshold'])

    def resolve_ref(self, ref):
        if ref.ref.endswith('.target_groups.'+self.name):
            return self
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IListenerRules)
class ListenerRules(Named, dict):
    pass

@implementer(schemas.IListenerRule)
class ListenerRule(Named, Deployable):
    rule_type = FieldProperty(schemas.IListenerRule['rule_type'])
    priority = FieldProperty(schemas.IListenerRule['priority'])
    host = FieldProperty(schemas.IListenerRule['host'])
    redirect_host = FieldProperty(schemas.IListenerRule['redirect_host'])
    target_group = FieldProperty(schemas.IListenerRule['target_group'])
    path_pattern = FieldProperty(schemas.IListenerRule['path_pattern'])

@implementer(schemas.IListeners)
class Listeners(Named, dict):
    pass

@implementer(schemas.IListener)
class Listener(Named, PortProtocol):
    redirect = FieldProperty(schemas.IListener['redirect'])
    ssl_certificates = FieldProperty(schemas.IListener['ssl_certificates'])
    ssl_policy = FieldProperty(schemas.IListener['ssl_policy'])
    target_group = FieldProperty(schemas.IListener['target_group'])
    rules = FieldProperty(schemas.IListener['rules'])

    troposphere_props = troposphere.elasticloadbalancingv2.Listener.props
    cfn_mapping = {
        # 'Certificates': computed in template
        # 'DefaultActions': computed in template
        # 'LoadBalancerArn': (basestring, True),
        'Port': 'port',
        'Protocol': 'protocol',
        # 'SslPolicy': computed in template
    }

@implementer(schemas.IDNS)
class DNS(Named, Parent):
    hosted_zone = FieldProperty(schemas.IDNS['hosted_zone'])
    private_hosted_zone = FieldProperty(schemas.IDNS['private_hosted_zone'])
    domain_name = FieldProperty(schemas.IDNS['domain_name'])
    ssl_certificate = FieldProperty(schemas.IDNS['ssl_certificate'])
    ttl = FieldProperty(schemas.IDNS['ttl'])

    def resolve_ref(self, ref):
        if ref.resource_ref == "ssl_certificate.arn":
            return self.ssl_certificate
        return ref.resource.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ILoadBalancer)
class LoadBalancer(ApplicationResource):
    target_groups = FieldProperty(schemas.ILoadBalancer['target_groups'])
    listeners = FieldProperty(schemas.ILoadBalancer['listeners'])
    dns = FieldProperty(schemas.ILoadBalancer['dns'])
    scheme = FieldProperty(schemas.ILoadBalancer['scheme'])
    security_groups = FieldProperty(schemas.ILoadBalancer['security_groups'])
    segment = FieldProperty(schemas.ILoadBalancer['segment'])
    idle_timeout_secs = FieldProperty(schemas.ILoadBalancer['idle_timeout_secs'])
    enable_access_logs = FieldProperty(schemas.ILoadBalancer['enable_access_logs'])
    access_logs_bucket = FieldProperty(schemas.ILoadBalancer['access_logs_bucket'])
    access_logs_prefix = FieldProperty(schemas.ILoadBalancer['access_logs_prefix'])

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IApplicationLoadBalancer)
class ApplicationLoadBalancer(LoadBalancer):
    pass

@implementer(schemas.INetworkLoadBalancer)
class NetworkLoadBalancer(LoadBalancer):
    pass

@implementer(schemas.IACM)
class ACM(ApplicationResource):
    domain_name = FieldProperty(schemas.IACM['domain_name'])
    subject_alternative_names = FieldProperty(schemas.IACM['subject_alternative_names'])
    external_resource = FieldProperty(schemas.IACM['external_resource'])
    private_ca = FieldProperty(schemas.IACM['private_ca'])
    region = FieldProperty(schemas.IACM['region'])

    def resolve_ref(self, ref):
        if ref.resource_ref == 'domain_name':
            return self.domain_name
        if ref.parts[-2] == 'resources':
            return self
        return ref.resource.stack

@implementer(schemas.ILambdaVariable)
class LambdaVariable(Parent):
    """
    Lambda Environment Variable
    """
    key = FieldProperty(schemas.ILambdaVariable['key'])
    value = FieldProperty(schemas.ILambdaVariable['value'])

    def __init__(self, __parent__, key='', value=''):
        self.__parent__ = __parent__
        self.key = key
        self.value = value

@implementer(schemas.ILambdaEnvironment)
class LambdaEnvironment(Parent):
    """
    Lambda Environment
    """
    variables = FieldProperty(schemas.ILambdaEnvironment['variables'])

    def __init__(self, __parent__):
        self.__parent__ = __parent__
        self.variables = []

@implementer(schemas.ILambdaFunctionCode)
class LambdaFunctionCode(Parent):
    zipfile = FieldProperty(schemas.ILambdaFunctionCode['zipfile'])
    s3_bucket = FieldProperty(schemas.ILambdaFunctionCode['s3_bucket'])
    s3_key = FieldProperty(schemas.ILambdaFunctionCode['s3_key'])

@implementer(schemas.ILambdaVpcConfig)
class LambdaVpcConfig(Named):
    segments = FieldProperty(schemas.ILambdaVpcConfig['segments'])
    security_groups = FieldProperty(schemas.ILambdaVpcConfig['security_groups'])

@implementer(schemas.ILambdaAtEdgeConfiguration)
class LambdaAtEdgeConfiguration(Named, Enablable):
    auto_publish_version = FieldProperty(schemas.ILambdaAtEdgeConfiguration['auto_publish_version'])

@implementer(schemas.ILambda)
class Lambda(ApplicationResource, Monitorable):
    """
    Lambda Function resource
    """
    description = FieldProperty(schemas.ILambda['description'])
    code = FieldProperty(schemas.ILambda['code'])
    edge = FieldProperty(schemas.ILambda['edge'])
    environment = FieldProperty(schemas.ILambda['environment'])
    iam_role = FieldProperty(schemas.ILambda['iam_role'])
    handler = FieldProperty(schemas.ILambda['handler'])
    memory_size = FieldProperty(schemas.ILambda['memory_size'])
    reserved_concurrent_executions = FieldProperty(schemas.ILambda['reserved_concurrent_executions'])
    runtime = FieldProperty(schemas.ILambda['runtime'])
    # The amount of time that Lambda allows a function to run before stopping it. The default is 3 seconds. The maximum allowed value is 900 seconds.
    timeout = FieldProperty(schemas.ILambda['timeout'])
    sdb_cache = FieldProperty(schemas.ILambda['sdb_cache'])
    layers = FieldProperty(schemas.ILambda['layers'])
    sns_topics = FieldProperty(schemas.ILambda['sns_topics'])
    vpc_config = FieldProperty(schemas.ILambda['vpc_config'])

    def add_environment_variable(self, name, value):
        """Adds a Name-Value pair to the environment field.
        If an environment variable with the name already exists, it will be set to the new value."""
        if self.environment == None:
            self.environment = LambdaEnvironment(self)

        for variable in self.environment.variables:
            if variable.key == name:
                variable.value = value
                return
        self.environment.variables.append(
            LambdaVariable(self.environment, name, value)
        )

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ISNSTopicSubscription)
class SNSTopicSubscription(Parent):
    protocol = FieldProperty(schemas.ISNSTopicSubscription['protocol'])
    endpoint = FieldProperty(schemas.ISNSTopicSubscription['endpoint'])
    filter_policy = FieldProperty(schemas.ISNSTopicSubscription['filter_policy'])

@implementer(schemas.ISNSTopic)
class SNSTopic(Enablable, Resource):
    type = "SNSTopic"
    display_name = FieldProperty(schemas.ISNSTopic['display_name'])
    subscriptions = FieldProperty(schemas.ISNSTopic['subscriptions'])
    cross_account_access = FieldProperty(schemas.ISNSTopic['cross_account_access'])
    locations = FieldProperty(schemas.ISNSTopic["locations"])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.locations = []

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ICloudFrontCustomOriginConfig)
class CloudFrontCustomOriginConfig(Named):
    http_port = FieldProperty(schemas.ICloudFrontCustomOriginConfig['http_port'])
    https_port = FieldProperty(schemas.ICloudFrontCustomOriginConfig['https_port'])
    protocol_policy = FieldProperty(schemas.ICloudFrontCustomOriginConfig['protocol_policy'])
    ssl_protocols = FieldProperty(schemas.ICloudFrontCustomOriginConfig['ssl_protocols'])
    read_timeout = FieldProperty(schemas.ICloudFrontCustomOriginConfig['read_timeout'])
    keepalive_timeout = FieldProperty(schemas.ICloudFrontCustomOriginConfig['keepalive_timeout'])


@implementer(schemas.ICloudFrontCookies)
class CloudFrontCookies(Named):
    forward = FieldProperty(schemas.ICloudFrontCookies['forward'])
    whitelisted_names = FieldProperty(schemas.ICloudFrontCookies['whitelisted_names'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.whitelisted_names = []

@implementer(schemas.ICloudFrontForwardedValues)
class CloudFrontForwardedValues(Named):
    query_string = FieldProperty(schemas.ICloudFrontForwardedValues['query_string'])
    cookies = FieldProperty(schemas.ICloudFrontForwardedValues['cookies'])
    headers = FieldProperty(schemas.ICloudFrontForwardedValues['headers'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        #self.cookies = CloudFrontCookies('cookies', self)
        #self.headers = []

@implementer(schemas.ICloudFrontLambdaFunctionAssocation)
class CloudFrontLambdaFunctionAssocation(Named):
    event_type = FieldProperty(schemas.ICloudFrontLambdaFunctionAssocation['event_type'])
    include_body = FieldProperty(schemas.ICloudFrontLambdaFunctionAssocation['include_body'])
    lambda_function = FieldProperty(schemas.ICloudFrontLambdaFunctionAssocation['lambda_function'])

@implementer(schemas.ICloudFrontDefaultCacheBehavior)
class CloudFrontDefaultCacheBehavior(Named):
    allowed_methods = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['allowed_methods'])
    cached_methods = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['cached_methods'])
    cache_policy_id = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['cache_policy_id'])
    default_ttl = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['default_ttl'])
    min_ttl = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['min_ttl'])
    max_ttl = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['max_ttl'])
    origin_request_policy_id = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['origin_request_policy_id'])
    target_origin = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['target_origin'])
    viewer_protocol_policy = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['viewer_protocol_policy'])
    forwarded_values = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['forwarded_values'])
    compress = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['compress'])

@implementer(schemas.ICloudFrontCacheBehavior)
class CloudFrontCacheBehavior(CloudFrontDefaultCacheBehavior):
    path_pattern = FieldProperty(schemas.ICloudFrontCacheBehavior['path_pattern'])

@implementer(schemas.ICloudFrontViewerCertificate)
class CloudFrontViewerCertificate(Named):
    certificate = FieldProperty(schemas.ICloudFrontViewerCertificate['certificate'])
    ssl_supported_method = FieldProperty(schemas.ICloudFrontViewerCertificate['ssl_supported_method'])
    minimum_protocol_version = FieldProperty(schemas.ICloudFrontViewerCertificate['minimum_protocol_version'])

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ICloudFrontCustomErrorResponse)
class CloudFrontCustomErrorResponse():
    error_caching_min_ttl = FieldProperty(schemas.ICloudFrontCustomErrorResponse['error_caching_min_ttl'])
    error_code = FieldProperty(schemas.ICloudFrontCustomErrorResponse['error_code'])
    response_code = FieldProperty(schemas.ICloudFrontCustomErrorResponse['response_code'])
    response_page_path = FieldProperty(schemas.ICloudFrontCustomErrorResponse['response_page_path'])

@implementer(schemas.ICloudFrontOrigins)
class CloudFrontOrigins(Named, dict):
    pass

@implementer(schemas.ICloudFrontOrigin)
class CloudFrontOrigin(Named):
    s3_bucket = FieldProperty(schemas.ICloudFrontOrigin['s3_bucket'])
    domain_name = FieldProperty(schemas.ICloudFrontOrigin['domain_name'])
    custom_origin_config = FieldProperty(schemas.ICloudFrontOrigin['custom_origin_config'])

    def resolve_ref(self, ref):
        if ref.parts[-2] == 'origins':
            return ref.last_part

@implementer(schemas.ICloudFrontFactories)
class CloudFrontFactories(Named, dict):
    pass

@implementer(schemas.ICloudFrontFactory)
class CloudFrontFactory(Named):
    domain_aliases = FieldProperty(schemas.ICloudFrontFactory['domain_aliases'])
    viewer_certificate = FieldProperty(schemas.ICloudFrontFactory['viewer_certificate'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.domain_aliases = []

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ICloudFront)
class CloudFront(ApplicationResource, Deployable, Monitorable):
    domain_aliases = FieldProperty(schemas.ICloudFront['domain_aliases'])
    default_root_object = FieldProperty(schemas.ICloudFront['default_root_object'])
    default_cache_behavior = FieldProperty(schemas.ICloudFront['default_cache_behavior'])
    cache_behaviors = FieldProperty(schemas.ICloudFront['cache_behaviors'])
    viewer_certificate = FieldProperty(schemas.ICloudFront['viewer_certificate'])
    price_class = FieldProperty(schemas.ICloudFront['price_class'])
    custom_error_responses = FieldProperty(schemas.ICloudFront['custom_error_responses'])
    origins = FieldProperty(schemas.ICloudFront['origins'])
    webacl_id = FieldProperty(schemas.ICloudFront['webacl_id'])
    factory = FieldProperty(schemas.ICloudFront['factory'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.custom_error_responses = []
        self.cache_behaviors = []
        self.custom_error_responses = []

    def s3_origin_exists(self):
        for origin_config in self.origins.values():
            if origin_config.s3_bucket != None:
                return True
        return False

@implementer(schemas.IDBParameters)
class DBParameters(dict):
    pass

@implementer(schemas.IDBParameterGroup)
class DBParameterGroup(ApplicationResource):
    description = FieldProperty(schemas.IDBParameterGroup['description'])
    family = FieldProperty(schemas.IDBParameterGroup['family'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.parameters = DBParameters()

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IDBClusterParameterGroup)
class DBClusterParameterGroup(DBParameterGroup):
    pass

@implementer(schemas.IRDSDBClusterEventNotifications)
class RDSDBClusterEventNotifications(Named):
    groups = FieldProperty(schemas.IRDSDBClusterEventNotifications['groups'])
    event_categories = FieldProperty(schemas.IRDSDBClusterEventNotifications['event_categories'])

@implementer(schemas.IRDSDBInstanceEventNotifications)
class RDSDBInstanceEventNotifications(Named):
    groups = FieldProperty(schemas.IRDSDBInstanceEventNotifications['groups'])
    event_categories = FieldProperty(schemas.IRDSDBInstanceEventNotifications['event_categories'])

@implementer(schemas.IRDSOptionConfiguration)
class RDSOptionConfiguration():
    option_name = FieldProperty(schemas.IRDSOptionConfiguration['option_name'])
    option_settings = FieldProperty(schemas.IRDSOptionConfiguration['option_settings'])
    option_version = FieldProperty(schemas.IRDSOptionConfiguration['option_version'])
    port = FieldProperty(schemas.IRDSOptionConfiguration['port'])

@implementer(schemas.IRDS)
class RDS(ApplicationResource, Monitorable):
    backup_preferred_window = FieldProperty(schemas.IRDS['backup_preferred_window'])
    backup_retention_period = FieldProperty(schemas.IRDS['backup_retention_period'])
    cloudwatch_logs_export = FieldProperty(schemas.IRDS['cloudwatch_logs_exports'])
    db_snapshot_identifier = FieldProperty(schemas.IRDS['db_snapshot_identifier'])
    deletion_protection = FieldProperty(schemas.IRDS['deletion_protection'])
    dns = FieldProperty(schemas.IRDS['dns'])
    engine_version = FieldProperty(schemas.IRDS['engine_version'])
    kms_key_id = FieldProperty(schemas.IRDS['kms_key_id'])
    maintenance_preferred_window = FieldProperty(schemas.IRDS['maintenance_preferred_window'])
    master_username = FieldProperty(schemas.IRDS['master_username'])
    master_user_password = FieldProperty(schemas.IRDS['master_user_password'])
    port = FieldProperty(schemas.IRDS['port'])
    secrets_password = FieldProperty(schemas.IRDS['secrets_password'])
    security_groups = FieldProperty(schemas.IRDS['security_groups'])
    segment = FieldProperty(schemas.IRDS['segment'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dns = []
        self.cloudwatch_logs_exports = []
        self.backup_vault_plans = []

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

    def get_aws_name(self):
        "RDS Name for AWS"
        netenv = get_parent_by_interface(self, schemas.INetworkEnvironment)
        env = get_parent_by_interface(self, schemas.IEnvironment)
        app = get_parent_by_interface(self, schemas.IApplication)
        resource_group = get_parent_by_interface(self, schemas.IResourceGroup)
        name = self.create_resource_name_join(
                name_list=[
                    'ne',
                    netenv.name,
                    env.name,
                    'app',
                    app.name,
                    resource_group.name,
                    self.name,
                    'RDS'
                ],
                separator='-',
                camel_case=True
        )
        return name.lower()

    def get_arn(self):
        return 'arn:aws:rds:{}:{}:db:{}'.format(
            self.region_name,
            self.get_account().account_id,
            self.get_aws_name()
        )

@implementer(schemas.IRDSInstance)
class RDSInstance(RDS):
    allow_major_version_upgrade = FieldProperty(schemas.IRDSInstance['allow_major_version_upgrade'])
    auto_minor_version_upgrade = FieldProperty(schemas.IRDSInstance['auto_minor_version_upgrade'])
    db_instance_type = FieldProperty(schemas.IRDSInstance['db_instance_type'])
    license_model = FieldProperty(schemas.IRDSInstance['license_model'])
    option_configurations = FieldProperty(schemas.IRDSInstance['option_configurations'])
    parameter_group = FieldProperty(schemas.IRDSInstance['parameter_group'])
    publically_accessible = FieldProperty(schemas.IRDSInstance['publically_accessible'])
    storage_encrypted = FieldProperty(schemas.IRDSInstance['storage_encrypted'])
    storage_size_gb = FieldProperty(schemas.IRDSInstance['storage_size_gb'])
    storage_type = FieldProperty(schemas.IRDSInstance['storage_type'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.option_configurations = []

@implementer(schemas.IRDSMultiAZ)
class RDSMultiAZ(RDSInstance):
    multi_az = FieldProperty(schemas.IRDSMultiAZ['multi_az'])

@implementer(schemas.IRDSMysql)
class RDSPostgresql(RDSMultiAZ):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.engine = 'postgres'

@implementer(schemas.IRDSMysql)
class RDSMysql(RDSMultiAZ):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.engine = 'mysql'

class BaseRDSClusterInstance(Named, Enablable, Monitorable):

    @property
    def type(self):
        return self.dbcluster.type

@implementer(schemas.IRDSClusterDefaultInstance)
class RDSClusterDefaultInstance(BaseRDSClusterInstance):
    allow_major_version_upgrade = FieldProperty(schemas.IRDSClusterDefaultInstance['allow_major_version_upgrade'])
    auto_minor_version_upgrade = FieldProperty(schemas.IRDSClusterDefaultInstance['auto_minor_version_upgrade'])
    availability_zone = FieldProperty(schemas.IRDSClusterDefaultInstance['availability_zone'])
    db_instance_type = FieldProperty(schemas.IRDSClusterDefaultInstance['db_instance_type'])
    enable_performance_insights = FieldProperty(schemas.IRDSClusterDefaultInstance['enable_performance_insights'])
    enhanced_monitoring_interval_in_seconds = FieldProperty(schemas.IRDSClusterDefaultInstance['enhanced_monitoring_interval_in_seconds'])
    parameter_group = FieldProperty(schemas.IRDSClusterDefaultInstance['parameter_group'])
    publicly_accessible = FieldProperty(schemas.IRDSClusterDefaultInstance['publicly_accessible'])

    @property
    def dbcluster(self):
        return self.__parent__

@implementer(schemas.IRDSClusterInstance)
class RDSClusterInstance(BaseRDSClusterInstance):
    allow_major_version_upgrade = FieldProperty(schemas.IRDSClusterInstance['allow_major_version_upgrade'])
    auto_minor_version_upgrade = FieldProperty(schemas.IRDSClusterInstance['auto_minor_version_upgrade'])
    availability_zone = FieldProperty(schemas.IRDSClusterInstance['availability_zone'])
    db_instance_type = FieldProperty(schemas.IRDSClusterInstance['db_instance_type'])
    enable_performance_insights = FieldProperty(schemas.IRDSClusterInstance['enable_performance_insights'])
    enhanced_monitoring_interval_in_seconds = FieldProperty(schemas.IRDSClusterInstance['enhanced_monitoring_interval_in_seconds'])
    external_resource = FieldProperty(schemas.IRDSClusterInstance['external_resource'])
    external_instance_name = FieldProperty(schemas.IRDSClusterInstance['external_instance_name'])
    parameter_group = FieldProperty(schemas.IRDSClusterInstance['parameter_group'])
    publicly_accessible = FieldProperty(schemas.IRDSClusterInstance['publicly_accessible'])

    @property
    def dbcluster(self):
        return self.__parent__.__parent__

    def resolve_ref(self, ref):
        return self.dbcluster.resolve_ref_obj.resolve_ref(ref)

    def get_value_or_default(self, fieldname):
        "Return a field value or if does not exist fall-back to default_instance value if it exists"
        value = getattr(self, fieldname, None)
        if value == None:
            default_instance = self.dbcluster.default_instance
            return getattr(default_instance, fieldname, None)
        return value

@implementer(schemas.IRDSClusterInstances)
class RDSClusterInstances(Named, dict):
    pass

@implementer(schemas.IRDSAurora)
class RDSAurora(RDS):
    availability_zones = FieldProperty(schemas.IRDSAurora['availability_zones'])
    backtrack_window_in_seconds = FieldProperty(schemas.IRDSAurora['backtrack_window_in_seconds'])
    cluster_parameter_group = FieldProperty(schemas.IRDSAurora['cluster_parameter_group'])
    db_instances = FieldProperty(schemas.IRDSAurora['db_instances'])
    default_instance = FieldProperty(schemas.IRDSAurora['default_instance'])
    enable_http_endpoint = FieldProperty(schemas.IRDSAurora['enable_http_endpoint'])
    enable_kms_encryption = FieldProperty(schemas.IRDSAurora['enable_kms_encryption'])
    engine_mode = FieldProperty(schemas.IRDSAurora['engine_mode'])
    read_dns = FieldProperty(schemas.IRDSAurora['read_dns'])
    restore_type = FieldProperty(schemas.IRDSAurora['restore_type'])
    use_latest_restorable_time = FieldProperty(schemas.IRDSAurora['use_latest_restorable_time'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.db_instances = RDSClusterInstances('db_instances', self)

    @property
    def engine(self):
        "Engine: either aurora (MySQL 5.6), aurora-mysql(MySQL 5.7) or aurora-postgresql (PostgreSQL)"
        if hasattr(self, '_engine'):
            return self._engine
        if self.engine_version.startswith('5.6'):
            return 'aurora'
        else:
            return 'aurora-mysql'

    @property
    def backtrack_cfn(self):
        # only include BacktrackWindow for aurora mysql
        if self.engine in ('aurora', 'aurora-mysql'):
            return self.backtrack_window_in_seconds
        return None

    troposphere_props = troposphere.rds.DBCluster.props
    cfn_mapping = {
        # 'AssociatedRoles': not yet implmented
        # 'AvailabilityZones': computed in template
        'BacktrackWindow': 'backtrack_cfn',
        'BackupRetentionPeriod': 'backup_retention_period',
        'DatabaseName': 'database_name',
        # 'DBClusterIdentifier': computed in template
        # 'DBClusterParameterGroupName': computed in template
        # 'DBSubnetGroupName': computed in template
        'DeletionProtection': 'deletion_protection',
        # 'EnableCloudwatchLogsExports': computed in template
        'EnableHttpEndpoint': 'enable_http_endpoint',
        # 'EnableIAMDatabaseAuthentication': not yet implemented
        'Engine': 'engine',
        'EngineMode': 'engine_mode',
        'EngineVersion': 'engine_version',
        # 'KmsKeyId': not yet implemented
        # 'MasterUsername': computed in template
        # 'MasterUserPassword': computed in template
        'Port': 'port',
        'PreferredBackupWindow': 'backup_preferred_window',
        'PreferredMaintenanceWindow': 'maintenance_preferred_window',
        # 'ReplicationSourceIdentifier': not yet implemented
        'RestoreType': 'restore_type',
        # 'ScalingConfiguration': not yet implemented (only for Serverless)
        # 'SnapshotIdentifier': computed in template
        # 'SourceDBClusterIdentifier': not yet implemented
        # 'SourceRegion': not yet implemented
        # 'StorageEncrypted': not yet implemented
        # 'Tags': not yet implemented
        'UseLatestRestorableTime': 'use_latest_restorable_time',
        # 'VpcSecurityGroupIds': computed in template
    }

@implementer(schemas.IRDSMysqlAurora)
class RDSMysqlAurora(RDSAurora):
    type = 'RDSMysqlAurora'
    database_name = FieldProperty(schemas.IRDSMysqlAurora['database_name'])

@implementer(schemas.IRDSPostgresqlAurora)
class RDSPostgresqlAurora(RDSAurora):
    type = 'RDSPostgresqlAurora'
    database_name = FieldProperty(schemas.IRDSPostgresqlAurora['database_name'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self._engine = 'aurora-postgresql'


@implementer(schemas.IElastiCache)
class ElastiCache():
    description = FieldProperty(schemas.IElastiCache['description'])
    engine = FieldProperty(schemas.IElastiCache['engine'])
    engine_version = FieldProperty(schemas.IElastiCache['engine_version'])
    automatic_failover_enabled = FieldProperty(schemas.IElastiCache['automatic_failover_enabled'])
    port = FieldProperty(schemas.IElastiCache['port'])
    at_rest_encryption = FieldProperty(schemas.IElastiCache['at_rest_encryption'])
    number_of_read_replicas = FieldProperty(schemas.IElastiCache['number_of_read_replicas'])
    auto_minor_version_upgrade = FieldProperty(schemas.IElastiCache['auto_minor_version_upgrade'])
    az_mode = FieldProperty(schemas.IElastiCache['az_mode'])
    cache_node_type = FieldProperty(schemas.IElastiCache['cache_node_type'])
    maintenance_preferred_window = FieldProperty(schemas.IElastiCache['maintenance_preferred_window'])
    security_groups = FieldProperty(schemas.IElastiCache['security_groups'])
    segment = FieldProperty(schemas.IElastiCache['segment'])
    parameter_group = FieldProperty(schemas.IElastiCache['parameter_group'])
    cache_clusters = FieldProperty(schemas.IElastiCache['cache_clusters'])

@implementer(schemas.IElastiCacheRedis)
class ElastiCacheRedis(ApplicationResource, ElastiCache, Monitorable):
    cache_parameter_group_family = FieldProperty(schemas.IElastiCacheRedis['cache_parameter_group_family'])
    snapshot_retention_limit_days = FieldProperty(schemas.IElastiCacheRedis['snapshot_retention_limit_days'])
    snapshot_window = FieldProperty(schemas.IElastiCacheRedis['snapshot_window'])

    troposphere_props = troposphere.elasticache.ReplicationGroup.props
    cfn_mapping = {
        'AtRestEncryptionEnabled': 'at_rest_encryption',
        # 'AuthToken': (basestring, False),
        'AutoMinorVersionUpgrade': 'auto_minor_version_upgrade',
        'AutomaticFailoverEnabled': 'automatic_failover_enabled',
        'CacheNodeType': 'cache_node_type',
        'CacheParameterGroupName': 'parameter_group',
        # 'CacheSecurityGroupNames': ([basestring], False),
        # 'CacheSubnetGroupName': (basestring, False),
        'Engine': 'engine',
        'EngineVersion': 'engine_version',
        # 'KmsKeyId': (basestring, False),
        # 'NodeGroupConfiguration': (list, False),
        # 'NotificationTopicArn': (basestring, False),
        'NumCacheClusters': 'cache_clusters',
        # 'NumNodeGroups': (integer, False),
        'Port': 'port',
        # 'PreferredCacheClusterAZs': ([basestring], False),
        'PreferredMaintenanceWindow': 'maintenance_preferred_window',
        # 'PrimaryClusterId': (basestring, False),
        'ReplicasPerNodeGroup': 'number_of_read_replicas',
        # 'ReplicationGroupDescription': computed in template
        'ReplicationGroupId': 'cfn_aws_name',
        # 'SecurityGroupIds': computed in template
        # 'SnapshotArns': ([basestring], False),
        # 'SnapshotName': (basestring, False),
        'SnapshotRetentionLimit': 'snapshot_retention_limit_days',
        # 'SnapshottingClusterId': (basestring, False),
        'SnapshotWindow': 'snapshot_window',
        # 'Tags': (Tags, False),
        # 'TransitEncryptionEnabled': (boolean, False),
    }

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.engine = 'redis'
        self.port = 6379

    @property
    def cfn_aws_name(self):
        return self.get_aws_name()

    def get_aws_name(self):
        "ElastiCache Name for AWS"
        netenv = get_parent_by_interface(self, schemas.INetworkEnvironment)
        env = get_parent_by_interface(self, schemas.IEnvironment)
        app = get_parent_by_interface(self, schemas.IApplication)
        resource_group = get_parent_by_interface(self, schemas.IResourceGroup)
        result = self.create_resource_name_join(
            name_list=[app.name, resource_group.name, self.name],
            separator='-',
            filter_id='ElastiCache.ReplicationGroup.ReplicationGroupId',
            hash_long_names=True
        )
        # The replication group identifier is stored as a lowercase string
        # lower-case the name so that the Dimension name handles MiXeDCase.
        return result.lower()


@implementer(schemas.IESAdvancedOptions)
class ESAdvancedOptions(dict):
    "A dict of ElasticSearch key-value advanced options"

@implementer(schemas.IEBSOptions)
class EBSOptions(CFNExport):
    enabled = FieldProperty(schemas.IEBSOptions['enabled'])
    iops = FieldProperty(schemas.IEBSOptions['iops'])
    volume_size_gb = FieldProperty(schemas.IEBSOptions['volume_size_gb'])
    volume_type = FieldProperty(schemas.IEBSOptions['volume_type'])

    troposphere_props = troposphere.elasticsearch.EBSOptions.props
    cfn_mapping = {
        'EBSEnabled': 'enabled',
        'Iops': 'iops',
        'VolumeSize': 'volume_size_gb',
        'VolumeType': 'volume_type'
    }

@implementer(schemas.IElasticsearchCluster)
class ElasticsearchCluster(CFNExport):
    dedicated_master_count = FieldProperty(schemas.IElasticsearchCluster['dedicated_master_count'])
    dedicated_master_enabled = FieldProperty(schemas.IElasticsearchCluster['dedicated_master_enabled'])
    dedicated_master_type = FieldProperty(schemas.IElasticsearchCluster['dedicated_master_type'])
    instance_count = FieldProperty(schemas.IElasticsearchCluster['instance_count'])
    instance_type = FieldProperty(schemas.IElasticsearchCluster['instance_type'])
    zone_awareness_availability_zone_count = FieldProperty(schemas.IElasticsearchCluster['zone_awareness_availability_zone_count'])
    zone_awareness_enabled = FieldProperty(schemas.IElasticsearchCluster['zone_awareness_enabled'])

    @property
    def zone_awareness_availability_zone_count_cfn(self):
        if self.zone_awareness_enabled:
            return {'AvailabilityZoneCount': self.zone_awareness_availability_zone_count}

    troposphere_props = troposphere.elasticsearch.ElasticsearchClusterConfig.props
    cfn_mapping = {
        'DedicatedMasterCount': 'dedicated_master_count',
        'DedicatedMasterEnabled': 'dedicated_master_enabled',
        'DedicatedMasterType': 'dedicated_master_type',
        'InstanceCount': 'instance_count',
        'InstanceType': 'instance_type',
        'ZoneAwarenessConfig': 'zone_awareness_availability_zone_count_cfn',
        'ZoneAwarenessEnabled': 'zone_awareness_enabled',
    }

@implementer(schemas.IElasticsearchDomain)
class ElasticsearchDomain(ApplicationResource, Monitorable):
    type = "ElasticsearchDomain"
    access_policies_json = FieldProperty(schemas.IElasticsearchDomain['access_policies_json'])
    advanced_options = FieldProperty(schemas.IElasticsearchDomain['advanced_options'])
    ebs_volumes = FieldProperty(schemas.IElasticsearchDomain['ebs_volumes'])
    cluster = FieldProperty(schemas.IElasticsearchDomain['cluster'])
    elasticsearch_version = FieldProperty(schemas.IElasticsearchDomain['elasticsearch_version'])
    node_to_node_encryption = FieldProperty(schemas.IElasticsearchDomain['node_to_node_encryption'])
    snapshot_start_hour = FieldProperty(schemas.IElasticsearchDomain['snapshot_start_hour'])
    security_groups = FieldProperty(schemas.IElasticsearchDomain['security_groups'])
    segment = FieldProperty(schemas.IElasticsearchDomain['segment'])

    @property
    def ebsoptions_cfn(self):
        if self.ebs_volumes != None:
            return self.ebs_volumes.cfn_export_dict

    @property
    def cluster_cfn(self):
        if self.cluster != None:
            return self.cluster.cfn_export_dict

    @property
    def snapshot_cfn(self):
        if self.snapshot_start_hour != None:
            return {'AutomatedSnapshotStartHour': self.snapshot_start_hour}

    troposphere_props = troposphere.elasticsearch.Domain.props
    cfn_mapping = {
        # 'AccessPolicies': convert to JSON in the template
        'AdvancedOptions': 'advanced_options',
        # 'DomainName': computed by AWS,
        'EBSOptions': 'ebsoptions_cfn',
        'ElasticsearchClusterConfig': 'cluster_cfn',
        'ElasticsearchVersion': 'elasticsearch_version',
        # 'EncryptionAtRestOptions': (EncryptionAtRestOptions, False),
        'NodeToNodeEncryptionOptions': 'node_to_node_encryption',
        'SnapshotOptions': 'snapshot_cfn',
        # 'Tags': ((Tags, list), False),
        #'VPCOptions': computed in template,
    }

@implementer(schemas.IDeploymentPipelineConfiguration)
class DeploymentPipelineConfiguration(Named):
    artifacts_bucket = FieldProperty(schemas.IDeploymentPipelineConfiguration['artifacts_bucket'])
    account = FieldProperty(schemas.IDeploymentPipelineConfiguration['account'])

    def resolve_ref(self, ref):
        value = getattr(self, ref.resource_ref, None)
        if value != None:
            return value
        return self.resolve_ref_obj(ref)

@implementer(schemas.IDeploymentPipelineStageAction)
class DeploymentPipelineStageAction(Named, Enablable, dict):
    type = FieldProperty(schemas.IDeploymentPipelineStageAction['type'])
    run_order = FieldProperty(schemas.IDeploymentPipelineStageAction['run_order'])

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IDeploymentPipelineSourceCodeCommit)
class DeploymentPipelineSourceCodeCommit(DeploymentPipelineStageAction):
    codecommit_repository = FieldProperty(schemas.IDeploymentPipelineSourceCodeCommit['codecommit_repository'])
    deployment_branch_name = FieldProperty(schemas.IDeploymentPipelineSourceCodeCommit['deployment_branch_name'])

@implementer(schemas.IDeploymentPipelineLambdaInvoke)
class DeploymentPipelineLambdaInvoke(DeploymentPipelineStageAction):
    target_lambda = FieldProperty(schemas.IDeploymentPipelineLambdaInvoke['target_lambda'])
    user_parameters = FieldProperty(schemas.IDeploymentPipelineLambdaInvoke['user_parameters'])

@implementer(schemas.IDeploymentPipelinePacoCreateThenDeployImage)
class DeploymentPipelinePacoCreateThenDeployImage(DeploymentPipelineStageAction):
    resource_name = FieldProperty(schemas.IDeploymentPipelinePacoCreateThenDeployImage['resource_name'])


@implementer(schemas.IDeploymentPipelineSourceECR)
class DeploymentPipelineSourceECR(DeploymentPipelineStageAction):
    repository = FieldProperty(schemas.IDeploymentPipelineSourceECR['repository'])
    image_tag = FieldProperty(schemas.IDeploymentPipelineSourceECR['image_tag'])


@implementer(schemas.IDeploymentPipelineSourceGitHub)
class DeploymentPipelineSourceGitHub(DeploymentPipelineStageAction):
    deployment_branch_name = FieldProperty(schemas.IDeploymentPipelineSourceGitHub['deployment_branch_name'])
    github_owner = FieldProperty(schemas.IDeploymentPipelineSourceGitHub['github_owner'])
    github_repository = FieldProperty(schemas.IDeploymentPipelineSourceGitHub['github_repository'])
    github_access_token = FieldProperty(schemas.IDeploymentPipelineSourceGitHub['github_access_token'])
    poll_for_source_changes = FieldProperty(schemas.IDeploymentPipelineSourceGitHub['poll_for_source_changes'])

@implementer(schemas.IECRRepositoryPermission)
class ECRRepositoryPermission(Parent):
    repository = FieldProperty(schemas.IECRRepositoryPermission['repository'])
    permission = FieldProperty(schemas.IECRRepositoryPermission['permission'])

@implementer(schemas.IDeploymentPipelineBuildReleasePhase)
class DeploymentPipelineBuildReleasePhase(Named):
    ecs = FieldProperty(schemas.IDeploymentPipelineBuildReleasePhase['ecs'])

@implementer(schemas.IDeploymentPipelineBuildReleasePhaseCommand)
class DeploymentPipelineBuildReleasePhaseCommand(Parent):
    service = FieldProperty(schemas.IDeploymentPipelineBuildReleasePhaseCommand['service'])
    command = FieldProperty(schemas.IDeploymentPipelineBuildReleasePhaseCommand['command'])

@implementer(schemas.IDeploymentPipelineBuildCodeBuild)
class DeploymentPipelineBuildCodeBuild(DeploymentPipelineStageAction):
    buildspec = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['buildspec'])
    codebuild_image = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['codebuild_image'])
    codebuild_compute_type = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['codebuild_compute_type'])
    codecommit_repo_users = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['codecommit_repo_users'])
    deployment_environment = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['deployment_environment'])
    ecr_repositories = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['ecr_repositories'])
    privileged_mode = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['privileged_mode'])
    release_phase = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['release_phase'])
    role_policies = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['role_policies'])
    secrets = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['secrets'])
    timeout_mins = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['timeout_mins'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.codecommit_repo_users = []
        self.ecr_repositories = []
        self.role_policies = []

@implementer(schemas.IDeploymentPipelineDeployS3)
class DeploymentPipelineDeployS3(DeploymentPipelineStageAction):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.input_artifacts = []

    bucket = FieldProperty(schemas.IDeploymentPipelineDeployS3['bucket'])
    extract = FieldProperty(schemas.IDeploymentPipelineDeployS3['extract'])
    object_key = FieldProperty(schemas.IDeploymentPipelineDeployS3['object_key'])
    input_artifacts = FieldProperty(schemas.IDeploymentPipelineDeployS3['input_artifacts'])
    #kms_encryption_key_arn = FieldProperty(schemas.IDeploymentPipelineDeployS3['kms_encryption_key_arn'])

@implementer(schemas.IDeploymentPipelineManualApproval)
class DeploymentPipelineManualApproval(DeploymentPipelineStageAction):
    manual_approval_notification_email = FieldProperty(schemas.IDeploymentPipelineManualApproval['manual_approval_notification_email'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.manual_approval_notification_email = []

@implementer(schemas.ICodeDeployMinimumHealthyHosts)
class CodeDeployMinimumHealthyHosts(Named):
    type = FieldProperty(schemas.ICodeDeployMinimumHealthyHosts['type'])
    value = FieldProperty(schemas.ICodeDeployMinimumHealthyHosts['value'])


@implementer(schemas.IDeploymentPipelineDeployCodeDeploy)
class DeploymentPipelineDeployCodeDeploy(DeploymentPipelineStageAction):
    auto_scaling_group = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['auto_scaling_group'])
    auto_rollback_enabled = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['auto_rollback_enabled'])
    minimum_healthy_hosts = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['minimum_healthy_hosts'])
    deploy_style_option = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['deploy_style_option'])
    deploy_instance_role = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['deploy_instance_role'])
    elb_name = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['elb_name'])
    alb_target_group = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['alb_target_group'])


@implementer(schemas.IDeploymentPipelineDeployECS)
class DeploymentPipelineDeployECS(DeploymentPipelineStageAction):
    cluster = FieldProperty(schemas.IDeploymentPipelineDeployECS['cluster'])
    service = FieldProperty(schemas.IDeploymentPipelineDeployECS['service'])

@implementer(schemas.IDeploymentPipelineSourceStage)
class DeploymentPipelineSourceStage(Named, dict):
    pass

@implementer(schemas.IDeploymentPipelineBuildStage)
class DeploymentPipelineBuildStage(Named, dict):
    pass

@implementer(schemas.IDeploymentPipelineDeployStage)
class DeploymentPipelineDeployStage(Named, dict):
    pass

@implementer(schemas.ICodePipelineStage)
class CodePipelineStage(Named, dict):
    pass

@implementer(schemas.ICodePipelineStages)
class CodePipelineStages(Named, dict):
    pass

@implementer(schemas.IDeploymentPipeline)
class DeploymentPipeline(ApplicationResource, Monitorable):
    configuration = FieldProperty(schemas.IDeploymentPipeline['configuration'])
    source = FieldProperty(schemas.IDeploymentPipeline['source'])
    build = FieldProperty(schemas.IDeploymentPipeline['build'])
    deploy = FieldProperty(schemas.IDeploymentPipeline['deploy'])
    notification_events = FieldProperty(schemas.IDeploymentPipeline['notification_events'])
    stages = FieldProperty(schemas.IDeploymentPipeline['stages'])

    def resolve_ref(self, ref):
        if ref.resource_ref == 'kms':
            return self
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IEFSMount)
class EFSMount(Resource):
    folder = FieldProperty(schemas.IEFSMount['folder'])
    target = FieldProperty(schemas.IEFSMount['target'])

@implementer(schemas.IEFS)
class EFS(ApplicationResource):
    encrypted = FieldProperty(schemas.IEFS['encrypted'])
    security_groups = FieldProperty(schemas.IEFS['security_groups'])
    segment = FieldProperty(schemas.IEFS['segment'])

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IGenerateSecretString)
class GenerateSecretString(Parent, Deployable, CFNExport):
    """Generate SecretString"""
    exclude_characters = FieldProperty(schemas.IGenerateSecretString['exclude_characters'])
    exclude_lowercase = FieldProperty(schemas.IGenerateSecretString['exclude_lowercase'])
    exclude_numbers = FieldProperty(schemas.IGenerateSecretString['exclude_numbers'])
    exclude_punctuation = FieldProperty(schemas.IGenerateSecretString['exclude_punctuation'])
    exclude_uppercase = FieldProperty(schemas.IGenerateSecretString['exclude_uppercase'])
    generate_string_key = FieldProperty(schemas.IGenerateSecretString['generate_string_key'])
    include_space = FieldProperty(schemas.IGenerateSecretString['include_space'])
    password_length = FieldProperty(schemas.IGenerateSecretString['password_length'])
    require_each_included_type = FieldProperty(schemas.IGenerateSecretString['require_each_included_type'])
    secret_string_template = FieldProperty(schemas.IGenerateSecretString['secret_string_template'])

    troposphere_props = troposphere.secretsmanager.GenerateSecretString.props
    cfn_mapping = {
        'ExcludeUppercase': 'exclude_uppercase',
        'RequireEachIncludedType': 'require_each_included_type',
        'IncludeSpace': 'include_space',
        'ExcludeCharacters': 'exclude_characters',
        'GenerateStringKey': 'generate_string_key',
        'PasswordLength': 'password_length',
        'ExcludePunctuation': 'exclude_punctuation',
        'ExcludeLowercase': 'exclude_lowercase',
        'SecretStringTemplate': 'secret_string_template',
        'ExcludeNumbers': 'exclude_numbers',
    }

@implementer(schemas.ISecretsManagerSecret)
class SecretsManagerSecret(Named, Deployable):
    """Secrets Manager Application Name"""
    account = FieldProperty(schemas.ISecretsManagerSecret['account'])
    generate_secret_string = FieldProperty(schemas.ISecretsManagerSecret['generate_secret_string'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ISecretsManagerGroup)
class SecretsManagerGroup(Named, dict):
    """Secrets Manager Group"""

@implementer(schemas.ISecretsManagerApplication)
class SecretsManagerApplication(Named, dict):
    """Secrets Manager Application"""

@implementer(schemas.ISecretsManager)
class SecretsManager(Named, dict):
    """Secrets Manager"""

@implementer(schemas.IDeploymentGroupS3Location)
class DeploymentGroupS3Location(Parent):
    bucket = FieldProperty(schemas.IDeploymentGroupS3Location['bucket'])
    bundle_type = FieldProperty(schemas.IDeploymentGroupS3Location['bundle_type'])
    key = FieldProperty(schemas.IDeploymentGroupS3Location['key'])

@implementer(schemas.ICodeDeployDeploymentGroups)
class CodeDeployDeploymentGroups(Named, dict):
    pass

@implementer(schemas.ICodeDeployDeploymentGroup)
class CodeDeployDeploymentGroup(Named, Deployable):
    ignore_application_stop_failures = FieldProperty(schemas.ICodeDeployDeploymentGroup['ignore_application_stop_failures'])
    revision_location_s3 = FieldProperty(schemas.ICodeDeployDeploymentGroup['revision_location_s3'])
    autoscalinggroups = FieldProperty(schemas.ICodeDeployDeploymentGroup['autoscalinggroups'])
    role_policies = FieldProperty(schemas.ICodeDeployDeploymentGroup['role_policies'])

@implementer(schemas.ICodeDeployApplication)
class CodeDeployApplication(ApplicationResource):
    compute_platform = FieldProperty(schemas.ICodeDeployApplication['compute_platform'])
    deployment_groups = FieldProperty(schemas.ICodeDeployApplication['deployment_groups'])

@implementer(schemas.IIAMUserResource)
class IAMUserResource(ApplicationResource):
    allows = FieldProperty(schemas.IIAMUserResource['allows'])
    programmatic_access = FieldProperty(schemas.IIAMUserResource['programmatic_access'])
    account = FieldProperty(schemas.IIAMUserResource['account'])

@implementer(schemas.IPinpointSMSChannel)
class PinpointSMSChannel(Parent):
    enable_sms = FieldProperty(schemas.IPinpointSMSChannel['enable_sms'])
    sender_id = FieldProperty(schemas.IPinpointSMSChannel['sender_id'])
    short_code = FieldProperty(schemas.IPinpointSMSChannel['short_code'])

    troposphere_props = troposphere.pinpoint.SMSChannel.props
    cfn_mapping = {
        # 'ApplicationId':set in the template
        'Enabled': 'enable_sms',
        'SenderId': 'sender_id',
        'ShortCode': 'short_code',
    }

@implementer(schemas.IPinpointEmailChannel)
class PinpointEmailChannel(Parent):
    enable_email = FieldProperty(schemas.IPinpointEmailChannel['enable_email'])
    from_address = FieldProperty(schemas.IPinpointEmailChannel['from_address'])

    troposphere_props = troposphere.pinpoint.EmailChannel.props
    cfn_mapping = {
        # 'ApplicationId': set in the template
        # 'ConfigurationSet': (basestring, False), What is this?
        'Enabled': 'enable_email',
        'FromAddress': 'from_address',
        # 'Identity': set in the template
        # 'RoleArn': (basestring, False),
    }

@implementer(schemas.IPinpointApplication)
class PinpointApplication(ApplicationResource):
    sms_channel = FieldProperty(schemas.IPinpointApplication['sms_channel'])
    email_channel = FieldProperty(schemas.IPinpointApplication['email_channel'])

# DynamoDB

@implementer(schemas.IDynamoDBProvisionedThroughput)
class DynamoDBProvisionedThroughput(Named):
    read_capacity_units = FieldProperty(schemas.IDynamoDBProvisionedThroughput['read_capacity_units'])
    write_capacity_units = FieldProperty(schemas.IDynamoDBProvisionedThroughput['write_capacity_units'])

    troposphere_props = troposphere.dynamodb.ProvisionedThroughput.props
    cfn_mapping = {
        "ReadCapacityUnits": 'read_capacity_units',
        "WriteCapacityUnits": 'write_capacity_units',
    }

@implementer(schemas.IDynamoDBTables)
class DynamoDBTables(Named, dict):
    pass

@implementer(schemas.IDynamoDBAttributeDefinition)
class DynamoDBAttributeDefinition(Parent):
    name = FieldProperty(schemas.IDynamoDBAttributeDefinition['name'])
    type = FieldProperty(schemas.IDynamoDBAttributeDefinition['type'])

    troposphere_props = troposphere.dynamodb.AttributeDefinition.props
    cfn_mapping = {
        "AttributeName": 'name',
        "AttributeType": 'type',
    }

@implementer(schemas.IDynamoDBKeySchema)
class DynamoDBKeySchema(Parent):
    name = FieldProperty(schemas.IDynamoDBKeySchema['name'])
    type = FieldProperty(schemas.IDynamoDBKeySchema['type'])

    troposphere_props = troposphere.dynamodb.KeySchema.props
    cfn_mapping = {
        "AttributeName": 'name',
        "KeyType": 'type',
    }

@implementer(schemas.IDynamoDBProjection)
class DynamoDBProjection(Parent):
    type = FieldProperty(schemas.IDynamoDBProjection['type'])
    non_key_attributes = FieldProperty(schemas.IDynamoDBProjection['non_key_attributes'])

    troposphere_props = troposphere.dynamodb.KeySchema.props
    cfn_mapping = {
        "NonKeyAttributes": 'non_key_attributes',
        "ProjectionType": 'type',
    }

@implementer(schemas.IDynamoDBGlobalSecondaryIndex)
class DynamoDBGlobalSecondaryIndex(Parent):
    index_name = FieldProperty(schemas.IDynamoDBGlobalSecondaryIndex['index_name'])
    key_schema = FieldProperty(schemas.IDynamoDBGlobalSecondaryIndex['key_schema'])
    projection = FieldProperty(schemas.IDynamoDBGlobalSecondaryIndex['projection'])
    provisioned_throughput = FieldProperty(schemas.IDynamoDBGlobalSecondaryIndex['provisioned_throughput'])

    @property
    def key_schema_cfn(self):
        return [ key_schema.cfn_export_dict for key_schema in self.key_schema ]

    @property
    def projection_cfn(self):
        if self.projection == None:
            return None
        return self.projection.cfn_export_dict

    @property
    def provisioned_throughput_cfn(self):
        if self.provisioned_throughput == None:
            return None
        return self.provisioned_throughput.cfn_export_dict

    troposphere_props = troposphere.dynamodb.GlobalSecondaryIndex.props
    cfn_mapping = {
        "IndexName": 'index_name',
        "KeySchema": 'key_schema_cfn',
        "Projection": 'projection_cfn',
        "ProvisionedThroughput": 'provisioned_throughput_cfn',
    }

@implementer(schemas.IDynamoDBTargetTrackingScalingPolicy)
class DynamoDBTargetTrackingScalingPolicy(Parent):
    max_capacity = FieldProperty(schemas.IDynamoDBTargetTrackingScalingPolicy['max_capacity'])
    min_capacity = FieldProperty(schemas.IDynamoDBTargetTrackingScalingPolicy['min_capacity'])
    target_value = FieldProperty(schemas.IDynamoDBTargetTrackingScalingPolicy['target_value'])
    scale_in_cooldown = FieldProperty(schemas.IDynamoDBTargetTrackingScalingPolicy['scale_in_cooldown'])
    scale_out_cooldown = FieldProperty(schemas.IDynamoDBTargetTrackingScalingPolicy['scale_out_cooldown'])

@implementer(schemas.IDynamoDBTable)
class DynamoDBTable(Named, dict):
    attribute_definitions = FieldProperty(schemas.IDynamoDBTable['attribute_definitions'])
    billing_mode = FieldProperty(schemas.IDynamoDBTable['billing_mode'])
    key_schema = FieldProperty(schemas.IDynamoDBTable['key_schema'])
    global_secondary_indexes = FieldProperty(schemas.IDynamoDBTable['global_secondary_indexes'])
    provisioned_throughput = FieldProperty(schemas.IDynamoDBTable['provisioned_throughput'])
    target_tracking_scaling_policy = FieldProperty(schemas.IDynamoDBTable['target_tracking_scaling_policy'])

    def resolve_ref(self, ref):
        dynamodb = get_parent_by_interface(self, schemas.IDynamoDB)
        return dynamodb.stack

    @property
    def get_billing_mode(self):
        "Return default billing mode if not override locally"
        if self.billing_mode == None:
            dynamodb = get_parent_by_interface(self, schemas.IDynamoDB)
            return dynamodb.default_billing_mode
        return self.billing_mode

    @property
    def attribute_definitions_cfn(self):
        return [ attr_def.cfn_export_dict for attr_def in self.attribute_definitions ]

    @property
    def global_secondary_indexes_cfn(self):
        return [ gsi.cfn_export_dict for gsi in self.global_secondary_indexes ]

    @property
    def key_schema_cfn(self):
        return [ key_schema.cfn_export_dict for key_schema in self.key_schema ]

    @property
    def provisioned_throughput_cfn(self):
        """
        None if billing mode is pay_per_request, otherwise local provisioned_throughput
        if specified, otherwise default provisioned_throughput
        """
        if self.get_billing_mode == 'pay_per_request':
            return None
        if self.provisioned_throughput == None:
            dynamodb = get_parent_by_interface(self, schemas.IDynamoDB)
            return dynamodb.default_provisioned_throughput.cfn_export_dict
        return self.provisioned_throughput.cfn_export_dict

    @property
    def billing_mode_cfn(self):
        if self.billing_mode == 'pay_per_request':
            return 'PAY_PER_REQUEST'
        return 'PROVISIONED'

    troposphere_props = troposphere.dynamodb.Table.props
    cfn_mapping = {
        'AttributeDefinitions': 'attribute_definitions_cfn',
        'BillingMode': 'billing_mode_cfn',
        'GlobalSecondaryIndexes': 'global_secondary_indexes_cfn',
        'KeySchema': 'key_schema_cfn',
        # 'LocalSecondaryIndexes': ([LocalSecondaryIndex], False),
        # 'PointInTimeRecoverySpecification': (PointInTimeRecoverySpecification, False),
        'ProvisionedThroughput': 'provisioned_throughput_cfn',
        # 'SSESpecification': (SSESpecification, False),
        # 'StreamSpecification': (StreamSpecification, False),
        # 'TableName': generated by CloudFormation
        # 'Tags': (Tags, False),
        # 'TimeToLiveSpecification': (TimeToLiveSpecification, False),
    }

@implementer(schemas.IDynamoDB)
class DynamoDB(ApplicationResource):
    default_billing_mode = FieldProperty(schemas.IDynamoDB['default_billing_mode'])
    default_provisioned_throughput = FieldProperty(schemas.IDynamoDB['default_provisioned_throughput'])
    tables = FieldProperty(schemas.IDynamoDB['tables'])

# Cognito

@implementer(schemas.ICognitoUserPoolSchemaAttribute)
class CognitoUserPoolSchemaAttribute(Parent):
    attribute_name = FieldProperty(schemas.ICognitoUserPoolSchemaAttribute['attribute_name'])
    attribute_data_type = FieldProperty(schemas.ICognitoUserPoolSchemaAttribute['attribute_data_type'])
    mutable = FieldProperty(schemas.ICognitoUserPoolSchemaAttribute['mutable'])
    required = FieldProperty(schemas.ICognitoUserPoolSchemaAttribute['required'])

    @property
    def attribute_data_type_cfn(self):
        if self.attribute_data_type == 'boolean':
            return 'Boolean'
        elif self.attribute_data_type == 'datetime':
            return 'DateTime'
        elif self.attribute_data_type == 'number':
            return 'Number'
        elif self.attribute_data_type == 'string':
            return 'String'

    troposphere_props = troposphere.cognito.SchemaAttribute.props
    cfn_mapping = {
        'AttributeDataType': 'attribute_data_type_cfn',
        # 'DeveloperOnlyAttribute': (boolean, False),
        'Mutable': 'mutable',
        'Name': 'attribute_name',
        # 'NumberAttributeConstraints': (NumberAttributeConstraints, False),
        # 'StringAttributeConstraints': (StringAttributeConstraints, False),
        'Required': 'required',
    }

@implementer(schemas.ICognitoUICustomizations)
class CognitoUICustomizations(Named):
    logo_file = FieldProperty(schemas.ICognitoUICustomizations['logo_file'])
    css_file = FieldProperty(schemas.ICognitoUICustomizations['css_file'])

@implementer(schemas.ICognitoUserPoolClient)
class CognitoUserPoolClient(Named):
    allowed_oauth_flows = FieldProperty(schemas.ICognitoUserPoolClient['allowed_oauth_flows'])
    allowed_oauth_scopes = FieldProperty(schemas.ICognitoUserPoolClient['allowed_oauth_scopes'])
    callback_urls = FieldProperty(schemas.ICognitoUserPoolClient['callback_urls'])
    domain_name = FieldProperty(schemas.ICognitoUserPoolClient['domain_name'])
    generate_secret = FieldProperty(schemas.ICognitoUserPoolClient['generate_secret'])
    identity_providers = FieldProperty(schemas.ICognitoUserPoolClient['identity_providers'])
    logout_urls = FieldProperty(schemas.ICognitoUserPoolClient['logout_urls'])

    def resolve_ref(self, ref):
        return self.__parent__.__parent__.stack

    @property
    def allowed_oauth_flows_userpool_client_cfn(self):
        "AllowedOAuthFlowsUserPoolClient is True if any OAuth configuration is set"
        if len(self.allowed_oauth_flows) > 0 or len(self.allowed_oauth_scopes) > 0:
            return True
        return False

    @property
    def identity_providers_cfn(self):
        ips = []
        for ip in self.identity_providers:
            if ip == 'cognito':
                ips.append('COGNITO')
            elif ip == 'facebook':
                ips.append('Facebook')
            elif ip == 'google':
                ips.append('Google')
            elif ip == 'facebook':
                ips.append('LoginWithAmazon')
        return ips

    troposphere_props = troposphere.cognito.UserPoolClient.props
    cfn_mapping = {
        'AllowedOAuthFlows': 'allowed_oauth_flows',
        'AllowedOAuthFlowsUserPoolClient': 'allowed_oauth_flows_userpool_client_cfn',
        'AllowedOAuthScopes': 'allowed_oauth_scopes',
        # 'AnalyticsConfiguration': (AnalyticsConfiguration, False),
        'CallbackURLs': 'callback_urls',
        'ClientName': 'name',
        # 'DefaultRedirectURI': (basestring, False),
        # 'ExplicitAuthFlows': ([basestring], False),
        'GenerateSecret': 'generate_secret',
        'LogoutURLs': 'logout_urls',
        # 'PreventUserExistenceErrors': (basestring, False),
        # 'ReadAttributes': ([basestring], False),
        # 'RefreshTokenValidity': (positive_integer, False),
        'SupportedIdentityProviders': 'identity_providers_cfn',
        # 'UserPoolId': computed in template
        # 'WriteAttributes': ([basestring], False),
    }

@implementer(schemas.ICognitoUserPoolClients)
class CognitoUserPoolClients(Named, dict):
    pass

@implementer(schemas.ICognitoInviteMessageTemplates)
class CognitoInviteMessageTemplates(Named):
    email_subject = FieldProperty(schemas.ICognitoInviteMessageTemplates['email_subject'])
    email_message = FieldProperty(schemas.ICognitoInviteMessageTemplates['email_message'])
    sms_message = FieldProperty(schemas.ICognitoInviteMessageTemplates['sms_message'])

@implementer(schemas.ICognitoUserCreation)
class CognitoUserCreation(Named):
    admin_only = FieldProperty(schemas.ICognitoUserCreation['admin_only'])
    unused_account_validity_in_days = FieldProperty(schemas.ICognitoUserCreation['unused_account_validity_in_days'])
    invite_message_templates = FieldProperty(schemas.ICognitoUserCreation['invite_message_templates'])

@implementer(schemas.ICognitoEmailConfiguration)
class CognitoEmailConfiguration(Named):
    from_address = FieldProperty(schemas.ICognitoEmailConfiguration['from_address'])
    reply_to_address = FieldProperty(schemas.ICognitoEmailConfiguration['reply_to_address'])
    verification_message = FieldProperty(schemas.ICognitoEmailConfiguration['verification_message'])
    verification_subject = FieldProperty(schemas.ICognitoEmailConfiguration['verification_subject'])

@implementer(schemas.ICognitoUserPoolPasswordPolicy)
class CognitoUserPoolPasswordPolicy(Named):
    minimum_length = FieldProperty(schemas.ICognitoUserPoolPasswordPolicy['minimum_length'])
    require_lowercase = FieldProperty(schemas.ICognitoUserPoolPasswordPolicy['require_lowercase'])
    require_uppercase = FieldProperty(schemas.ICognitoUserPoolPasswordPolicy['require_uppercase'])
    require_numbers = FieldProperty(schemas.ICognitoUserPoolPasswordPolicy['require_numbers'])
    require_symbols = FieldProperty(schemas.ICognitoUserPoolPasswordPolicy['require_symbols'])

@implementer(schemas.ICognitoLambdaTriggers)
class CognitoLambdaTriggers(Parent):
    create_auth_challenge = FieldProperty(schemas.ICognitoLambdaTriggers['create_auth_challenge'])
    custom_message = FieldProperty(schemas.ICognitoLambdaTriggers['custom_message'])
    define_auth_challenge = FieldProperty(schemas.ICognitoLambdaTriggers['define_auth_challenge'])
    post_authentication = FieldProperty(schemas.ICognitoLambdaTriggers['post_authentication'])
    post_confirmation = FieldProperty(schemas.ICognitoLambdaTriggers['post_confirmation'])
    pre_authentication = FieldProperty(schemas.ICognitoLambdaTriggers['pre_authentication'])
    pre_sign_up = FieldProperty(schemas.ICognitoLambdaTriggers['pre_sign_up'])
    pre_token_generation = FieldProperty(schemas.ICognitoLambdaTriggers['pre_token_generation'])
    user_migration = FieldProperty(schemas.ICognitoLambdaTriggers['user_migration'])
    verify_auth_challenge_response = FieldProperty(schemas.ICognitoLambdaTriggers['verify_auth_challenge_response'])

@implementer(schemas.ICognitoUserPool)
class CognitoUserPool(Resource):
    app_clients = FieldProperty(schemas.ICognitoUserPool['app_clients'])
    account_recovery = FieldProperty(schemas.ICognitoUserPool['account_recovery'])
    auto_verified_attributes = FieldProperty(schemas.ICognitoUserPool['auto_verified_attributes'])
    email = FieldProperty(schemas.ICognitoUserPool['email'])
    lambda_triggers = FieldProperty(schemas.ICognitoUserPool['lambda_triggers'])
    mfa = FieldProperty(schemas.ICognitoUserPool['mfa'])
    mfa_methods = FieldProperty(schemas.ICognitoUserPool['mfa_methods'])
    schema = FieldProperty(schemas.ICognitoUserPool['schema'])
    user_creation = FieldProperty(schemas.ICognitoUserPool['user_creation'])
    ui_customizations = FieldProperty(schemas.ICognitoUserPool['ui_customizations'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.app_clients = CognitoUserPoolClients('app_clients', self)
        self.schema = []

    def resolve_ref(self, ref):
        return self.stack

    @property
    def account_recovery_cfn(self):
        if self.account_recovery == None:
            return []
        values = []
        count = 1
        for option in self.account_recovery.split(','):
            option = option.strip().lower()
            values.append({
                'Name': option,
                'Priority': count,
            })
            count += 1
        return { 'RecoveryMechanisms': values }

    @property
    def auto_verified_attributes_cfn(self):
        values = []
        for option in self.auto_verified_attributes.split(','):
            values.append(option.strip().lower())
        return values

    @property
    def admin_create_user_config_cfn(self):
        if self.user_creation == None:
            return None
        cfn_export_dict = {
            "AllowAdminCreateUserOnly" : self.user_creation.admin_only,
            "UnusedAccountValidityDays" : self.user_creation.unused_account_validity_in_days,
        }
        if self.user_creation.invite_message_templates != None:
            imt = self.user_creation.invite_message_templates
            imt_dict = {}
            if imt.email_message != None:
                imt_dict['EmailMessage'] = imt.email_message
            if imt.email_subject != None:
                imt_dict['EmailSubject'] = imt.email_subject
            if imt.sms_message != None:
                imt_dict['SMSMessage'] = imt.sms_message
            if imt_dict:
                cfn_export_dict['InviteMessageTemplate'] = imt_dict
        return cfn_export_dict

    @property
    def mfa_cfn(self):
        return self.mfa.upper()

    @property
    def email_configuration_cfn(self):
        if self.email == None:
            return None
        email_dict = {}
        if self.email.from_address != None:
            email_dict['From']= self.email.from_address
        if self.email.reply_to_address != None:
            email_dict['ReplyToEmailAddress'] = self.email.reply_to_address
        if email_dict:
            return email_dict
        return None

    @property
    def schema_cfn(self):
        return [schema_attr.cfn_export_dict for schema_attr in self.schema]

    @property
    def enabled_mfas_cfn(self):
        mfas = []
        for method in self.mfa_methods:
            if method == 'sms':
                mfas.append('SMS_MFA')
            elif method == 'software_token':
                mfas.append('SOFTWARE_TOKEN_MFA')
        return mfas

    @property
    def policies_cfn(self):
        if self.password == None:
            return None
        pass_dict = {}
        if self.password.minimum_length != None:
            pass_dict['MinimumLength'] = self.password.minimum_length
        if self.password.require_lowercase != None:
            pass_dict['RequireLowercase'] = self.password.require_lowercase
        if self.password.require_numbers != None:
            pass_dict['RequireNumbers'] = self.password.require_numbers
        if self.password.require_symbols != None:
            pass_dict['RequireSymbols'] = self.password.require_symbols
        if self.password.require_uppercase != None:
            pass_dict['RequireUppercase'] = self.password.require_uppercase
        if pass_dict:
            return {'PasswordPolicy': pass_dict}
        return None

    @property
    def email_verification_message_cfn(self):
        if self.email and self.email.verification_message != None:
            return self.email.verification_message

    @property
    def email_verification_subject_cfn(self):
        if self.email and self.email.verification_subject != None:
            return self.email.verification_subject

    troposphere_props = troposphere.cognito.UserPool.props
    cfn_mapping = {
        'AccountRecoverySetting': 'account_recovery_cfn',
        'AdminCreateUserConfig': 'admin_create_user_config_cfn',
        # 'AliasAttributes': ([basestring], False),
        'AutoVerifiedAttributes': 'auto_verified_attributes_cfn',
        # 'DeviceConfiguration': (DeviceConfiguration, False),
        'EmailConfiguration': 'email_configuration_cfn',
        'EmailVerificationMessage': 'email_verification_message_cfn',
        'EmailVerificationSubject': 'email_verification_subject_cfn',
        'EnabledMfas': 'enabled_mfas_cfn',
        # 'LambdaConfig': computed in template
        'MfaConfiguration': 'mfa_cfn',
        'Policies': 'policies_cfn',
        'Schema': 'schema_cfn',
        # 'SmsAuthenticationMessage': (basestring, False),
        # 'SmsConfiguration': computed in template
        # 'SmsVerificationMessage': (basestring, False),
        # 'UserPoolAddOns': (UserPoolAddOns, False),
        # 'UserPoolName': (basestring, False),
        # 'UserPoolTags': (dict, False),
        # 'UsernameAttributes': ([basestring], False),
        # 'UsernameConfiguration': (UsernameConfiguration, False),
        # 'VerificationMessageTemplate': (VerificationMessageTemplate, False),
    }

@implementer(schemas.ICognitoIdentityProvider)
class CognitoIdentityProvider(Parent):
    userpool_client = FieldProperty(schemas.ICognitoIdentityProvider['userpool_client'])
    serverside_token_check = FieldProperty(schemas.ICognitoIdentityProvider['serverside_token_check'])

@implementer(schemas.ICognitoIdentityPool)
class CognitoIdentityPool(Resource):
    allow_unauthenticated_identities = FieldProperty(schemas.ICognitoIdentityPool['allow_unauthenticated_identities'])
    identity_providers = FieldProperty(schemas.ICognitoIdentityPool['identity_providers'])
    unauthenticated_role = FieldProperty(schemas.ICognitoIdentityPool['unauthenticated_role'])
    authenticated_role = FieldProperty(schemas.ICognitoIdentityPool['authenticated_role'])

    troposphere_props = troposphere.cognito.IdentityPool.props
    cfn_mapping = {
        'AllowUnauthenticatedIdentities': 'allow_unauthenticated_identities',
        # 'CognitoEvents': (dict, False),
        # 'CognitoIdentityProviders': computed in template
        # 'CognitoStreams': (CognitoStreams, False),
        # 'DeveloperProviderName': (basestring, False),
        # 'IdentityPoolName': (basestring, False),
        # 'OpenIdConnectProviderARNs': ([basestring], False),
        # 'PushSync': (PushSync, False),
        # 'SamlProviderARNs': ([basestring], False),
        # 'SupportedLoginProviders': (dict, False),
    }
