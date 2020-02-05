"""
All things Application Engine.
"""

import troposphere
import troposphere.elasticache
import troposphere.s3
import troposphere.secretsmanager
import troposphere.autoscaling
import troposphere.elasticloadbalancingv2
from paco.models import loader
from paco.models import schemas
from paco.models.base import Parent, Named, Deployable, Regionalized, Resource, AccountRef, \
    DNSEnablable, CFNExport, md5sum
from paco.models.exceptions import InvalidPacoBucket
from paco.models.formatter import get_formatted_model_context, smart_join
from paco.models.locations import get_parent_by_interface
from paco.models.metrics import Monitorable, AlarmNotifications
from paco.models.vocabulary import application_group_types, aws_regions
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


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
class ResourceGroup(Named, Deployable, DNSEnablable):
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

#@implementer(schemas.IDeployment)
#class Deployment(Named, Deployable):
#    type = FieldProperty(schemas.IDeployment['type'])

@implementer(schemas.ICodePipeBuildDeploy)
class CodePipeBuildDeploy(Resource):
    title = "CodePipeBuildDeploy"
    deployment_environment = FieldProperty(schemas.ICodePipeBuildDeploy['deployment_environment'])
    deployment_branch_name = FieldProperty(schemas.ICodePipeBuildDeploy['deployment_branch_name'])
    manual_approval_enabled = FieldProperty(schemas.ICodePipeBuildDeploy['manual_approval_enabled'])
    manual_approval_notification_email = FieldProperty(schemas.ICodePipeBuildDeploy['manual_approval_notification_email'])
    auto_rollback_enabled = FieldProperty(schemas.ICodePipeBuildDeploy['auto_rollback_enabled'])
    deploy_config_type = FieldProperty(schemas.ICodePipeBuildDeploy['deploy_config_type'])
    deploy_style_option = FieldProperty(schemas.ICodePipeBuildDeploy['deploy_style_option'])
    deploy_config_value = FieldProperty(schemas.ICodePipeBuildDeploy['deploy_config_value'])
    elb_name = FieldProperty(schemas.ICodePipeBuildDeploy['elb_name'])
    tools_account = FieldProperty(schemas.ICodePipeBuildDeploy['tools_account'])
    cross_account_support = FieldProperty(schemas.ICodePipeBuildDeploy['cross_account_support'])
    asg = FieldProperty(schemas.ICodePipeBuildDeploy['asg'])
    alb_target_group = FieldProperty(schemas.ICodePipeBuildDeploy['alb_target_group'])
    artifacts_bucket = FieldProperty(schemas.ICodePipeBuildDeploy['artifacts_bucket'])
    codecommit_repository = FieldProperty(schemas.ICodePipeBuildDeploy['codecommit_repository'])
    deploy_instance_role = FieldProperty(schemas.ICodePipeBuildDeploy['deploy_instance_role'])
    codebuild_image = FieldProperty(schemas.ICodePipeBuildDeploy['codebuild_image'])
    codebuild_compute_type = FieldProperty(schemas.ICodePipeBuildDeploy['codebuild_compute_type'])
    timeout_mins = FieldProperty(schemas.ICodePipeBuildDeploy['timeout_mins'])

    def resolve_ref(self, ref):
        if ref.resource_ref == 'kms':
            return self
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IS3BucketPolicy)
class S3BucketPolicy(Parent):
    action = FieldProperty(schemas.IS3BucketPolicy['action'])
    aws = FieldProperty(schemas.IS3BucketPolicy['aws'])
    condition = FieldProperty(schemas.IS3BucketPolicy['condition'])
    effect = FieldProperty(schemas.IS3BucketPolicy['effect'])
    principal = FieldProperty(schemas.IS3BucketPolicy['principal'])
    resource_suffix = FieldProperty(schemas.IS3BucketPolicy['resource_suffix'])

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
    title = "S3Bucket"
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

        ne = get_parent_by_interface(self, schemas.INetworkEnvironment)
        app = get_parent_by_interface(self, schemas.IApplication)


        bucket_name_list_standard = [
                self.bucket_name_prefix,
                self.bucket_name,
                self.bucket_name_suffix,
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
            # NE buckets are in the format:
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
        # currently only seen in Services ... ToDo: allow these names to add an additional prefix?
        elif app != None:
            # Application buckets are in the format:
            # app-<app>-<resourcegroup>-<resource>-<bucket_name_prefix>-<bucketname>-<bucket_name_suffix>-<shortregionname>
            bucket_name_list.extend([
                'app',
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
            if self.bucket_name_prefix == None or self.bucket_name_suffix == None:
                raise InvalidPacoBucket("""
                Custom named bucket requires a bucket_name_prefix and bucket_name_suffix attributes to be set.

                {}
                """.format(get_formatted_model_context(self)))
            bucket_name_list.extend([
                self.bucket_name_prefix,
                self.name,
                self.bucket_name,
                self.bucket_name_suffix
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

#@implementer(schemas.IService)
#class Service(Named, dict):
#    pass

@implementer(schemas.IASGLifecycleHooks)
class ASGLifecycleHooks(Named, dict):
    title = 'ASGLifecycleHooks'
    pass

@implementer(schemas.IASGLifecycleHook)
class ASGLifecycleHook(Named, Deployable):
    title = 'ASGLifecycleHook'
    lifecycle_transition = FieldProperty(schemas.IASGLifecycleHook['lifecycle_transition'])
    notification_target_arn = FieldProperty(schemas.IASGLifecycleHook['notification_target_arn'])
    role_arn = FieldProperty(schemas.IASGLifecycleHook['role_arn'])
    default_result = FieldProperty(schemas.IASGLifecycleHook['default_result'])

@implementer(schemas.IASGScalingPolicies)
class ASGScalingPolicies(Named, dict):
    title = "ASGSCalingPolices"
    pass


@implementer(schemas.IASGScalingPolicy)
class ASGScalingPolicy(Named, Deployable):
    title = "ASGScalingPolicy"
    policy_type = FieldProperty(schemas.IASGScalingPolicy['policy_type'])
    adjustment_type = FieldProperty(schemas.IASGScalingPolicy['adjustment_type'])
    scaling_adjustment = FieldProperty(schemas.IASGScalingPolicy['scaling_adjustment'])
    cooldown = FieldProperty(schemas.IASGScalingPolicy['cooldown'])
    alarms = FieldProperty(schemas.IASGScalingPolicy['alarms'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.alarms = []

@implementer(schemas.IEIP)
class EIP(Resource):
    title = "Elastic IP"
    dns = FieldProperty(schemas.IEIP['dns'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dns = []

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IEBSVolumeMount)
class EBSVolumeMount(Parent, Deployable):
    title = 'EBS Volume Mount Folder and Volume reference'
    folder = FieldProperty(schemas.IEBSVolumeMount['folder'])
    volume = FieldProperty(schemas.IEBSVolumeMount['volume'])
    device = FieldProperty(schemas.IEBSVolumeMount['device'])
    filesystem = FieldProperty(schemas.IEBSVolumeMount['filesystem'])

@implementer(schemas.IEBS)
class EBS(Resource):
    title = "Elastic Block Store Volume"
    size_gib = FieldProperty(schemas.IEBS['size_gib'])
    availability_zone = FieldProperty(schemas.IEBS['availability_zone'])
    volume_type = FieldProperty(schemas.IEBS['volume_type'])

@implementer(schemas.IEC2LaunchOptions)
class EC2LaunchOptions(Named):
    title = "EC2 Launch Options"
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
    device_name =  FieldProperty(schemas.IBlockDeviceMapping['device_name'])
    ebs =  FieldProperty(schemas.IBlockDeviceMapping['ebs'])
    virtual_name =  FieldProperty(schemas.IBlockDeviceMapping['virtual_name'])

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
class ASGRollingUpdatePolicy(Named, Deployable):
    title = "RollingUpdatePolicy"
    max_batch_size = FieldProperty(schemas.IASGRollingUpdatePolicy['max_batch_size'])
    min_instances_in_service = FieldProperty(schemas.IASGRollingUpdatePolicy['min_instances_in_service'])
    pause_time = FieldProperty(schemas.IASGRollingUpdatePolicy['pause_time'])
    wait_on_resource_signals = FieldProperty(schemas.IASGRollingUpdatePolicy['wait_on_resource_signals'])

@implementer(schemas.IASG)
class ASG(Resource, Monitorable):
    title = "AutoScalingGroup"
    cfn_init =  FieldProperty(schemas.IASG['cfn_init'])
    desired_capacity =  FieldProperty(schemas.IASG['desired_capacity'])
    min_instances =  FieldProperty(schemas.IASG['min_instances'])
    max_instances =  FieldProperty(schemas.IASG['max_instances'])
    update_policy_max_batch_size =  FieldProperty(schemas.IASG['update_policy_max_batch_size'])
    update_policy_min_instances_in_service =  FieldProperty(schemas.IASG['update_policy_min_instances_in_service'])
    associate_public_ip_address =  FieldProperty(schemas.IASG['associate_public_ip_address'])
    cooldown_secs =  FieldProperty(schemas.IASG['cooldown_secs'])
    ebs_optimized =  FieldProperty(schemas.IASG['ebs_optimized'])
    health_check_type =  FieldProperty(schemas.IASG['health_check_type'])
    health_check_grace_period_secs =  FieldProperty(schemas.IASG['health_check_grace_period_secs'])
    eip =  FieldProperty(schemas.IASG['eip'])
    instance_iam_role =  FieldProperty(schemas.IASG['instance_iam_role'])
    instance_ami =  FieldProperty(schemas.IASG['instance_ami'])
    instance_ami_type =  FieldProperty(schemas.IASG['instance_ami_type'])
    instance_key_pair =  FieldProperty(schemas.IASG['instance_key_pair'])
    instance_type =  FieldProperty(schemas.IASG['instance_type'])
    segment =  FieldProperty(schemas.IASG['segment'])
    termination_policies =  FieldProperty(schemas.IASG['termination_policies'])
    security_groups =  FieldProperty(schemas.IASG['security_groups'])
    target_groups = FieldProperty(schemas.IASG['target_groups'])
    load_balancers = FieldProperty(schemas.IASG['load_balancers'])
    termination_policies =  FieldProperty(schemas.IASG['termination_policies'])
    user_data_script =  FieldProperty(schemas.IASG['user_data_script'])
    user_data_pre_script =  FieldProperty(schemas.IASG['user_data_pre_script'])
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

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.secrets = []
        self.target_groups = []
        self.load_balancers = []
        self.efs_mounts = []
        self.ebs_volume_mounts = []

    def get_aws_name(self):
        "AutoScalingGroup Name for AWS"
        netenv = get_parent_by_interface(self, schemas.INetworkEnvironment)
        env = get_parent_by_interface(self, schemas.IEnvironment)
        app = get_parent_by_interface(self, schemas.IApplication)
        resource_group = get_parent_by_interface(self, schemas.IResourceGroup)
        return self.create_resource_name_join(
                name_list=[
                    netenv.name,
                    env.name,
                    app.name,
                    resource_group.name,
                    self.name
                ],
                separator='-',
                camel_case=True
        )

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


@implementer(schemas.IEC2)
class EC2(Resource):
    "EC2"
    title = "EC2"


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
    health_check_interval = FieldProperty(schemas.ITargetGroup['health_check_interval'])
    health_check_timeout = FieldProperty(schemas.ITargetGroup['health_check_timeout'])
    healthy_threshold = FieldProperty(schemas.ITargetGroup['healthy_threshold'])
    unhealthy_threshold = FieldProperty(schemas.ITargetGroup['unhealthy_threshold'])
    health_check_http_code = FieldProperty(schemas.ITargetGroup['health_check_http_code'])
    health_check_path = FieldProperty(schemas.ITargetGroup['health_check_path'])
    connection_drain_timeout = FieldProperty(schemas.ITargetGroup['connection_drain_timeout'])

    def resolve_ref(self, ref):
        if ref.ref.endswith('.target_groups.'+self.name):
            return self
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IListenerRule)
class ListenerRule(Deployable):
    rule_type = FieldProperty(schemas.IListenerRule['rule_type'])
    priority = FieldProperty(schemas.IListenerRule['priority'])
    host = FieldProperty(schemas.IListenerRule['host'])
    redirect_host = FieldProperty(schemas.IListenerRule['redirect_host'])
    target_group = FieldProperty(schemas.IListenerRule['target_group'])

@implementer(schemas.IListeners)
class Listeners(Named, dict):
    pass

@implementer(schemas.IListener)
class Listener(Named, PortProtocol):
    redirect = FieldProperty(schemas.IListener['redirect'])
    ssl_certificates = FieldProperty(schemas.IListener['ssl_certificates'])
    target_group = FieldProperty(schemas.IListener['target_group'])
    rules = FieldProperty(schemas.IListener['rules'])

    troposphere_props = troposphere.elasticloadbalancingv2.Listener.props
    cfn_mapping = {
        # 'Certificates': computed in template
        # 'DefaultActions': computed in template
        # 'LoadBalancerArn': (basestring, True),
        'Port': 'port',
        'Protocol': 'protocol',
        # 'SslPolicy': (basestring, False)
    }

@implementer(schemas.IDNS)
class DNS(Parent):
    hosted_zone = FieldProperty(schemas.IDNS['hosted_zone'])
    domain_name = FieldProperty(schemas.IDNS['domain_name'])
    ssl_certificate = FieldProperty(schemas.IDNS['ssl_certificate'])
    ttl = FieldProperty(schemas.IDNS['ttl'])

    def resolve_ref(self, ref):
        if ref.resource_ref == "ssl_certificate.arn":
            return self.ssl_certificate
        return ref.resource.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ILBApplication)
class LBApplication(Resource):
    title = "Application ELB"
    target_groups = FieldProperty(schemas.ILBApplication['target_groups'])
    listeners = FieldProperty(schemas.ILBApplication['listeners'])
    dns = FieldProperty(schemas.ILBApplication['dns'])
    scheme = FieldProperty(schemas.ILBApplication['scheme'])
    security_groups = FieldProperty(schemas.ILBApplication['security_groups'])
    segment = FieldProperty(schemas.ILBApplication['segment'])
    idle_timeout_secs = FieldProperty(schemas.ILBApplication['idle_timeout_secs'])
    enable_access_logs = FieldProperty(schemas.ILBApplication['enable_access_logs'])
    access_logs_bucket = FieldProperty(schemas.ILBApplication['access_logs_bucket'])
    access_logs_prefix = FieldProperty(schemas.ILBApplication['access_logs_prefix'])

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IAWSCertificateManager)
class AWSCertificateManager(Resource):
    title = 'Certificate Manager'
    domain_name = FieldProperty(schemas.IAWSCertificateManager['domain_name'])
    subject_alternative_names = FieldProperty(schemas.IAWSCertificateManager['subject_alternative_names'])
    external_resource = FieldProperty(schemas.IAWSCertificateManager['external_resource'])

    def resolve_ref(self, ref):
        if ref.resource_ref == 'domain_name':
            return self.domain_name
        if ref.parts[-2] == 'resources':
            return self
        return ref.resource.resolve_ref_obj.resolve_ref(ref)

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

@implementer(schemas.ILambda)
class Lambda(Resource, Monitorable):
    """
    Lambda Function resource
    """
    title ="Lambda"
    description = FieldProperty(schemas.ILambda['description'])
    code = FieldProperty(schemas.ILambda['code'])
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

@implementer(schemas.ISNSTopic)
class SNSTopic(Resource):
    title = "SNSTopic"
    type = "SNSTopic"
    display_name = FieldProperty(schemas.ISNSTopic['display_name'])
    subscriptions = FieldProperty(schemas.ISNSTopic['subscriptions'])
    cross_account_access = FieldProperty(schemas.ISNSTopic['cross_account_access'])

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

@implementer(schemas.ICloudFrontDefaultCacheBehavior)
class CloudFrontDefaultCacheBehavior(Named):
    allowed_methods = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['allowed_methods'])
    cached_methods = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['cached_methods'])
    default_ttl = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['default_ttl'])
    min_ttl = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['min_ttl'])
    max_ttl = FieldProperty(schemas.ICloudFrontDefaultCacheBehavior['max_ttl'])
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

@implementer(schemas.ICloudFrontOrigin)
class CloudFrontOrigin(Named):
    s3_bucket = FieldProperty(schemas.ICloudFrontOrigin['s3_bucket'])
    domain_name = FieldProperty(schemas.ICloudFrontOrigin['domain_name'])
    custom_origin_config = FieldProperty(schemas.ICloudFrontOrigin['custom_origin_config'])

    def resolve_ref(self, ref):
        if ref.parts[-2] == 'origins':
            return ref.last_part

@implementer(schemas.ICloudFrontFactory)
class CloudFrontFactory(Named):
    title = 'CloudFront Factory'
    domain_aliases = FieldProperty(schemas.ICloudFrontFactory['domain_aliases'])
    viewer_certificate = FieldProperty(schemas.ICloudFrontFactory['viewer_certificate'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.domain_aliases = []

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ICloudFront)
class CloudFront(Resource, Deployable, Monitorable):
    title = "CloudFront"
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
class DBParameterGroup(Resource):
    title = "RDS DB Parameter Group"
    description = FieldProperty(schemas.IDBParameterGroup['description'])
    family = FieldProperty(schemas.IDBParameterGroup['family'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.parameters = DBParameters()

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IRDSOptionConfiguration)
class RDSOptionConfiguration():
    option_name = FieldProperty(schemas.IRDSOptionConfiguration['option_name'])
    option_settings = FieldProperty(schemas.IRDSOptionConfiguration['option_settings'])
    option_version = FieldProperty(schemas.IRDSOptionConfiguration['option_version'])
    port = FieldProperty(schemas.IRDSOptionConfiguration['port'])

@implementer(schemas.IRDS)
class RDS(Resource, Monitorable):
    title = "RDS"
    engine = FieldProperty(schemas.IRDS['engine'])
    engine_version = FieldProperty(schemas.IRDS['engine_version'])
    db_instance_type = FieldProperty(schemas.IRDS['db_instance_type'])
    segment = FieldProperty(schemas.IRDS['segment'])
    port = FieldProperty(schemas.IRDS['port'])
    storage_type = FieldProperty(schemas.IRDS['storage_type'])
    storage_size_gb = FieldProperty(schemas.IRDS['storage_size_gb'])
    storage_encrypted = FieldProperty(schemas.IRDS['storage_encrypted'])
    kms_key_id = FieldProperty(schemas.IRDS['kms_key_id'])
    allow_major_version_upgrade = FieldProperty(schemas.IRDS['allow_major_version_upgrade'])
    auto_minor_version_upgrade = FieldProperty(schemas.IRDS['auto_minor_version_upgrade'])
    publically_accessible = FieldProperty(schemas.IRDS['publically_accessible'])
    master_username = FieldProperty(schemas.IRDS['master_username'])
    master_user_password = FieldProperty(schemas.IRDS['master_user_password'])
    backup_preferred_window = FieldProperty(schemas.IRDS['backup_preferred_window'])
    backup_retention_period = FieldProperty(schemas.IRDS['backup_retention_period'])
    maintenance_preferred_window = FieldProperty(schemas.IRDS['maintenance_preferred_window'])
    security_groups = FieldProperty(schemas.IRDS['security_groups'])
    dns = FieldProperty(schemas.IRDS['dns'])
    db_snapshot_identifier = FieldProperty(schemas.IRDS['db_snapshot_identifier'])
    option_configurations = FieldProperty(schemas.IRDS['option_configurations'])
    license_model = FieldProperty(schemas.IRDS['license_model'])
    cloudwatch_logs_export = FieldProperty(schemas.IRDS['cloudwatch_logs_exports'])
    deletion_protection = FieldProperty(schemas.IRDS['deletion_protection'])
    parameter_group = FieldProperty(schemas.IRDS['parameter_group'])
    secrets_password = FieldProperty(schemas.IRDS['secrets_password'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dns = []
        self.option_configurations = []
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

@implementer(schemas.IRDSMysql)
class RDSMysql(RDS, Resource):
    title = "RDS Mysql"
    multi_az = FieldProperty(schemas.IRDSMysql['multi_az'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.engine = 'mysql'

@implementer(schemas.IRDSAurora)
class RDSAurora(RDS, Resource):
    title = 'RDS Aurora'
    secondary_domain_name = FieldProperty(schemas.IRDSAurora['secondary_domain_name'])
    secondary_hosted_zone = FieldProperty(schemas.IRDSAurora['secondary_hosted_zone'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.engine = 'aurora'

@implementer(schemas.IElastiCache)
class ElastiCache():
    title = "ElastiCache"
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
class ElastiCacheRedis(Resource, ElastiCache, Monitorable):
    title = "ElastiCache Redis"
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
class DeploymentPipelineStageAction(Named, Deployable, dict):
    type = FieldProperty(schemas.IDeploymentPipelineStageAction['type'])
    run_order = FieldProperty(schemas.IDeploymentPipelineStageAction['run_order'])

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IDeploymentPipelineSourceCodeCommit)
class DeploymentPipelineSourceCodeCommit(DeploymentPipelineStageAction):
    title = 'CodeBuild.Build'
    codecommit_repository = FieldProperty(schemas.IDeploymentPipelineSourceCodeCommit['codecommit_repository'])
    deployment_branch_name = FieldProperty(schemas.IDeploymentPipelineSourceCodeCommit['deployment_branch_name'])

@implementer(schemas.IDeploymentPipelineBuildCodeBuild)
class DeploymentPipelineBuildCodeBuild(DeploymentPipelineStageAction):
    title = 'CodeBuild.Build'
    deployment_environment = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['deployment_environment'])
    codebuild_image = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['codebuild_image'])
    codebuild_compute_type = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['codebuild_compute_type'])
    timeout_mins = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['timeout_mins'])
    role_policies = FieldProperty(schemas.IDeploymentPipelineBuildCodeBuild['role_policies'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.role_policies = []

@implementer(schemas.IDeploymentPipelineDeployS3)
class DeploymentPipelineDeployS3(DeploymentPipelineStageAction):
    title = 'S3.Deploy'
    bucket = FieldProperty(schemas.IDeploymentPipelineDeployS3['bucket'])
    extract = FieldProperty(schemas.IDeploymentPipelineDeployS3['extract'])
    object_key = FieldProperty(schemas.IDeploymentPipelineDeployS3['object_key'])
    #kms_encryption_key_arn = FieldProperty(schemas.IDeploymentPipelineDeployS3['kms_encryption_key_arn'])

@implementer(schemas.IDeploymentPipelineManualApproval)
class DeploymentPipelineManualApproval(DeploymentPipelineStageAction):
    title = 'ManualApproval'
    manual_approval_notification_email = FieldProperty(schemas.IDeploymentPipelineManualApproval['manual_approval_notification_email'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.manual_approval_notification_email = []

@implementer(schemas.ICodeDeployMinimumHealthyHosts)
class CodeDeployMinimumHealthyHosts(Named):
    title = 'CodeDeployMinimumHealthyHosts'
    type = FieldProperty(schemas.ICodeDeployMinimumHealthyHosts['type'])
    value = FieldProperty(schemas.ICodeDeployMinimumHealthyHosts['value'])


@implementer(schemas.IDeploymentPipelineDeployCodeDeploy)
class DeploymentPipelineDeployCodeDeploy(DeploymentPipelineStageAction):
    title = 'CodeDeploy.Source'
    auto_scaling_group = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['auto_scaling_group'])
    auto_rollback_enabled = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['auto_rollback_enabled'])
    minimum_healthy_hosts = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['minimum_healthy_hosts'])
    deploy_style_option = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['deploy_style_option'])
    deploy_instance_role = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['deploy_instance_role'])
    elb_name = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['elb_name'])
    alb_target_group = FieldProperty(schemas.IDeploymentPipelineDeployCodeDeploy['alb_target_group'])


@implementer(schemas.IDeploymentPipelineSourceStage)
class DeploymentPipelineSourceStage(Named, dict):
    pass

@implementer(schemas.IDeploymentPipelineBuildStage)
class DeploymentPipelineBuildStage(Named, dict):
    pass

@implementer(schemas.IDeploymentPipelineDeployStage)
class DeploymentPipelineDeployStage(Named, dict):
    pass

@implementer(schemas.IDeploymentPipeline)
class DeploymentPipeline(Resource):
    title = "DeploymentPipeline"
    configuration = FieldProperty(schemas.IDeploymentPipeline['configuration'])
    source = FieldProperty(schemas.IDeploymentPipeline['source'])
    build = FieldProperty(schemas.IDeploymentPipeline['build'])
    deploy = FieldProperty(schemas.IDeploymentPipeline['deploy'])

    def resolve_ref(self, ref):
        if ref.resource_ref == 'kms':
            return self
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IEFSMount)
class EFSMount(Resource):
    title = 'EFS Mount Folder and Target'
    folder = FieldProperty(schemas.IEFSMount['folder'])
    target = FieldProperty(schemas.IEFSMount['target'])

@implementer(schemas.IEFS)
class EFS(Resource):
    title = 'EFS'
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
    generate_secret_string = FieldProperty(schemas.ISecretsManagerSecret['generate_secret_string'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.generate_secret_string = GenerateSecretString(self)

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
class CodeDeployApplication(Resource):
    compute_platform = FieldProperty(schemas.ICodeDeployApplication['compute_platform'])
    deployment_groups = FieldProperty(schemas.ICodeDeployApplication['deployment_groups'])
