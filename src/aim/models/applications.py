"""
All things Application Engine.
"""

from aim.models import loader
from aim.models import schemas
from aim.models.base import Named, Deployable, Regionalized, Resource, ServiceAccountRegion
from aim.models.locations import get_parent_by_interface
from aim.models.metrics import Monitorable, AlarmNotifications
from aim.models.vocabulary import application_group_types
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@implementer(schemas.IApplicationEngines)
class ApplicationEngines(Named, dict):
    pass

@implementer(schemas.IApplicationEngine)
class ApplicationEngine(Named, Deployable, Regionalized, dict):
    groups = FieldProperty(schemas.IApplicationEngine['groups'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.groups = ResourceGroups('groups', self)
        self.notifications = AlarmNotifications()

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
class ServiceEnvironment(ServiceAccountRegion, Named):
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
class ResourceGroup(Named, dict):

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

    def resolve_ref(self, ref):
        if ref.resource_ref == 'kms':
            return self
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IS3BucketPolicy)
class S3BucketPolicy():
    action = FieldProperty(schemas.IS3BucketPolicy['action'])
    aws = FieldProperty(schemas.IS3BucketPolicy['aws'])
    condition = FieldProperty(schemas.IS3BucketPolicy['condition'])
    effect = FieldProperty(schemas.IS3BucketPolicy['effect'])
    principal = FieldProperty(schemas.IS3BucketPolicy['principal'])
    resource_suffix = FieldProperty(schemas.IS3BucketPolicy['resource_suffix'])

    def __init__(self):
        self.processed = False

@implementer(schemas.IS3Bucket)
class S3Bucket(Resource, Deployable):
    bucket_name = FieldProperty(schemas.IS3Bucket['bucket_name'])
    account = FieldProperty(schemas.IS3Bucket['account'])
    deletion_policy = FieldProperty(schemas.IS3Bucket['deletion_policy'])
    policy = FieldProperty(schemas.IS3Bucket['policy'])
    region = FieldProperty(schemas.IS3Bucket['region'])
    cloudfront_origin = FieldProperty(schemas.IS3Bucket['cloudfront_origin'])
    external_resource = FieldProperty(schemas.IS3Bucket['external_resource'])

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

#@implementer(schemas.IService)
#class Service(Named, dict):
#    pass


@implementer(schemas.IASG)
class ASG(Resource, Monitorable):
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
    instance_iam_role =  FieldProperty(schemas.IASG['instance_iam_role'])
    instance_ami =  FieldProperty(schemas.IASG['instance_ami'])
    instance_key_pair =  FieldProperty(schemas.IASG['instance_key_pair'])
    instance_type =  FieldProperty(schemas.IASG['instance_type'])
    segment =  FieldProperty(schemas.IASG['segment'])
    termination_policies =  FieldProperty(schemas.IASG['termination_policies'])
    security_groups =  FieldProperty(schemas.IASG['security_groups'])
    target_groups = FieldProperty(schemas.IASG['target_groups'])
    load_balancers = FieldProperty(schemas.IASG['load_balancers'])
    termination_policies =  FieldProperty(schemas.IASG['termination_policies'])
    user_data_script =  FieldProperty(schemas.IASG['user_data_script'])
    instance_monitoring = FieldProperty(schemas.IASG['instance_monitoring'])
    scaling_policy_cpu_average = FieldProperty(schemas.IASG['scaling_policy_cpu_average'])

    def resolve_ref(self, ref):
        if ref.resource_ref == 'name':
            return self.resolve_ref_obj.resolve_ref(ref)
        elif ref.resource_ref == 'instance_iam_role':
            return self.instance_iam_role
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


@implementer(schemas.IPortProtocol)
class PortProtocol():
    port = FieldProperty(schemas.IPortProtocol['port'])
    protocol = FieldProperty(schemas.IPortProtocol['protocol'])

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
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IListenerRule)
class ListenerRule(Deployable):
    rule_type = FieldProperty(schemas.IListenerRule['rule_type'])
    priority = FieldProperty(schemas.IListenerRule['priority'])
    host = FieldProperty(schemas.IListenerRule['host'])
    redirect_host = FieldProperty(schemas.IListenerRule['redirect_host'])
    target_group = FieldProperty(schemas.IListenerRule['target_group'])

@implementer(schemas.IListener)
class Listener(PortProtocol):
    redirect = FieldProperty(schemas.IListener['redirect'])
    ssl_certificates = FieldProperty(schemas.IListener['ssl_certificates'])
    target_group = FieldProperty(schemas.IListener['target_group'])
    rules = FieldProperty(schemas.IListener['rules'])

@implementer(schemas.IDNS)
class DNS():
    hosted_zone = FieldProperty(schemas.IDNS['hosted_zone'])
    domain_name = FieldProperty(schemas.IDNS['domain_name'])
    ssl_certificate = FieldProperty(schemas.IDNS['ssl_certificate'])

    def resolve_ref(self, ref):
        if ref.resource_ref == "ssl_certificate.arn":
            return self.ssl_certificate
        return ref.resource.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ILBApplication)
class LBApplication(Resource, dict):
    target_groups = FieldProperty(schemas.ILBApplication['target_groups'])
    listeners = FieldProperty(schemas.ILBApplication['listeners'])
    dns = FieldProperty(schemas.ILBApplication['dns'])
    scheme = FieldProperty(schemas.ILBApplication['scheme'])
    security_groups = FieldProperty(schemas.ILBApplication['security_groups'])
    segment = FieldProperty(schemas.ILBApplication['segment'])

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IAWSCertificateManager)
class AWSCertificateManager(Resource):
    domain_name = FieldProperty(schemas.IAWSCertificateManager['domain_name'])
    subject_alternative_names = FieldProperty(schemas.IAWSCertificateManager['subject_alternative_names'])

    def resolve_ref(self, ref):
        if ref.resource_ref == 'domain_name':
            return self.domain_name
        if ref.parts[-2] == 'resources':
            return self
        return ref.resource.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ILambdaVariable)
class LambdaVariable():
    """
    Lambda Environment Variable
    """
    key = FieldProperty(schemas.ILambdaVariable['key'])
    value = FieldProperty(schemas.ILambdaVariable['value'])

@implementer(schemas.ILambdaEnvironment)
class LambdaEnvironment(dict):
    """
    Lambda Environment
    """
    variables = FieldProperty(schemas.ILambdaEnvironment['variables'])

@implementer(schemas.ILambdaFunctionCode)
class LambdaFunctionCode():
    s3_bucket = FieldProperty(schemas.ILambdaFunctionCode['s3_bucket'])
    s3_key = FieldProperty(schemas.ILambdaFunctionCode['s3_key'])

@implementer(schemas.ILambda)
class Lambda(Resource, Monitorable):
    """
    Lambda Function resource
    """
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

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ISNSTopicSubscription)
class SNSTopicSubscription():
    protocol = FieldProperty(schemas.ISNSTopicSubscription['protocol'])
    endpoint = FieldProperty(schemas.ISNSTopicSubscription['endpoint'])

@implementer(schemas.ISNSTopic)
class SNSTopic(Resource):
    display_name = FieldProperty(schemas.ISNSTopic['display_name'])
    subscriptions = FieldProperty(schemas.ISNSTopic['subscriptions'])

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ICloudFrontCustomOriginConfig)
class CloudFrontCustomOriginConfig():
    http_port = FieldProperty(schemas.ICloudFrontCustomOriginConfig['http_port'])
    https_port = FieldProperty(schemas.ICloudFrontCustomOriginConfig['https_port'])
    protocol_policy = FieldProperty(schemas.ICloudFrontCustomOriginConfig['protocol_policy'])
    ssl_protocols = FieldProperty(schemas.ICloudFrontCustomOriginConfig['ssl_protocols'])
    read_timeout = FieldProperty(schemas.ICloudFrontCustomOriginConfig['read_timeout'])
    keepalive_timeout = FieldProperty(schemas.ICloudFrontCustomOriginConfig['keepalive_timeout'])


@implementer(schemas.ICloudFrontCookies)
class CloudFrontCookies():
    forward = FieldProperty(schemas.ICloudFrontCookies['forward'])
    white_listed_names = FieldProperty(schemas.ICloudFrontCookies['white_listed_names'])

@implementer(schemas.ICloudFrontForwardedValues)
class CloudFrontForwardedValues():
    query_string = FieldProperty(schemas.ICloudFrontForwardedValues['query_string'])
    cookies = FieldProperty(schemas.ICloudFrontForwardedValues['cookies'])
    headers = FieldProperty(schemas.ICloudFrontForwardedValues['headers'])

    def __init__(self):
        self.cookies = CloudFrontCookies()

@implementer(schemas.ICloudFrontDefaultCacheBehaviour)
class CloudFrontDefaultCacheBehaviour():
    allowed_methods = FieldProperty(schemas.ICloudFrontDefaultCacheBehaviour['allowed_methods'])
    default_ttl = FieldProperty(schemas.ICloudFrontDefaultCacheBehaviour['default_ttl'])
    target_origin = FieldProperty(schemas.ICloudFrontDefaultCacheBehaviour['target_origin'])
    viewer_protocol_policy = FieldProperty(schemas.ICloudFrontDefaultCacheBehaviour['viewer_protocol_policy'])
    forwarded_values = FieldProperty(schemas.ICloudFrontDefaultCacheBehaviour['forwarded_values'])

    def __init__(self):
        self.forwarded_values = CloudFrontForwardedValues()

@implementer(schemas.ICloudFrontViewerCertificate)
class CloudFrontViewerCertificate(Deployable):
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
    domain_aliases = FieldProperty(schemas.ICloudFrontFactory['domain_aliases'])
    viewer_certificate = FieldProperty(schemas.ICloudFrontFactory['viewer_certificate'])

@implementer(schemas.ICloudFront)
class CloudFront(Resource, Deployable):
    domain_aliases = FieldProperty(schemas.ICloudFront['domain_aliases'])
    default_cache_behavior = FieldProperty(schemas.ICloudFront['default_cache_behavior'])
    viewer_certificate = FieldProperty(schemas.ICloudFront['viewer_certificate'])
    price_class = FieldProperty(schemas.ICloudFront['price_class'])
    custom_error_responses = FieldProperty(schemas.ICloudFront['custom_error_responses'])
    origins = FieldProperty(schemas.ICloudFront['origins'])
    webacl_id = FieldProperty(schemas.ICloudFront['webacl_id'])
    factory = FieldProperty(schemas.ICloudFront['factory'])

    def s3_origin_exists(self):
        for origin_config in self.origins.values():
            if origin_config.s3_bucket != None:
                return True
        return False


@implementer(schemas.IRDS)
class RDS():
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
    allow_minor_version_upgrade = FieldProperty(schemas.IRDS['allow_minor_version_upgrade'])
    publically_accessible = FieldProperty(schemas.IRDS['publically_accessible'])
    master_username = FieldProperty(schemas.IRDS['master_username'])
    master_user_password = FieldProperty(schemas.IRDS['master_user_password'])
    backup_preferred_window = FieldProperty(schemas.IRDS['backup_preferred_window'])
    backup_retention_period = FieldProperty(schemas.IRDS['backup_retention_period'])
    maintenance_preferred_window = FieldProperty(schemas.IRDS['maintenance_preferred_window'])
    security_groups = FieldProperty(schemas.IRDS['security_groups'])
    primary_domain_name = FieldProperty(schemas.IRDS['primary_domain_name'])
    primary_hosted_zone = FieldProperty(schemas.IRDS['primary_hosted_zone'])

@implementer(schemas.IRDSMysql)
class RDSMysql(RDS, Resource):
    multi_az = FieldProperty(schemas.IRDSMysql['multi_az'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.engine = 'mysql'

@implementer(schemas.IRDSAurora)
class RDSAurora(RDS, Resource):
    secondary_domain_name = FieldProperty(schemas.IRDSAurora['secondary_domain_name'])
    secondary_hosted_zone = FieldProperty(schemas.IRDSAurora['secondary_hosted_zone'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.engine = 'aurora'

@implementer(schemas.IElastiCache)
class ElastiCache():
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

@implementer(schemas.IElastiCacheRedis)
class ElastiCacheRedis(Resource, ElastiCache):
    cache_parameter_group_family = FieldProperty(schemas.IElastiCacheRedis['cache_parameter_group_family'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.engine = 'redis'
        self.port = 6379