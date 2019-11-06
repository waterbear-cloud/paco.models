"""
The loader is responsible for reading an AIM Project and creating a tree of Python
model objects.
"""

from aim.models.locations import get_parent_by_interface
from aim.models.formatter import get_formatted_model_context
from aim.models.logging import CloudWatchLogSources, CloudWatchLogSource, MetricFilters, MetricFilter, \
    CloudWatchLogGroups, CloudWatchLogGroup, CloudWatchLogSets, CloudWatchLogSet, CloudWatchLogging, \
    MetricTransformation
from aim.models.exceptions import InvalidAimFieldType, InvalidAimProjectFile, UnusedAimProjectField, \
    TroposphereConversionError
from aim.models.metrics import MonitorConfig, Metric, ec2core, CloudWatchAlarm, SimpleCloudWatchAlarm, \
    AlarmSet, AlarmSets, AlarmNotifications, AlarmNotification, NotificationGroups, Dimension, \
    HealthChecks, CloudWatchLogAlarm
from aim.models.networks import NetworkEnvironment, Environment, EnvironmentDefault, \
    EnvironmentRegion, Segment, Network, VPC, VPCPeering, VPCPeeringRoute, NATGateway, VPNGateway, \
    PrivateHostedZone, SecurityGroup, IngressRule, EgressRule
from aim.models.project import Project, Credentials
from aim.models.applications import Application, ResourceGroups, ResourceGroup, RDS, CodePipeBuildDeploy, ASG, \
    Resource, Resources, LBApplication, TargetGroup, Listener, DNS, PortProtocol, EC2, S3Bucket, \
    S3NotificationConfiguration, S3LambdaConfiguration, \
    S3BucketPolicy, AWSCertificateManager, ListenerRule, Lambda, LambdaEnvironment, LambdaVpcConfig, \
    LambdaFunctionCode, LambdaVariable, SNSTopic, SNSTopicSubscription, \
    CloudFront, CloudFrontFactory, CloudFrontCustomErrorResponse, CloudFrontOrigin, CloudFrontCustomOriginConfig, \
    CloudFrontDefaultCacheBehavior, CloudFrontCacheBehavior, CloudFrontForwardedValues, CloudFrontCookies, CloudFrontViewerCertificate, \
    RDSMysql, ElastiCacheRedis, RDSOptionConfiguration, DeploymentPipeline, DeploymentPipelineConfiguration, \
    DeploymentPipelineSourceStage, DeploymentPipelineBuildStage, DeploymentPipelineDeployStage, \
    DeploymentPipelineSourceCodeCommit, DeploymentPipelineBuildCodeBuild, DeploymentPipelineDeployCodeDeploy, \
    DeploymentPipelineManualApproval, CodeDeployMinimumHealthyHosts, DeploymentPipelineDeployS3, \
    EFS, EFSMount, ASGScalingPolicies, ASGScalingPolicy, ASGLifecycleHooks, ASGLifecycleHook, EIP, \
    EBS, EBSVolumeMount, SecretsManager, SecretsManagerApplication, SecretsManagerGroup, SecretsManagerSecret, \
    GenerateSecretString, EC2LaunchOptions, DBParameterGroup, DBParameters
from aim.models.resources import EC2Resource, EC2KeyPair, S3Resource, \
    Route53Resource, Route53HostedZone, Route53RecordSet, Route53HostedZoneExternalResource, \
    CodeCommit, CodeCommitRepository, CodeCommitUser, \
    CloudTrailResource, CloudTrails, CloudTrail, \
    ApiGatewayRestApi, ApiGatewayMethods, ApiGatewayMethod, ApiGatewayStages, ApiGatewayStage, \
    ApiGatewayResources, ApiGatewayResource, ApiGatewayModels, ApiGatewayModel, \
    ApiGatewayMethodMethodResponse, ApiGatewayMethodMethodResponseModel, ApiGatewayMethodIntegration, \
    ApiGatewayMethodIntegrationResponse, \
    IAMResource, IAMUser, IAMUserPermission, IAMUserPermissions, IAMUserProgrammaticAccess, \
    IAMUserPermissionCodeCommitRepository, IAMUserPermissionCodeCommit, IAMUserPermissionAdministrator, \
    IAMUserPermissionCodeBuild, IAMUserPermissionCodeBuildResource, IAMUserPermissionCustomPolicy, \
    Route53HealthCheck
from aim.models.cfn_init import CloudFormationConfigSets, CloudFormationConfigurations, CloudFormationInitVersionedPackageSet, \
    CloudFormationInitPathOrUrlPackageSet, CloudFormationInitPackages, CloudFormationInitGroups, CloudFormationInitUsers, \
    CloudFormationInitSources, CloudFormationInitFiles, CloudFormationInitFile, CloudFormationInitCommands, \
    CloudFormationInitCommand, CloudFormationInitServices, CloudFormationConfiguration, CloudFormationInit, \
    CloudFormationParameters, CloudFormationInitServiceCollection, CloudFormationInitService
from aim.models.events import EventsRule
from aim.models.iam import IAMs, IAM, ManagedPolicy, Role, Policy, AssumeRolePolicy, Statement
from aim.models.base import get_all_fields, most_specialized_interfaces, NameValuePair, RegionContainer
from aim.models.accounts import Account, AdminIAMUser
from aim.models.references import Reference, TextReference, FileReference
from aim.models.vocabulary import aws_regions
from aim.models.references import resolve_ref, is_ref
from aim.models.yaml import ModelYAML
from aim.models import schemas
from pathlib import Path
from ruamel.yaml.compat import StringIO
from zope.schema.interfaces import ConstraintNotSatisfied, ValidationError
import aim.models.services
import itertools, os, copy
import logging
import pathlib
import pkg_resources
import re
import ruamel.yaml
import sys
import troposphere
import zope.schema
import zope.schema.interfaces
import zope.interface.exceptions


def get_logger():
    log = logging.getLogger("aim.models")
    log.setLevel(logging.DEBUG)
    return log

logger = get_logger()

DEPLOYMENT_PIPELINE_STAGE_ACTION_CLASS_MAP = {
    'CodeCommit.Source': DeploymentPipelineSourceCodeCommit,
    'CodeBuild.Build': DeploymentPipelineBuildCodeBuild,
    'ManualApproval': DeploymentPipelineManualApproval,
    'CodeDeploy.Deploy': DeploymentPipelineDeployCodeDeploy,
    'S3.Deploy': DeploymentPipelineDeployS3
}

IAM_USER_PERMISSIONS_CLASS_MAP = {
    'CodeBuild': IAMUserPermissionCodeBuild,
    'CodeCommit': IAMUserPermissionCodeCommit,
    'Administrator': IAMUserPermissionAdministrator,
    'CustomPolicy': IAMUserPermissionCustomPolicy
}

RESOURCES_CLASS_MAP = {
    'ApiGatewayRestApi': ApiGatewayRestApi,
    'ASG': ASG,
    'CodePipeBuildDeploy': CodePipeBuildDeploy,
    'ACM': AWSCertificateManager,
    'RDS': RDS,
    'DBParameterGroup': DBParameterGroup,
    'LBApplication': LBApplication,
    'EC2': EC2,
    'Lambda': Lambda,
    'ManagedPolicy': ManagedPolicy,
    'S3Bucket': S3Bucket,
    'SNSTopic': SNSTopic,
    'CloudFront': CloudFront,
    'RDSMysql': RDSMysql,
    'ElastiCacheRedis': ElastiCacheRedis,
    'DeploymentPipeline': DeploymentPipeline,
    'EFS': EFS,
    'EIP': EIP,
    'Route53HealthCheck': Route53HealthCheck,
    'EventsRule': EventsRule,
    'EBS': EBS,
    'EBSVolumeMount': EBSVolumeMount
}

SUB_TYPES_CLASS_MAP = {
    # CloudFormation Init
    CloudFormationInit: {
        'config_sets': ('dynamic_dict', CloudFormationConfigSets),
        'configurations': ('container', (CloudFormationConfigurations, CloudFormationConfiguration)),
        'parameters': ('dynamic_dict', CloudFormationParameters)
    },
    CloudFormationConfiguration: {
        'packages': ('obj', CloudFormationInitPackages),
        'commands': ('container', (CloudFormationInitCommands, CloudFormationInitCommand)),
        'files': ('container', (CloudFormationInitFiles, CloudFormationInitFile)),
        'services': ('obj', CloudFormationInitServices),
        'sources': ('dynamic_dict', CloudFormationInitSources)
    },
    CloudFormationInitPackages: {
        'apt': ('dynamic_dict', CloudFormationInitVersionedPackageSet),
        'msi': ('dynamic_dict', CloudFormationInitPathOrUrlPackageSet),
        'python': ('dynamic_dict', CloudFormationInitVersionedPackageSet),
        'rpm': ('dynamic_dict', CloudFormationInitPathOrUrlPackageSet),
        'rubygems': ('dynamic_dict', CloudFormationInitVersionedPackageSet),
        'yum': ('dynamic_dict', CloudFormationInitVersionedPackageSet)
    },
    CloudFormationInitServices: {
        'sysvinit': ('container', (CloudFormationInitServiceCollection, CloudFormationInitService)),
        'windows': ('container', (CloudFormationInitServiceCollection, CloudFormationInitService))
    },

    # Assorted unsorted
    EIP: {
        'dns': ('obj_list', DNS)
    },
    EFS: {
        'security_groups': ('str_list', TextReference)
    },
    DBParameterGroup: {
        'parameters': ('dynamic_dict', DBParameters)
    },
    DeploymentPipelineBuildCodeBuild: {
        'role_policies': ('obj_list', Policy)
    },
    DeploymentPipelineDeployCodeDeploy: {
        'minimum_healthy_hosts': ('direct_obj', CodeDeployMinimumHealthyHosts)
    },
    DeploymentPipeline: {
        'configuration': ('direct_obj', DeploymentPipelineConfiguration),
        'source': ('deployment_pipeline_stage', DeploymentPipelineSourceStage),
        'build': ('deployment_pipeline_stage', DeploymentPipelineBuildStage),
        'deploy': ('deployment_pipeline_stage', DeploymentPipelineDeployStage),
    },
    ApiGatewayRestApi: {
        'methods': ('container', (ApiGatewayMethods, ApiGatewayMethod)),
        'models': ('container', (ApiGatewayModels, ApiGatewayModel)),
        'resources': ('container', (ApiGatewayResources, ApiGatewayResource)),
        'stages': ('container', (ApiGatewayStages, ApiGatewayStage)),
    },
    ApiGatewayMethodIntegration: {
        'integration_responses': ('obj_list', ApiGatewayMethodIntegrationResponse),
    },
    ApiGatewayMethod: {
        'method_responses': ('obj_list', ApiGatewayMethodMethodResponse),
        'integration': ('direct_obj', ApiGatewayMethodIntegration),
    },
    ApiGatewayMethodMethodResponse: {
        'response_models': ('obj_list', ApiGatewayMethodMethodResponseModel)
    },
    RDSOptionConfiguration: {
        'option_settings': ('obj_list', NameValuePair)
    },
    RDSMysql: {
        'option_configurations': ('obj_list', RDSOptionConfiguration),
        'security_groups': ('str_list', TextReference),
        'dns': ('obj_list', DNS),
        'monitoring': ('direct_obj', MonitorConfig)
    },
    ElastiCacheRedis: {
        'security_groups': ('str_list', TextReference),
        'monitoring': ('direct_obj', MonitorConfig)
    },
    CloudFront: {
        'default_cache_behavior': ('direct_obj', CloudFrontDefaultCacheBehavior),
        'cache_behaviors': ('obj_list', CloudFrontCacheBehavior),
        'domain_aliases': ('obj_list', DNS),
        'custom_error_responses': ('obj_list', CloudFrontCustomErrorResponse),
        'origins': ('named_obj', CloudFrontOrigin),
        'viewer_certificate': ('direct_obj', CloudFrontViewerCertificate),
        'factory': ('named_obj', CloudFrontFactory),
        'monitoring': ('direct_obj', MonitorConfig),
    },
    CloudFrontDefaultCacheBehavior: {
        'allowed_methods': ('str_list', zope.schema.TextLine),
        'forwarded_values': ('direct_obj', CloudFrontForwardedValues)
    },
    CloudFrontCacheBehavior: {
        'allowed_methods': ('str_list', zope.schema.TextLine),
        'forwarded_values': ('direct_obj', CloudFrontForwardedValues)
    },
    CloudFrontForwardedValues: {
        'cookies': ('obj', CloudFrontCookies),
        'headers': ('str_list', zope.schema.TextLine),
    },
    CloudFrontCookies: {
        'whitelisted_names': ('str_list', zope.schema.TextLine)
    },
    CloudFrontOrigin: {
        'custom_origin_config': ('direct_obj', CloudFrontCustomOriginConfig)
    },
    CloudFrontCustomOriginConfig: {
        'ssl_protocols': ('str_list', zope.schema.TextLine)
    },
    CloudFrontFactory: {
        'domain_aliases': ('obj_list', DNS),
        'viewer_certificate': ('direct_obj', CloudFrontViewerCertificate),
    },
    SNSTopic: {
        'subscription': ('obj_list', SNSTopicSubscription),
    },
    # Resource sub-objects
    CloudWatchAlarm: {
        'dimensions': ('obj_list', Dimension)
    },
    CloudWatchLogAlarm: {
        'dimensions': ('obj_list', Dimension)
    },
    LBApplication: {
        'target_groups': ('named_obj', TargetGroup),
        'security_groups': ('str_list', TextReference),
        'listeners': ('named_obj', Listener),
        'dns': ('obj_list', DNS),
        'monitoring': ('direct_obj', MonitorConfig)
    },
    SimpleCloudWatchAlarm: {
        'dimensions': ('obj_list', Dimension)
    },
    ASGScalingPolicy: {
        'alarms': ('obj_list', SimpleCloudWatchAlarm),
        'dimensions': ('obj_list', Dimension)
    },
    ASG: {
        'security_groups': ('str_list', TextReference),
        'target_groups': ('str_list', TextReference),
        'monitoring': ('direct_obj', MonitorConfig),
        'instance_iam_role': ('direct_obj', Role),
        'efs_mounts': ('obj_list', EFSMount),
        'ebs_volume_mounts': ('obj_list', EBSVolumeMount),
        'scaling_policies': ('container', (ASGScalingPolicies, ASGScalingPolicy)),
        'lifecycle_hooks': ('container', (ASGLifecycleHooks, ASGLifecycleHook)),
        'secrets': ('str_list', TextReference),
        'launch_options': ('obj', EC2LaunchOptions),
        'cfn_init': ('obj_raw_config', CloudFormationInit)
    },
    EC2LaunchOptions: {
        'cfn_init_config_sets': ('str_list', zope.schema.TextLine)
    },
    Listener: {
        'redirect': ('direct_obj', PortProtocol),
        'rules': ('named_obj', ListenerRule)
    },
    EC2: {
        'security_groups': ('str_list', TextReference)
    },
    DeploymentPipelineManualApproval: {
        'manual_approval_notification_email': ('str_list', zope.schema.TextLine)
    },
    CodePipeBuildDeploy: {
        'artifacts_bucket': ('named_obj', S3Bucket)
    },
    S3Bucket: {
        'policy': ('obj_list', S3BucketPolicy),
        'notifications': ('direct_obj', S3NotificationConfiguration)
    },
    S3NotificationConfiguration: {
        'lambdas': ('obj_list', S3LambdaConfiguration)
    },
    CloudTrailResource: {
        'trails': ('container', (CloudTrails, CloudTrail)),
    },
    CloudTrail: {
        'cloudwatchlogs_log_group': ('direct_obj', CloudWatchLogGroup),
    },

    # monitoring and logging
    MonitorConfig: {
        'metrics': ('obj_list', Metric),
        'alarm_sets': ('alarm_sets', AlarmSets),
        'health_checks': ('type_container', (HealthChecks, RESOURCES_CLASS_MAP)),
        'log_sets': ('log_sets', CloudWatchLogSets),
        'notifications': ('notifications', AlarmNotifications)
    },
    CloudWatchLogging: {
        'log_sets': ('container', (CloudWatchLogSets, CloudWatchLogSet)),
    },
    CloudWatchLogGroup: {
        'metric_filters': ('container', (MetricFilters, MetricFilter)),
        'sources': ('container', (CloudWatchLogSources, CloudWatchLogSource)),
    },
    MetricFilter: {
        'metric_transformations': ('obj_list', MetricTransformation)
    },
    CloudWatchLogSet: {
        'log_groups': ('container', (CloudWatchLogGroups, CloudWatchLogGroup)),
    },
    RegionContainer: {
        'alarm_sets': ('twolevel_container', (AlarmSets, AlarmSet, CloudWatchAlarm))
    },

    # Networking
    NetworkEnvironment: {
        'vpc': ('direct_obj', VPC)
    },
    Network: {
        'vpc': ('direct_obj', VPC)
    },
    NATGateway: {
        'default_route_segments': ('str_list', TextReference)
    },
    VPC: {
        'nat_gateway': ('named_obj', NATGateway),
        'vpn_gateway': ('named_obj', VPNGateway),
        'private_hosted_zone': ('direct_obj', PrivateHostedZone),
        'segments': ('named_obj', Segment),
        'security_groups': ('named_twolevel_dict', SecurityGroup),
        'peering': ('named_obj', VPCPeering)
    },
    PrivateHostedZone: {
        'vpc_associations': ('str_list', zope.schema.TextLine)
    },
    VPCPeering: {
        'routing': ('obj_list', VPCPeeringRoute)
    },
    SecurityGroup: {
        'ingress': ('obj_list', IngressRule),
        'egress' : ('obj_list', EgressRule)
    },

    # Application
    Application: {
        'groups': ('container', (ResourceGroups, ResourceGroup)),
        'notifications': ('notifications', AlarmNotifications),
        'monitoring': ('direct_obj', MonitorConfig),
    },
    ResourceGroup: {
        'resources': ('type_container', (Resources, RESOURCES_CLASS_MAP)),
    },

    # IAM
    IAM: {
        'roles': ('direct_obj', Role)
        #'policies': ('named_obj', ManagedPolicies)
    },
    Role: {
        'policies': ('obj_list', Policy),
        'assume_role_policy': ('direct_obj', AssumeRolePolicy)
    },
    Policy: {
        'statement': ('obj_list', Statement)
    },
    Statement: {
        'action': ('str_list', zope.schema.TextLine),
        'resource': ('str_list', zope.schema.TextLine)
    },
    Lambda: {
        'environment': ('direct_obj', LambdaEnvironment),
        'code': ('direct_obj', LambdaFunctionCode),
        'iam_role': ('direct_obj', Role),
        'monitoring': ('direct_obj', MonitorConfig),
        'vpc_config': ('obj', LambdaVpcConfig)
    },
    LambdaVpcConfig: {
        'security_groups': ('str_list', TextReference),
        'segments': ('str_list', TextReference)
    },
    LambdaEnvironment: {
        'variables': ('obj_list', LambdaVariable)
    },
    ManagedPolicy: {
        'roles': ('str_list', zope.schema.TextLine),
        'statement': ('obj_list', Statement)
    },
    # Accounts
    Account: {
        'admin_iam_users': ('named_obj', AdminIAMUser)
    },
    Route53RecordSet: {
        'values': ('str_list', zope.schema.TextLine)
    },
    Route53HostedZone: {
        'record_sets': ('obj_list', Route53RecordSet),
        'external_resource': ('obj', Route53HostedZoneExternalResource)
    },
    Route53Resource: {
        'hosted_zones': ('named_obj', Route53HostedZone)
    },
    SNSTopic: {
        'subscriptions': ('obj_list', SNSTopicSubscription)
    },
    CodeCommitRepository: {
        'users': ('named_obj', CodeCommitUser)
    },
    IAMResource: {
        'users': ('named_obj', IAMUser)
    },
    IAMUser: {
        'programmatic_access': ('direct_obj', IAMUserProgrammaticAccess),
        'permissions': ('iam_user_permissions', IAMUserPermissions)
    },
    IAMUserPermissionCodeBuild: {
        'resources': ('obj_list', IAMUserPermissionCodeBuildResource)
    },
    IAMUserPermissionCodeCommit: {
        'repositories': ('obj_list', IAMUserPermissionCodeCommitRepository)
    },
    IAMUserPermissionCustomPolicy: {
        'policies': ('obj_list', Policy)
    },
    # Secrets Manager
    SecretsManagerSecret: {
        'generate_secret_string': ('direct_obj', GenerateSecretString)
    }
}

def deepcopy_except_parent(obj):
    """Returns a deepcopy on on the object, but does not recurse up the
    __parent__ attribute to prevent copying the entire model.
    """
    if not hasattr(obj, '__parent__'):
        return copy.deepcopy(obj)

    # set __parent__ to None, copy the object, then restore __parent__
    parent = getattr(obj, '__parent__', None)
    obj.__parent__ = None
    copy_obj = copy.deepcopy(obj)
    obj.__parent__ = parent
    return copy_obj

def merge(base, override):
    """
    Merge two dictionaries of arbitray depth
    """
    if isinstance(base, dict) and isinstance(override, dict):
        new_dict = dict(base)
        new_dict.update(
            {k: merge(base.get(k, None), override[k]) for k in override}
        )
        return new_dict

    if isinstance(base, list) and isinstance(override, list):
        return [merge(x, y) for x, y in itertools.zip_longest(base, override)]

    return deepcopy_except_parent(base) if override is None else deepcopy_except_parent(override)

def annotate_base_config(obj, override_config, base_config):
    """
    Adds attributes prefixed with __base__<name> with values from the
    base configuration for every attribute that has been overriden.
    """
    for name in override_config.keys():
        value = getattr(base_config, name, None)
        if value:
            setattr(obj, '__base__' + name, value)

def gen_yaml_filename(folder, filename):
    for ext in ['.yaml', '.yml']:
        yaml_file = os.path.join(folder, filename+ext)
        if os.path.isfile(yaml_file):
            return yaml_file
    return yaml_file


def get_all_nodes(root):
    "Return a list of all nodes in aim.model"
    nodes = []
    stack = [root]
    while stack:
        cur_node = stack[0]
        stack = stack[1:]
        nodes.append(cur_node)
        if type({}) == type(cur_node) or zope.interface.common.mapping.IMapping.providedBy(cur_node):
            for child in cur_node.values():
                stack.insert(0, child)
        # check for obj or dict attributes
        for field_name, field in get_all_fields(cur_node).items():
            # drill down into objects for non-locatable nodes
            if zope.schema.interfaces.IObject.providedBy(field):
                obj = getattr(cur_node, field_name, None)
                if obj:
                    stack.insert(0, obj)
            elif zope.schema.interfaces.IDict.providedBy(field):
                # dicts are model nodes, don't return them - only their values
                obj = getattr(cur_node, field_name, None)
                if obj:
                    for child in obj.values():
                        stack.insert(0, child)
            elif zope.schema.interfaces.IList.providedBy(field):
                # skip computed fields
                if field.readonly: continue
                # don't drill down into lists of strings - only lists of model objects
                if getattr(cur_node, field_name, []) == None:
                    message = "Field name is None: {}\n".format(field_name)
                    if hasattr(cur_node, 'aim_ref_parts'):
                        message += "Ref: {}\n".format(cur_node.aim_ref_parts)
                    raise InvalidAimProjectFile(message)
                for obj in getattr(cur_node, field_name, []):
                    if type(obj) != type(''):
                        stack.insert(0, obj)
    return nodes

def add_metric(obj, metric):
    """Add metrics to a resource"""
    if not obj.monitoring:
        obj.monitoring = MonitorConfig('monitoring', obj)
    obj.monitoring.metrics.insert(0, metric)


def cast_to_schema(obj, fieldname, value, fields=None):
    """
    Return a value that has been cast to match the schema of the field.
    For example, YAML will cast a bare 10 to an int(), but if the field to be set is a float()
    it needs to be cast to a float().
    """
    if fields == None:
        fields = get_all_fields(obj)
    field = fields[fieldname]
    if zope.schema.interfaces.IFloat.providedBy(field):
        return float(value)
    if schemas.IYAMLFileReference.providedBy(field):
        # Prevent Troposphere objects from being cast to a string
        return value
    if isinstance(field, (zope.schema.TextLine, zope.schema.Text)) and type(value) != str:
        # YAML loads 'field: 404' as an Int where the field could be Text or TextLine
        # You can force a string with "field: '404'" but this removes the need to do that.
        value = str(value)
    return value

def apply_attributes_from_config(obj, config, config_folder=None, lookup_config=None, read_file_path=''):
    """
    Iterates through the field an object's schema has
    and applies the values from configuration.

    Also handles loading of sub-types ...
    """
    # throw an error if there are fields which do not match the schema
    fields = get_all_fields(obj)
    if not zope.interface.common.mapping.IMapping.providedBy(obj):
        for key in config.keys():
            if key not in fields:
                raise UnusedAimProjectField("""Error in config file at: {}
Unneeded field: {}.{}

Verify that '{}' has the correct indentation in the config file.
""".format(read_file_path, obj.__class__.__name__, key, key))

    # all most-specialized interfaces implemented by obj
    for interface in most_specialized_interfaces(obj):
        fields = zope.schema.getFields(interface)
        for name, field in fields.items():
            if schemas.IEnvironmentDefault.providedBy(obj) and name == 'secrets_manager':
                continue
            if schemas.IEnvironmentDefault.providedBy(obj) and name == 'applications':
                continue
            if schemas.IEnvironmentDefault.providedBy(obj) and name == 'network':
                continue

            # Locatable Objects get their name from their key in the config, for example:
            #   environments:
            #     demo:
            # creates an Environment with the name 'demo'.
            # These objects implement the INamed interface.
            # Do not try to find their 'name' attr from the config.
            if name != 'name' or not schemas.INamed.providedBy(obj):
                value = config.get(name, None)
                # FileReferences load the string from file - the original path value is lost ¯\_(ツ)_/¯
                if schemas.IFileReference.providedBy(field) and value:
                    if read_file_path:
                        # set it to the containing directory of the file
                        path = Path(read_file_path)
                        base_path = os.sep.join(path.parts[:-1])[1:]
                    else:
                        base_path = None
                    # Load as a YAML - parse !Sub, !Join and other CloudFormation Functions
                    value = load_string_from_path(
                        value,
                        base_path=base_path,
                        is_yaml=schemas.IYAMLFileReference.providedBy(field)
                    )

                # CommaList: Parse comma separated list into python list()
                elif type(field) == type(schemas.CommaList()):
                    value = []
                    for list_value in config[name].split(','):
                        value.append(list_value.strip())

                if value != None:
                    value = cast_to_schema(obj, name, value, fields)
                    # is the value a reference?
                    if type(value) == type(str()) and is_ref(value):
                        # some fields are meant to be reference only
                        if schemas.ITextReference.providedBy(field):
                            setattr(obj, name, value)
                        else:
                            # reference - set a special _ref_ attribute for later look-up
                            setattr(obj, '_ref_' + name, deepcopy_except_parent(value))
                        continue

                    try:
                        if type(obj) in SUB_TYPES_CLASS_MAP:
                            if name in SUB_TYPES_CLASS_MAP[type(obj)]:
                                value = sub_types_loader(
                                    obj,
                                    name,
                                    value,
                                    config_folder,
                                    lookup_config,
                                    read_file_path
                                )
                                setattr(obj, name, value)
                            else:
                                setattr(obj, name, deepcopy_except_parent(value))
                        else:
                            setattr(obj, name, deepcopy_except_parent(value))
                    except (ValidationError, AttributeError) as exc:
                        raise_invalid_schema_error(obj, name, value, read_file_path, exc)

    # validate the object
    # don't validate credentials as sometimes it's left blank
    # ToDo: validate it if exists ...
    if schemas.ICredentials.providedBy(obj):
        return
    for interface in most_specialized_interfaces(obj):
        # invariants (these are also validate if they are explicitly part of a schema.Object() field)
        try:
            interface.validateInvariants(obj)
        except zope.interface.exceptions.Invalid as exc:
            raise_invalid_schema_error(obj, name, value, read_file_path, exc)

        # validate all fields - this catches validation for required fields
        fields = zope.schema.getFields(interface)
        for name, field in fields.items():
            try:
                if not field.readonly:
                    field.validate(getattr(obj, name, None))
            except ValidationError as exc:
                raise_invalid_schema_error(obj, name, value, read_file_path, exc)

def raise_invalid_schema_error(obj, name, value, read_file_path, exc):
    """
    Raise an InvalidAimProjectFile error with helpful information
    """
    try:
        field_context_name = exc.field.context.name
    except AttributeError:
        field_context_name = 'Not applicable'

    hint = ""
    if not schemas.IResource.providedBy(obj):
        if type(obj) not in SUB_TYPES_CLASS_MAP:
            hint = "Hint: {} was not found in the SUB_TYPES_CLASS_MAP or RESOURCES_CLASS_MAP\n".format(obj.__class__.__name__)
        elif name not in SUB_TYPES_CLASS_MAP[type(obj)]:
            hint = "Hint: {} not found in SUB_TYPES_CLASS_MAP[{}]\n".format(name, obj.__class__.__name__)
    raise InvalidAimProjectFile(
        """Error in file at {}

Invalid config for field '{}' for object type '{}'.
Exception: {}
Value supplied: {}
Field Context name: {}
Reason: {}

{}
Object
------
{}
""".format(read_file_path, name, obj.__class__.__name__, exc, value, field_context_name, exc.__doc__, hint, get_formatted_model_context(obj))
    )

def sub_types_loader(obj, name, value, config_folder=None, lookup_config=None, read_file_path=''):
    """
    Load sub types
    """
    sub_type, sub_class = SUB_TYPES_CLASS_MAP[type(obj)][name]

    if sub_type == 'named_obj':
        sub_dict = {}
        for sub_key, sub_value in value.items():
            # ToDo: named objects should always implement INamed - do we have exceptions?
            if schemas.INamed.implementedBy(sub_class):
                sub_obj = sub_class(sub_key, obj)
            elif schemas.IParent.implementedBy(sub_class):
                sub_obj = sub_class(obj)
            else:
                sub_obj = sub_class()
            apply_attributes_from_config(sub_obj, sub_value, config_folder, lookup_config, read_file_path)
            sub_dict[sub_key] = sub_obj
        return sub_dict

    elif sub_type == 'obj':
        sub_obj = sub_class(name, obj)
        apply_attributes_from_config(sub_obj, value, config_folder, lookup_config, read_file_path)
        return sub_obj

    elif sub_type == 'obj_raw_config':
        sub_obj = sub_class(name, obj)
        apply_attributes_from_config(sub_obj, value, config_folder, lookup_config, read_file_path)
        sub_obj.raw_config = value
        return sub_obj

    elif sub_type == 'container':
        container_class = sub_class[0]
        object_class = sub_class[1]
        container = container_class(name, obj)
        for sub_key, sub_value in value.items():
            sub_obj = object_class(sub_key, container)
            apply_attributes_from_config(sub_obj, sub_value, config_folder, lookup_config, read_file_path)
            container[sub_key] = sub_obj
        return container

    elif sub_type == 'type_container':
        container_class = sub_class[0]
        class_mapping = sub_class[1]
        container = container_class(name, obj)
        for name, config in value.items():
            if isinstance(config, dict) == False:
                raise InvalidAimProjectFile("""
Error in file at {}
Resource: '{}'
Invalid config type: '{}'.

Configuration section:
{}""".format(read_file_path, name, type(config), config))
                raise InvalidAimProjectFile("""
Error in file at {}
Type of '{}' does not exist for '{}'

Configuration section:
{}
""".format(read_file_path, config['type'], name, config))

            try:
                klass = class_mapping[config['type']]
            except KeyError:
                if 'type' not in config:
                    raise InvalidAimProjectFile("""
Error in file at {}
No type specified for resource '{}'.

Configuration section:
{}""".format(read_file_path, name, config))
                raise InvalidAimProjectFile("""
Error in file at {}
Type of '{}' does not exist for '{}'

Configuration section:
{}
""".format(read_file_path, config['type'], name, config))
            sub_obj = klass(name, container)
            apply_attributes_from_config(
                sub_obj,
                config,
                config_folder,
                lookup_config,
                read_file_path
            )
            container[name] = sub_obj
        return container

    elif sub_type == 'twolevel_container':
        container_class = sub_class[0]
        first_object_class = sub_class[1]
        second_object_class = sub_class[2]
        container = container_class(name, obj)
        for first_key, first_value in value.items():
            # special case for AlarmSet.notifications
            if first_key == 'notifications' and schemas.IAlarmSet.implementedBy(first_object_class):
                notifications = instantiate_notifications(value['notifications'], obj, read_file_path)
                container.notifications = notifications
            else:
                first_obj = first_object_class(first_key, container)
                container[first_key] = first_obj
            for second_key, second_value in first_value.items():
                # special case for Alarm.notifications
                if second_key == 'notifications' and schemas.IAlarm.implementedBy(second_object_class):
                    notifications = instantiate_notifications(value[first_key]['notifications'], obj, read_file_path)
                    container[first_key].notifications = notifications
                else:
                    second_obj = second_object_class(second_key, container[first_key])
                    apply_attributes_from_config(second_obj, second_value, config_folder, lookup_config, read_file_path)
                    container[first_key][second_key] = second_obj
        return container

    elif sub_type == 'named_twolevel_dict':
        sub_dict = {}
        for first_key, first_value in value.items():
            sub_dict[first_key]  = {}
            for sub_key, sub_value in first_value.items():
                if schemas.INamed.implementedBy(sub_class):
                    sub_obj = sub_class(name+'.'+first_key+'.'+sub_key, obj)
                else:
                    sub_obj = sub_class()
                apply_attributes_from_config(sub_obj, sub_value, config_folder, lookup_config, read_file_path)
                sub_dict[first_key][sub_key] = sub_obj
        return sub_dict

    elif sub_type == 'direct_obj':
        if schemas.INamed.implementedBy(sub_class):
            sub_obj = sub_class(name, obj)
        elif schemas.IParent.implementedBy(sub_class):
            sub_obj = sub_class(obj)
        else:
            sub_obj = sub_class()
        apply_attributes_from_config(sub_obj, value, config_folder, lookup_config, read_file_path)
        return sub_obj

    elif sub_type == 'dynamic_dict':
        # for dictionaries with no fixed schema
        # load all unconstrained key/value pairs
        if schemas.INamed.implementedBy(sub_class):
            sub_obj = sub_class(name, obj)
        elif schemas.IParent.implementedBy(sub_class):
            sub_obj = sub_class(obj)
        else:
            sub_obj = sub_class()

        for k, v in value.items():
            sub_obj[k] = v

        return sub_obj

    elif sub_type == 'obj_list':
        sub_list = []
        for sub_value in value:
            if schemas.INamed.implementedBy(sub_class):
                sub_obj = sub_class(name, obj)
            elif schemas.IParent.implementedBy(sub_class):
                sub_obj = sub_class(obj)
            else:
                sub_obj = sub_class()
            apply_attributes_from_config(sub_obj, sub_value, config_folder, lookup_config, read_file_path)
            sub_list.append(sub_obj)
        return sub_list

    elif sub_type == 'str_list':
        sub_list = []
        # If we expect a string list but only get one string,
        # return that string as the only item in the list
        if isinstance(value, str) == True:
            value = [value]
        if isinstance(value, list) == False:
            raise_invalid_schema_error(
                obj,
                name,
                value,
                read_file_path,
                InvalidAimFieldType("Expected list type but got %s" % type(value))
            )
        for sub_value in value:
            sub_obj = sub_class().fromUnicode(sub_value)
            sub_list.append(sub_obj)
        return sub_list

    elif sub_type == 'log_sets':
        # Special loading for CloudWatch Log Sets
        default_config = lookup_config['logging']['cw_logging']
        merged_config = merge(default_config['log_sets'], value)
        log_sets = CloudWatchLogSets('log_sets', obj)
        for log_set_name in value.keys():
            log_set = CloudWatchLogSet(log_set_name, log_sets)
            apply_attributes_from_config(log_set, merged_config[log_set_name], config_folder, read_file_path=read_file_path)
            log_sets[log_set_name] = log_set
        return log_sets

    elif sub_type == 'alarm_sets':
        # Special loading for AlarmSets
        alarm_sets = AlarmSets('alarm_sets', obj)
        for alarm_set_name in value.keys():
            # look-up AlarmsSet by Resource type and name
            resource_type = obj.__parent__.type
            alarm_set = AlarmSet(alarm_set_name, alarm_sets)
            alarm_set.resource_type = resource_type
            lookup_config['alarms'][resource_type][alarm_set_name]
            for alarm_name, alarm_config in lookup_config['alarms'][resource_type][alarm_set_name].items():
                if 'type' in alarm_config and alarm_config['type'] == 'LogAlarm':
                    alarm = CloudWatchLogAlarm(alarm_name, alarm_set)
                else:
                    alarm = CloudWatchAlarm(alarm_name, alarm_set)
                apply_attributes_from_config(alarm, alarm_config, config_folder, read_file_path=read_file_path)
                alarm_set[alarm_name] = alarm
            alarm_sets[alarm_set_name] = alarm_set

            # check for and apply overrides
            if value[alarm_set_name] is not None:
                for alarm_name in value[alarm_set_name].keys():
                    for setting_name, setting_value in value[alarm_set_name][alarm_name].items():
                        # 'notifications' is a reserved name for AlarmSet and Alarm objects
                        # load notifications for an AlarmSet
                        if alarm_name == 'notifications':
                            alarm_sets[alarm_set_name].notifications = instantiate_notifications(
                                value[alarm_set_name]['notifications'],
                                obj,
                                read_file_path
                            )
                        # load notifications for an Alarm
                        elif setting_name == 'notifications':
                            alarm_sets[alarm_set_name][alarm_name].notifications = instantiate_notifications(
                                value[alarm_set_name][alarm_name]['notifications'],
                                obj,
                                read_file_path
                            )
                        else:
                            if setting_name == 'dimensions':
                                setting_value = [
                                    Dimension(
                                        alarm_sets[alarm_set_name][alarm_name],
                                        item['name'],
                                        item['value']
                                    )
                                    for item in setting_value
                                ]
                            setting_value = cast_to_schema(
                                alarm_sets[alarm_set_name][alarm_name],
                                setting_name,
                                setting_value
                            )
                            setattr(alarm_sets[alarm_set_name][alarm_name], setting_name, setting_value)

        return alarm_sets

    elif sub_type == 'notifications':
        # Special loading for AlarmNotifications
        return instantiate_notifications(value, obj, read_file_path)
    elif sub_type == 'iam_user_permissions':
        return instantiate_iam_user_permissions(value, obj, read_file_path)
    elif sub_type == 'deployment_pipeline_stage':
        return instantiate_deployment_pipeline_stage(name, sub_class, value, obj, read_file_path)

def instantiate_notifications(value, obj, read_file_path):
    notifications = AlarmNotifications('notifications', obj)
    for notification_name in value.keys():
        notification = AlarmNotification(notification_name, notifications)
        apply_attributes_from_config(notification, value[notification_name], read_file_path=read_file_path)
        notifications[notification_name] = notification
    return notifications

def instantiate_iam_user_permissions(value, parent, read_file_path):
    permissions_obj = IAMUserPermissions('permissions', parent)
    for permission_name in value.keys():
        permission_config = value[permission_name]
        permission_obj = IAM_USER_PERMISSIONS_CLASS_MAP[permission_config['type']](permission_name, permissions_obj)
        apply_attributes_from_config(permission_obj, permission_config, read_file_path=read_file_path)
        permissions_obj[permission_name] = permission_obj
    return permissions_obj

def instantiate_deployment_pipeline_stage(name, stage_class, value, parent, read_file_path):
    stage_obj = stage_class(name, parent)
    for action_name in value.keys():
        action_config = value[action_name]
        if action_config['enabled'] == False:
            continue
        action_obj = DEPLOYMENT_PIPELINE_STAGE_ACTION_CLASS_MAP[action_config['type']](action_name, stage_obj)
        apply_attributes_from_config(action_obj, action_config, read_file_path=read_file_path)
        stage_obj[action_name] = action_obj
    return stage_obj

def load_string_from_path(path, base_path=None, is_yaml=False):
    """Reads file contents from a path and returns a string.
    If is_yaml is True then it will load it as a YAML file.
    """
    if not base_path.endswith(os.sep):
        base_path += os.sep
    if base_path:
        path = base_path + path
    path = Path(path)
    if path.is_file():
        if is_yaml:
            return read_yaml_file(path)
        else:
            fh = path.open()
            return fh.read()
    else:
        # ToDo: better error help
        raise InvalidAimProjectFile("For FileReference field, File does not exist at filesystem path {}".format(path))

def read_yaml_file(path):
    "Same as the ModelLoader method, but available outside that class"
    yaml = ModelYAML(typ="safe", pure=True)
    yaml.default_flow_sytle = False
    yaml.add_troposphere_constructors()
    with open(path, 'r') as stream:
        data = yaml.load(stream)
    yaml.restore_existing_constructors()
    return data


class ModelLoader():
    """
    Loads YAML config files into aim.model instances
    """

    def __init__(self, config_folder, config_processor=None):
        self.config_folder = config_folder
        self.config_subdirs = {
            "MonitorConfig": self.instantiate_monitor_config,
            "Accounts": self.instantiate_accounts,
            "NetworkEnvironments": self.instantiate_network_environments,
            "Resources": self.instantiate_resources,
        }
        self.config_processor = config_processor
        self.project = None

    def read_yaml_file(self, path):
        with open(path, 'r') as stream:
            data = self.yaml.load(stream)
        return data

    def read_yaml(self, sub_dir='', fname=''):
        """Read a YAML file"""
        # default is to load root project.yaml
        if sub_dir == '':
            path = self.config_folder + os.sep + fname
        else:
            path = self.config_folder + os.sep + sub_dir + os.sep + fname
        logger.debug("Loading YAML: %s" % (path))

        # Credential files must be secured. This seems hacky, is there a better way?
        if fname == '.credentials.yaml':
            cred_stat = os.stat(path)
            oct_perm = oct(cred_stat.st_mode)
            if oct_perm != '0o100400':
                raise PermissionError('Credentials file permissions are too relaxed. Run: chmod 0400 %s' % (path))

        # Validate Configuration
        if self.config_processor != None:
            self.config_processor(sub_dir, fname)

        # everytime a file is read, update read_file_path to assist with debugging messages
        self.read_file_path = path

        # read the YAML!
        return self.read_yaml_file(path)

    def load_all(self):
        'Basically does a LOAD "*",8,1'
        # set-up the Troposphere YAML constructors
        # ToDo: YAML constructors appear to be global (set on the SafeConstructor class)
        # This approach replaces AIM CFN constructors with ones that load CFN Tags as
        # Troposphere objects, then when the model is finished loading, restores the
        # AIM CFN constructors back
        self.yaml = ModelYAML(typ="safe", pure=True)
        self.yaml.default_flow_sytle = False
        self.yaml.add_troposphere_constructors()

        aim_project_version = self.read_aim_project_version()
        self.check_aim_project_version(aim_project_version)
        self.instantiate_project('project', self.read_yaml('', 'project.yaml'))
        self.project.aim_project_version = '{}.{}'.format(aim_project_version[0], aim_project_version[1])

        if os.path.isfile(self.config_folder + os.sep + '.credentials.yaml'):
            self.instantiate_project('.credentials', self.read_yaml('', '.credentials.yaml'))
        for subdir, instantiate_method in self.config_subdirs.items():
            for fname in os.listdir(self.config_folder + os.sep + subdir):
                if fname.endswith('.yml') or fname.endswith('.yaml'):
                    if fname.endswith('.yml'):
                        name = fname[:-4]
                    elif fname.endswith('.yaml'):
                        name = fname[:-5]
                    config = self.read_yaml(subdir, fname)
                    instantiate_method(name, config, os.path.join(subdir, fname))
        self.instantiate_services()
        self.check_notification_config()
        self.load_outputs()
        self.load_core_monitoring()
        self.yaml.restore_existing_constructors()

    def read_aim_project_version(self):
        "Reads <project>/aim-project-version.txt and returns a tuple (major,medium) version"
        version_file = self.config_folder + os.sep + 'aim-project-version.txt'
        if not os.path.isfile(version_file):
            raise InvalidAimProjectFile(
                'You need a <project>/aim-project-version.txt file that declares your AIM Project file format version.'
            )
        with open(version_file) as f:
            version = f.read()
        version = version.strip().replace(' ', '')
        major, medium = version.split('.')
        major = int(major)
        medium = int(medium)
        return (major, medium)

    def check_aim_project_version(self, version):
        aim_models_version = pkg_resources.get_distribution('aim.models').version
        aim_major, aim_medium = aim_models_version.split('.')[0:2]
        if version[0] != int(aim_major) or version[1] != int(aim_medium):
            raise InvalidAimProjectFile(
                "Version mismatch: project declares AIM Project version {}.{} but aim.models is at version {}".format(
                    version[0], version[1], aim_models_version
                ))

    def load_references(self):
        """
        Resolves all references
        A reference is a string that refers to another value in the model. The original
        reference string is stored as '_ref_<attribute>' while the resolved reference is
        stored in the attribute.
        """
        # walk the model
        for model in get_all_nodes(self.project):
            for name, field in get_all_fields(model).items():
                # check for lists of refs
                #if zope.schema.interfaces.IList.providedBy(field):

                # check for refs as normal attrs
                if hasattr(model, '_ref_' + name):
                    value = resolve_ref(getattr(model, '_ref_' + name), self.project)
                    setattr(model, name, value)

    def load_core_monitoring(self):
        "Loads monitoring metrics that are built into resources"
        for model in get_all_nodes(self.project):
            # ToDo: only doing metrics for ASG right now
            if schemas.IASG.providedBy(model):
                add_metric(model, ec2core)

    def load_outputs_file(self, rfile, ne_outputs_path):
        # parse filename
        info = rfile.split('.')[0]
        ne_name = info.split('-')[0]
        env_name = info.split('-')[1]
        region = info[len(ne_name) + len(env_name) + 2:]

        env_reg = self.project['netenv'][ne_name][env_name][region]
        reg_config = self.read_yaml(ne_outputs_path, rfile)
        if reg_config == None:
            return
        if 'applications' in reg_config:
            for app_name in reg_config['applications'].keys():
                groups_config = reg_config['applications'][app_name]['groups']
                for grp_name in groups_config:
                    for res_name in groups_config[grp_name]['resources']:
                        # Standard AWS Resources in an Application's Resource Group
                        resource_config = groups_config[grp_name]['resources'][res_name]
                        resource = env_reg.applications[app_name].groups[grp_name].resources[res_name]

                        if 'fullname' in resource_config:
                            resource.resource_fullname = resource_config['fullname']['__name__']
                        if 'name' in resource_config:
                            # ALB have a name attribute with an embedded __name__
                            resource.resource_name = resource_config['name']['__name__']
                            # TargetGroups are nested in the ALB Output
                            if 'target_groups' in resource_config:
                                for tg_name, tg_config in resource_config['target_groups'].items():
                                    tg_resource = resource.target_groups[tg_name]
                                    tg_resource.resource_name = tg_config['name']['__name__']
                                    tg_resource.resource_fullname = tg_config['arn']['__name__'].split(':')[-1:][0]
                        elif '__name__' in resource_config:
                            resource.resource_name = resource_config['__name__']

                        # CloudWatch Alarms
                        if 'monitoring' in resource_config:
                            if 'alarm_sets' in resource_config['monitoring']:
                                for alarm_set_name in resource_config['monitoring']['alarm_sets']:
                                    for alarm_name in resource_config['monitoring']['alarm_sets'][alarm_set_name]:
                                        alarm = resource.monitoring.alarm_sets[alarm_set_name][alarm_name]
                                        alarm.resource_name = resource_config['monitoring']['alarm_sets'][alarm_set_name][alarm_name]['__name__']

    def load_outputs(self):
        "Loads resource ids from CFN Outputs"

        base_output_path = 'Outputs' + os.sep
        # monitor_config_output_path = base_output_path + 'MonitorConfig'
        # if os.path.isfile(self.config_folder + os.sep + monitor_config_output_path + os.sep + 'NotificationGroups.yaml'):
        #     notif_groups_config = self.read_yaml(monitor_config_output_path, 'NotificationGroups.yaml')
        #     if 'groups' in notif_groups_config:
        #         notif_groups = self.project['notificationgroups']
        #         for group_name in notif_groups_config['groups'].keys():
        #             notif_groups[group_name].resource_name = notif_groups_config['groups'][group_name]['__name__']

        ne_outputs_path = base_output_path + 'NetworkEnvironments'
        if os.path.isdir(self.config_folder + os.sep + ne_outputs_path):
            for rfile in os.listdir(self.config_folder + os.sep + ne_outputs_path):
                try:
                    self.load_outputs_file(rfile, ne_outputs_path)
                except KeyError:
                    outputs_file_path = pathlib.Path(self.config_folder + os.sep + ne_outputs_path, rfile)
                    print("!! Outputs File: Missing key detected, removing: {}".format(outputs_file_path))
                    outputs_file_path.unlink()

    def load_iam_group(self, res_groups, app_config, local_config={}):
        """
        Loads resources for IAM
        """

        if 'groups' not in app_config:
            app_config['groups'] = {}

        # layer env config over base app config
        if  len(local_config.keys()) > 0:
            merged_config = merge(app_config['groups'], local_config)
        # if no customizations, use only base config
        else:
            merged_config = app_config

        for grp_key, grp_config in merged_config['groups'].items():
            obj = ResourceGroup(grp_key, res_groups)
            apply_attributes_from_config(obj, grp_config, self.config_folder, read_file_path=self.read_file_path)
            res_groups[grp_key] = obj
            for res_key, res_config in grp_config['resources'].items():
                try:
                    klass = RESOURCES_CLASS_MAP[res_config['type']]
                except KeyError:
                    if 'type' not in res_config:
                        raise InvalidAimProjectFile("No type for resource {}".format(res_key))
                    raise InvalidAimProjectFile(
                        "No mapping for type {} for {}".format(res_config['type'], res_key)
                    )
                obj = klass(res_key, res_groups)
                apply_attributes_from_config(obj, res_config, self.config_folder, read_file_path=self.read_file_path)
                res_groups[grp_key].resources[res_key] = obj

    def create_apply_and_save(self, name, parent, klass, config):
        """
        Helper to create a new model instance
        apply config to it
        and save in the object hierarchy
        """
        obj = klass(name, parent)
        apply_attributes_from_config(obj, config, self.config_folder, read_file_path=self.read_file_path)
        parent[name] = obj
        return obj

    def insert_env_ref_aim_sub(self, aim_ref, env_id, region, application):
        """
        aim.sub substition
        """
        # Isolate string between quotes: aim.sub ''
        sub_idx = aim_ref.find('aim.sub')
        if sub_idx == -1:
            return aim_ref
        end_idx = aim_ref.find('\n', sub_idx)
        if end_idx == -1:
            end_idx = len(aim_ref)
        str_idx = aim_ref.find("'", sub_idx, end_idx)
        if str_idx == -1:
            raise StackException(AimErrorCode.Unknown)
        str_idx += 1
        end_str_idx = aim_ref.find("'", str_idx, end_idx)
        if end_str_idx == -1:
            raise StackException(AimErrorCode.Unknown)

        # Isolate any ${} replacements
        first_pass = True
        while True:
            dollar_idx = aim_ref.find("${", str_idx, end_str_idx)
            if dollar_idx == -1:
                if first_pass == True:
                    raise StackException(AimErrorCode.Unknown)
                else:
                    break
            rep_1_idx = dollar_idx
            rep_2_idx = aim_ref.find("}", rep_1_idx, end_str_idx)+1
            netenv_ref_idx = aim_ref.find(
                "aim.ref netenv.", rep_1_idx, rep_2_idx)
            if netenv_ref_idx != -1:
                sub_ref_idx = netenv_ref_idx
                sub_ref_end_idx = sub_ref_idx+(rep_2_idx-sub_ref_idx-1)
                sub_ref = aim_ref[sub_ref_idx:sub_ref_end_idx]
                new_ref = self.insert_env_ref_str(sub_ref, env_id, region, application)
                sub_var = aim_ref[sub_ref_idx:sub_ref_end_idx]
                if sub_var == new_ref:
                    break
                aim_ref = aim_ref.replace(sub_var, new_ref, 1)
            else:
                break
            first_pass = False

        return aim_ref

    def insert_env_ref_str(self, aim_ref, env_id, region, application=None):
        """Inserts the environment name and region name into an aim.ref netenv reference"""
        netenv_ref_idx = aim_ref.find("aim.ref netenv.")
        if netenv_ref_idx == -1:
            return aim_ref

        if aim_ref.startswith("aim.sub "):
            return self.insert_env_ref_aim_sub(aim_ref, env_id, region, application)

        netenv_ref_raw = aim_ref
        sub_ref_len = len(netenv_ref_raw)
        netenv_ref = netenv_ref_raw[0:sub_ref_len]
        ref = Reference(netenv_ref)
        if ref.type == 'netenv' and ref.parts[2] == env_id and ref.parts[3] == region:
            return aim_ref

        # Update application names to reflect unique app name for applications with unique suffixes
        if ref.parts[2] == 'applications':
            # only needs to apply to non-unique applications
            app_name = ref.parts[3]
            if application._duplicate:
                app_name = ref.parts[3]
                # app: --> app
                # app{dog} --> appdog
                # apple: <-- ToDo: fix this use-case
                # ToDo: look at application._suffix
                if application.name.startswith(app_name) and application.name != app_name:
                    ref.parts[3] = application.name

        ref.parts.insert(2, env_id)
        ref.parts.insert(3, region)
        new_ref_parts = '.'.join(ref.parts)
        new_ref = ' '.join(['aim.ref', new_ref_parts])
        return new_ref

    def normalize_environment_refs(self, env_config, env_name, env_region):
        """
        Resolves all references
        A reference is a string that refers to another value in the model. The original
        reference string is stored as '_ref_<attribute>' while the resolved reference is
        stored in the attribute.
        Inserts the Environment and Region into any aim.ref netenv.references.
        """
        # walk the model
        model_list = get_all_nodes(env_config)
        for model in model_list:
            all_fields = get_all_fields(model).items()
            for name, field in all_fields:
                if hasattr(model, name) == False:
                    continue
                if isinstance(field, (str, zope.schema.TextLine, zope.schema.Text)) and field.readonly == False:
                    ref_name = '_ref_' + name
                    if hasattr(model, '_ref_' + name):
                        attr_name = ref_name
                    else:
                        attr_name = name
                    value = getattr(model, attr_name)
                    if value != None and value.find('aim.ref netenv.') != -1:
                        application = get_parent_by_interface(model, schemas.IApplication)
                        value = self.insert_env_ref_str(value, env_name, env_region, application)
                        setattr(model, attr_name, value)
                elif zope.schema.interfaces.IList.providedBy(field) and field.readonly == False:
                    new_list = []
                    attr_name = name
                    modified = False
                    for item in getattr(model, name):
                        if isinstance(item, (str, zope.schema.TextLine, zope.schema.Text)):
                            # Need to search for 'aim.ref netenv' just incase its aim.sub
                            if item.find('aim.ref netenv') != -1:
                            #if is_ref(item):
                                application = get_parent_by_interface(model, schemas.IApplication)
                                value = self.insert_env_ref_str(item, env_name, env_region, application)
                                modified = True
                        else:
                            value = item
                        new_list.append(value)
                    if modified == True:
                        setattr(model, attr_name, new_list)
                elif zope.schema.interfaces.IDict.providedBy(field) and field.readonly == False:
                    new_dict = {}
                    attr_name = name
                    modified = False
                    dict_attr = getattr(model, name)
                    if dict_attr != None:
                        for key, item in getattr(model, name).items():
                            # Same as IList above, needs to search for 'aim.ref netenv'
                            if is_ref(item):
                                application = get_parent_by_interface(model, schemas.IApplication)
                                value = self.insert_env_ref_str(item, env_name, env_region, application)
                                modified = True
                            else:
                                value = item
                            new_dict[key] = value
                        if modified == True:
                            setattr(model, attr_name, new_dict)

    def instantiate_project(self, name, config):
        if name == 'project':
            self.project = Project(config['name'], None)
            self.project['home'] = self.config_folder
            apply_attributes_from_config(self.project, config, self.config_folder, read_file_path=self.read_file_path)
        elif name == '.credentials':
            apply_attributes_from_config(self.project['credentials'], config, self.config_folder, read_file_path=self.read_file_path)

    def instantiate_services(self):
        """
        Load Services
        These are loaded from an entry point named 'aim.services'.
        The entry point name will match a filename at:
          <AIMProject>/Services/<EntryPointName>(.yml|.yaml)
        """
        service_plugins = aim.models.services.list_service_plugins()
        services_dir = self.config_folder + os.sep + 'Services' + os.sep
        for plugin_name, plugin_module in service_plugins.items():
            if os.path.isfile(services_dir + plugin_name + '.yml'):
                fname = plugin_name + '.yml'
            elif os.path.isfile(services_dir + plugin_name + '.yaml'):
                fname = plugin_name + '.yaml'
            else:
                continue
            config = self.read_yaml('Services', fname)
            service = plugin_module.instantiate_model(
                config,
                self.project,
                self.monitor_config,
                read_file_path=services_dir + fname
            )
            self.project['service'][plugin_name.lower()] = service
            if hasattr(plugin_module, 'load_outputs'):
                plugin_module.load_outputs(self)
        return

    def check_notification_config(self):
        """Detect misconfigured alarm notification situations.
        This happens after both MonitorConfig and NetworkEnvironments have loaded.
        """
        if 'notificationgroups' in self.project['resource']:
            for app in self.project.get_all_applications():
                if app.is_enabled():
                    for alarm_info in app.list_alarm_info():
                        alarm = alarm_info['alarm']
                        # warn on alarms with no subscriptions
                        if len(alarm.notification_groups) == 0:
                            print("Alarm {} for app {} does not have any notifications.".format(
                                alarm.name,
                                app.name
                            ))
                        # alarms with groups that do not exist
                        region = self.project.active_regions[0] # regions are all the same, just choose the first
                        for groupname in alarm.notification_groups:
                            if groupname not in self.project['resource']['notificationgroups'][region]:
                                raise InvalidAimProjectFile(
                                    "Alarm {} for app {} notifies to group '{}' which does belong in Notification service group names.".format(
                                        alarm.name,
                                        app.name,
                                        groupname
                                    )
                                )

    def instantiate_monitor_config(self, name, config, read_file_path):
        """
        Loads Logging and AlarmSets config
        These do not get directly loaded into the model, their config is simply stored
        in Loader and applied to the model when named in alarm_sets and log_sets configuration
        in a NetworkEnvironment.
        """
        if not hasattr(self, 'monitor_config'):
            self.monitor_config = {}
        if name.lower() == 'alarmsets':
            self.monitor_config['alarms'] = config
        elif name.lower() == 'logging':
            if 'cw_logging' in config:
                # load the CloudWatch logging into the model, currently this is
                # just done to validate the YAML
                cw_logging = CloudWatchLogging('cw_logging', self.project)
                apply_attributes_from_config(cw_logging, config['cw_logging'])
                self.project['cw_logging'] = cw_logging
            self.monitor_config['logging'] = config

    def instantiate_notificationgroups(self, config):
        notificationgroups = NotificationGroups('notificationgroups', self.project.resource)
        if 'groups' in config:
            # 'groups' gets duplicated and placed into a region_name key for every active region
            groups_config = deepcopy_except_parent(config['groups'])
            del config['groups']
            apply_attributes_from_config(notificationgroups, config, read_file_path=self.read_file_path)
            # load SNS Topics
            for region_name in self.project.active_regions:
                region = RegionContainer(region_name, notificationgroups)
                notificationgroups[region_name] = region
                for topicname, topic_config in groups_config.items():
                    topic = SNSTopic(topicname, region)
                    apply_attributes_from_config(topic, topic_config, read_file_path=self.read_file_path)
                    region[topicname] = topic
        else:
            raise InvalidAimProjectFile("Resource/NotificationGroups.yaml does not have a top-level `groups:`.")

        return notificationgroups

    def instantiate_cloudwatch_log_groups(self, config):
        cw_log_groups = CWLogGroups()
        self.project['cloudwatch_log_groups'] = cw_log_groups
        if 'log_groups' in config:
            apply_attributes_from_config(cw_log_groups, config['log_groups'])

    def instantiate_accounts(self, name, config, read_file_path=''):
        accounts = self.project['accounts']
        self.create_apply_and_save(
            name,
            self.project['accounts'],
            Account,
            config
        )
        self.project['accounts'][name]._read_file_path = pathlib.Path(read_file_path)

    def instantiate_cloudtrail(self, config):
        obj = CloudTrailResource('cloudtrail', self.project.resource)
        if config != None:
            apply_attributes_from_config(obj, config, self.config_folder)
        return obj

    def instantiate_route53(self, config):
        obj = Route53Resource('route53', self.project.resource, config)
        if config != None:
            apply_attributes_from_config(obj, config, self.config_folder)
        return obj

    def instantiate_codecommit(self, config):
        if config == None:
            return
        codecommit_obj = CodeCommit()
        codecommit_obj.repository_groups = {}
        for group_id in config.keys():
            group_config = config[group_id]
            codecommit_obj.repository_groups[group_id] = {}
            for repo_id in group_config.keys():
                repo_config = group_config[repo_id]
                repo_obj = CodeCommitRepository(repo_config['repository_name'], codecommit_obj)
                apply_attributes_from_config(repo_obj, repo_config, self.config_folder)
                codecommit_obj.repository_groups[group_id][repo_id] = repo_obj
        codecommit_obj.gen_repo_by_account()

        return codecommit_obj

    def instantiate_ec2(self, config):
        if config == None or 'keypairs' not in config.keys():
            return
        ec2_obj = EC2Resource('ec2', self.project.resource)
        ec2_obj.keypairs = {}
        for keypair_id in config['keypairs'].keys():
            keypair_config = config['keypairs'][keypair_id]
            keypair_obj = EC2KeyPair(keypair_config['name'], ec2_obj)
            apply_attributes_from_config(keypair_obj, keypair_config, self.config_folder)
            ec2_obj.keypairs[keypair_id] = keypair_obj
        return ec2_obj

    def instantiate_s3(self, config):
        if config == None or 'buckets' not in config.keys():
            return
        s3_obj = S3Resource('s3', self.project.resource)
        s3_obj.buckets = {}
        for bucket_id in config['buckets'].keys():
            bucket_config = config['buckets'][bucket_id]
            bucket_obj = S3Bucket(bucket_id, s3_obj)
            apply_attributes_from_config(bucket_obj, bucket_config, self.config_folder)
            s3_obj.buckets[bucket_id] = bucket_obj
        return s3_obj

    def instantiate_iam(self, config):
        iam_obj = IAMResource('iam', self.project.resource)
        apply_attributes_from_config(iam_obj, config)
        return iam_obj

    def instantiate_resources(self, name, config, read_file_path=None):
        name = name.lower()
        # Functions:
        #   route53
        #   codecommit
        #   ec2
        #   s3
        #   cloudtrail
        #   iam
        #   notificationgroups
        instantiate_method = getattr(self, 'instantiate_'+name, None)
        if instantiate_method == None:
            print("!! No method to instantiate resource: {}: {}".format(name, read_file_path))
        else:
            self.project['resource'][name] = instantiate_method(config)
            if self.project['resource'][name] != None:
                self.project['resource'][name]._read_file_path = pathlib.Path(read_file_path)
        return

    def raise_env_name_mismatch(self, item_name, config_name, env_region):
        raise InvalidAimProjectFile(
            "Could not find config for '{}' in '{}', for environment '{}' in netenv '{}'.".format(
                item_name, config_name, env_region.__parent__.name, env_region.__parent__.__parent__.name
            )
        )

    def instantiate_applications(
        self,
        env_region_config,
        env_region,
        global_config
    ):
        """Load applications into an EnvironmentRegion

        Applications merge the global ApplicationEngine configuration
        with the EnvironmentDefault configuration with the final
        EnvironmentRegion configuration.

        If applications names in environments have the format:

          <name>{suffix}

        Then the <name> is the applications name for the default configuration
        and the braces are removed to form a new unique application name in the environment.

            namesuffix

        In this way the same application can be instiated more than once in the same network,
        with different configuration for each instance.
        """
        if 'applications' not in env_region_config:
            return
        global_item_config = global_config['applications']

        for item_name, item_config in env_region_config['applications'].items():
            match = re.match('^(.*){(.*)}$', item_name)
            if match:
                # application is duplicated with a unique suffix
                app_name, unique_suffix = match.groups()
                unique_app_name = app_name + unique_suffix
                duplicate = True
                suffix = unique_suffix
            else:
                # normal one-to-one environments.applications.name to applications.app.name
                app_name = item_name
                unique_app_name = app_name
                duplicate = False
                suffix = ''
            item = Application(unique_app_name, getattr(env_region, 'applications'))
            # Application objects are marked as duplicate if more than one exist the same environment
            item._duplicate = duplicate
            item._suffix = suffix
            if env_region.name == 'default':
                # merge global with default
                try:
                    global_config['applications'][app_name]
                except KeyError:
                    self.raise_env_name_mismatch(app_name, 'applications', env_region)
                item_config = merge(
                    global_config['applications'][app_name],
                    env_region_config['applications'][item_name]
                )
                annotate_base_config(item, item_config, global_item_config[app_name])
            else:
                # merge global with default, then merge that with local config
                env_default = global_config['environments'][env_region.__parent__.name]['default']
                if 'applications' in env_default and unique_app_name in env_default['applications']:
                    try:
                        default_region_config = env_default['applications'][unique_app_name]
                        global_item_config[app_name]
                    except KeyError:
                        self.raise_env_name_mismatch(unique_app_name, 'applications', env_region)
                    default_config = merge(global_item_config[app_name], default_region_config)
                    item_config = merge(default_config, item_config)
                    annotate_base_config(item, item_config, default_config)
                # no default config, merge local with global
                else:
                    try:
                        global_item_config[app_name]
                    except KeyError:
                        self.raise_env_name_mismatch(item_name, 'applications', env_region)
                    item_config = merge(global_item_config[app_name], item_config)
                    annotate_base_config(item, item_config, global_item_config[app_name])

            env_region.applications[unique_app_name] = item # save
            apply_attributes_from_config(
                item,
                item_config,
                self.config_folder,
                lookup_config=self.monitor_config,
                read_file_path=self.read_file_path
            )

    def instantiate_secrets_manager(
        self,
        env_region_config,
        env_region,
        global_config
    ):
        """Load secrets_manager into an EnvironmentRegion

        SecretsManager merge the global ApplicationEngine configuration
        with the EnvironmentDefault configuration with the final
        EnvironmentRegion configuration.
        """
        if 'secrets_manager' not in env_region_config:
            return
        global_app_config = global_config['secrets_manager']
        for app_name, app_config in env_region_config['secrets_manager'].items():
            secrets_app = SecretsManagerApplication(app_name, getattr(env_region, 'secrets_manager'))
            for group_name, group_config in app_config.items():
                secrets_group = SecretsManagerGroup(group_name, secrets_app)
                for secret_name, secret_config in group_config.items():
                    secret = SecretsManagerSecret(secret_name, secrets_group)

                    if env_region.name == 'default':
                        # merge global with default
                        try:
                            global_secret_config = global_config['secrets_manager'][app_name][group_name][secret_name]
                        except KeyError:
                            self.raise_env_name_mismatch('{}.{}.{}'.format(app_name, group_name, secret_name), 'secrets_manager', env_region)
                        secret_config = merge(
                            global_secret_config,
                            env_region_config['secrets_manager'][app_name][group_name][secret_name])
                        annotate_base_config(secret, secret_config, global_secret_config)
                    else:
                        # merge global with default, then merge that with local config
                        env_default = global_config['environments'][env_region.__parent__.name]['default']
                        if 'secrets_manager' in env_default:
                            try:
                                default_region_config = env_default['secrets_manager'][app_name][group_name][secret_name]
                                global_secret_config = global_app_config[app_name][group_name][secret_name]
                            except KeyError:
                                self.raise_env_name_mismatch('{}.{}.{}'.format(app_name, group_name, secret_name), 'secrets_manager', env_region)
                            default_config = merge(global_secret_config, default_region_config)
                            secret_config = merge(default_config, secret_config)
                            annotate_base_config(secret, secret_config, default_config)
                        # no default config, merge local with global
                        else:
                            try:
                                global_secret_config = global_app_config[app_name][group_name][secret_name]
                            except KeyError:
                                self.raise_env_name_mismatch('{}.{}.{}'.format(app_name, group_name, secret_name), 'secrets_manager', env_region)
                            secret_config = merge(global_secret_config, secret_config)
                            annotate_base_config(secret, secret_config, global_secret_config)

                    apply_attributes_from_config(
                        secret,
                        secret_config,
                        self.config_folder,
                        lookup_config=self.monitor_config,
                        read_file_path=self.read_file_path
                    )
                    secrets_group[secret_name] = secret
                secrets_app[group_name] = secrets_group

            env_region.secrets_manager[app_name] = secrets_app # save

    def instantiate_network_environments(self, name, config, read_file_path):
        "Instantiates objects for everything in a NetworkEnvironments/some-workload.yaml file"
         # Network Environment
        if config['network'] == None:
            raise InvalidAimProjectFile("NetworkEnvironment {} has no network".format(name))
        net_env = self.create_apply_and_save(
            name,
            self.project['netenv'],
            NetworkEnvironment,
            config['network']
        )
        net_env._read_file_path = pathlib.Path(read_file_path)

        # Environments
        if 'environments' in config:
            for env_name, env_config in config['environments'].items():
                env = self.create_apply_and_save(
                    env_name,
                    net_env,
                    Environment,
                    env_config
                )
                # Load the EnvironmentRegion(s) and EnvironmentDefault
                for env_reg_name, env_reg_config in config['environments'][env_name].items():
                    # skip attributes
                    if env_reg_name == 'title': continue
                    # key must be a valid aws region name
                    if env_reg_name != 'default' and env_reg_name not in aws_regions:
                        raise InvalidAimProjectFile(
                            "Environment region name is not valid: {} in {}".format(env_reg_name, env_name)
                        )
                    if env_reg_name is not 'default':
                        env_region_config = merge(env_config['default'], env_reg_config)
                    else:
                        env_region_config = env_config['default']

                    klass = EnvironmentRegion
                    if env_reg_name == 'default':
                        klass = EnvironmentDefault
                    env_region = self.create_apply_and_save(
                        env_reg_name,
                        env,
                        klass,
                        env_region_config
                    )

                    # Network
                    network = env_region.network
                    # merge default only with base netenv
                    if env_reg_name == 'default':
                        if not 'network' in env_reg_config:
                            raise InvalidAimProjectFile(
                                "Default Environment {} must have base network config".format(env_region.__parent__.name)
                            )
                        net_config = merge(config['network'], env_reg_config['network'])
                    # merge EnvDefault and base network, then merge that with any EnvReg config
                    else:
                        default = config['environments'][env_region.__parent__.name]['default']
                        if not 'network' in default:
                            raise InvalidAimProjectFile(
                                "Default Environment {} must have base network config".format(env_region.__parent__.name)
                            )
                        net_config = merge(
                            config['network'],
                            default['network']
                        )
                        if 'network' in env_reg_config:
                            net_config = merge(net_config, env_reg_config['network'])
                    apply_attributes_from_config(network, net_config, self.config_folder, read_file_path=self.read_file_path)

                    # Applications
                    self.instantiate_applications(
                        env_region_config,
                        env_region,
                        config
                    )
                    self.instantiate_secrets_manager(
                        env_region_config,
                        env_region,
                        config
                    )
                    if env_reg_name != 'default':
                        # Insert the environment and region into any Refs
                        self.normalize_environment_refs(env_region, env_name, env_reg_name)
