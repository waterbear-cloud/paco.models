from zope.interface import Interface, Attribute, invariant, Invalid, classImplements, taggedValue
from zope.interface.common.mapping import IMapping
from zope.interface.common.sequence import ISequence
from zope import schema
from zope.schema.fieldproperty import FieldProperty
from paco.models import vocabulary
from paco.models.references import PacoReference, FileReference, StringFileReference, YAMLFileReference
import json
import re
import ipaddress


# Constraints

class InvalidLayerARNList(schema.ValidationError):
    __doc__ = 'Not a valid list of Layer ARNs'

LAYER_ARN = re.compile(r"arn:aws:lambda:(.*):(\d+):layer:(.*):(.*)")
def isListOfLayerARNs(value):
    "Validate a list of Lambda Layer ARNs"
    if len(value) > 5:
        raise InvalidLayerARNList
    for arn in value:
        m = LAYER_ARN.match(arn)
        if not m:
            raise InvalidLayerARNList
        else:
            if m.groups()[0] not in vocabulary.aws_regions:
                raise InvalidLayerARNList
    return True

class InvalidStringConditionOperator(schema.ValidationError):
    __doc__ = 'String Condition operator must be one of: StringEquals, StringNotEquals, StringEqualsIgnoreCase, StringNotEqualsIgnoreCase, StringLike, StringNotLike.',

def isValidStringConditionOperator(value):
    if value.lower() not in ('stringequals', 'stringnotequals', 'stringequalsignorecase', 'stringnotequalsignorecase', 'stringlike', 'stringnotlike'):
        raise InvalidStringConditionOperator
    return True

class InvalidBackupNotification(schema.ValidationError):
    __doc__ = 'Backup Vault notification event must be one of: BACKUP_JOB_STARTED, BACKUP_JOB_COMPLETED, RESTORE_JOB_STARTED, RESTORE_JOB_COMPLETED, RECOVERY_POINT_MODIFIED.'

def isValidBackupNotification(value):
    for item in value:
        if item not in ('BACKUP_JOB_STARTED', 'BACKUP_JOB_COMPLETED', 'RESTORE_JOB_STARTED', 'RESTORE_JOB_COMPLETED', 'RECOVERY_POINT_MODIFIED'):
            raise InvalidBackupNotification
    return True

class InvalidCodeDeployComputePlatform(schema.ValidationError):
    __doc__ = 'compute_platform must be one of ECS, Lambda or Server.'

def isValidCodeDeployComputePlatform(value):
    if value not in ('ECS', 'Lambda', 'Server'):
        raise InvalidCodeDeployComputePlatform
    return True

class InvalidDeploymentGroupBundleType(schema.ValidationError):
    __doc__ = 'Bundle Type must be one of JSON, tar, tgz, YAML or zip.'

def isValidDeploymentGroupBundleType(value):
    if value not in ('JSON', 'tar', 'tgz', 'YAML', 'zip'):
        raise InvalidDeploymentGroupBundleType
    return True

class InvalidS3KeyPrefix(schema.ValidationError):
    __doc__ = 'Not a valid S3 bucket prefix. Can not start or end with /.'

def isValidS3KeyPrefix(value):
    if value.startswith('/') or value.endswith('/'):
        raise InvalidS3KeyPrefix
    return True

class InvalidSNSSubscriptionProtocol(schema.ValidationError):
    __doc__ = 'Not a valid SNS Subscription protocol.'

def isValidSNSSubscriptionProtocol(value):
    if value not in vocabulary.subscription_protocols:
        raise InvalidSNSSubscriptionProtocol
    return True

class InvalidSNSSubscriptionEndpoint(schema.ValidationError):
    __doc__ = 'Not a valid SNS Endpoint.'

class InvalidJSON(schema.ValidationError):
    __doc__ = "Not a valid JSON document."

def isValidJSONOrNone(value):
    if not value:
        return True
    try:
        json.load(value)
    except json.decoder.JSONDecodeError:
        raise InvalidJSON
    return True

class InvalidApiGatewayAuthorizationType(schema.ValidationError):
    __doc__ = 'Not a valid Api Gateway Method Authorization Type.'

def isValidApiGatewayAuthorizationType(value):
    if value not in ('NONE', 'AWS_IAM', 'CUSTOM', 'COGNITO_USER_POOLS'):
        raise InvalidApiGatewayAuthorizationType
    return True

class InvalidApiGatewayIntegrationType(schema.ValidationError):
    __doc__ = 'Not a valid API Gateway Method Integration Type.'

def isValidApiGatewayIntegrationType(value):
    if value not in ('AWS', 'AWS_PROXY', 'HTTP', 'HTTP_PROXY', 'MOCK'):
        raise InvalidApiGatewayIntegrationType
    return True

class InvalidHttpMethod(schema.ValidationError):
    __doc__ = 'Not a valid HTTP Method.'

def isValidHttpMethod(value):
    if value not in ('ANY', 'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'):
        raise InvalidHttpMethod
    return True

class InvalidApiKeySourceType(schema.ValidationError):
    __doc__ = 'Not a valid Api Key Source Type.'

def isValidApiKeySourceType(value):
    if value not in ('HEADER', 'AUTHORIZER'):
        raise InvalidApiKeySourceType
    return True

class InvalidEndpointConfigurationType(schema.ValidationError):
    __doc__ = "Not a valid endpoint configuration type, must be one of: 'EDGE', 'REGIONAL', 'PRIVATE'"

def isValidEndpointConfigurationType(value):
    if value not in ('EDGE', 'REGIONAL', 'PRIVATE'):
        raise
    return True

class InvalidBinaryMediaTypes(schema.ValidationError):
    __doc__ = 'Not a valid binary media types.'

def isValidBinaryMediaTypes(value):
    if len(value) == 0: return True
    d = {}
    # detect duplicates and / chars
    for item in value:
        if item not in d:
            d[item] = None
        else:
            raise InvalidBinaryMediaTypes("Entry {} is provided more than once".format(item))
        if item.find('/') != -1:
            raise InvalidBinaryMediaTypes("Entry {} must not contain a / character.".format(item))

    return True

class InvalidAWSRegion(schema.ValidationError):
    __doc__ = 'Not a valid AWS Region name.'

def isValidAWSRegionName(value):
    # Allow for missing_value
    if value == 'no-region-set': return True
    if value not in vocabulary.aws_regions:
        raise InvalidAWSRegion
    return True

def isValidAWSRegionNameOrNone(value):
    if value == '':
        return True
    if value not in vocabulary.aws_regions:
        raise InvalidAWSRegion
    return True

def isValidAWSRegionList(value):
    for region in value:
        isValidAWSRegionName(region)
    return True

def isValidAWSRegionOrAllList(value):
    if value == ['ALL']: return True
    for region in value:
        isValidAWSRegionName(region)
    return True

class InvalidAWSHealthCheckRegion(schema.ValidationError):
    __doc__ = "AWS Health Check regions are: 'sa-east-1', 'us-west-1', 'us-west-2', 'ap-northeast-1', 'ap-southeast-1', 'eu-west-1', 'us-east-1', 'ap-southeast-2'"

def isValidHealthCheckAWSRegionList(value):
    # must be at least 3 but 0 is Okay too
    if len(value) == 1 or len(value) == 2:
        raise InvalidAWSHealthCheckRegion("If health_check_regions is specified, it must contain at least 3 regions.")
    regions = ('sa-east-1', 'us-west-1', 'us-west-2', 'ap-northeast-1', 'ap-southeast-1', 'eu-west-1', 'us-east-1', 'ap-southeast-2')
    for region in value:
        if region not in regions:
            raise InvalidAWSHealthCheckRegion("Region {} is not a valid Route53 health check region.".format(region))
    return True


valid_legacy_flags = (
        'cftemplate_aws_name_2019_09_17',
        'route53_controller_type_2019_09_18',
        'codecommit_controller_type_2019_09_18',
        'lambda_controller_type_2019_09_18',
        'cloudwatch_controller_type_2019_09_18',
        'cftemplate_iam_user_delegates_2019_10_02',
        'route53_hosted_zone_2019_10_12',
        'iam_user_default_password_2019_10_12',
        'netenv_loggroup_name_2019_10_13',
        'route53_record_set_2019_10_16',
        'target_group_name_2019_10_29',
        'aim_name_2019_11_28'
    )
class InvalidLegacyFlag(schema.ValidationError):
    __doc__ = 'Not a valid legacy flag. Must be one of: '
    first = True
    for flag in valid_legacy_flags:
        if first == False:
            __doc__ += ' | '
        __doc__ += flag
        first = False

def isValidLegacyFlag(value):
    if value not in valid_legacy_flags:
        raise InvalidLegacyFlag
    return True

def isValidLegacyFlagList(value):
    for flag in value:
        isValidLegacyFlag(flag)
    return True

class InvalidEmailAddress(schema.ValidationError):
    __doc__ = 'Malformed email address'

EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")
def isValidEmail(value):
    if not EMAIL_RE.match(value):
        raise InvalidEmailAddress
    return True

class InvalidHttpUrl(schema.ValidationError):
    __doc__ = 'Malformed HTTP URL'

HTTP_RE = re.compile(r"^http:\/\/(.*)")
def isValidHttpUrl(value):
    if not HTTP_RE.match(value):
        raise InvalidHttpUrl
    return True

class InvalidHttpsUrl(schema.ValidationError):
    __doc__ = 'Malformed HTTPS URL'

HTTPS_RE = re.compile(r"^https:\/\/(.*)")
def isValidHttpsUrl(value):
    if not HTTPS_RE.match(value):
        raise InvalidHttpsUrl
    return True

class InvalidInstanceSizeError(schema.ValidationError):
    __doc__ = 'Not a valid instance size (or update the instance_size_info vocabulary).'

def isValidInstanceSize(value):
    if value not in vocabulary.instance_size_info:
        raise InvalidInstanceSizeError
    return True

class InvalidInstanceAMITypeError(schema.ValidationError):
    __doc__ = 'Not a valid instance AMI type (or update the ami_types vocabulary).'

def isValidInstanceAMIType(value):
    if value not in vocabulary.ami_types:
        raise InvalidInstanceAMITypeError
    return True

class InvalidHealthCheckTypeError(schema.ValidationError):
    __doc__ = 'Not a valid health check type (can only be EC2 or ELB).'

def isValidHealthCheckType(value):
    if value not in ('EC2', 'ELB'):
        raise InvalidHealthCheckTypeError
    return True

class InvalidRoute53HealthCheckTypeError(schema.ValidationError):
    __doc__ = 'Route53 health check type must be one of HTTP, HTTPS or TCP.'

def isValidRoute53HealthCheckType(value):
    if value not in ('HTTP', 'HTTPS', 'TCP'):
        raise InvalidRoute53HealthCheckTypeError
    return True

class InvalidRoute53RecordSetTypeError(schema.ValidationError):
    __doc__ = 'Route53 RecordSet "type" be one of: A | MX | CNAME | Alias | SRV | TXT | NS | SOA'

def isValidRoute53RecordSetType(value):
    if value not in ('A', 'MX', 'CNAME', 'Alias', 'SRV', 'TXT', 'NS', 'SOA'):
        raise InvalidRoute53RecordSetTypeError
    return True

class InvalidStringCanOnlyContainDigits(schema.ValidationError):
    __doc__ = 'String must only contain digits.'

def isOnlyDigits(value):
    if re.match('\d+', value):
        return True
    raise InvalidStringCanOnlyContainDigits

class InvalidCloudWatchLogRetention(schema.ValidationError):
    __doc__ = 'String must be valid log retention value: {}'.format(', '.join(vocabulary.cloudwatch_log_retention.keys()))

def isValidCloudWatchLogRetention(value):
    if value == '': return True
    if value not in vocabulary.cloudwatch_log_retention:
        raise InvalidCloudWatchLogRetention
    return True

class InvalidCidrIpv4(schema.ValidationError):
    __doc__ = 'String must be a valid CIDR v4 (e.g. 20.50.120.4/30)'

def isValidCidrIpv4orBlank(value):
    """
    A valid CIDR v4 block or an empty string
    """
    if value == '':
        return True
    try:
        ip, cidr = value.split('/')
    except ValueError:
        raise InvalidCidrIpv4
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise InvalidCidrIpv4
    try:
        cidr = int(cidr)
    except ValueError:
        raise InvalidCidrIpv4
    if cidr < 0 or cidr > 32:
        raise InvalidCidrIpv4
    return True

class InvalidComparisonOperator(schema.ValidationError):
    __doc__ = 'Comparison Operator must be one of: GreaterThanThreshold, GreaterThanOrEqualToThreshold, LessThanThreshold, or LessThanOrEqualToThreshold.'

def isComparisonOperator(value):
    if value not in vocabulary.cloudwatch_comparison_operators:
        raise InvalidComparisonOperator
    return True

class InvalidAlarmSeverity(schema.ValidationError):
    __doc__ = 'Severity must be one of: low, critical'

def isValidAlarmSeverity(value):
    if value not in ('low','critical'):
        raise InvalidAlarmSeverity
    return True

def isValidAlarmSeverityFilter(value):
    "Filters can be None or ''"
    if not value: return True
    return isValidAlarmSeverity(value)

class InvalidMissingDataValue(schema.ValidationError):
    __doc__ = 'treat_missing_data must be one of: breaching, notBreaching, ignore or missing'

def isMissingDataValue(value):
    if value not in ('breaching', 'notBreaching', 'ignore', 'missing'):
        raise InvalidMissingDataValue
    return True

class InvalidAlarmStatistic(schema.ValidationError):
    __doc__ = 'statistic must be one of: Average, Maximum, Minimum, SampleCount or Sum.'

def isValidAlarmStatisticValue(value):
    if value not in ('Average', 'Maximum', 'Minimum', 'SampleCount', 'Sum'):
        raise InvalidAlarmStatistic
    return True

class InvalidExtendedStatisticValue(schema.ValidationError):
    __doc__ = '`extended_statistic` must match pattern p(\d{1,2}(\.\d{0,2})?|100). Examlpes: p95, p0.0, p98.59, p100'

def isValidExtendedStatisticValue(value):
    if re.match('^p\d{1,2}((\.\d{0,2})?|100)$', value):
        return True
    else:
        raise InvalidExtendedStatisticValue

class InvalidEvaluateLowSampleCountPercentileValue(schema.ValidationError):
    __doc__ = 'evaluate_low_sample_count_percentile must be one of: evaluate or ignore.'

def isValidEvaluateLowSampleCountPercentileValue(value):
    if value not in ('evaluate', 'ignore'):
        raise InvalidEvaluateLowSampleCountPercentileValue
    return True

class InvalidAlarmClassification(schema.ValidationError):
    __doc__ = 'Classification must be one of: health, performance, security'

def isValidAlarmClassification(value):
    if value not in vocabulary.alarm_classifications:
        raise InvalidAlarmClassification
    return True

def isValidAlarmClassificationFilter(value):
    "Filters can be None or ''"
    if not value: return True
    return isValidAlarmClassification(value)

class InvalidASGMetricName(schema.ValidationError):
    __doc__ = 'ASG Metric name is not valid'

def isValidASGMetricNames(value):
    for string in value:
        if string not in vocabulary.asg_metrics:
            raise InvalidASGMetricName
    return True

class InvalidCWAgentTimezone(schema.ValidationError):
    __doc__ = 'Timezone choices for CW Agent'

def isValidCWAgentTimezone(value):
    if value not in ('Local','UTC'):
        raise InvalidCWAgentTimezone
    return True

class InvalidCFViewerProtocolPolicy(schema.ValidationError):
    __doc__ = 'Viewer Protocol Policy must be one of: allow-all | https-only | redirect-to-https'

def isValidCFViewerProtocolPolicy(value):
    if value not in ('allow-all','https-only','redirect-to-https'):
        raise InvalidCFViewerProtocolPolicy
    return True

class InvalidCloudFrontCookiesForward(schema.ValidationError):
    __doc__ = 'Cookies Forward must be one of: all | none | whitelist'

def isValidCloudFrontCookiesForward(value):
    if value not in ('all', 'none', 'whitelist'):
        raise InvalidCloudFrontCookiesForward
    return True

class InvalidCFSSLSupportedMethod(schema.ValidationError):
    __doc__ = 'SSL Supported Methods must be one of: sni-only | vip'

def isValidCFSSLSupportedMethod(value):
    if value not in ('sni-only', 'vip'):
        raise InvalidCFSSLSupportedMethod
    return True

class InvalidCFMinimumProtocolVersion(schema.ValidationError):
    __doc__ = 'Mimimum SSL Protocol Version must be one of: SSLv3 | TLSv1 | TLSv1.1_2016 | TLSv1.2_2018 | TLSv1_2016'

def isValidCFMinimumProtocolVersion(value):
    if value not in ('SSLv3', 'TLSv1', 'TLSv1.1_2016', 'TLSv1.2_2018', 'TLSv1_2016'):
        raise InvalidCFMinimumProtocolVersion
    return True

class InvalidCFPriceClass(schema.ValidationError):
    __doc__ = 'Price Class must be one of: 100 | 200 | All'

def isValidCFPriceClass(value):
    if value not in ('100', '200', 'All'):
        raise InvalidCFPriceClass
    return True

class InvalidCFProtocolPolicy(schema.ValidationError):
    __doc__ = 'Protocol Policy must be one of: http-only | https-only | match-viewer'

def isValidCFProtocolPolicy(value):
    if value not in ('http-only', 'https-only', 'match-viewer'):
        raise InvalidCFPProtocolPolicy
    return True

class InvalidCFSSLProtocol(schema.ValidationError):
    __doc__ = 'SSL Protocols must be one of: SSLv3 | TLSv1 | TLSv1.1 | TLSv1.2'

def isValidCFSSLProtocol(value):
    for protocol in value:
        if protocol not in ('SSLv3', 'TLSv1', 'TLSv1.1', 'TLSv1.2'):
            raise InvalidCFSSLProtocol
    return True

# ElastiCache
class InvalidAZMode(schema.ValidationError):
    __doc__ = 'AZMode must be one of: cross-az | single-az'

def isValidAZMode(value):
    if value not in ('cross-az', 'single-az'):
        raise InvalidAZMode
    return True

class InvalidRedisCacheParameterGroupFamily(schema.ValidationError):
    __doc__ = 'cache_parameter_group_family must be one of: redis2.6 | redis2.8 | redis3.2 | redis4.0 | redis5.0'

def isRedisCacheParameterGroupFamilyValid(value):
    if value not in ('redis2.6', 'redis2.8', 'redis3.2', 'redis4.0', 'redis5.0'):
        raise InvalidRedisCacheParameterGroupFamily
    return True


# IAM
class InvalidPacoCodeCommitPermissionPolicy(schema.ValidationError):
    __doc__ = 'permission must be one of: ReadWrite | ReadOnly'

def isPacoCodeCommitPermissionPolicyValid(value):
    if value not in ('ReadWrite', 'ReadOnly'):
        raise InvalidPacoCodeCommitPermissionPolicy
    return True

# CodeBuild
class InvalidCodeBuildComputeType(schema.ValidationError):
    __doc__ = 'codebuild_compute_type must be one of: BUILD_GENERAL1_SMALL | BUILD_GENERAL1_MEDIUM | BUILD_GENERAL1_LARGE'

def isValidCodeBuildComputeType(value):
    if value not in ('BUILD_GENERAL1_SMALL', 'BUILD_GENERAL1_MEDIUM', 'BUILD_GENERAL1_LARGE'):
        raise InvalidCodeBuildComputeType
    return True

# ASG Scaling Policy Type
class InvalidASGScalignPolicyType(schema.ValidationError):
    __doc__ = 'policy_type must be one of: SimpleScaling | StepScaling | TargetTrackingScaling'

def IsValidASGScalignPolicyType(value):
    if value not in ('SimpleScaling', 'StepScaling', 'TargetTrackingScaling'):
        raise InvalidASGScalignPolicyType
    return True

# ASG Scaling Policy Adjustment Type
class InvalidASGScalingPolicyAdjustmentType(schema.ValidationError):
    __doc__ = 'policy_type must be one of: ChangeInCapacity | ExactCapacity | PercentChangeInCapacity'

def IsValidASGScalingPolicyAdjustmentType(value):
    if value not in ('ChangeInCapacity', 'ExactCapacity', 'PercentChangeInCapacity'):
        raise InvalidASGScalingPolicyAdjustmentType
    return True

# ASG Scaling Policy Adjustment Type
class InvalidASGLifecycleTransition(schema.ValidationError):
    __doc__ = 'lifecycle_transition must be one of: autoscaling:EC2_INSTANCE_LAUNCHING | autoscaling:EC2_INSTANCE_TERMINATING'

def IsValidASGLifecycleTransition(value):
    if value not in ('autoscaling:EC2_INSTANCE_LAUNCHING', 'autoscaling:EC2_INSTANCE_TERMINATING'):
        raise InvalidASGLifecycleTransition
    return True

# ASG Scaling Policy Adjustment Type
class InvalidASGLifecycleDefaultResult(schema.ValidationError):
    __doc__ = 'default_result must be one of: CONTINUE | ABANDON'

def IsValidASGLifecycleDefaultResult(value):
    if value not in ('CONTINUE', 'ABANDON'):
        raise InvalidASGLifecycleTransition
    return True

# ASG AvailabilityZones
class InvalidASGAvailabilityZone(schema.ValidationError):
    __doc__ = 'availability_zone must be one of: all | 1 | 2 | 3 | 4 | ...'

def IsValidASGAvailabilityZone(value):
    if value == 'all':
        return True
    if value.isnumeric() == False:
        raise InvalidASGAvailabilityZone
    if int(value) < 0 or int(value) > 10:
        raise InvalidASGAvailabilityZone
    return True

# EBS Volume Type
class InvalidEBSVolumeType(schema.ValidationError):
    __doc__ = 'volume_type must be one of: gp2 | io1 | sc1 | st1 | standard'

def isValidEBSVolumeType(value):
    if value not in ('gp2', 'io1', 'sc1', 'st1', 'standard'):
        raise InvalidEBSVolumeType
    return True

# NAT Gateway
class InvalidNATGatewayType(schema.ValidationError):
    __doc__ = 'NATGateay type must be one of: Managed | EC2'

def IsValidNATGatewayType(value):
    if value not in ['Managed', 'EC2']:
        raise InvalidNATGatewayType
    return True

# ----------------------------------------------------------------------------
# Here be Schemas!
#
class IDNSEnablable(Interface):
    """Provides a parent with an inheritable DNS enabled field"""
    dns_enabled = schema.Bool(
        title='Boolean indicating whether DNS record sets will be created.',
        default=True,
        required=False,
    )

class CommaList(schema.List):
    """Comma separated list of valeus"""

    def constraint(self, value):
        """
        Validate something
        """
        return True
        # ToDo: how to get the PACO_HOME and change to that directory from here?
        #path = pathlib.Path(value)
        #return path.exists()

class IParent(Interface):
    """
An object in the Paco project model tree with a reference to a parent object.
    """
    __parent__ = Attribute("Object reference to the parent in the object hierarchy")

class ITitle(Interface):
    """
A title is a human-readable name. It can be as long as you want, and can change without
breaking any configuration.
    """
    title=schema.TextLine(
        title="Title",
        default="",
        required=False,
    )

class INamed(IParent, ITitle):
    """
A name given to a cloud resource. Names identify resources and changing them
can break configuration.
"""
    name = schema.TextLine(
        title="Name",
        default="",
        required=False,
    )

class IDeployable(Interface):
    """
Indicates if this configuration tree should be enabled or not.
    """
    enabled = schema.Bool(
        title="Enabled",
        description="Could be deployed to AWS",
        default=False,
        required=False,
    )

class IName(Interface):
    """
A name that can be changed or duplicated with other similar cloud resources without breaking anything.
    """
    name = schema.TextLine(
        title="Name",
        default="",
        required=False,
    )

class IFunction(Interface):
    """
A callable function that returns a value.
    """

class IFileReference(Interface):
    pass

class IStringFileReference(IFileReference):
    pass

class IYAMLFileReference(IFileReference):
    pass

class IPacoReference(Interface):
    """A field containing a reference an paco model object or attribute"""
    pass

# work around circular imports for references
classImplements(PacoReference, IPacoReference)
classImplements(FileReference, IFileReference)
classImplements(StringFileReference, IStringFileReference)
classImplements(YAMLFileReference, IYAMLFileReference)


class INameValuePair(Interface):
    """A Name/Value pair to use for RDS Option Group configuration"""
    name = schema.TextLine(
        title="Name",
        required=False,
    )
    value = schema.TextLine(
        title="Value",
        required=False,
    )

class IAdminIAMUser(IDeployable):
    """An AWS Account Administerator IAM User"""
    username = schema.TextLine(
        title="IAM Username",
        default="",
        required=False,
    )

class IAccounts(IMapping):
    "Collection of Accounts"
    pass

class IAccount(INamed, IDeployable):
    "Cloud account information"
    account_type = schema.TextLine(
        title="Account Type",
        description="Supported types: 'AWS'",
        default="AWS",
        required=False,
    )
    account_id = schema.TextLine(
        title="Account ID",
        description="Can only contain digits.",
        required=False,
        constraint = isOnlyDigits
    )
    admin_delegate_role_name = schema.TextLine(
        title="Administrator delegate IAM Role name for the account",
        description="",
        default="",
        required=False,
    )
    is_master = schema.Bool(
        title="Boolean indicating if this a Master account",
        default=False,
        required=False,
    )
    region = schema.TextLine(
        title="Region to install AWS Account specific resources",
        default="no-region-set",
        missing_value = "no-region-set",
        required=True,
        description='Must be a valid AWS Region name',
        constraint = isValidAWSRegionName
    )
    root_email = schema.TextLine(
        title="The email address for the root user of this account",
        required=True,
        description='Must be a valid email address.',
        constraint = isValidEmail
    )
    organization_account_ids = schema.List(
        title="A list of account ids to add to the Master account's AWS Organization",
        value_type = schema.TextLine(),
        required=False,
        description='Each string in the list must contain only digits.'
    )
    admin_iam_users = schema.Dict(
        title="Admin IAM Users",
        value_type = schema.Object(IAdminIAMUser),
        required=False,
    )

class ISecurityGroupRule(IName):
    cidr_ip = schema.TextLine(
        title="CIDR IP",
        default="",
        description="A valid CIDR v4 block or an empty string",
        constraint = isValidCidrIpv4orBlank,
        required=False,
    )
    cidr_ip_v6 = schema.TextLine(
        title="CIDR IP v6",
        description="A valid CIDR v6 block or an empty string",
        default="",
        required=False,
    )
    description=schema.TextLine(
        title="Description",
        default="",
        description="Max 255 characters. Allowed characters are a-z, A-Z, 0-9, spaces, and ._-:/()#,@[]+=;{}!$*.",
        required=False,
    )
    from_port = schema.Int(
        title="From port",
        description="A value of -1 indicates all ICMP/ICMPv6 types. If you specify all ICMP/ICMPv6 types, you must specify all codes.",
        default=-1,
        required=False
    )
    protocol = schema.TextLine(
        title="IP Protocol",
        description="The IP protocol name (tcp, udp, icmp, icmpv6) or number.",
        required=False,
    )
    to_port = schema.Int(
        title="To port",
        description="A value of -1 indicates all ICMP/ICMPv6 types. If you specify all ICMP/ICMPv6 types, you must specify all codes.",
        default=-1,
        required=False
    )
    port = schema.Int(
        title="Port",
        description="A value of -1 indicates all ICMP/ICMPv6 types. If you specify all ICMP/ICMPv6 types, you must specify all codes.",
        default=-1,
        required=False
    )

    @invariant
    def to_from_or_port(obj):
        if obj.port != -1 and (obj.to_port != -1 or obj.from_port != -1):
            raise Invalid("Both 'port' and 'to_port/from_port' must not have values.")
        elif obj.to_port == -1 and obj.from_port != -1:
            raise Invalid("The 'from_port' field must not be blank when 'to_port' has a value.")
        elif obj.from_port == -1 and obj.to_port != -1:
            raise Invalid("The 'to_port' field must not be blank when 'from_port' has a value.")

class IIngressRule(IParent, ISecurityGroupRule):
    "Security group ingress"
    source_security_group = PacoReference(
        title="Source Security Group Reference",
        required=False,
        description="A Paco Reference to a SecurityGroup",
        str_ok=True,
        schema_constraint='ISecurityGroup'
    )

class IEgressRule(IParent, ISecurityGroupRule):
    "Security group egress"
    destination_security_group = PacoReference(
        title="Destination Security Group Reference",
        required=False,
        description="A Paco reference to a SecurityGroup",
        str_ok=True,
        schema_constraint='ISecurityGroup'
    )

class ISecurityGroup(INamed, IDeployable):
    """
AWS Resource: Security Group
    """
    group_name = schema.TextLine(
        title="Group name",
        default="",
        description="Up to 255 characters in length. Cannot start with sg-.",
        required=False,
    )
    group_description=schema.TextLine(
        title="Group description",
        default="",
        description="Up to 255 characters in length",
        required=False,
    )
    ingress = schema.List(
        title="Ingress",
        value_type=schema.Object(schema=IIngressRule),
        description="Every list item must be an IngressRule",
        required=False,
    )
    egress = schema.List(
        title="Egress",
        value_type=schema.Object(schema=IEgressRule),
        description="Every list item must be an EgressRule",
        required=False,
    )


class IApplicationEngines(INamed, IMapping):
    "A container for Application Engines"
    taggedValue('contains', 'IApplicationEngine')

class IType(Interface):
    type = schema.TextLine(
        title="Type of Resources",
        description="A valid AWS Resource type: ASG, LBApplication, etc.",
        required=False,
    )

class IResource(IType, INamed, IDeployable, IDNSEnablable):
    """
AWS Resource to support an Application
    """
    order = schema.Int(
        title="The order in which the resource will be deployed",
        description="",
        min=0,
        default=0,
        required=False,
    )
    change_protected = schema.Bool(
        title="Boolean indicating whether this resource can be modified or not.",
        default=False,
        required=False,
    )

class IServices(INamed, IMapping):
    """
Services
    """
    taggedValue('contains', 'IService')


class IAccountRef(Interface):
    "An account and region for a service"
    account = PacoReference(
        title="Account Reference",
        required=False,
        schema_constraint=IAccount
    )

class IServiceEnvironment(IAccountRef, INamed):
    "A service composed of one or more applications"
    applications = schema.Object(
        title="Applications",
        schema = IApplicationEngines,
        required=False,
    )
    region = schema.TextLine(
        title="Region",
        required=False,
        constraint = isValidAWSRegionName,
    )

class IGlobalResources(INamed, IMapping):
    "A container for global Resources"
    taggedValue('contains', 'mixed')

class IResources(INamed, IMapping):
    "A container of Resources to support an `Application`_."
    taggedValue('contains', 'mixed')

class IResourceGroup(INamed, IDeployable, IDNSEnablable):
    "A group of `Resources`_ to support an `Application`_."
    title=schema.TextLine(
        title="Title",
        default="",
        required=False,
    )
    type = schema.TextLine(
        title="Type"
    )
    order = schema.Int(
        title="The order in which the group will be deployed",
        description="",
        min=0,
        required=True
    )
    resources = schema.Object(IResources)
    dns_enabled = schema.Bool(
        title="",
        required=False,
    )


class IResourceGroups(INamed, IMapping):
    "A container of Application `ResourceGroup`_ objects."
    taggedValue('contains', 'IResourceGroup')

# Alarm and notification schemas

class IAlarmNotifications(INamed, IMapping):
    """
Container for `AlarmNotification`_ objects.
    """
    taggedValue('contains', 'IAlarmNotification')

class IAlarmNotification(INamed):
    """
Alarm Notification
    """
    groups = schema.List(
        title="List of groups",
        value_type=schema.TextLine(
            title="Group"
        ),
        required=True
    )
    classification = schema.TextLine(
        title="Classification filter",
        description="Must be one of: 'performance', 'security', 'health' or ''.",
        constraint = isValidAlarmClassificationFilter,
        default='',
        required=False,
    )
    severity = schema.TextLine(
        title="Severity filter",
        constraint = isValidAlarmSeverityFilter,
        description="Must be one of: 'low', 'critical'",
        required=False,
    )

class INotifiable(Interface):
    """
A notifiable object
    """
    notifications = schema.Object(
        title="Alarm Notifications",
        schema = IAlarmNotifications,
        required=False,
    )

class IAlarmSet(INamed, IMapping, INotifiable):
    """
A container of Alarm objects.
    """
    taggedValue('contains', 'mixed')
    resource_type = schema.TextLine(
        title="Resource type",
        description="Must be a valid AWS resource type",
        required=False,
    )


class IAlarmSets(INamed, IMapping):
    """
Alarm Sets are defined in the file ``monitor/alarmsets.yaml``.

AlarmSets are named to match a Paco Resource type, then a unique AlarmSet name.


.. code-block:: yaml
    :caption: Structure of an alarmets.yaml file

    # AutoScalingGroup alarms
    ASG:
        launch-health:
            GroupPendingInstances-Low:
                # alarm config here ...
            GroupPendingInstances-Critical:
                # alarm config here ...

    # Application LoadBalancer alarms
    LBApplication:
        instance-health:
            HealthyHostCount-Critical:
                # alarm config here ...
        response-latency:
            TargetResponseTimeP95-Low:
                # alarm config here ...
            HTTPCode_Target_4XX_Count-Low:
                # alarm config here ...


The base `Alarm`_ schema contains fields to add additional metadata to alarms. For CloudWatchAlarms, this
metadata set in the AlarmDescription field as JSON:

Alarms can have different contexts, which increases the number of metadata that is populated in the AlarmDescription field:

 * Global context. Only has base context. e.g. a CloudTrail log alarm.

 * NetworkEnvironmnet context. Base and NetworkEnvironment context. e.g. a VPC flow log alarm.

 * Application context alarm. Base, NetworkEnvironment and Application contexts. e,g, an external HTTP health check alarm

 * Resource context alarm. Base, NetworkEnvironment, Application and Resource contexts. e.g. an AutoScalingGroup CPU alarm

.. code-block:: yaml

    Base context for all alarms
    ----------------------------

    "project_name": Project name
    "project_title": Project title
    "account_name": Account name
    "alarm_name": Alarm name
    "classification": Classification
    "severity": Severity
    "topic_arns": SNS Topic ARN subscriptions
    "description": Description (only if supplied)
    "runbook_url": Runbook URL (only if supplied)

    NetworkEnvironment context alarms
    ---------------------------------

    "netenv_name": NetworkEnvironment name
    "netenv_title": NetworkEnvironment title
    "env_name": Environment name
    "env_title": Environment title
    "envreg_name": EnvironmentRegion name
    "envreg_title": EnvironmentRegion title

    Application context alarms
    --------------------------

    "app_name": Application name
    "app_title": Application title

     Resource context alarms
     -----------------------

    "resource_group_name": Resource Group name
    "resource_group_title": Resource Group title
    "resource_name": Resource name
    "resource_title": Resource title

Alarms can be set in the ``monitoring:`` field for `Application`_ and `Resource`_ objects. The name of
each `AlarmSet` should be listed in the ``alarm_sets:`` field. It is possible to override the individual fields of
an Alarm in a netenv file.

.. code-block:: yaml
    :caption: Examples of adding AlarmSets to Environmnets

    environments:
      prod:
        title: "Production"
        default:
          enabled: true
          applications:
            app:
              monitoring:
                enabled: true
                alarm_sets:
                  special-app-alarms:
              groups:
                site:
                  resources:
                    alb:
                      monitoring:
                        enabled: true
                        alarm_sets:
                          core:
                          performance:
                            # Override the SlowTargetResponseTime Alarm threshold field
                            SlowTargetResponseTime:
                              threshold: 2.0

Stylistically, ``monitoring`` and ``alarm_sets`` can be specified in the base ``applications:`` section in a netenv file,
and set to ``enabled: false``. Then only the production environment can override the enabled field to true. This makes it
easy to enable a dev or test environment if you want to test alarms before using in a production environment.

Alternatively, you may wish to only specify the monitoring in the ``environments:`` section of your netenv file only
for production, and keep the base ``applications:`` configuration shorter.


Alarm notifications tell alarms which SNS Topics to notify. Alarm notifications are set with the ``notifications:`` field
at the `Application`_, `Resource`_, `AlarmSet`_ and `Alarm`_ level.

.. code-block:: yaml
    :caption: Examples of Alarm notifications

    applications:
      app:
        enabled: true
        # Application level notifications
        notifications:
          ops_team:
            groups:
            - cloud_ops
        groups:
          site:
            resources:
              web:
                monitoring:
                  # Resource level notifications
                  notifications:
                    web_team:
                      groups:
                      - web
                  alarm_sets:
                    instance-health-cwagent:
                      notifications:
                        # AlarmSet notifications
                        alarmsetnotif:
                          groups:
                          - misterteam
                      SwapPercent-Low:
                        # Alarm level notifications
                        notifications:
                          singlealarm:
                            groups:
                            - oneguygetsthis

Notifications can be filtered for specific ``severity`` and ``classification`` levels. This allows you to direct
critical severity to one group and low severity to another, or to send only performance classification alarms to one
group and security classification alarms to another.

.. code-block:: yaml
    :caption: Examples of severity and classification filters

    notifications:
      severe_security:
        groups:
        - security_group
        severity: 'critical'
        classification: 'security'

Note that although you can configure multiple SNS Topics to subscribe to a single alarm, CloudWatch has a maximum
limit of five SNS Topics that a given alarm may be subscribed to.

It is also possible to write a Paco add-on that overrides the default CloudWatch notifications and instead notifies
a single SNS Topic. This is intended to allow you to write an add-on that directs all alarms through a single Lambda
(regardless or account or region) which is then responsible for delivering or taking action on alarms.

Currently Global and NetworkEnvironment alarms are only supported through Paco add-ons.


.. code-block:: yaml
    :caption: Example alarmsets.yaml for Application, ALB, ASG, RDSMySQL and LogAlarms

    App:
      special-app-alarms:
        CustomMetric:
          description: "Custom metric has been triggered."
          classification: health
          severity: low
          metric_name: "custom_metric"
          period: 86400 # 1 day
          evaluation_periods: 1
          threshold: 1
          comparison_operator: LessThanThreshold
          statistic: Average
          treat_missing_data: breaching
          namespace: 'CustomMetric'

    LBApplication:
      core:
        HealthyHostCount-Critical:
          classification: health
          severity: critical
          description: "Alert if fewer than X number of backend hosts are passing health checks"
          metric_name: "HealthyHostCount"
          dimensions:
            - name: LoadBalancer
              value: paco.ref netenv.wa.applications.ap.groups.site.resources.alb.fullname
            - name: TargetGroup
              value: paco.ref netenv.wa.applications.ap.groups.site.resources.alb.target_groups.ap.fullname
          period: 60
          evaluation_periods: 5
          statistic: Minimum
          threshold: 1
          comparison_operator: LessThanThreshold
          treat_missing_data: breaching
      performance:
        SlowTargetResponseTime:
          severity: low
          classification: performance
          description: "Average HTTP response time is unusually slow"
          metric_name: "TargetResponseTime"
          period: 60
          evaluation_periods: 5
          statistic: Average
          threshold: 1.5
          comparison_operator: GreaterThanOrEqualToThreshold
          treat_missing_data: missing
          dimensions:
            - name: LoadBalancer
              value: paco.ref netenv.wa.applications.ap.groups.site.resources.alb.fullname
            - name: TargetGroup
              value: paco.ref netenv.wa.applications.ap.groups.site.resources.alb.target_groups.ap.fullname
        HTTPCode4XXCount:
          classification: performance
          severity: low
          description: "Large number of 4xx HTTP error codes"
          metric_name: "HTTPCode_Target_4XX_Count"
          period: 60
          evaluation_periods: 5
          statistic: Sum
          threshold: 100
          comparison_operator: GreaterThanOrEqualToThreshold
          treat_missing_data: notBreaching
        HTTPCode5XXCount:
          classification: performance
          severity: low
          description: "Large number of 5xx HTTP error codes"
          metric_name: "HTTPCode_Target_5XX_Count"
          period: 60
          evaluation_periods: 5
          statistic: Sum
          threshold: 100
          comparison_operator: GreaterThanOrEqualToThreshold
          treat_missing_data: notBreaching

    ASG:
      core:
        StatusCheck:
          classification: health
          severity: critical
          metric_name: "StatusCheckFailed"
          namespace: AWS/EC2
          period: 60
          evaluation_periods: 5
          statistic: Maximum
          threshold: 0
          comparison_operator: GreaterThanThreshold
          treat_missing_data: breaching
        CPUTotal:
          classification: performance
          severity: critical
          metric_name: "CPUUtilization"
          namespace: AWS/EC2
          period: 60
          evaluation_periods: 30
          threshold: 90
          statistic: Average
          treat_missing_data: breaching
          comparison_operator: GreaterThanThreshold
      cwagent:
        SwapPercentLow:
          classification: performance
          severity: low
          metric_name: "swap_used_percent"
          namespace: "CWAgent"
          period: 60
          evaluation_periods: 5
          statistic: Maximum
          threshold: 80
          comparison_operator: GreaterThanThreshold
          treat_missing_data: breaching
        DiskSpaceLow:
          classification: health
          severity: low
          metric_name: "disk_used_percent"
          namespace: "CWAgent"
          period: 300
          evaluation_periods: 1
          statistic: Minimum
          threshold: 60
          comparison_operator: GreaterThanThreshold
          treat_missing_data: breaching
        DiskSpaceCritical:
          classification: health
          severity: low
          metric_name: "disk_used_percent"
          namespace: "CWAgent"
          period: 300
          evaluation_periods: 1
          statistic: Minimum
          threshold: 80
          comparison_operator: GreaterThanThreshold
          treat_missing_data: breaching

      # CloudWatch Log Alarms
      log-alarms:
        CfnInitError:
          type: LogAlarm
          description: "CloudFormation Init Errors"
          classification: health
          severity: critical
          log_set_name: 'cloud'
          log_group_name: 'cfn_init'
          metric_name: "CfnInitErrorMetric"
          period: 300
          evaluation_periods: 1
          threshold: 1.0
          treat_missing_data: notBreaching
          comparison_operator: GreaterThanOrEqualToThreshold
          statistic: Sum
        CodeDeployError:
          type: LogAlarm
          description: "CodeDeploy Errors"
          classification: health
          severity: critical
          log_set_name: 'cloud'
          log_group_name: 'codedeploy'
          metric_name: "CodeDeployErrorMetric"
          period: 300
          evaluation_periods: 1
          threshold: 1.0
          treat_missing_data: notBreaching
          comparison_operator: GreaterThanOrEqualToThreshold
          statistic: Sum
        WsgiError:
          type: LogAlarm
          description: "HTTP WSGI Errors"
          classification: health
          severity: critical
          log_set_name: 'ap'
          log_group_name: 'httpd_error'
          metric_name: "WsgiErrorMetric"
          period: 300
          evaluation_periods: 1
          threshold: 1.0
          treat_missing_data: notBreaching
          comparison_operator: GreaterThanOrEqualToThreshold
          statistic: Sum
        HighHTTPTraffic:
          type: LogAlarm
          description: "High number of http access logs"
          classification: performance
          severity: low
          log_set_name: 'ap'
          log_group_name: 'httpd_access'
          metric_name: "HttpdLogCountMetric"
          period: 300
          evaluation_periods: 1
          threshold: 1000
          treat_missing_data: ignore
          comparison_operator: GreaterThanOrEqualToThreshold
          statistic: Sum

    RDSMysql:
      basic-database:
        CPUTotal-Low:
          classification: performance
          severity: low
          metric_name: "CPUUtilization"
          namespace: AWS/RDS
          period: 300
          evaluation_periods: 6
          threshold: 90
          comparison_operator: GreaterThanOrEqualToThreshold
          statistic: Average
          treat_missing_data: breaching

        FreeableMemoryAlarm:
          classification: performance
          severity: low
          metric_name: "FreeableMemory"
          namespace: AWS/RDS
          period: 300
          evaluation_periods: 1
          threshold: 100000000
          comparison_operator: LessThanOrEqualToThreshold
          statistic: Minimum
          treat_missing_data: breaching

        FreeStorageSpaceAlarm:
          classification: performance
          severity: low
          metric_name: "FreeStorageSpace"
          namespace: AWS/RDS
          period: 300
          evaluation_periods: 1
          threshold: 5000000000
          comparison_operator: LessThanOrEqualToThreshold
          statistic: Minimum
          treat_missing_data: breaching


    """
    taggedValue('contains', 'IAlarmSet')


class IDimension(IParent):
    """
A dimension of a metric
    """
    name = schema.TextLine(
        title="Dimension name",
        required=False,
    )
    value = PacoReference(
        title="String or a Paco Reference to resource output.",
        required=False,
        str_ok=True,
        schema_constraint='Interface'
    )

class IAlarm(INamed, IDeployable, IName, INotifiable):
    """
A Paco Alarm.

This is a base schema which defines metadata useful to categorize an alarm.
    """
    classification = schema.TextLine(
        title="Classification",
        description="Must be one of: 'performance', 'security' or 'health'",
        constraint = isValidAlarmClassification,
        required=True,
        default='unset',
        missing_value = 'unset',
    )
    description=schema.TextLine(
        title="Description",
        required=False,
    )
    notification_groups = schema.List(
        readonly = True,
        title="List of notificationn groups the alarm is subscribed to.",
        value_type=schema.TextLine(title="Notification group name"),
        required=False,
    )
    runbook_url = schema.TextLine(
        title="Runbook URL",
        required=False,
    )
    severity = schema.TextLine(
        title="Severity",
        default="low",
        constraint = isValidAlarmSeverity,
        description="Must be one of: 'low', 'critical'",
        required=False,
    )

class ICloudWatchAlarm(IType, IAlarm):
    """
A CloudWatch Alarm
    """
    @invariant
    def evaluate_low_sample_statistic(obj):
        if getattr(obj, 'evaluate_low_sample_count_percentile', None):
            if getattr(obj, 'statistic', None):
                raise Invalid('Field `evaluate_low_sample_count_percentile` can not be used with the `statistic` field, only with the `extended_statistic` field.')
            if not getattr(obj, 'extended_statistic', None):
                raise Invalid('Field `evaluate_low_sample_count_percentile` requires field `extended_statistic` to be a valid percentile value.')

    @invariant
    def check_statistic(obj):
        "Must be one of ExtendedStatistic, Metrics or Statistic"
        # ToDo: implement Metrics
        if not getattr(obj, 'statistic', None) and not getattr(obj, 'extended_statistic', None):
            raise Invalid('Must include one of `statistic` or `extended_statistic`.')

    alarm_actions = schema.List(
        title="Alarm Actions",
        readonly = True,
        value_type = schema.TextLine(
            title="Alarm Action",
            required=False,
        ),
        required=False,
    )
    alarm_description=schema.Text(
        title="Alarm Description",
        readonly = True,
        description="Valid JSON document with Paco fields.",
        required=False,
    )
    actions_enabled = schema.Bool(
        title="Actions Enabled",
        readonly = True,
        required=False,
    )
    comparison_operator = schema.TextLine(
        title="Comparison operator",
        constraint = isComparisonOperator,
        description="Must be one of: 'GreaterThanThreshold','GreaterThanOrEqualToThreshold', 'LessThanThreshold', 'LessThanOrEqualToThreshold'",
        required=False,
    )
    dimensions = schema.List(
        title="Dimensions",
        value_type = schema.Object(schema=IDimension),
        required=False,
    )
    enable_ok_actions = schema.Bool(
        title="Enable Actions when alarm transitions to the OK state.",
        default=False,
        required=False,
    )
    enable_insufficient_data_actions = schema.Bool(
        title="Enable Actions when alarm transitions to the INSUFFICIENT_DATA state.",
        default=False,
        required=False,
    )
    evaluate_low_sample_count_percentile = schema.TextLine(
        title="Evaluate low sample count percentile",
        description="Must be one of `evaluate` or `ignore`.",
        required=False,
        constraint = isValidEvaluateLowSampleCountPercentileValue,
    )
    evaluation_periods = schema.Int(
        title="Evaluation periods",
        min=1,
        required=False,
    )
    extended_statistic = schema.TextLine(
        title="Extended statistic",
        description="A value between p0.0 and p100.",
        required=False,
        constraint = isValidExtendedStatisticValue,
    )
    # ToDo: implement Metrics - also update invariant
    # metrics = schema.List()
    metric_name = schema.TextLine(
        title="Metric name",
        required=True,
    )
    namespace = schema.TextLine(
        title="Namespace",
        required=False,
    )
    period = schema.Int(
        title="Period in seconds",
        required=False,
        min=1,
    )
    statistic = schema.TextLine(
        title="Statistic",
        required=False,
        description="Must be one of `Maximum`, `SampleCount`, `Sum`, `Minimum`, `Average`.",
        constraint = isValidAlarmStatisticValue,
    )
    threshold = schema.Float(
        title="Threshold",
        required=False,
    )
    treat_missing_data = schema.TextLine(
        title="Treat missing data",
        description="Must be one of `breaching`, `notBreaching`, `ignore` or `missing`.",
        required=False,
        constraint = isMissingDataValue,
    )

class ICloudWatchLogAlarm(ICloudWatchAlarm):
    log_set_name = schema.TextLine(
        title="Log Set Name",
        required=True
    )
    log_group_name = schema.TextLine(
        title="Log Group Name",
        required=True
    )

class INotificationGroups(IAccountRef):
    "Container for Notification Groups"
    regions = schema.List(
        title="Regions to provision the Notification Groups in. Special list of ['ALL'] will select all of the project's active regions.",
        required=False,
        default=['ALL'],
        constraint=isValidAWSRegionOrAllList
    )

class IDashboardVariables(INamed, IMapping):
    """
Variables to make available to the dashboard JSON for interpolation.
    """
    taggedValue('contains', 'mixed')

class ICloudWatchDashboard(IResource):
    dashboard_file = StringFileReference(
        title="File path to a JSON templated dashboard.",
        required=True
    )
    variables = schema.Dict(
        title="Dashboard Variables",
        default={},
        required=False
    )

# Logging schemas

class ICloudWatchLogRetention(Interface):
    expire_events_after_days = schema.TextLine(
        title="Expire Events After. Retention period of logs in this group",
        description="",
        default="",
        constraint = isValidCloudWatchLogRetention,
        required=False,
    )

class ICloudWatchLogSources(INamed, IMapping):
    """
A container of `CloudWatchLogSource`_ objects.
    """
    taggedValue('contains', 'ICloudWatchLogSource')

class ICloudWatchLogSource(INamed, ICloudWatchLogRetention):
    """
Log source for a CloudWatch agent.
    """
    encoding = schema.TextLine(
        title="Encoding",
        default="utf-8",
        required=False,
    )
    log_stream_name = schema.TextLine(
        title="Log stream name",
        description="CloudWatch Log Stream name",
        required=True,
        min_length=1
    )
    multi_line_start_pattern = schema.Text(
        title="Multi-line start pattern",
        default="",
        required=False,
    )
    path = schema.TextLine(
        title="Path",
        default="",
        required=True,
        description="Must be a valid filesystem path expression. Wildcard * is allowed."
    )
    timestamp_format = schema.TextLine(
        title="Timestamp format",
        default="",
        required=False,
    )
    timezone = schema.TextLine(
        title="Timezone",
        default="Local",
        constraint = isValidCWAgentTimezone,
        description="Must be one of: 'Local', 'UTC'",
        required=False,
    )

class IMetricTransformation(Interface):
    """
Metric Transformation
    """
    default_value = schema.Float(
        title="The value to emit when a filter pattern does not match a log event.",
        required=False,
    )
    metric_name = schema.TextLine(
        title="The name of the CloudWatch Metric.",
        required=True,
    )
    metric_namespace = schema.TextLine(
        title="The namespace of the CloudWatch metric. If not set, the namespace used will be 'AIM/{log-group-name}'.",
        required=False,
        max_length = 255,
    )
    metric_value = schema.TextLine(
        title="The value that is published to the CloudWatch metric.",
        required=True,
    )

class IMetricFilters(INamed, IMapping):
    """
Container for `Metric`Filter` objects.
    """
    taggedValue('contains', 'IMetricFilter')

class IMetricFilter(INamed):
    """
    Metric filter
    """
    filter_pattern = schema.Text(
        title="Filter pattern",
        default="",
        required=False,
    )
    metric_transformations = schema.List(
        title="Metric transformations",
        value_type=schema.Object(
            title="Metric Transformation",
            schema=IMetricTransformation
        ),
        required=False,
    )

class ICloudWatchLogGroups(INamed, IMapping):
    """
Container for `CloudWatchLogGroup`_ objects.
    """
    taggedValue('contains', 'ICloudWatchLogGroup')


class ICloudWatchLogGroup(INamed, ICloudWatchLogRetention):
    """
A CloudWatchLogGroup is responsible for retention, access control and metric filters
    """
    metric_filters = schema.Object(
        title="Metric Filters",
        schema = IMetricFilters,
        required=False,
    )
    sources = schema.Object(
        title="A CloudWatchLogSources container",
        schema = ICloudWatchLogSources,
        required=False,
    )
    log_group_name = schema.TextLine(
        title="Log group name. Can override the LogGroup name used from the name field.",
        description="",
        default="",
        required=False,
    )

class ICloudWatchLogSets(INamed, IMapping):
    """
Container for `CloudWatchLogSet`_ objects.
    """
    taggedValue('contains', 'ICloudWatchLogSet')

class ICloudWatchLogSet(INamed, ICloudWatchLogRetention):
    """
A set of Log Group objects
    """
    log_groups = schema.Object(
        title="A CloudWatchLogGroups container",
        schema = ICloudWatchLogGroups,
        required=False,
    )

class ICloudWatchLogging(INamed, ICloudWatchLogRetention):
    """
CloudWatch Logging configuration
    """
    log_sets = schema.Object(
        title="A CloudWatchLogSets container",
        schema = ICloudWatchLogSets,
        required=False,
    )

# Events

class IEventsRule(IResource):
    """
Events Rule
    """
    # ToDo: add event_pattern field and invariant to make schedule_expression conditional
    # ToDo: constraint regex that validates schedule_expression
    description=schema.Text(
        title="Description",
        required=False,
        default='',
        max_length=512,
    )
    schedule_expression = schema.TextLine(
        title="Schedule Expression",
        required=True
    )
    # ToDo: constrain List to not be empty
    targets = schema.List(
        title="The AWS Resources that are invoked when the Rule is triggered.",
        description="",
        required=True,
        value_type=PacoReference(
            title="Paco Reference to an AWS Resource to invoke",
            schema_constraint='Interface',
        ),
    )

# Metric and monitoring schemas

class IMetric(Interface):
    """
A set of metrics to collect and an optional collection interval:

- name: disk
    measurements:
    - free
    collection_interval: 900
    """
    name = schema.TextLine(
        title="Metric(s) group name",
        required=False,
    )
    measurements = schema.List(
        title="Measurements",
        value_type=schema.TextLine(title="Metric measurement name"),
        required=False,
    )
    collection_interval = schema.Int(
        title="Collection interval",
        description="",
        min=1,
        required=False,
    )
    resources = schema.List(
        title="List of resources for this metric",
        value_type=schema.TextLine(title="Metric resource"),
        required=False
    )
    drop_device = schema.Bool(
        title="Drops the device name from disk metrics",
        default=True,
        required=False
    )


class IHealthChecks(INamed, IMapping):
    "Container for `Route53HealthCheck`_ objects."
    taggedValue('contains', 'IRoute53HealthCheck')

class IMonitorConfig(IDeployable, INamed, INotifiable):
    """
A set of metrics and a default collection interval
    """
    asg_metrics = schema.List(
        title="ASG Metrics",
        value_type=schema.TextLine(),
        constraint=isValidASGMetricNames,
        description="Must be one of: 'GroupMinSize', 'GroupMaxSize', 'GroupDesiredCapacity', 'GroupInServiceInstances', 'GroupPendingInstances', 'GroupStandbyInstances', 'GroupTerminatingInstances', 'GroupTotalInstances'",
        required=False,
    )
    alarm_sets = schema.Object(
        title="Sets of Alarm Sets",
        schema=IAlarmSets,
        required=False,
    )
    collection_interval = schema.Int(
        title="Collection interval",
        min=1,
        default=60,
        required=False,
    )
    health_checks = schema.Object(
        title="Set of Health Checks",
        schema=IHealthChecks,
        required=False,
    )
    log_sets = schema.Object(
        title="Sets of Log Sets",
        schema=ICloudWatchLogSets,
        required=False,
    )
    metrics = schema.List(
        title="Metrics",
        value_type=schema.Object(IMetric),
        required=False,
    )

class IMonitorable(Interface):
    """
A monitorable resource
    """
    monitoring = schema.Object(
        schema = IMonitorConfig,
        required=False,
    )

class IS3BucketPolicy(Interface):
    """
S3 Bucket Policy
    """
    # ToDo: Validate actions using awacs
    action = schema.List(
        title="List of Actions",
        value_type=schema.TextLine(
            title="Action"
        ),
        required=True,
    )
    aws = schema.List(
        title="List of AWS Principles.",
        description="Either this field or the principal field must be set.",
        value_type = schema.TextLine(
            title="AWS Principle"
        ),
        required=False,
    )
    condition = schema.Dict(
        title="Condition",
        description='Each Key is the Condition name and the Value must be a dictionary of request filters. e.g. { "StringEquals" : { "aws:username" : "johndoe" }}',
        default={},
        required=False,
        # ToDo: Use awacs to add a constraint to check for valid conditions
    )
    # ToDo: validate principal using awacs
    # ToDo: validate that only one principal type is supplied, as that is all that is currently supported by paco.cftemplates.s3.py
    principal = schema.Dict(
        title="Prinicpals",
        description="Either this field or the aws field must be set. Key should be one of: AWS, Federated, Service or CanonicalUser. Value can be either a String or a List.",
        default={},
        required=False,
    )
    effect = schema.TextLine(
        title="Effect",
        default="Deny",
        required=True,
        description="Must be one of: 'Allow', 'Deny'",
    )
    resource_suffix = schema.List(
        title="List of AWS Resources Suffixes",
        value_type=schema.TextLine(
            title="Resources Suffix"
        ),
        required=True,
    )
    @invariant
    def aws_or_principal(obj):
        if obj.aws == [] and obj.principal == {}:
            raise Invalid("Either the aws or the principal field must not be blank.")
        if obj.aws != [] and obj.principal != {}:
            raise Invalid("Can not set bot the aws and the principal fields.")


class IS3LambdaConfiguration(IParent):
    # ToDo: add constraint
    event = schema.TextLine(
        title="S3 bucket event for which to invoke the AWS Lambda function",
        description="Must be a supported event type: https://docs.aws.amazon.com/AmazonS3/latest/dev/NotificationHowTo.html",
        required=False,
    )
    function = PacoReference(
        title="Lambda function to notify",
        required=False,
        schema_constraint='ILambda',
    )

class IS3NotificationConfiguration(IParent):
    lambdas = schema.List(
        title="Lambda configurations",
        value_type = schema.Object(IS3LambdaConfiguration),
        required=False,
    )

class IS3StaticWebsiteHostingRedirectRequests(IParent):
    target = PacoReference(
        title="Target S3 Bucket or domain.",
        str_ok=True,
        required=True,
        schema_constraint='IS3Bucket'
    )
    protocol = schema.TextLine(
        title="Protocol",
        required=True
    )

class IS3StaticWebsiteHosting(IParent, IDeployable):
    redirect_requests = schema.Object(
        title="Redirect requests configuration.",
        schema=IS3StaticWebsiteHostingRedirectRequests,
        required=False
    )

class IS3Bucket(IResource, IDeployable):
    """
S3 Bucket
    """
    bucket_name = schema.TextLine(
        title="Bucket Name",
        description="A short unique name to assign the bucket.",
        default="bucket",
        required=True,
    )
    account = PacoReference(
        title="Account that S3 Bucket belongs to.",
        required=False,
        schema_constraint='IAccount',
    )
    deletion_policy = schema.TextLine(
        title="Bucket Deletion Policy",
        default="delete",
        required=False,
    )
    notifications = schema.Object(
        title="Notification configuration",
        schema = IS3NotificationConfiguration,
        required=False,
    )
    policy = schema.List(
        title="List of S3 Bucket Policies",
        description="",
        value_type=schema.Object(IS3BucketPolicy),
        required=False,
    )
    region = schema.TextLine(
        title="Bucket region",
        default=None,
        required=False
    )
    cloudfront_origin = schema.Bool(
        title="Creates and listens for a CloudFront Access Origin Identity",
        required=False,
        default=False,
    )
    external_resource = schema.Bool(
        title='Boolean indicating whether the S3 Bucket already exists or not',
        default=False,
        required=False,
    )
    versioning = schema.Bool(
        title="Enable Versioning on the bucket.",
        default=False,
        required=False,
    )
    static_website_hosting = schema.Object(
        title="Static website hosting configuration.",
        required=False,
        schema = IS3StaticWebsiteHosting
    )

class IS3Resource(INamed):
    """
EC2 Resource Configuration
    """
    buckets = schema.Dict(
        title="Dictionary of S3Bucket objects",
        value_type = schema.Object(IS3Bucket),
        default={},
        required=False,
    )

class IApplicationEngine(INamed, IDeployable, INotifiable, IMonitorable, IDNSEnablable):
    """
Application Engine : A template describing an application
    """
    order = schema.Int(
        title="The order in which the application will be processed",
        description="",
        min=0,
        default=0,
        required=False
    )
    groups = schema.Object(IResourceGroups)


class IApplication(IApplicationEngine):
    """
An Application is groups of cloud resources to support a workload.
    """

class ICodePipeBuildDeploy(IResource):
    """
Code Pipeline: Build and Deploy
    """
    deployment_environment = schema.TextLine(
        title="Deployment Environment",
        description="",
        default="",
        required=False,
    )
    deployment_branch_name = schema.TextLine(
        title="Deployment Branch Name",
        description="",
        default="",
        required=False,
    )
    manual_approval_enabled = schema.Bool(
        title="Manual approval enabled",
        description="",
        default=False,
        required=False,
    )
    manual_approval_notification_email = schema.TextLine(
        title="Manual approval notification email",
        description="",
        default="",
        required=False,
    )
    codecommit_repository = PacoReference(
        title='CodeCommit Respository',
        required=False,
        schema_constraint='ICodeCommitRepository',
    )
    asg = PacoReference(
        title="ASG Reference",
        required=False,
        schema_constraint='IASG'
    )
    auto_rollback_enabled = schema.Bool(
        title="Automatic rollback enabled",
        description="",
        default=True,
        required=False,
    )
    deploy_config_type = schema.TextLine(
        title="Deploy Config Type",
        description="",
        default="HOST_COUNT",
        required=False,
    )
    deploy_style_option = schema.TextLine(
        title="Deploy Style Option",
        description="",
        default="WITH_TRAFFIC_CONTROL",
        required=False,
    )
    deploy_config_value = schema.Int(
        title="Deploy Config Value",
        description="",
        default=0,
        required=False,
    )
    deploy_instance_role = PacoReference(
        title="Deploy Instance Role Reference",
        required=False,
        schema_constraint='IRole'
    )
    elb_name = schema.TextLine(
        title="ELB Name",
        description="",
        default="",
        required=False,
    )
    alb_target_group = PacoReference(
        title="ALB Target Group to deploy to",
        required=False,
        schema_constraint='ITargetGroup'
    )
    tools_account = PacoReference(
        title="Account where CodePipeline runs",
        required=False,
        schema_constraint='IAccount'
    )
    cross_account_support = schema.Bool(
        title="Cross Account Support",
        description="",
        default=False,
        required=False,
    )
    artifacts_bucket = PacoReference(
        title="S3 Bucket for Artifacts",
        description="",
        required=False,
        schema_constraint=IS3Bucket
    )
    codebuild_image = schema.TextLine(
        title='CodeBuild Docker Image',
        required=False,
    )
    codebuild_compute_type = schema.TextLine(
        title='CodeBuild Compute Type',
        constraint = isValidCodeBuildComputeType,
        required=False,
    )
    timeout_mins = schema.Int(
        title='Timeout in Minutes',
        min=5,
        max=480,
        default=60,
        required=False,
    )

class IEC2KeyPair(INamed):
    """
EC2 SSH Key Pair
    """
    keypair_name = schema.TextLine(
        title="The name of the EC2 KeyPair",
        description="",
        required=True
    )
    region = schema.TextLine(
        title="AWS Region",
        description="Must be a valid AWS Region name",
        default="no-region-set",
        missing_value="no-region-set",
        required=True,
        constraint=isValidAWSRegionName,
    )
    account = PacoReference(
        title='AWS Account the key pair belongs to',
        required=False,
        schema_constraint='IAccount'
    )

class IEC2KeyPairs(INamed, IMapping):
    """
Container for `EC2KeyPair`_ objects.
    """
    taggedValue('contains', 'IEC2KeyPair')

class IEC2Resource(INamed):
    """
EC2 Resource Configuration
    """
    keypairs = schema.Object(
        title="Group of EC2 Key Pairs",
        schema=IEC2KeyPairs,
        required=False,
    )

class IService(IResource):
    """
Specialized type of Resource
    """

class IEC2(IResource):
    """
EC2 Instance
    """
    associate_public_ip_address = schema.Bool(
        title="Associate Public IP Address",
        description="",
        default=False,
        required=False,
    )
    instance_iam_profile = Attribute("Instance IAM Profile")
    instance_ami = schema.TextLine(
        title="Instance AMI",
        description="",
        required=False,
    )
    instance_key_pair = PacoReference(
        title="key pair for connections to instance",
        description="",
        required=False,
        schema_constraint=IEC2KeyPair
    )
    instance_type = schema.TextLine(
        title="Instance type",
        description="",
        required=False,
    )
    segment = schema.TextLine(
        title="Segment",
        description="",
        required=False,
    )
    security_groups = schema.List(
        title="Security groups",
        description="",
        value_type=PacoReference(
            title="Paco reference",
            schema_constraint='ISecurityGroup',
        ),
        required=False,
    )
    root_volume_size_gb = schema.Int(
        title="Root volume size GB",
        description="",
        default=8,
        min=8,
        required=False,
    )
    disable_api_termination = schema.Bool(
        title="Disable API Termination",
        description="",
        default=False,
        required=False,
    )
    private_ip_address = schema.TextLine(
        title="Private IP Address",
        description="",
        required=False,
    )
    user_data_script = schema.Text(
        title="User data script",
        description="",
        default="",
        required=False,
    )


class INetworkEnvironments(INamed, IMapping):
    """
Container for `NetworkEnvironment`_ objects.
    """
    taggedValue('contains', 'INetworkEnvironment')

class IProject(INamed, IMapping):
    "Project : the root node in the config for a Paco Project"
    taggedValue('contains', 'mixed')
    paco_project_version = schema.TextLine(
        title="Paco project version",
        default="",
        required=False,
    )
    active_regions = schema.List(
        title="Regions that resources can be provisioned in",
        value_type = schema.TextLine(),
        constraint = isValidAWSRegionList,
        required=False,
    )
    legacy_flags = schema.List(
        title='List of Legacy Flags',
        value_type = schema.TextLine(),
        constraint = isValidLegacyFlagList,
        required=False,
    )

class IInternetGateway(IDeployable):
    """
AWS Resource: IGW
    """

class INATGateway(INamed, IDeployable):
    """
NAT Gateway
    """
    type = schema.TextLine(
        title='NAT Gateway type',
        default='Managed',
        required=False,
        constraint=IsValidNATGatewayType
    )
    availability_zone = schema.TextLine(
        title='Availability Zones to launch instances in.',
        description="Can be 'all' or number of AZ: 1, 2, 3, 4 ...",
        default='all',
        required=False,
        constraint=IsValidASGAvailabilityZone
    )
    segment = PacoReference(
        title="Segment",
        description="",
        required=False,
        schema_constraint='ISegment'
    )
    default_route_segments = schema.List(
        title="Default Route Segments",
        description="",
        value_type=PacoReference(
            title="Segment",
            schema_constraint="ISegment"
        ),
        required=False,
    )
    security_groups = schema.List(
        title="Security Groups",
        value_type=PacoReference(
            title="Paco reference",
            schema_constraint='ISecurityGroup'
        ),
        required=False,
    )
    ec2_key_pair = PacoReference(
        title="EC2 key pair",
        description="",
        required=False,
        schema_constraint=IEC2KeyPair
    )
    ec2_instance_type = schema.TextLine(
        title="EC2 Instance Type",
        required=False,
        default='t2.nano'
    )


class IVPNGateway(IDeployable):
    """
VPN Gateway
    """

class IPrivateHostedZone(IDeployable):
    """
Private Hosted Zone
    """
    name = schema.TextLine(
        title="Hosted zone name",
        required=False,
    )
    vpc_associations = schema.List(
        title="List of VPC Ids",
        required=False,
        value_type = schema.TextLine(
            title="VPC ID"
        ),
        default=None
    )

class ISegment(INamed, IDeployable):
    """
Segment
    """
    internet_access = schema.Bool(
        title="Internet Access",
        default=False,
        required=False,
    )
    az1_cidr = schema.TextLine(
        title="Availability Zone 1 CIDR",
        default="",
        required=False,
    )
    az2_cidr = schema.TextLine(
        title="Availability Zone 2 CIDR",
        default="",
        required=False,
    )
    az3_cidr = schema.TextLine(
        title="Availability Zone 3 CIDR",
        default="",
        required=False,
    )
    az4_cidr = schema.TextLine(
        title="Availability Zone 4 CIDR",
        default="",
        required=False,
    )
    az5_cidr = schema.TextLine(
        title="Availability Zone 5 CIDR",
        default="",
        required=False,
    )
    az6_cidr = schema.TextLine(
        title="Availability Zone 6 CIDR",
        default="",
        required=False,
    )

class IVPCPeeringRoute(IParent):
    """
VPC Peering Route
    """
    segment = PacoReference(
        title="Segment",
        required=False,
        schema_constraint='ISegment'
    )
    cidr = schema.TextLine(
        title="CIDR IP",
        default="",
        description="A valid CIDR v4 block or an empty string",
        constraint = isValidCidrIpv4orBlank,
        required=False,
    )

class IVPCPeering(INamed, IDeployable):
    """
VPC Peering
    """
    # peer_* is used when peering with an external VPC
    peer_role_name = schema.TextLine(
        title='Remote peer role name',
        required=False
    )
    peer_vpcid = schema.TextLine(
        title='Remote peer VPC Id',
        required=False
    )
    peer_account_id = schema.TextLine(
        title='Remote peer AWS account Id',
        required=False
    )
    peer_region = schema.TextLine(
        title='Remote peer AWS region',
        required=False
    )
    # network_environment is used when peering with a network environment
    # local to the project.
    network_environment = PacoReference(
        title='Network Environment Reference',
        required=False,
        schema_constraint='INetworkEnvironment'
    )
    # Routes forward traffic to the peering connection
    routing = schema.List(
        title="Peering routes",
        value_type = schema.Object(IVPCPeeringRoute),
        required=True
    )

class IVPC(INamed, IDeployable):
    """
AWS Resource: VPC
    """
    cidr = schema.TextLine(
        title="CIDR",
        description="",
        default="",
        required=False,
    )
    enable_dns_hostnames = schema.Bool(
        title="Enable DNS Hostnames",
        description="",
        default=False,
        required=False,
    )
    enable_dns_support = schema.Bool(
        title="Enable DNS Support",
        description="",
        default=False,
        required=False,
    )
    enable_internet_gateway = schema.Bool(
        title="Internet Gateway",
        description="",
        default=False,
        required=False,
    )
    nat_gateway = schema.Dict(
        title="NAT Gateway",
        description="",
        value_type = schema.Object(INATGateway),
        required=True,
        default={}
    )
    vpn_gateway = schema.Dict(
        title="VPN Gateway",
        description="",
        value_type = schema.Object(IVPNGateway),
        required=True,
        default={}
    )
    private_hosted_zone = schema.Object(
        title="Private hosted zone",
        description="",
        schema = IPrivateHostedZone,
        required=False,
    )
    security_groups = schema.Dict(
        # This is a dict of dicts ...
        title="Security groups",
        default={},
        description="Two level deep dictionary: first key is Application name, second key is Resource name.",
        required=False,
    )
    segments = schema.Dict(
        title="Segments",
        value_type = schema.Object(ISegment),
        required=False,
    )
    peering = schema.Dict(
        title='VPC Peering',
        value_type = schema.Object(IVPCPeering),
        required=False,
    )

class INetworkEnvironment(INamed, IDeployable, IMapping):
    """
NetworkEnvironment : A template for a network.
    """
    # technically contains IEnvironment but there are set by the loader
    # for the docs we do not want to indicate that environments are configured from within
    # the network: key.
    taggedValue('contains', 'mixed')
    availability_zones = schema.Int(
        title="Availability Zones",
        description="",
        default=0,
        required=False,
    )
    vpc = schema.Object(
        title="VPC",
        description="",
        schema=IVPC,
        required=False,
    )

class ICredentials(INamed):
    aws_access_key_id = schema.TextLine(
        title="AWS Access Key ID",
        description="",
        default="",
        required=False,
    )
    aws_secret_access_key = schema.TextLine(
        title="AWS Secret Access Key",
        description="",
        default="",
        required=False,
    )
    aws_default_region = schema.TextLine(
        title="AWS Default Region",
        description="Must be a valid AWS Region name",
        default="no-region-set",
        missing_value = "no-region-set",
        required=True,
        constraint = isValidAWSRegionName
    )
    master_account_id = schema.TextLine(
        title="Master AWS Account ID",
        description="",
        default="",
        required=False,
    )
    master_admin_iam_username = schema.TextLine(
        title="Master Account Admin IAM Username",
        description="",
        default="",
        required=False,
    )
    admin_iam_role_name = schema.TextLine(
        title="Administrator IAM Role Name",
        required=False,
    )
    mfa_session_expiry_secs = schema.Int(
        title='The number of seconds before an MFA token expires.',
        default=60 * 60,    # 1 hour: 3600 seconds
        min=60 * 15,        # 15 minutes: 900 seconds
        max=(60 * 60) * 12, # 12 hours: 43200 seconds
        required=False,
    )
    assume_role_session_expiry_secs = schema.Int(
        title='The number of seconds before an assumed role token expires.',
        default=60 * 15,   # 15 minutes: 900 seconds
        min=60 * 15,       # 15 minutes: 900 seconds
        max=60 * 60,       # 1 hour: 3600 seconds
        required=False,
    )

class INetwork(INetworkEnvironment):
    # contains Environment objects but do not indicate this
    # in the docs, they are configured under `environments:`.
    taggedValue('contains', 'mixed')
    aws_account = PacoReference(
        title='Account this Network belongs to',
        required=False,
        schema_constraint='IAccount',
    )

# Secrets Manager schemas

class IGenerateSecretString(IParent, IDeployable):
    exclude_characters = schema.Text(
        title="A string that includes characters that should not be included in the generated password.",
        required=False,
        max_length=4096
    )
    exclude_lowercase = schema.Bool(
        title="The generated password should not include lowercase letters.",
        default=False,
        required=False
    )
    exclude_numbers = schema.Bool(
        title="The generated password should exclude digits.",
        default=False,
        required=False
    )
    exclude_punctuation = schema.Bool(
        title="The generated password should not include punctuation characters.",
        default=False,
        required=False
    )
    exclude_uppercase = schema.Bool(
        title="The generated password should not include uppercase letters.",
        default=False,
        required=False
    )
    generate_string_key = schema.TextLine(
        title="The JSON key name that's used to add the generated password to the JSON structure.",
        required=False,
        max_length=10240
    )
    include_space = schema.Bool(
        title="The generated password can include the space character.",
        required=False
    )
    password_length = schema.Int(
        title="The desired length of the generated password.",
        default=32,
        required=False
    )
    require_each_included_type = schema.Bool(
        title="The generated password must include at least one of every allowed character type.",
        default=True,
        required=False
    )
    secret_string_template = schema.Text(
        title="A properly structured JSON string that the generated password can be added to.",
        required=False,
        max_length=10240
    )


class ISecretsManagerSecret(INamed, IDeployable):
    """Secret for the Secrets Manager."""
    generate_secret_string = schema.Object(
        title="Generate SecretString object",
        required=False,
        schema=IGenerateSecretString,
        default=None
    )

class ISecretsManagerGroup(INamed, IMapping):
    """Container for `SecretsManagerSecret`_ objects."""
    taggedValue('contains', 'ISecretsManagerSecret')

class ISecretsManagerApplication(INamed, IMapping):
    """Container for `SecretsManagerGroup`_ objects."""
    taggedValue('contains', 'ISecretsManagerGroup')

class ISecretsManager(INamed, IMapping):
    """Secrets Manager contains `SecretManagerApplication` objects."""
    taggedValue('contains', 'ISecretsManagerApplication')

# Environment, Account and Region containers

class IAccountContainer(INamed, IMapping):
    """Container for `RegionContainer`_ objects."""
    taggedValue('contains', 'IRegionContainer')

class IRegionContainer(INamed, IMapping):
    "Container for objects which do not belong to a specific Environment."
    taggedValue('contains', 'mixed')
    alarm_sets = schema.Object(
        title="Alarm Sets",
        schema=IAlarmSets,
        required=False
    )

class IEnvironmentDefault(IRegionContainer):
    """
Default values for an Environment's configuration
    """
    # EnvironmentDefault inherits from RegionContainer so
    # technically it can contain non-environment objects directly,
    # but it should never do so.
    taggedValue('contains', 'mixed')
    applications = schema.Object(
        title="Application container",
        required=True,
        schema = IApplicationEngines,
    )
    network = schema.Object(
        title="Network",
        required=False,
        schema = INetwork,
    )
    secrets_manager = schema.Object(
        title="Secrets Manager",
        required=False,
        schema = ISecretsManager
    )

class IEnvironmentRegion(IEnvironmentDefault, IDeployable):
    """
An actual provisioned Environment in a specific region.
May contains overrides of the IEnvironmentDefault where needed.
    """
    taggedValue('contains', 'mixed')

class IEnvironment(INamed, IMapping):
    """
Environment
    """
    # contains 'default' EnvironmentDefault and 'us-west-2' EnvironmentRegion objects
    taggedValue('contains', 'mixed')

# Networking

class IAWSCertificateManager(IResource):
    domain_name = schema.TextLine(
        title="Domain Name",
        description="",
        default="",
        required=False,
    )
    subject_alternative_names = schema.List(
        title="Subject alternative names",
        description="",
        value_type=schema.TextLine(
            title="alternative name"
        ),
        required=False,
    )
    external_resource = schema.Bool(
        title="Marks this resource as external to avoid creating and validating it.",
        default=False,
        required=False,
    )

class IPortProtocol(Interface):
    """Port and Protocol"""
    port = schema.Int(
        title="Port",
        required=False,
    )
    protocol = schema.Choice(
        title="Protocol",
        vocabulary=vocabulary.target_group_protocol,
        required=False,
    )

class ITargetGroups(INamed, IMapping):
    """
Container for `TargetGroup`_ objects.
    """
    taggedValue('contains', 'ITargetGroup')

class ITargetGroup(IPortProtocol, IResource):
    """Target Group"""
    health_check_interval = schema.Int(
        title="Health check interval",
        required=False,
    )
    health_check_timeout = schema.Int(
        title="Health check timeout",
        required=False,
    )
    healthy_threshold = schema.Int(
        title="Healthy threshold",
        required=False,
    )
    unhealthy_threshold = schema.Int(
        title="Unhealthy threshold",
        required=False,
    )
    health_check_http_code = schema.TextLine(
        title="Health check HTTP codes",
        required=False,
    )
    health_check_path = schema.TextLine(
        title="Health check path",
        default="/",
        required=False,
    )
    connection_drain_timeout = schema.Int(
        title="Connection drain timeout",
        required=False,
    )

class IListenerRule(IDeployable):
    rule_type = schema.TextLine(
        title="Type of Rule",
        required=False,
    )
    priority = schema.Int(
        title="Forward condition priority",
        required=False,
        default=1
    )
    host = schema.TextLine(
        title="Host header value",
        required=False,
    )
    # Redirect Rule Variables
    redirect_host = schema.TextLine(
        title="The host to redirect to",
        required=False,
    )
    # Forward Rule Variables
    target_group = schema.TextLine(
        title="Target group name",
        required=False,
    )

class IListeners(INamed, IMapping):
    """
Container for `Listener`_ objects.
    """
    taggedValue('contains', 'IListener')

class IListener(IParent, IPortProtocol):
    redirect = schema.Object(
        title="Redirect",
        schema=IPortProtocol,
        required=False,
    )
    ssl_certificates = schema.List(
        title="List of SSL certificate References",
        value_type = PacoReference(
            title="SSL Certificate Reference",
            schema_constraint='IAWSCertificateManager'
        ),
        required=False,
    )
    target_group = schema.TextLine(
        title="Target group",
        default="",
        required=False
    )
    rules = schema.Dict(
        title="Container of listener rules",
        value_type = schema.Object(IListenerRule),
        required=False,
        default=None
    )

class IDNS(IParent):
    hosted_zone = PacoReference(
        title="Hosted Zone Id",
        required=False,
        str_ok=True,
        schema_constraint='IRoute53HostedZone'
    )
    domain_name = PacoReference(
        title="Domain name",
        required=False,
        str_ok=True,
        schema_constraint='IRoute53HostedZone'
     )
    ssl_certificate = PacoReference(
        title="SSL certificate Reference",
        required=False,
        schema_constraint='IAWSCertificateManager'
    )
    ttl = schema.Int(
        title="TTL",
        default=300,
        required=False
    )

class ILBApplication(IResource, IMonitorable):
    """
The ``LBApplication`` resource type creates an Application Load Balancer. Use load balancers to route traffic from
the internet to your web servers.

Load balancers have ``listeners`` which will accept requrests on specified ports and protocols. If a listener
uses the HTTPS protocol, it can have a Paco reference to an SSL Certificate. A listener can then either
redirect the traffic to another port/protcol or send it one of it's named ``target_groups``.

Each target group will specify it's health check configuration. To specify which resources will belong
to a target group, use the ``target_groups`` field on an ASG resource.

.. sidebar:: Prescribed Automation

    ``dns``: Creates Route 53 Record Sets that will resolve DNS records to the domain name of the load balancer.

    ``enable_access_logs``: Set to True to turn on access logs for the load balancer, and will automatically create
    an S3 Bucket with permissions for AWS to write to that bucket.

    ``access_logs_bucket``: Name an existing S3 Bucket (in the same region) instead of automatically creating a new one.
    Remember that if you supply your own S3 Bucket, you are responsible for ensuring that the bucket policy for
    it grants AWS the `s3:PutObject` permission.

.. code-block:: yaml
    :caption: Example LBApplication load balancer resource YAML

    type: LBApplication
    enabled: true
    enable_access_logs: true
    target_groups:
        api:
            health_check_interval: 30
            health_check_timeout: 10
            healthy_threshold: 2
            unhealthy_threshold: 2
            port: 3000
            protocol: HTTP
            health_check_http_code: 200
            health_check_path: /
            connection_drain_timeout: 30
    listeners:
        http:
            port: 80
            protocol: HTTP
            redirect:
                port: 443
                protocol: HTTPS
        https:
            port: 443
            protocol: HTTPS
            ssl_certificates:
                - paco.ref netenv.app.applications.app.groups.certs.resources.root
            target_group: api
    dns:
        - hosted_zone: paco.ref resource.route53.mynetenv
          domain_name: api.example.com
    scheme: internet-facing
    security_groups:
        - paco.ref netenv.app.network.vpc.security_groups.app.alb
    segment: public

"""
    target_groups = schema.Object(
        title="Target Groups",
        schema=ITargetGroups,
        required=False,
    )
    listeners = schema.Object(
        title="Listeners",
        schema=IListeners,
        required=False,
    )
    dns = schema.List(
        title="List of DNS for the ALB",
        value_type=schema.Object(IDNS),
        required=False,
    )
    scheme = schema.Choice(
        title="Scheme",
        vocabulary=vocabulary.lb_scheme,
        required=False,
    )
    security_groups = schema.List(
        title="Security Groups",
        value_type=PacoReference(
            title="Paco reference",
            schema_constraint='ISecurityGroup',
        ),
        required=False,
    )
    segment = schema.TextLine(
        title="Id of the segment stack",
        required=False,
    )
    idle_timeout_secs = schema.Int(
        title='Idle timeout in seconds',
        description='The idle timeout value, in seconds.',
        default=60,
        required=False,
    )
    enable_access_logs = schema.Bool(
        title="Write access logs to an S3 Bucket",
        required=False
    )
    access_logs_bucket=PacoReference(
        title="Bucket to store access logs in",
        required=False,
        schema_constraint='IS3Bucket'
    )
    access_logs_prefix = schema.TextLine(
        title="Access Logs S3 Bucket prefix",
        required=False
    )

class IStatement(INamed):
    effect = schema.TextLine(
        title="Effect",
        description="Must be one of: 'Allow', 'Deny'",
        required=False,
        # ToDo: check constraint
        # constraint = vocabulary.iam_policy_effect
    )
    action = schema.List(
        title="Action(s)",
        value_type=schema.TextLine(),
        required=False,
    )
    resource =schema.List(
        title="Resrource(s)",
        value_type=schema.TextLine(),
        required=False,
    )

class IPolicy(IParent):
    name = schema.TextLine(
        title="Policy name",
        default="",
        required=False,
    )
    statement = schema.List(
        title="Statements",
        value_type=schema.Object(
            title="Statement",
            schema=IStatement
        ),
        required=False,
    )

class IAssumeRolePolicy(IParent):
    effect = schema.TextLine(
        title="Effect",
        required=False,
        # ToDo: check constraint
        # constraint = vocabulary.iam_policy_effect
    )
    aws = schema.List(
        title="List of AWS Principles",
        value_type=schema.TextLine(
            title="AWS Principle",
            default="",
            required=False
        ),
        required=False
    )
    service = schema.List(
        title="Service",
        value_type=schema.TextLine(
            title="Service",
            default="",
            required=False
        ),
        required=False
    )
    # ToDo: what are 'aws' keys for? implement ...

class IRole(INamed, IDeployable):
    assume_role_policy = schema.Object(
        title="Assume role policy",
        schema=IAssumeRolePolicy,
        required=False
    )
    instance_profile = schema.Bool(
        title="Instance profile",
        default=False,
        required=False
    )
    path = schema.TextLine(
        title="Path",
        default="/",
        required=False
    )
    role_name = schema.TextLine(
        title="Role name",
        default="",
        required=False
    )
    global_role_name = schema.Bool(
        title="Role name is globally unique and will not be hashed",
        required=False,
        default=False,
    )
    policies = schema.List(
        title="Policies",
        value_type=schema.Object(
            schema=IPolicy
        ),
        required=False
    )
    managed_policy_arns = schema.List(
        title="Managed policy ARNs",
        value_type=schema.TextLine(
            title="Managed policy ARN"
        ),
        required=False
    )
    max_session_duration = schema.Int(
        title="Maximum session duration",
        description="The maximum session duration (in seconds)",
        min=3600,
        max=43200,
        default=3600,
        required=False
    )
    permissions_boundary = schema.TextLine(
        title="Permissions boundary ARN",
        description="Must be valid ARN",
        default="",
        required=False
    )

#class IManagedPolicies(IMapping):
#    """
#    Container of IAM Managed Policices
#    """

class IManagedPolicy(INamed, IDeployable):
    """
IAM Managed Policy
    """
    roles = schema.List(
        title="List of Role Names",
        value_type=schema.TextLine(
            title="Role Name"
        ),
        required=False,
    )
    users = schema.List(
        title="List of IAM Users",
        value_type=schema.TextLine(
            title="IAM User name"
        ),
        required=False,
    )
    statement = schema.List(
        title="Statements",
        value_type=schema.Object(
            title="Statement",
            schema=IStatement
        ),
        required=False,
    )
    path = schema.TextLine(
        title="Path",
        default="/",
        required=False,
    )


class IIAM(INamed):
    roles = schema.Dict(
        title="Roles",
        value_type=schema.Object(
            title="Role",
            schema=IRole
        ),
        required=False,
    )
    policies = schema.Dict(
        title="Policies",
        value_type=schema.Object(
            title="ManagedPolicy",
            schema=IManagedPolicy
        ),
        required=False,
    )

class IEFSMount(IDeployable):
    """
EFS Mount Folder and Target Configuration
    """
    folder = schema.TextLine(
        title='Folder to mount the EFS target',
        required=True
    )
    target = PacoReference(
        title='EFS Target Resource Reference',
        required=True,
        str_ok=True,
        schema_constraint='IEFS'
    )

class ISimpleCloudWatchAlarm(IParent):
    """
A Simple CloudWatch Alarm
    """
    alarm_description=schema.Text(
        title="Alarm Description",
        description="Valid JSON document with Paco fields.",
        required=False,
    )
    actions_enabled = schema.Bool(
        title="Actions Enabled",
        required=False,
    )
    comparison_operator = schema.TextLine(
        title="Comparison operator",
        constraint = isComparisonOperator,
        description="Must be one of: 'GreaterThanThreshold','GreaterThanOrEqualToThreshold', 'LessThanThreshold', 'LessThanOrEqualToThreshold'",
        required=False,
    )
    evaluation_periods = schema.Int(
        title="Evaluation periods",
        required=False,
    )
    metric_name = schema.TextLine(
        title="Metric name",
        required=True,
    )
    namespace = schema.TextLine(
        title="Namespace",
        required=False,
    )
    period = schema.Int(
        title="Period in seconds",
        required=False,
    )
    statistic = schema.TextLine(
        title="Statistic",
        required=False,
    )
    threshold = schema.Float(
        title="Threshold",
        required=False,
    )
    dimensions = schema.List(
        title='Dimensions',
        value_type=schema.Object(IDimension),
        required=False,
    )

# CloudFormation Init schemas

class ICloudFormationConfigSets(INamed, IMapping):
    taggedValue('contains', 'mixed')
    @invariant
    def configurations_lists(obj):
        """
        ConfigSets:

        ascending:
            - "config1"
            - "config2"
        descending:
            - "config2"
            - "config1"
        """
        for key, value in obj.items():
            if type(key) != type(str()):
                raise Invalid('ConfigSet name must be a string')
            if len(key) < 1:
                raise Invalid('ConfigSet name must be at least 1 char')
            configurations = obj.__parent__.configurations
            if configurations == None:
                # if configurations haven't loaded yet, they can't be validated
                return
            for item in value:
                if item not in configurations:
                    raise Invalid('ConfigSet name does not match any configurations')

class ICloudFormationConfigurations(INamed, IMapping):
    taggedValue('contains', 'ICloudFormationConfiguration')

class ICloudFormationInitVersionedPackageSet(IMapping):
    taggedValue('contains', 'mixed')
    @invariant
    def packages_with_optional_versions(obj):
        """
        Packages lists should look like this:

        yum:
            httpd: ["0.10.2"]
            php: ["5.1", "5.2"]
            wordpress: []
        """
        for key, value in obj.items():
            if type(key) != type(str()):
                raise Invalid('Package name must be a string')
            if len(key) < 1:
                raise Invalid('Package name must be at least 1 char')
            if type(value) != type(list()):
                raise Invalid('Package version must be a list')
            for item in value:
                if type(item) != type(str()):
                    raise Invalid('Package version must be a string')
                if len(item) < 1:
                    raise Invalid('Package version must be at least 1 char')

class ICloudFormationInitPathOrUrlPackageSet(IMapping):
    taggedValue('contains', 'mixed')
    @invariant
    def packages_with_path_or_url(obj):
        """
        Packages should look like this:

        rpm:
            epel: "http://download.fedoraproject.org/pub/epel/5/i386/epel-release-5-4.noarch.rpm"

        """
        for key, value in obj.items():
            if type(key) != type(str()):
                raise Invalid('Package name must be a string')
            if len(key) < 1:
                raise Invalid('Package name must be at least 1 char')
            if type(value) != type(str()):
                raise Invalid('Package path/URL must be a string')
            if len(value) < 1:
                raise Invalid('Package path/URL must be at least 1 char')

class ICloudFormationInitPackages(INamed):
    apt = schema.Object(
        title="Apt packages",
        schema=ICloudFormationInitVersionedPackageSet,
        required=False
    )
    msi = schema.Object(
        title="MSI packages",
        schema=ICloudFormationInitPathOrUrlPackageSet,
        required=False
    )
    python = schema.Object(
        title="Apt packages",
        schema=ICloudFormationInitVersionedPackageSet,
        required=False
    )
    rpm = schema.Object(
        title="RPM packages",
        schema=ICloudFormationInitPathOrUrlPackageSet,
        required=False
    )
    rubygems = schema.Object(
        title="Rubygems packages",
        schema=ICloudFormationInitVersionedPackageSet,
        required=False
    )
    yum = schema.Object(
        title="Yum packages",
        schema=ICloudFormationInitVersionedPackageSet,
        required=False
    )

class ICloudFormationInitGroup(Interface):
    gid = schema.TextLine(
        title="Gid",
        required=False,
    )

class ICloudFormationInitGroups(Interface):
    """
Container for CloudFormationInit Groups
    """

class ICloudFormationInitUser(Interface):
    groups = schema.List(
        title="Groups",
        required=False,
        value_type=schema.TextLine(
            title="Group"
        ),
        default=[]
    )
    uid = schema.Int(
        title="Uid",
        required=False,
        min=100,
        max=65535
    )
    home_dir = schema.TextLine(
        title="Home dir",
        required=True
    )

class ICloudFormationInitUsers(Interface):
    """
Container for CloudFormationInit Users
    """

class ICloudFormationInitSources(INamed, IMapping):
    taggedValue('contains', 'mixed')

class InvalidCfnInitEncoding(schema.ValidationError):
    __doc__ = 'File encoding must be one of plain or base64.'

def isValidCfnInitEncoding(value):
    if value not in ('plain', 'base64'):
        raise InvalidCfnInitEncoding

def isValidS3KeyPrefix(value):
    if value.startswith('/') or value.endswith('/'):
        raise InvalidS3KeyPrefix
    return True

class ICloudFormationInitFiles(INamed, IMapping):
    taggedValue('contains', 'mixed')

class ICloudFormationInitFile(INamed):
    @invariant
    def content_or_source(obj):
        if obj.content != None and obj.content_file != None and obj.content_cfn_file != None:
            raise Invalid("Can not specify more than one of content, content_cfn_file and content_file for cfn-init file configuration.")
        elif obj.content != None and obj.source != None:
            raise Invalid("Can not specify both content and source for cfn-init file configuration.")
        elif obj.content_file != None and obj.source != None:
            raise Invalid("Can not specify both content_file and source for cfn-init file configuration.")

    @invariant
    def encoding_for_source(obj):
        if obj.encoding != None and obj.content == None:
            raise Invalid("For cfn-init file configuration, encoding requires the content to be set.")

    content = schema.Object(
        title="""Either a string or a properly formatted YAML object.""",
        required=False,
        schema=Interface
    )
    content_file = StringFileReference(
        title="""File path to a string.""",
        required=False
    )
    content_cfn_file = YAMLFileReference(
        title="File path to a properly formatted CloudFormation Functions YAML object.",
        required=False
    )
    source = schema.TextLine(
        title="A URL to load the file from.",
        required=False
    )
    encoding = schema.TextLine(
        title="The encoding format.",
        required=False,
        constraint=isValidCfnInitEncoding
    )
    group = schema.TextLine(
        title="The name of the owning group for this file. Not supported for Windows systems.",
        required=False
    )
    owner = schema.TextLine(
        title="The name of the owning user for this file. Not supported for Windows systems.",
        required=False
    )
    mode = schema.TextLine(
        title="""A six-digit octal value representing the mode for this file.""",
        min_length=6,
        max_length=6,
        required=False
    )
    authentication = schema.TextLine(
        title="""The name of an authentication method to use.""",
        required=False
    )
    context = schema.TextLine(
        title="""Specifies a context for files that are to be processed as Mustache templates.""",
        required=False
    )

class ICloudFormationInitCommands(INamed, IMapping):
    taggedValue('contains', 'mixed')

class ICloudFormationInitCommand(Interface):
    command = schema.Text(
        title="Command",
        required=True,
        min_length=1
    )
    env = schema.Dict(
        title="Environment Variables. This property overwrites, rather than appends, the existing environment.",
        required=False,
        default={}
    )
    cwd = schema.TextLine(
        title="Cwd. The working directory",
        required=False,
        min_length=1
    )
    test = schema.TextLine(
        title="A test command that determines whether cfn-init runs commands that are specified in the command key. If the test passes, cfn-init runs the commands.",
        required=False,
        min_length=1
    )
    ignore_errors = schema.Bool(
        title="Ingore errors - determines whether cfn-init continues to run if the command in contained in the command key fails (returns a non-zero value). Set to true if you want cfn-init to continue running even if the command fails.",
        required=False,
        default=False
    )

class ICloudFormationInitService(Interface):
    # ToDo: Invariant to check commands list
    ensure_running = schema.Bool(
        title="Ensure that the service is running or stopped after cfn-init finishes.",
        required=False
    )
    enabled = schema.Bool(
        title="Ensure that the service will be started or not started upon boot.",
        required=False
    )
    files = schema.List(
        title="A list of files. If cfn-init changes one directly via the files block, this service will be restarted",
        required=False,
        value_type=schema.TextLine(
            title="File"
        ),
    )
    sources = schema.List(
        title="A list of directories. If cfn-init expands an archive into one of these directories, this service will be restarted.",
        required=False,
        value_type=schema.TextLine(
            title="Sources"
        ),
    )
    packages = schema.Dict(
        title="A map of package manager to list of package names. If cfn-init installs or updates one of these packages, this service will be restarted.",
        required=False,
        default={}
    )
    commands = schema.List(
        title="A list of command names. If cfn-init runs the specified command, this service will be restarted.",
        required=False,
        value_type=schema.TextLine(
            title="Commands"
        ),
    )

class ICloudFormationInitServiceCollection(INamed, IMapping):
    taggedValue('contains', 'mixed')

class ICloudFormationInitServices(INamed):
    sysvinit = schema.Object(
        title="SysVInit Services for Linux OS",
        schema=ICloudFormationInitServiceCollection,
        required=False
    )
    windows = schema.Object(
        title="Windows Services for Windows OS",
        schema=ICloudFormationInitServiceCollection,
        required=False
    )

class ICloudFormationConfiguration(INamed):
    @invariant
    def check_user_group_duplicates(obj):
        for username in obj.users.keys():
            if username in obj.groups:
                raise Invalid("Both user and group with the name {} can not be set. When a user is created it automatically creates a group with the same name. Explicitly creating the group will cause the user add operation to fail.".format(username))

    packages = schema.Object(
        title="Packages",
        schema=ICloudFormationInitPackages,
        required=False
    )
    groups = schema.Object(
        title="Groups",
        schema=ICloudFormationInitGroups,
        required=False
    )
    users = schema.Object(
        title="Users",
        schema=ICloudFormationInitUsers,
        required=False
    )
    sources = schema.Object(
        title="Sources",
        schema=ICloudFormationInitSources,
        required=False
    )
    files = schema.Object(
        title="Files",
        schema=ICloudFormationInitFiles,
        required=False
    )
    commands = schema.Object(
        title="Commands",
        schema=ICloudFormationInitCommands,
        required=False
    )
    services = schema.Object(
        title="Services",
        schema=ICloudFormationInitServices,
        required=False
    )

class ICloudFormationParameters(INamed, IMapping):
    taggedValue('contains', 'mixed')

class ICloudFormationInit(INamed):
    """
`CloudFormation Init`_ is a method to configure an EC2 instance after it is launched.
CloudFormation Init is a much more complete and robust method to install configuration files and
pakcages than using a UserData script.

It stores information about packages, files, commands and more in CloudFormation metadata. It is accompanied
by a ``cfn-init`` script which will run on the instance to fetch this configuration metadata and apply
it. The whole system is often referred to simply as cfn-init after this script.

The ``cfn_init`` field of for an ASG contains all of the cfn-init configuration. After an instance
is launched, it needs to run a local cfn-init script to pull the configuration from the CloudFromation
stack and apply it. After cfn-init has applied configuration, you will run cfn-signal to tell CloudFormation
the configuration was successfully applied. Use the ``launch_options`` field for an ASG to let Paco take care of all this
for you.

.. sidebar:: Prescribed Automation

    ``launch_options``: The ``cfn_init_config_sets:`` field is a list of cfn-init configurations to
    apply at launch. This list will be applied in order. On Amazon Linux the cfn-init script is pre-installed
    in /opt/aws/bin. If you enable a cfn-init launch option, Paco will install cfn-init in /opt/paco/bin for you.

Refer to the `CloudFormation Init`_ docs for a complete description of all the configuration options
available.

.. code-block:: yaml
    :caption: cfn_init with launch_options

    launch_options:
        cfn_init_config_sets:
        - "Install"
    cfn_init:
      parameters:
        BasicKey: static-string
        DatabasePasswordarn: paco.ref netenv.mynet.secrets_manager.app.site.database.arn
      config_sets:
        Install:
          - "Install"
      configurations:
        Install:
          packages:
            rpm:
              epel: "http://download.fedoraproject.org/pub/epel/5/i386/epel-release-5-4.noarch.rpm"
            yum:
              jq: []
              python3: []
          files:
            "/tmp/get_rds_dsn.sh":
              content_cfn_file: ./webapp/get_rds_dsn.sh
              mode: '000700'
              owner: root
              group: root
            "/etc/httpd/conf.d/saas_wsgi.conf":
              content_file: ./webapp/saas_wsgi.conf
              mode: '000600'
              owner: root
              group: root
            "/etc/httpd/conf.d/wsgi.conf":
              content: "LoadModule wsgi_module modules/mod_wsgi.so"
              mode: '000600'
              owner: root
              group: root
            "/tmp/install_codedeploy.sh":
              source: https://aws-codedeploy-us-west-2.s3.us-west-2.amazonaws.com/latest/install
              mode: '000700'
              owner: root
              group: root
          commands:
            10_install_codedeploy:
              command: "/tmp/install_codedeploy.sh auto > /var/log/cfn-init-codedeploy.log 2>&1"
          services:
            sysvinit:
              codedeploy-agent:
                enabled: true
                ensure_running: true

The ``parameters`` field is a set of Parameters that will be passed to the CloudFormation stack. This
can be static strings or ``paco.ref`` that are looked up from already provisioned cloud resources.

CloudFormation Init can be organized into Configsets. With raw cfn-init using Configsets is optional,
but is required with Paco.

In a Configset, the ``files`` field has four fields for specifying the file contents.

 * ``content_file:`` A path to a file on the local filesystem. A convenient practice is to make a
   sub-directory in the ``netenv`` directory for keeping cfn-init files.

 * ``content_cfn_file:`` A path to a file on the local filesystem. This file will have FnSub and FnJoin
   CloudFormation applied to it.

 * ``content:`` For small files, the content can be in-lined directly in this field.

 * ``source:`` Fetches the file from a URL.

If you are using ``content_cfn_file`` to interpolate Parameters, the file might look like:

.. code-block:: bash

    !Sub |
        #!/bin/bash

        echo "Database ARN is " ${DatabasePasswordarn}
        echo "AWS Region is " ${AWS::Region}

If you want to include a raw ``${SomeValue}`` string in your file, use the ! character to escape it like this:
``${!SomeValue}``. cfn-init also supports interpolation with Mustache templates, but Paco support for this is
not yet implemented.

.. _CloudFormation Init: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-init.html

    """
    config_sets = schema.Object(
        title="CloudFormation Init configSets",
        schema=ICloudFormationConfigSets,
        required=True
    )
    configurations = schema.Object(
        title="CloudFormation Init configurations",
        schema=ICloudFormationConfigurations,
        required=True
    )
    parameters = schema.Dict(
        title="Parameters",
        default={},
        required=False
    )

# AutoScalingGroup schemas

class IASGLifecycleHooks(INamed, IMapping):
    """
Container for `ASGLifecycleHook` objects.
    """
    taggedValue('contains', 'IASGLifecycleHook')

class IASGLifecycleHook(INamed, IDeployable):
    """
ASG Lifecycle Hook
    """
    lifecycle_transition = schema.TextLine(
        title='ASG Lifecycle Transition',
        constraint = IsValidASGLifecycleTransition,
        required=True
    )
    notification_target_arn = schema.TextLine(
        title='Lifecycle Notification Target Arn',
        required=True
    )
    role_arn = schema.TextLine(
        title='Licecycel Publish Role ARN',
        required=True
    )
    default_result = schema.TextLine(
        title='Default Result',
        required=False,
        constraint = IsValidASGLifecycleDefaultResult
    )

class IASGScalingPolicies(INamed, IMapping):
    """
Container for `ASGScalingPolicy`_ objects.
    """
    taggedValue('contains', 'IASGScalingPolicy')

class IASGScalingPolicy(INamed, IDeployable):
    """
Auto Scaling Group Scaling Policy
    """
    policy_type = schema.TextLine(
        title='Policy Type',
        default='SimpleScaling',
        # SimpleScaling, StepScaling, and TargetTrackingScaling
        constraint=IsValidASGScalignPolicyType,
    )
    adjustment_type = schema.TextLine(
        title='Adjustment Type',
        default='ChangeInCapacity',
        # ChangeInCapacity, ExactCapacity, and PercentChangeInCapacity
        constraint=IsValidASGScalingPolicyAdjustmentType,
    )
    scaling_adjustment = schema.Int(
        title='Scaling Adjustment'
    )
    cooldown = schema.Int(
        title='Scaling Cooldown in Seconds',
        default=300,
        min=0,
        required=False
    )
    alarms = schema.List(
        title='Alarms',
        value_type=schema.Object(ISimpleCloudWatchAlarm),
    )

    @invariant
    def required_simple_scaling_properties(obj):
        if obj.policy_type == 'SimpleScaling':
            if obj.scaling_adjustment == None:
                raise Invalid("'scaling_adjustment' must be specified when policy_type is 'SimpleScaling'")
        if obj.policy_type != 'SimpleScaling':
            if obj.scaling_adjustment != None:
                raise Invalid("'policy_type' must be 'SimpleScaling' when 'scaling_adjustment' is used.")
            if obj.cooldown != None:
                raise Invalid("'cooldown' may only be used when policy_type is 'SimpleScaling'")

class IEIP(IResource):
    """
Elastic IP (EIP) resource.

.. sidebar:: Prescribed Automation

    ``dns``: Adds a DNS CNAME to resolve to this EIP's IP address to the Route 53 HostedZone.

.. code-block:: yaml
    :caption: Example EIP resource YAML

    eip:
      type: EIP
      order: 5
      enabled: true
      dns:
        - domain_name: example.com
          hosted_zone: paco.ref resource.route53.examplecom
          ttl: 60

    """
    dns = schema.List(
        title="List of DNS for the EIP",
        value_type = schema.Object(IDNS),
        required=False
    )

class IEBSVolumeMount(IParent, IDeployable):
    """
EBS Volume Mount Configuration
    """
    folder = schema.TextLine(
        title='Folder to mount the EBS Volume',
        required=True
    )
    volume = PacoReference(
        title='EBS Volume Resource Reference',
        required=True,
        str_ok=True,
        schema_constraint='IEBS'
    )
    device = schema.TextLine(
        title='Device to mount the EBS Volume with.',
        required=True
    )
    filesystem = schema.TextLine(
        title='Filesystem to mount the EBS Volume with.',
        required=True
    )

class IEBS(IResource):
    """
Elastic Block Store (EBS) Volume.

It is required to specify the ``availability_zone`` the EBS Volume will be created in.
If the volume is going to be used by an ASG, it should launch an instance in the same
``availability_zone`` (and region).

.. code-block:: yaml
    :caption: Example EBS resource YAML

    my_volume:
      type: EBS
      order: 5
      enabled: true
      size_gib: 4
      volume_type: gp2
      availability_zone: 1

    """

    size_gib = schema.Int(
        title="Volume Size in GiB",
        description="",
        default=10,
        required=True
    )
    availability_zone = schema.Int(
        # Can be: 1 | 2 | 3 | 4 | ...
        title='Availability Zone to create Volume in.',
        required=True
    )
    volume_type = schema.TextLine(
        title="Volume Type",
        description="Must be one of: gp2 | io1 | sc1 | st1 | standard",
        default='gp2',
        constraint = isValidEBSVolumeType,
        required=False
    )

class IEC2LaunchOptions(INamed):
    """
EC2 Launch Options
    """
    update_packages = schema.Bool(
        title='Update Distribution Packages',
        required=False,
        default=False
    )
    cfn_init_config_sets = schema.List(
        title="List of cfn-init config sets",
        value_type = schema.TextLine(
            title="",
            required=False
        ),
        required=False,
        default=[]
    )

class IBlockDevice(IParent):
    delete_on_termination = schema.Bool(
        title="Indicates whether to delete the volume when the instance is terminated.",
        default=True,
        required=False
    )
    encrypted = schema.Bool(
        title="Specifies whether the EBS volume is encrypted.",
        required=False
    )
    iops = schema.Int(
        title="The number of I/O operations per second (IOPS) to provision for the volume.",
        description="The maximum ratio of IOPS to volume size (in GiB) is 50:1, so for 5,000 provisioned IOPS, you need at least 100 GiB storage on the volume.",
        min=100,
        max=20000,
        required=False
    )
    snapshot_id = schema.TextLine(
        title="The snapshot ID of the volume to use.",
        min_length=1,
        max_length=255,
        required=False
    )
    size_gib = schema.Int(
        title="The volume size, in Gibibytes (GiB).",
        description="This can be a number from 1-1,024 for standard, 4-16,384 for io1, 1-16,384 for gp2, and 500-16,384 for st1 and sc1.",
        min=1,
        max=16384,
        required=False
    )
    volume_type = schema.TextLine(
        title="The volume type, which can be standard for Magnetic, io1 for Provisioned IOPS SSD, gp2 for General Purpose SSD, st1 for Throughput Optimized HDD, or sc1 for Cold HDD.",
        description="Must be one of standard, io1, gp2, st1 or sc1.",
        constraint=isValidEBSVolumeType
    )

class IBlockDeviceMapping(IParent):
    @invariant
    def ebs_or_virtual_name(obj):
        if obj.ebs == None and obj.virtual_name == None:
            raise Invalid("Must set one of either ebs or virtual_name for block_device_mappings.")
        if obj.ebs != None and obj.virtual_name != None:
            raise Invalid("Can not set both ebs and virtual_name for block_device_mappings.")
        return True

    device_name = schema.TextLine(
        title="The device name exposed to the EC2 instance",
        required=True,
        min_length=1,
        max_length=255
    )
    ebs = schema.Object(
        title="Amazon Ebs volume",
        schema=IBlockDevice,
        required=False
    )
    virtual_name = schema.TextLine(
        title="The name of the virtual device.",
        description="The name must be in the form ephemeralX where X is a number starting from zero (0), for example, ephemeral0.",
        min_length=1,
        max_length=255,
        required=False
    )

class IASGRollingUpdatePolicy(INamed, IDeployable):
    """
Auto Scaling Group Roling Update Policy
    """
    max_batch_size = schema.Int(
        title="Maximum batch size",
        description="",
        default=1,
        required=False,
    )
    min_instances_in_service = schema.Int(
        title="Minimum instances in service",
        description="",
        default=1,
        required=False,
    )
    pause_time = schema.TextLine(
        title="Minimum instances in service",
        description="Healthy success timeout",
        required=False,
        default='PT0S'
        #constraint=IsValidUpdatePolicyPauseTime
    )
    wait_on_resource_signals = schema.Bool(
        title="Wait for resource signals",
        description="",
        default=False
    )

class IASG(IResource, IMonitorable):
    """
An Auto Scaling Group (ASG) contains a collection of Amazon EC2 instances that are treated as a
logical grouping for the purposes of automatic scaling and management.

The Paco ASG resource provisions an AutoScalingGroup as well as LaunchConfiguration and TargetGroups
for that ASG.


.. sidebar:: Prescribed Automation

    ASGs use Paco's **LaunchBundles**. A LaunchBundle is a zip file of code and configuration files that is
    automatically created and stored in an S3 Bucket that the ASG has read permissions to. Paco adds BASH code
    to the UserData script for the ASG's LaunchConfiguration that will iterate through all of the LaunchBundles
    and download and run them. For example, if you specify in-host metrics for an ASG, it will have a LaunchBundle
    created with the necessary CloudWatch agent configuration and a BASH script to install and configure the agent.

    ``cfn_init``: Contains CloudFormationInit (cfn-init) configuration. Paco allows reading cfn-init
    files from the filesystem, and also does additional validation checks on the configuration to ensure
    it is correct. The ``launch_options`` has a ``cfn_init_config_sets`` field to specify which
    CfnInitConfigurationSets you want to automatically call during instance launch with a LaunchBundle.

    ``ebs_volume_mounts``: Adds an EBS LaunchBundle that mounts all EBS Volumes
    to the EC2 instance launched by the ASG. If the EBS Volume is unformatted, it will be formatted to the
    specified filesystem. **This feature only works with "self-healing" ASGs**. A "self-healing" ASG is an ASG
    with ``max_instances`` set to 1. Trying to launch a second instance in the ASG will fail to mount the EBS Volume
    as it can only be mounted to one instance at a time.

    ``eip``: Adds an EIP LaunchBundle which will attach an Elastic IP to a launched instance.
    **This feature only works with "self-healing" ASGs**. A "self-healing" ASG is an ASG
    with ``max_instances`` set to 1. Trying to launch a second instance in the ASG will fail to attach the EIP
    as it can only be mounted to one instance at a time.

    ``efs_mounts``: Adds an EFS LaunchBundle that mounts all EFS locations. A SecurityGroup
    must still be manually configured to allow the ASG instances to network access to the EFS filesystem.

    ``monitoring``: Any fields specified in the ``metrics`` or ``log_sets`` fields will add a CloudWatchAgent LaunchBundle
    that will install a CloudWatch Agent and configure it to collect all specified metrics and log sources.

    ``secrets``: Adds a policy to the Instance Role which allows instances to access the specified secrets.


.. code-block:: yaml
    :caption: example ASG configuration

    type: ASG
    order: 30
    enabled: true
    associate_public_ip_address: false
    cooldown_secs: 200
    ebs_optimized: false
    health_check_grace_period_secs: 240
    health_check_type: EC2
    availability_zone: 1
    ebs_volume_mounts:
      - volume: paco.ref netenv.mynet.applications.app.groups.storage.resources.my_volume
        enabled: true
        folder: /var/www/html
        device: /dev/xvdf
        filesystem: ext4
    efs_mounts:
      - enabled: true
        folder: /mnt/wp_efs
        target: paco.ref netenv.mynet.applications.app.groups.storage.resources.my_efs
    instance_iam_role:
      enabled: true
      policies:
        - name: DNSRecordSet
          statement:
            - effect: Allow
              action:
                - route53:ChangeResourceRecordSets
              resource:
                - 'arn:aws:route53:::hostedzone/HHIHkjhdhu744'
    instance_ami: paco.ref function.aws.ec2.ami.latest.amazon-linux-2
    instance_ami_type: amazon
    instance_key_pair: paco.ref resource.ec2.keypairs.my_keypair
    instance_monitoring: true
    instance_type: t2.medium
    desired_capacity: 1
    max_instances: 1
    min_instances: 1
    target_groups:
      - paco.ref netenv.mynet.applications.app.groups.web.resources.alb.target_groups.cloud
    security_groups:
      - paco.ref netenv.mynet.network.vpc.security_groups.web.asg
    segment: private
    termination_policies:
      - Default
    update_policy_max_batch_size: 1
    update_policy_min_instances_in_service: 0
    scaling_policy_cpu_average: 60
    launch_options:
        cfn_init_config_sets:
        - "InstallApp"
    cfn_init:
      config_sets:
        InstallApp:
          - "InstallApp"
      configurations:
        InstallApp:
          packages:
            yum:
              python3: []
          users:
            www-data:
              uid: 2000
              home_dir: /home/www-data
          files:
            "/etc/systemd/system/pypiserver.service":
              content_file: ./pypi-config/pypiserver.service
              mode: '000755'
              owner: root
              group: root
          commands:
            00_pypiserver:
              command: "/bin/pip3 install pypiserver"
            01_passlib_dependency:
              command: "/bin/pip3 install passlib"
            02_prep_mount:
               command: "chown www-data:www-data /var/pypi"
          services:
            sysvinit:
              pypiserver:
                enabled: true
                ensure_running: true
    monitoring:
      enabled: true
      collection_interval: 60
      metrics:
        - name: swap
          measurements:
            - used_percent
        - name: disk
          measurements:
            - free
          resources:
            - '/'
            - '/var/www/html'
          collection_interval: 300
    user_data_script: |
      echo "Hello World!"

    """
    @invariant
    def min_instances(obj):
        if obj.rolling_update_policy != None:
            if obj.rolling_update_policy != None and obj.rolling_update_policy.min_instances_in_service >= obj.max_instances:
                raise Invalid("ASG rolling_update_policy.min_instances_in_service must be less than max_instances.")
        elif obj.update_policy_min_instances_in_service >= obj.max_instances:
            raise Invalid("ASG update_policy_min_instances_in_service must be less than max_instances.")
        if obj.min_instances > obj.max_instances:
            raise Invalid("ASG min_instances must be less than or equal to max_instances.")
        if obj.desired_capacity > obj.max_instances:
            raise Invalid("ASG desired_capacity must be less than or equal to max_instances.")

    associate_public_ip_address = schema.Bool(
        title="Associate Public IP Address",
        description="",
        default=False,
        required=False,
    )
    availability_zone = schema.TextLine(
        # Can be: all | 1 | 2 | 3 | 4 | ...
        title='Availability Zones to launch instances in.',
        default='all',
        required=False,
        constraint=IsValidASGAvailabilityZone
    )
    block_device_mappings = schema.List(
        title="Block Device Mappings",
        value_type=schema.Object(
            title="Block Device Mapping",
            schema=IBlockDeviceMapping
        ),
        required=False
    )
    cfn_init = schema.Object(
        title="CloudFormation Init",
        schema=ICloudFormationInit,
        required=False
    )
    cooldown_secs = schema.Int(
        title="Cooldown seconds",
        description="",
        default=300,
        required=False,
    )
    desired_capacity = schema.Int(
        title="Desired capacity",
        description="",
        default=1,
        required=False,
    )
    ebs_optimized = schema.Bool(
        title="EBS Optimized",
        description="",
        default=False,
        required=False,
    )
    ebs_volume_mounts = schema.List(
        title='Elastic Block Store Volume Mounts',
        value_type= schema.Object(IEBSVolumeMount),
        required=False,
    )
    efs_mounts = schema.List(
        title='Elastic Filesystem Configuration',
        value_type=schema.Object(IEFSMount),
        required=False,
    )
    eip = PacoReference(
        title="Elastic IP or AllocationId to attach to instance at launch",
        required=False,
        str_ok=True,
        schema_constraint='IEIP'
    )
    health_check_grace_period_secs = schema.Int(
        title="Health check grace period in seconds",
        description="",
        default=300,
        required=False,
    )
    health_check_type = schema.TextLine(
        title="Health check type",
        description="Must be one of: 'EC2', 'ELB'",
        default='EC2',
        constraint = isValidHealthCheckType,
        required=False,
    )
    instance_iam_role = schema.Object(IRole)
    instance_ami = PacoReference(
        title="Instance AMI",
        description="",
        str_ok=True,
        required=False,
        schema_constraint='IFunction'
    )
    instance_ami_type = schema.TextLine(
        title="The AMI Operating System family",
        description="Must be one of amazon, centos, suse, debian, ubuntu, microsoft or redhat.",
        constraint = isValidInstanceAMIType,
        default="amazon",
        required=False,
    )
    instance_key_pair = PacoReference(
        title="Key pair to connect to launched instances",
        description="",
        required=False,
        schema_constraint='IEC2KeyPair'
    )
    instance_monitoring = schema.Bool(
        title="Instance monitoring",
        description="",
        default=False,
        required=False,
    )
    instance_type = schema.TextLine(
        title="Instance type",
        description="",
        constraint = isValidInstanceSize,
        required=False,
    )
    launch_options = schema.Object(
        title='EC2 Launch Options',
        schema=IEC2LaunchOptions,
        required=False
    )
    lifecycle_hooks = schema.Object(
        title='Lifecycle Hooks',
        schema=IASGLifecycleHooks,
        required=False
    )
    load_balancers = schema.List(
        title="Target groups",
        description="",
        value_type=PacoReference(
            title="Paco reference",
            schema_constraint='ITargetGroup'
        ),
        required=False,
    )
    max_instances = schema.Int(
        title="Maximum instances",
        description="",
        default=2,
        required=False,
    )
    min_instances = schema.Int(
        title="Minimum instances",
        description="",
        default=1,
        required=False,
    )
    update_policy_max_batch_size = schema.Int(
        title="Update policy maximum batch size",
        description="",
        default=1,
        required=False,
    )
    update_policy_min_instances_in_service = schema.Int(
        title="Update policy minimum instances in service",
        description="",
        default=1,
        required=False,
    )
    scaling_policies = schema.Object(
        title='Scaling Policies',
        schema=IASGScalingPolicies,
        required=False,
    )
    scaling_policy_cpu_average = schema.Int(
        title="Average CPU Scaling Polciy",
        # Default is 0 == disabled
        default=0,
        min=0,
        max=100,
        required=False,
    )
    secrets = schema.List(
        title='List of Secrets Manager References',
        value_type=PacoReference(
            title='Secrets Manager Reference',
            schema_constraint='ISecretsManagerSecret'
        ),
        required=False
    )
    security_groups = schema.List(
        title="Security groups",
        description="",
        value_type=PacoReference(
            title="Paco reference",
            schema_constraint='ISecurityGroup'
        ),
        required=False,
    )
    segment = schema.TextLine(
        title="Segment",
        description="",
        required=False,
    )
    target_groups = schema.List(
        title="Target groups",
        description="",
        value_type=PacoReference(
            title="Paco reference",
            schema_constraint='ITargetGroup'
        ),
        required=False,
    )
    termination_policies = schema.List(
        title="Terminiation policies",
        description="",
        value_type=schema.TextLine(
            title="Termination policy",
            description=""
        ),
        required=False,
    )
    user_data_pre_script = schema.Text(
        title="User data pre-script",
        description="",
        default="",
        required=False,
    )
    user_data_script = schema.Text(
        title="User data script",
        description="",
        default="",
        required=False,
    )
    rolling_update_policy = schema.Object(
        title="Rolling Update Policy",
        description="",
        schema=IASGRollingUpdatePolicy,
        default=None,
        required=False
    )


# Lambda

class ILambdaVariable(IParent):
    """
    Lambda Environment Variable
    """
    key = schema.TextLine(
        title='Variable Name',
        required=True,
    )
    value = PacoReference(
        title='String Value or a Paco Reference to a resource output',
        required=True,
        str_ok=True,
        schema_constraint='Interface'
    )

class ILambdaEnvironment(IParent):
    """
Lambda Environment
    """
    variables = schema.List(
        title="Lambda Function Variables",
        value_type = schema.Object(ILambdaVariable),
        required=False,
    )

class ILambdaFunctionCode(IParent):
    """The deployment package for a Lambda function."""

    @invariant
    def is_either_s3_or_zipfile(obj):
        "Validate that either zipfile or s3 bucket is set."
        if not obj.zipfile and not (obj.s3_bucket and obj.s3_key):
            raise Invalid("Either zipfile or s3_bucket and s3_key must be set. Or zipfile fle is an empty file.")
        if obj.zipfile and obj.s3_bucket:
            raise Invalid("Can not set both zipfile and s3_bucket")
        if obj.zipfile and len(obj.zipfile) > 4096:
            raise Invalid("Too bad, so sad. Limit of inline code of 4096 characters exceeded. File is {} chars long.".format(len(obj.zipfile)))

    zipfile = StringFileReference(
        title="The function as an external file.",
        description="Maximum of 4096 characters.",
        required=False,
    )
    s3_bucket = PacoReference(
        title="An Amazon S3 bucket in the same AWS Region as your function",
        required=False,
        str_ok=True,
        schema_constraint='IS3Bucket'
    )
    s3_key = schema.TextLine(
        title="The Amazon S3 key of the deployment package.",
        required=False,
    )


class ILambdaVpcConfig(INamed):
    """
Lambda Environment
    """
    segments = schema.List(
        title="VPC Segments to attach the function",
        description="",
        value_type = PacoReference(
            title="Segment",
            schema_constraint='ISegment',
        ),
        required=False
    )
    security_groups = schema.List(
        title="List of VPC Security Group Ids",
        value_type = PacoReference(
            schema_constraint='ISecurityGroup'
        ),
        required=False
    )

class ILambda(IResource, IMonitorable):
    """
Lambda Functions allow you to run code without provisioning servers and only
pay for the compute time when the code is running.

For the code that the Lambda function will run, use the ``code:`` block and specify
``s3_bucket`` and ``s3_key`` to deploy the code from an S3 Bucket or use ``zipfile`` to read a local file from disk.

.. sidebar:: Prescribed Automation

    ``sdb_cache``: Create a SimpleDB Domain and IAM Policy that grants full access to that domain. Will
    also make the domain available to the Lambda function as an environment variable named ``SDB_CACHE_DOMAIN``.

    ``sns_topics``: Subscribes the Lambda to SNS Topics. For each Paco reference to an SNS Topic,
    Paco will create an SNS Topic Subscription so that the Lambda function will recieve all messages sent to that SNS Topic.
    It will also create a Lambda Permission granting that SNS Topic the ability to publish to the Lambda.

    **S3 Bucket Notification permission** Paco will check all resources in the Application for any S3 Buckets configured
    to notify this Lambda. Lambda Permissions will be created to allow those S3 Buckets to invoke the Lambda.

    **Events Rule permission** Paco will check all resources in the Application for CloudWatch Events Rule that are configured
    to notify this Lambda and create a Lambda permission to allow that Event Rule to invoke the Lambda.

.. code-block:: yaml
    :caption: Lambda function resource YAML

    type: Lambda
    enabled: true
    order: 1
    title: 'My Lambda Application'
    description: 'Checks the Widgets Service and applies updates to a Route 53 Record Set.'
    code:
        s3_bucket: my-bucket-name
        s3_key: 'myapp-1.0.zip'
    environment:
        variables:
        - key: 'VAR_ONE'
          value: 'hey now!'
        - key: 'VAR_TWO'
          value: 'Hank Kingsley'
    iam_role:
        enabled: true
        policies:
          - name: DNSRecordSet
            statement:
              - effect: Allow
                action:
                  - route53:ChangeResourceRecordSets
                resource:
                  - 'arn:aws:route53:::hostedzone/AJKDU9834DUY934'
    handler: 'myapp.lambda_handler'
    memory_size: 128
    runtime: 'python3.7'
    timeout: 900
    sns_topics:
      - paco.ref netenv.app.applications.app.groups.web.resources.snstopic
    vpc_config:
        segments:
          - paco.ref netenv.app.network.vpc.segments.public
        security_groups:
          - paco.ref netenv.app.network.vpc.security_groups.app.function

"""
    code = schema.Object(
        title="The function deployment package.",
        schema = ILambdaFunctionCode,
        required=True,
    )
    description=schema.TextLine(
        title="A description of the function.",
        required=True,
    )
    environment = schema.Object(
        title="Lambda Function Environment",
        schema = ILambdaEnvironment,
        default=None,
        required=False,
    )
    iam_role = schema.Object(
        title="The IAM Role this Lambda will execute as.",
        required=True,
        schema = IRole,
    )
    layers = schema.List(
        title="Layers",
        value_type = schema.TextLine(),
        description="Up to 5 Layer ARNs",
        constraint = isListOfLayerARNs
    )
    handler = schema.TextLine(
        title="Function Handler",
        required=True,
    )
    memory_size = schema.Int(
        title="Function memory size (MB)",
        min=128,
        max=3008,
        default=128,
        required=False,
    )
    reserved_concurrent_executions = schema.Int(
        title="Reserved Concurrent Executions",
        default=0,
        required=False,
    )
    runtime = schema.TextLine(
        title="Runtime environment",
        required=True,
        # dotnetcore1.0 | dotnetcore2.1 | go1.x | java8 | nodejs10.x | nodejs8.10 | provided | python2.7 | python3.6 | python3.7 | ruby2.5
        default='python3.7',
    )
    # The amount of time that Lambda allows a function to run before stopping it. The default is 3 seconds. The maximum allowed value is 900 seconds.
    timeout = schema.Int(
        title="Max function execution time in seconds.",
        description="Must be between 0 and 900 seconds.",
        min=0,
        max=900,
        required=False,
    )
    sdb_cache = schema.Bool(
        title="SDB Cache Domain",
        required=False,
        default=False,
    )
    sns_topics = schema.List(
        title="List of SNS Topic Paco references or SNS Topic ARNs to subscribe the Lambda to.",
        value_type =  PacoReference(
            str_ok=True,
            schema_constraint='ISNSTopic'
        ),
        required=False,
    )
    vpc_config = schema.Object(
        title="Vpc Configuration",
        required=False,
        schema = ILambdaVpcConfig
    )

# API Gateway

class IApiGatewayMethodMethodResponseModel(Interface):
    content_type = schema.TextLine(
        title="Content Type",
        required=False,
    )
    model_name = schema.TextLine(
        title="Model name",
        default="",
        required=False,
    )

class IApiGatewayMethodMethodResponse(Interface):
    status_code = schema.TextLine(
        title="HTTP Status code",
        description="",
        required=True,
    )
    response_models = schema.List(
        title="The resources used for the response's content type.",
        description="""Specify response models as key-value pairs (string-to-string maps),
with a content type as the key and a Model Paco name as the value.""",
        value_type = schema.Object(title="Response Model", schema = IApiGatewayMethodMethodResponseModel),
        required=False,
    )

class IApiGatewayMethodIntegrationResponse(Interface):
    content_handling = schema.TextLine(
        title="Specifies how to handle request payload content type conversions.",
        description="""Valid values are:

CONVERT_TO_BINARY: Converts a request payload from a base64-encoded string to a binary blob.

CONVERT_TO_TEXT: Converts a request payload from a binary blob to a base64-encoded string.

If this property isn't defined, the request payload is passed through from the method request
to the integration request without modification.
""",
        required=False
    )
    response_parameters = schema.Dict(
        title="Response Parameters",
        default={},
        required=False,
    )
    response_templates = schema.Dict(
        title="Response Templates",
        default={},
        required=False,
    )
    selection_pattern = schema.TextLine(
        title="A regular expression that specifies which error strings or status codes from the backend map to the integration response.",
        required=False,
    )
    status_code = schema.TextLine(
        title="The status code that API Gateway uses to map the integration response to a MethodResponse status code.",
        description  = "Must match a status code in the method_respones for this API Gateway REST API.",
        required=True,
    )

class IApiGatewayMethodIntegration(IParent):
    integration_responses = schema.List(
        title="Integration Responses",
        value_type = schema.Object(IApiGatewayMethodIntegrationResponse),
        required=False,
    )
    request_parameters = schema.Dict(
        title="The request parameters that API Gateway sends with the backend request.",
        description="""Specify request parameters as key-value pairs (string-to-string mappings),
with a destination as the key and a source as the value. Specify the destination by using the
following pattern `integration.request.location.name`, where `location` is query string, path,
or header, and `name` is a valid, unique parameter name.

The source must be an existing method request parameter or a static value. You must
enclose static values in single quotation marks and pre-encode these values based on
their destination in the request.
        """,
        default={},
        required=False,
    )
    integration_http_method = schema.TextLine(
        title="Integration HTTP Method",
        description="Must be one of ANY, DELETE, GET, HEAD, OPTIONS, PATCH, POST or PUT.",
        default="POST",
        constraint = isValidHttpMethod,
        required=False,
    )
    integration_type = schema.TextLine(
        title="Integration Type",
        description="Must be one of AWS, AWS_PROXY, HTTP, HTTP_PROXY or MOCK.",
        constraint = isValidApiGatewayIntegrationType,
        default="AWS",
        required=True,
    )
    integration_lambda = PacoReference(
        title="Integration Lambda",
        required=False,
        schema_constraint='ILambda'
    )
    uri = schema.TextLine(
        title="Integration URI",
        required=False,
    )


class IApiGatewayMethod(IResource):
    "API Gateway Method"
    authorization_type = schema.TextLine(
        title="Authorization Type",
        description="Must be one of NONE, AWS_IAM, CUSTOM or COGNITO_USER_POOLS",
        constraint = isValidApiGatewayAuthorizationType,
        required=True,
    )
    http_method = schema.TextLine(
        title="HTTP Method",
        description="Must be one of ANY, DELETE, GET, HEAD, OPTIONS, PATCH, POST or PUT.",
        constraint = isValidHttpMethod,
        required=False,
    )
    resource_id = schema.TextLine(
        title="Resource Id",
        required=False,
    )
    integration = schema.Object(
        title="Integration",
        schema = IApiGatewayMethodIntegration,
        required=False,
    )
    method_responses = schema.List(
        title="Method Responses",
        description="List of ApiGatewayMethod MethodResponses",
        value_type = schema.Object(IApiGatewayMethodMethodResponse),
        required=False,
    )
    request_parameters = schema.Dict(
        title="Request Parameters",
        description="""Specify request parameters as key-value pairs (string-to-Boolean mapping),
        with a source as the key and a Boolean as the value. The Boolean specifies whether
        a parameter is required. A source must match the format method.request.location.name,
        where the location is query string, path, or header, and name is a valid, unique parameter name.""",
        default={},
        required=False,
    )

class IApiGatewayModel(IResource):
    content_type = schema.TextLine(
        title="Content Type",
        required=False,
    )
    description=schema.Text(
        title="Description",
        required=False,
    )
    schema = schema.Dict(
        title="Schema",
        description='JSON format. Will use null({}) if left empty.',
        default={},
        required=False,
    )

class IApiGatewayResource(IResource):
    parent_id = schema.TextLine(
        title="Id of the parent resource. Default is 'RootResourceId' for a resource without a parent.",
        default="RootResourceId",
        required=False,
    )
    path_part = schema.TextLine(
        title="Path Part",
        required=True,
    )
    rest_api_id = schema.TextLine(
        title="Name of the API Gateway REST API this resource belongs to.",
        readonly = True,
    )

class IApiGatewayStage(IResource):
    "API Gateway Stage"
    deployment_id = schema.TextLine(
        title="Deployment ID",
        required=False,
    )
    description=schema.Text(
        title="Description",
        required=False,
    )
    stage_name = schema.TextLine(
        title="Stage name",
        required=False,
    )

class IApiGatewayModels(INamed, IMapping):
    "Container for `ApiGatewayModel`_ objects."
    taggedValue('contains', 'IApiGatewayModel')

class IApiGatewayMethods(INamed, IMapping):
    "Container for `ApiGatewayMethod`_ objects."
    taggedValue('contains', 'IApiGatewayMethod')

class IApiGatewayResources(INamed, IMapping):
    "Container for `ApiGatewayResource`_ objects."
    taggedValue('contains', 'IApiGatewayResource')

class IApiGatewayStages(INamed, IMapping):
    "Container for `ApiGatewayStage`_ objects"
    taggedValue('contains', 'IApiGatewayStages')

class IApiGatewayRestApi(IResource):
    """
An Api Gateway Rest API resource.

Intended to allow provisioning of all API Gateway REST API resources (currently only parital field support).

.. code-block:: yaml
    :caption: API Gateway REST API example

    type: ApiGatewayRestApi
    order: 10
    enabled: true
    fail_on_warnings: true
    description: "My REST API"
    endpoint_configuration:
      - 'REGIONAL'
    models:
      emptyjson:
        content_type: 'application/json'
    methods:
      get:
        http_method: GET
        integration:
          integration_type: AWS
          integration_lambda: paco.ref netenv.mynet.applications.app.groups.restapi.resources.mylambda
          integration_responses:
            - status_code: '200'
              response_templates:
                'application/json': ''
          request_parameters:
            "integration.request.querystring.my_id": "method.request.querystring.my_id"
        authorization_type: NONE
        request_parameters:
          "method.request.querystring.my_id": false
          "method.request.querystring.token": false
        method_responses:
          - status_code: '200'
            response_models:
              - content_type: 'application/json'
                model_name: 'emptyjson'
      post:
        http_method: POST
        integration:
          integration_type: AWS
          integration_lambda: paco.ref netenv.mynet.applications.app.groups.restapi.resources.mylambda
          integration_responses:
            - status_code: '200'
              response_templates:
                'application/json': ''
        authorization_type: NONE
        method_responses:
          - status_code: '200'
            response_models:
              - content_type: 'application/json'
                model_name: 'emptyjson'
    stages:
      prod:
        deployment_id: 'prod'
        description: 'Prod Stage'
        stage_name: 'prod'

    """
    @invariant
    def is_valid_body_location(obj):
        "Validate that only one of body or body_file_location or body_s3_location is set or all are empty."
        count = 0
        if obj._body: count += 1
        if obj.body_file_location: count += 1
        if obj.body_s3_location: count += 1
        if count > 1:
            raise Invalid("Only one of body, body_file_location or body_s3_location can be set.")

    api_key_source_type = schema.TextLine(
        title="API Key Source Type",
        description="Must be one of 'HEADER' to read the API key from the X-API-Key header of a request or 'AUTHORIZER' to read the API key from the UsageIdentifierKey from a Lambda authorizer.",
        constraint = isValidApiKeySourceType,
        required=False,
    )
    binary_media_types = schema.List(
        title="Binary Media Types. The list of binary media types that are supported by the RestApi resource, such as image/png or application/octet-stream. By default, RestApi supports only UTF-8-encoded text payloads.",
        description="Duplicates are not allowed. Slashes must be escaped with ~1. For example, image/png would be image~1png in the BinaryMediaTypes list.",
        constraint = isValidBinaryMediaTypes,
        value_type = schema.TextLine(
            title="Binary Media Type"
        ),
        required=False,
    )
    body = schema.Text(
        title="Body. An OpenAPI specification that defines a set of RESTful APIs in JSON or YAML format. For YAML templates, you can also provide the specification in YAML format.",
        description="Must be valid JSON.",
        required=False,
    )
    body_file_location = StringFileReference(
        title="Path to a file containing the Body.",
        description="Must be valid path to a valid JSON document.",
        required=False,
    )
    body_s3_location = schema.TextLine(
        title="The Amazon Simple Storage Service (Amazon S3) location that points to an OpenAPI file, which defines a set of RESTful APIs in JSON or YAML format.",
        description="Valid S3Location string to a valid JSON or YAML document.",
        required=False,
    )
    clone_from = schema.TextLine(
        title="CloneFrom. The ID of the RestApi resource that you want to clone.",
        required=False,
    )
    description=schema.Text(
        title="Description of the RestApi resource.",
        required=False,
    )
    endpoint_configuration = schema.List(
        title="Endpoint configuration. A list of the endpoint types of the API. Use this field when creating an API. When importing an existing API, specify the endpoint configuration types using the `parameters` field.",
        description="List of strings, each must be one of 'EDGE', 'REGIONAL', 'PRIVATE'",
        value_type = schema.TextLine(
            title="Endpoint Type",
            constraint = isValidEndpointConfigurationType
        ),
        required=False,
    )
    fail_on_warnings = schema.Bool(
        title="Indicates whether to roll back the resource if a warning occurs while API Gateway is creating the RestApi resource.",
        default=False,
        required=False,
    )
    methods = schema.Object(
        schema = IApiGatewayMethods,
        required=False,
    )
    minimum_compression_size = schema.Int(
        title="An integer that is used to enable compression on an API. When compression is enabled, compression or decompression is not applied on the payload if the payload size is smaller than this value. Setting it to zero allows compression for any payload size.",
        description="A non-negative integer between 0 and 10485760 (10M) bytes, inclusive.",
        default=None,
        required=False,
        min=0,
        max=10485760,
    )
    models = schema.Object(
        schema = IApiGatewayModels,
        required=False,
    )
    parameters = schema.Dict(
        title="Parameters. Custom header parameters for the request.",
        description="Dictionary of key/value pairs that are strings.",
        value_type = schema.TextLine(title="Value"),
        default={},
        required=False,
    )
    policy = schema.Text(
        title="""A policy document that contains the permissions for the RestApi resource, in JSON format. To set the ARN for the policy, use the !Join intrinsic function with "" as delimiter and values of "execute-api:/" and "*".""",
        description="Valid JSON document",
        constraint = isValidJSONOrNone,
        required=False,
    )
    resources = schema.Object(
        schema = IApiGatewayResources,
        required=False,
    )
    stages = schema.Object(
        schema = IApiGatewayStages,
        required=False,
    )

# Route53

class IRoute53RecordSet(Interface):
    """
Route53 Record Set
    """
    record_name = schema.TextLine(
        title='Record Set Full Name',
        required=True
    )
    type = schema.TextLine(
        title='Record Set Type',
        required=True,
        constraint = isValidRoute53RecordSetType
    )
    resource_records = schema.List(
        title='Record Set Values',
        required=True,
        value_type = schema.TextLine(title='Resource Record')
    )
    ttl = schema.Int(
        title='Record TTL',
        required=False,
        default=300
    )

    @invariant
    def is_valid_values_check(obj):
        if obj.type in ['CNAME', 'SOA']:
            if len(obj.resource_records) > 1:
                raise Invalid("If 'type' is {}, you may only specify one 'value'.".format(obj.type))

class IRoute53HostedZoneExternalResource(INamed, IDeployable):
    """
Existing Hosted Zone configuration
    """
    hosted_zone_id = schema.TextLine(
        title='ID of an existing Hosted Zone',
        required=True
    )
    nameservers = schema.List(
        title='List of the Hosted Zones Nameservers',
        value_type = schema.TextLine(title='Nameservers'),
        required=True
    )

class IRoute53HostedZone(INamed, IDeployable):
    """
Route53 Hosted Zone
    """
    domain_name = schema.TextLine(
        title="Domain Name",
        required=True
    )
    account = PacoReference(
        title="Account this Hosted Zone belongs to",
        required=True,
        schema_constraint='IAccount'
    )
    record_sets = schema.List(
        title='List of Record Sets',
        value_type = schema.Object(IRoute53RecordSet),
        required=True
    )
    parent_zone = schema.TextLine(
        title='Parent Hozed Zone name',
        required=False
    )
    external_resource = schema.Object(
        title='External HostedZone Id Configuration',
        schema = IRoute53HostedZoneExternalResource,
        required=False
    )


class IRoute53Resource(INamed):
    """
The ``resource/route53.yaml`` file manages AWS Route 53 hosted zones.

Provision Route 53 with:

.. code-block:: bash

    paco provision resource.route53

.. code-block:: yaml
    :caption: Example resource/route53.yaml file

    hosted_zones:
      example:
        enabled: true
        domain_name: example.com
        account: aim.ref accounts.prod

    """
    hosted_zones = schema.Dict(
        title="Hosted Zones",
        value_type = schema.Object(IRoute53HostedZone),
        default=None,
        required=False,
    )

class IRoute53HealthCheck(IResource):
    """Route53 Health Check"""
    @invariant
    def is_load_balancer_or_domain_name_or_ip_address(obj):
        if obj.domain_name == None and obj.load_balancer == None and obj.ip_address == None:
            raise Invalid("Must set either domain_name, load_balancer or ip_address field.")
        count = 0
        if obj.domain_name != None:
            count += 1
        if obj.load_balancer != None:
            count += 1
        if obj.ip_address != None:
            count += 1
        if count > 1:
            raise Invalid("Can set only one of the domain_name, load_balancer and ip_address fields.")

    @invariant
    def is_match_string_health_check(obj):
        if getattr(obj, 'match_string', None) != None:
            if obj.health_check_type not in ('HTTP', 'HTTPS'):
                raise Invalid("If match_string field supplied, health_check_type must be HTTP or HTTPS.")

    domain_name = schema.TextLine(
        title="Fully Qualified Domain Name",
        description="Either this or the load_balancer field can be set but not both.",
        required=False
    )
    enable_sni = schema.Bool(
        title="Enable SNI",
        required=False,
        default=False
    )
    failure_threshold = schema.Int(
        title="Number of consecutive health checks that an endpoint must pass or fail for Amazon Route 53 to change the current status of the endpoint from unhealthy to healthy or vice versa.",
        min=1,
        max=10,
        required=False,
        default=3,
    )
    health_check_type = schema.TextLine(
        title="Health Check Type",
        description="Must be one of HTTP, HTTPS or TCP",
        required=True,
        constraint=isValidRoute53HealthCheckType,
    )
    health_checker_regions = schema.List(
        title="Health checker regions",
        description="List of AWS Region names (e.g. us-west-2) from which to make health checks.",
        required=False,
        value_type=schema.TextLine(title="AWS Region"),
        constraint=isValidHealthCheckAWSRegionList,
    )
    ip_address = PacoReference(
        title="IP Address",
        str_ok=True,
        required=False,
        schema_constraint='IEIP'
    )
    load_balancer = PacoReference(
        title="Load Balancer Endpoint",
        str_ok=True,
        required=False,
        schema_constraint='ILBApplication'
    )
    latency_graphs = schema.Bool(
        title="Measure latency and display CloudWatch graph in the AWS Console",
        required=False,
        default=False,
    )
    match_string = schema.TextLine(
        title="String to match in the first 5120 bytes of the response",
        min_length=1,
        max_length=255,
        required=False,
    )
    port = schema.Int(
        title="Port",
        min=1,
        max=65535,
        required=False,
        default=80,
    )
    request_interval_fast = schema.Bool(
        title="Fast request interval will only wait 10 seconds between each health check response instead of the standard 30",
        default=False,
        required=False,
    )
    resource_path = schema.TextLine(
        title="Resource Path",
        description="String such as '/health.html'. Path should return a 2xx or 3xx. Query string parameters are allowed: '/search?query=health'",
        max_length=255,
        default="/",
        required=False,
    )


# CodeCommit

class ICodeCommitUser(Interface):
    """
CodeCommit User
    """
    username = schema.TextLine(
        title="CodeCommit Username",
        required=False,
    )
    public_ssh_key = schema.TextLine(
        title="CodeCommit User Public SSH Key",
        default=None,
        required=False,
    )

class ICodeCommitRepository(INamed, IDeployable):
    """
CodeCommit Repository
    """
    repository_name = schema.TextLine(
        title="Repository Name",
        required=False,
    )
    account = PacoReference(
        title="Account this repo belongs to.",
        required=True,
        schema_constraint='IAccount'
    )
    region = schema.TextLine(
        title="AWS Region",
        required=False,
    )
    description=schema.TextLine(
        title="Repository Description",
        required=False,
    )
    external_resource = schema.Bool(
        title='Boolean indicating whether the CodeCommit repository already exists or not',
        default=False,
        required=False,
    )
    users = schema.Dict(
        title="CodeCommit Users",
        value_type = schema.Object(ICodeCommitUser),
        default=None,
        required=False,
    )

class ICodeCommitRepositoryGroup(INamed, IMapping):
    """
Container for `CodeCommitRepository`_ objects.
    """
    taggedValue('contains', 'ICodeCommitRepository')

class ICodeCommitRepositoryGroups(INamed, IMapping):
    """
Container for `CodeCommitRepositoryGroup`_ objects.
    """
    taggedValue('contains', 'ICodeCommitRepositoryGroup')

class ICodeCommit(Interface):
    """
CodeCommit Service Configuration
    """
    repository_groups = schema.Object(
        title="Container of CodeCommitRepositoryGroup objects",
        required=True,
        schema=ICodeCommitRepositoryGroups,
    )

class ISNSTopicSubscription(Interface):

    @invariant
    def is_valid_endpoint_for_protocol(obj):
        "Validate enpoint"
        # ToDo: this relies on other validation functions, maybe catch an re-raise
        # with more helpful error message context.
        # also check the other protocols ...
        if obj.protocol == 'http':
            isValidHttpUrl(obj.endpoint)
        elif obj.protocol == 'https':
            isValidHttpsUrl(obj.endpoint)
        elif obj.protocol in ['email','email-json']:
            isValidEmail(obj.endpoint)

    protocol = schema.TextLine(
        title="Notification protocol",
        default="email",
        description="Must be a valid SNS Topic subscription protocol: 'http', 'https', 'email', 'email-json', 'sms', 'sqs', 'application', 'lambda'.",
        constraint = isValidSNSSubscriptionProtocol,
        required=False,
    )
    endpoint = PacoReference(
        title="SNS Topic ARN or Paco Reference",
        str_ok=True,
        required=False,
        schema_constraint='ISNSTopic'
    )

class ISNSTopic(IResource):
    """
Simple Notification Service (SNS) Topic resource.

.. sidebar:: Prescribed Automation

    ``cross_account_access``: Creates an SNS Topic Policy which will grant all of the AWS Accounts in this
    Paco Project access to the ``sns.Publish`` permission for this SNS Topic.

.. code-block:: yaml
    :caption: Example SNSTopic resource YAML

    type: SNSTopic
    order: 1
    enabled: true
    display_name: "Waterbear Cloud AWS"
    cross_account_access: true
    subscriptions:
      - endpoint: http://example.com/yes
        protocol: http
      - endpoint: https://example.com/orno
        protocol: https
      - endpoint: bob@example.com
        protocol: email
      - endpoint: bob@example.com
        protocol: email-json
      - endpoint: '555-555-5555'
        protocol: sms
      - endpoint: arn:aws:sqs:us-east-2:444455556666:queue1
        protocol: sqs
      - endpoint: arn:aws:sqs:us-east-2:444455556666:queue1
        protocol: application
      - endpoint: arn:aws:lambda:us-east-1:123456789012:function:my-function
        protocol: lambda

"""
    display_name = schema.TextLine(
        title="Display name for SMS Messages",
        required=False,
    )
    subscriptions = schema.List(
        title="List of SNS Topic Subscriptions",
        value_type = schema.Object(ISNSTopicSubscription),
        required=False,
    )
    cross_account_access = schema.Bool(
        title="Cross-account access from all other accounts in this project.",
        description="",
        required=False,
        default=False,
    )

class ICloudTrail(IResource):
    """
CloudTrail resource
    """
    accounts = schema.List(
        title="Accounts to enable this CloudTrail in. Leave blank to assume all accounts.",
        description="",
        value_type = PacoReference(
            title="Account Reference",
            schema_constraint='IAccount'
        ),
        required=False,
    )
    cloudwatchlogs_log_group = schema.Object(
        title="CloudWatch Logs LogGroup to deliver this trail to.",
        required=False,
        default=None,
        schema = ICloudWatchLogGroup,
    )
    enable_kms_encryption = schema.Bool(
        title="Enable KMS Key encryption",
        default=False,
    )
    enable_log_file_validation = schema.Bool(
        title="Enable log file validation",
        default=True,
        required=False,
    )
    include_global_service_events = schema.Bool(
        title="Include global service events",
        default=True,
        required=False,
    )
    is_multi_region_trail = schema.Bool(
        title="Is multi-region trail?",
        default=True,
        required=False,
    )
    region = schema.TextLine(
        title="Region to create the CloudTrail",
        default="",
        description='Must be a valid AWS Region name or empty string',
        constraint = isValidAWSRegionNameOrNone,
        required=False,
    )
    s3_bucket_account = PacoReference(
        title="Account which will contain the S3 Bucket that the CloudTrails will be stored in",
        description='Must be an paco.ref to an account',
        required=True,
        schema_constraint='IS3Bucket'
    )
    s3_key_prefix = schema.TextLine(
        title="S3 Key Prefix specifies the Amazon S3 key prefix that comes after the name of the bucket.",
        description="Do not include a leading or trailing / in your prefix. They are provided already.",
        default="",
        max_length = 200,
        constraint = isValidS3KeyPrefix,
        required=False,
    )

class ICloudTrails(INamed, IMapping):
    """
Container for `CloudTrail`_ objects.
    """
    taggedValue('contains', 'ICloudTrail')

class ICloudTrailResource(INamed):
    """
Global CloudTrail configuration
    """
    trails = schema.Object(
        title="CloudTrails",
        schema = ICloudTrails,
        default=None,
        required=False,
    )

class ICloudFrontCookies(INamed):
    forward = schema.TextLine(
        title="Cookies Forward Action",
        constraint = isValidCloudFrontCookiesForward,
        default='all',
        required=False
    )
    whitelisted_names = schema.List(
        title="White Listed Names",
        value_type = schema.TextLine(),
        required=False
    )

class ICloudFrontForwardedValues(INamed):
    query_string = schema.Bool(
        title="Forward Query Strings",
        default=True,
        required=False
    )
    cookies = schema.Object(
        title="Forward Cookies",
        schema = ICloudFrontCookies,
        required=False
    )
    headers = schema.List(
        title="Forward Headers",
        value_type = schema.TextLine(),
        default=['*'],
        required=False
    )

class ICloudFrontDefaultCacheBehavior(INamed):
    allowed_methods = schema.List(
        title="List of Allowed HTTP Methods",
        value_type = schema.TextLine(),
        default=[ 'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT' ],
        required=False
    )
    cached_methods = schema.List(
        title="List of HTTP Methods to cache",
        value_type = schema.TextLine(),
        default=[ 'GET', 'HEAD', 'OPTIONS' ],
        required=False
    )
    default_ttl = schema.Int(
        title="Default TTL",
        # Disable TTL bydefault, just pass through
        default=0
    )
    max_ttl = schema.Int(
        title="Maximum TTL",
        # -1 i unset
        default=-1
    )
    min_ttl = schema.Int(
        title="Minimum TTL",
        # -1 is unset
        default=-1
    )
    target_origin = PacoReference(
        title="Target Origin",
        schema_constraint='ICloudFrontOrigin'
    )
    viewer_protocol_policy = schema.TextLine(
        title="Viewer Protocol Policy",
        constraint = isValidCFViewerProtocolPolicy,
        default='redirect-to-https'
    )
    forwarded_values = schema.Object(
        title="Forwarded Values",
        schema = ICloudFrontForwardedValues,
        required=False
    )
    compress = schema.Bool(
        title="Compress certain files automatically",
        required=False,
        default=False
    )

class ICloudFrontCacheBehavior(ICloudFrontDefaultCacheBehavior):
    path_pattern = schema.TextLine(
        title="Path Pattern",
        required=True
    )

class ICloudFrontViewerCertificate(INamed):
    certificate = PacoReference(
        title="Certificate Reference",
        required=False,
        schema_constraint='IAWSCertificateManager'
    )
    ssl_supported_method = schema.TextLine(
        title="SSL Supported Method",
        constraint = isValidCFSSLSupportedMethod,
        required=False,
        default='sni-only'
    )
    minimum_protocol_version = schema.TextLine(
        title="Minimum SSL Protocol Version",
        constraint = isValidCFMinimumProtocolVersion,
        required=False,
        default='TLSv1.1_2016'
    )

class ICloudFrontCustomErrorResponse(Interface):
    error_caching_min_ttl = schema.Int(
        title="Error Caching Min TTL",
        required=False
    )
    error_code = schema.Int(
        title="HTTP Error Code",
        required=False
    )
    response_code = schema.Int(
        title="HTTP Response Code",
        required=False
    )
    response_page_path = schema.TextLine(
        title="Response Page Path",
        required=False
    )

class ICloudFrontCustomOriginConfig(INamed):
    http_port = schema.Int(
        title="HTTP Port",
        required=False
    )
    https_port = schema.Int(
        title="HTTPS Port",
        required=False,
    )
    protocol_policy = schema.TextLine(
        title="Protocol Policy",
        constraint = isValidCFProtocolPolicy,
        required=False,
    )
    ssl_protocols = schema.List(
        title="List of SSL Protocols",
        value_type = schema.TextLine(),
        constraint = isValidCFSSLProtocol,
        required=False,
    )
    read_timeout = schema.Int(
        title="Read timeout",
        min=4,
        max=60,
        default=30,
        required=False,
    )
    keepalive_timeout = schema.Int(
        title="HTTP Keepalive Timeout",
        min=1,
        max=60,
        default=5,
        required=False,
    )

class ICloudFrontOrigin(INamed):
    """
CloudFront Origin Configuration
    """
    s3_bucket = PacoReference(
        title="Origin S3 Bucket Reference",
        required=False,
        schema_constraint='IS3Bucket'
    )
    domain_name = PacoReference(
        title="Origin Resource Reference",
        str_ok=True,
        required=False,
        schema_constraint='IRoute53HostedZone'
    )
    custom_origin_config = schema.Object(
        title="Custom Origin Configuration",
        schema = ICloudFrontCustomOriginConfig,
        required=False,
    )

class ICloudFrontFactory(INamed):
    """
CloudFront Factory
    """
    domain_aliases = schema.List(
        title="List of DNS for the Distribution",
        value_type = schema.Object(IDNS),
        required=False,
    )

    viewer_certificate = schema.Object(
        title="Viewer Certificate",
        schema = ICloudFrontViewerCertificate,
        required=False,
    )

class ICloudFront(IResource, IDeployable, IMonitorable):
    """
CloudFront CDN Configuration
    """
    domain_aliases = schema.List(
        title="List of DNS for the Distribution",
        value_type = schema.Object(IDNS),
        required=False,
    )
    default_root_object = schema.TextLine(
        title="The default path to load from the origin.",
        default='index.html',
        required=False,
    )
    default_cache_behavior = schema.Object(
        title="Default Cache Behavior",
        schema = ICloudFrontDefaultCacheBehavior,
        required=False,
    )
    cache_behaviors = schema.List(
        title='List of Cache Behaviors',
        value_type = schema.Object(ICloudFrontCacheBehavior),
        required=False
    )
    viewer_certificate = schema.Object(
        title="Viewer Certificate",
        schema = ICloudFrontViewerCertificate,
        required=False,
    )
    price_class = schema.TextLine(
        title="Price Class",
        constraint = isValidCFPriceClass,
        default='All',
        required=False,
    )
    custom_error_responses = schema.List(
        title="List of Custom Error Responses",
        value_type = schema.Object(ICloudFrontCustomErrorResponse),
        default=None,
        required=False,
    )
    origins = schema.Dict(
        title="Map of Origins",
        value_type = schema.Object(ICloudFrontOrigin),
        required=False,
    )
    webacl_id = schema.TextLine(
        title="WAF WebACLId",
        required=False,
    )
    factory = schema.Dict(
        title="CloudFront Factory",
        value_type = schema.Object(ICloudFrontFactory),
        default=None,
        required=False,
    )

# RDS Schemas

class IDBParameters(IMapping):
    "A dict of database parameters"
    # ToDo: constraints for parameters ...(huge!)

class IDBParameterGroup(IResource):
    """
DBParameterGroup
    """
    description=schema.Text(
        title="Description",
        required=False
    )
    family = schema.TextLine(
        title="Database Family",
        required=True
        # ToDo: constraint for this is fairly complex and can change
    )
    parameters = schema.Object(
        title="Database Parameter set",
        schema=IDBParameters,
        required=True
    )

class IRDSOptionConfiguration(Interface):
    """
Option groups enable and configure features that are specific to a particular DB engine.
    """
    option_name = schema.TextLine(
        title='Option Name',
        required=False,
    )
    option_settings = schema.List(
        title='List of option name value pairs.',
        value_type = schema.Object(INameValuePair),
        required=False,
    )
    option_version = schema.TextLine(
        title='Option Version',
        required=False,
    )
    port = schema.TextLine(
        title='Port',
        required=False,
    )
    # - DBSecurityGroupMemberships
    #   A list of DBSecurityGroupMembership name strings used for this option.
    # - VpcSecurityGroupMemberships
    #   A list of VpcSecurityGroupMembership name strings used for this option.


class IRDS(IResource, IMonitorable):
    """
RDS Common Interface
    """
    @invariant
    def password_or_snapshot_or_secret(obj):
        count = 0
        if obj.db_snapshot_identifier:
            count += 1
        if obj.master_user_password:
            count += 1
        if obj.secrets_password:
            count += 1
        if count > 1:
            raise Invalid("Can only set one of db_snapshot_identifier, master_user_password or secrets_password for RDS.")
        elif count < 1:
            raise Invalid("Must set one of db_snapshot_identifier, master_user_password or secrets_password for RDS.")
        return True

    allow_major_version_upgrade = schema.Bool(
        title="Allow major version upgrades",
        required=False,
    )
    auto_minor_version_upgrade = schema.Bool(
        title="Automatic minor version upgrades",
        required=False,
    )
    backup_preferred_window = schema.TextLine(
        title="Backup Preferred Window",
        required=False,
    )
    backup_retention_period = schema.Int(
        title="Backup Retention Period in days",
        required=False,
    )
    cloudwatch_logs_exports = schema.List(
        title="List of CloudWatch Logs Exports",
        value_type=schema.TextLine(
            title="CloudWatch Log Export",
        ),
        required=False,
        # ToDo: Constraint that depends upon the database type, not applicable for Aurora
    )
    db_instance_type = schema.TextLine(
        title="RDS Instance Type",
        required=False,
    )
    db_snapshot_identifier = schema.TextLine(
        title="DB Snapshot Identifier to restore from",
        required=False,
    )
    deletion_protection = schema.Bool(
        title="Deletion Protection",
        default=False,
        required=False
    )
    dns = schema.List(
        title="List of DNS for the RDS",
        value_type=schema.Object(IDNS),
        required=False
    )
    engine = schema.TextLine(
        title="RDS Engine",
        required=False,
    )
    engine_version = schema.TextLine(
        title="RDS Engine Version",
        required=False,
    )
    kms_key_id = PacoReference(
        title="Enable Storage Encryption",
        required=False,
        schema_constraint='Interface'
    )
    license_model = schema.TextLine(
        title="License Model",
        required=False,
    )
    maintenance_preferred_window = schema.TextLine(
        title="Maintenance Preferred Window",
        required=False,
    )
    master_username = schema.TextLine(
        title="Master Username",
        required=False,
    )
    master_user_password = schema.TextLine(
        title="Master User Password",
        required=False,
    )
    option_configurations = schema.List(
        title="Option Configurations",
        value_type=schema.Object(IRDSOptionConfiguration),
        required=False,
    )
    parameter_group = PacoReference(
        title="RDS Parameter Group",
        required=False,
        schema_constraint='IDBParameterGroup'
    )
    primary_domain_name = PacoReference(
        title="Primary Domain Name",
        str_ok=True,
        required=False,
        schema_constraint='IRoute53HostedZone'
    )
    primary_hosted_zone = PacoReference(
        title="Primary Hosted Zone",
        required=False,
        schema_constraint='IRoute53HostedZone'
    )
    port = schema.Int(
        title="DB Port",
        required=False,
    )
    publically_accessible = schema.Bool(
        title="Assign a Public IP address",
        required=False,
    )
    secrets_password = PacoReference(
        title="Secrets Manager password",
        required=False,
        schema_constraint='ISecretsManagerSecret'
    )
    security_groups = schema.List(
        title="List of VPC Security Group Ids",
        value_type=PacoReference(
            schema_constraint='ISecurityGroup'
        ),
        required=False,
    )
    segment = PacoReference(
        title="Segment",
        required=False,
        schema_constraint='ISegment'
    )
    storage_encrypted = schema.Bool(
        title="Enable Storage Encryption",
        required=False,
    )
    storage_type = schema.TextLine(
        title="DB Storage Type",
        required=False,
    )
    storage_size_gb = schema.Int(
        title="DB Storage Size in Gigabytes",
        required=False,
    )


class IRDSMysql(IRDS):
    """
The RDSMysql type extends the base RDS schema with a ``multi_az`` field. When you provision a Multi-AZ DB Instance,
Amazon RDS automatically creates a primary DB Instance and synchronously replicates the data to a standby instance
in a different Availability Zone (AZ).
    """
    multi_az = schema.Bool(
        title="Multiple Availability Zone deployment",
        default=False,
        required=False,
    )

class IRDSAurora(IResource, IRDS):
    """
RDS Aurora
    """
    secondary_domain_name = PacoReference(
        title="Secondary Domain Name",
        str_ok=True,
        required=False,
        schema_constraint='IRoute53HostedZone'
    )
    secondary_hosted_zone = PacoReference(
        title="Secondary Hosted Zone",
        required=False,
        schema_constraint='IRoute53HostedZone'
    )

# Cache schemas

class IElastiCache(Interface):
    """
Base ElastiCache Interface
    """
    # ToDo: Invariant for cache_clusters
    # - This parameter is not used if there is more than one node group (shard). You should use ReplicasPerNodeGroup instead.
    # - If AutomaticFailoverEnabled is true, the value of this parameter must be at least 2.
    @invariant
    def cluster_layout(obj):
        "One of PrimaryClusterId, NumCacheClusters, NumNodeGroups or ReplicasPerNodeGroup are required"
        if obj.cache_clusters == None and obj.number_of_read_replicas == None:
            raise Invalid("Must supply either cache_clusters or number_of_read_replicas.")

    at_rest_encryption = schema.Bool(
        title="Enable encryption at rest",
        required=False,
    )
    auto_minor_version_upgrade = schema.Bool(
        title="Enable automatic minor version upgrades",
        required=False,
    )
    automatic_failover_enabled = schema.Bool(
        title="Specifies whether a read-only replica is automatically promoted to read/write primary if the existing primary fails",
        required=False,
    )
    az_mode = schema.TextLine(
        title="AZ mode",
        constraint=isValidAZMode,
        required=False,
    )
    cache_clusters = schema.Int(
        title="Number of Cache Clusters",
        required=False,
        min=1,
        max=6
    )
    cache_node_type = schema.TextLine(
        title="Cache Node Instance type",
        description="",
        required=False,
    )
    description=schema.Text(
        title="Replication Description",
        required=False,
    )
    engine = schema.TextLine(
        title="ElastiCache Engine",
        required=False
    )
    engine_version = schema.TextLine(
        title="ElastiCache Engine Version",
        required=False
    )
    maintenance_preferred_window = schema.TextLine(
        title='Preferred maintenance window',
        required=False,
    )
    number_of_read_replicas = schema.Int(
        title="Number of read replicas",
        required=False,
    )
    parameter_group = PacoReference(
        title='Parameter Group name',
        str_ok=True,
        required=False,
        schema_constraint='Interface'
    )
    port = schema.Int(
        title="Port",
        required=False,
    )
    security_groups = schema.List(
        title="List of Security Groups",
        value_type=PacoReference(
            schema_constraint='ISecurityGroup'
        ),
        required=False,
    )
    segment = PacoReference(
        title="Segment",
        required=False,
        schema_constraint='ISegment'
    )


class IElastiCacheRedis(IResource, IElastiCache, IMonitorable):
    """
Redis ElastiCache Interface
    """
    cache_parameter_group_family = schema.TextLine(
        title='Cache Parameter Group Family',
        constraint=isRedisCacheParameterGroupFamilyValid,
        required=False
    )
    snapshot_retention_limit_days = schema.Int(
        title="Snapshot Retention Limit in Days",
        required=False,
    )
    snapshot_window = schema.TextLine(
        title="The daily time range (in UTC) during which ElastiCache begins taking a daily snapshot of your node group (shard).",
        required=False,
        # ToDo: constraint for "windows"
    )

class IIAMUserProgrammaticAccess(IDeployable):
    """
IAM User Programmatic Access Configuration
    """
    access_key_1_version = schema.Int(
        title='Access key version id',
        default=0,
        required=False
    )
    access_key_2_version = schema.Int(
        title='Access key version id',
        default=0,
        required=False
    )

class IIAMUserPermission(INamed, IDeployable):
    """
IAM User Permission
    """
    type = schema.TextLine(
        title="Type of IAM User Access",
        description="A valid Paco IAM user access type: Administrator, CodeCommit, etc.",
        required=False,
    )

class IIAMUserPermissionAdministrator(IIAMUserPermission):
    """
Administrator IAM User Permission
    """
    accounts = CommaList(
        title='Comma separated list of Paco AWS account names this user has access to',
        required=False,
    )
    read_only = schema.Bool(
        title='Enabled ReadOnly access',
        default=False,
        required=False,
    )


class IIAMUserPermissionCodeCommitRepository(IParent):
    """
CodeCommit Repository IAM User Permission Definition
    """
    codecommit = PacoReference(
        title='CodeCommit Repository Reference',
        required=False,
        schema_constraint='ICodeCommitRepository'
    )
    permission = schema.TextLine(
        title='Paco Permission policy',
        constraint = isPacoCodeCommitPermissionPolicyValid,
        required=False,
    )
    console_access_enabled = schema.Bool(
        title='Console Access Boolean',
        required=False,
    )
    public_ssh_key = schema.TextLine(
        title="CodeCommit User Public SSH Key",
        default=None,
        required=False,
    )

class IIAMUserPermissionCodeCommit(IIAMUserPermission):
    """
CodeCommit IAM User Permission
    """
    repositories = schema.List(
        title='List of repository permissions',
        value_type = schema.Object(IIAMUserPermissionCodeCommitRepository),
        required=False,
    )

class IIAMUserPermissionCodeBuildResource(IParent):
    """
CodeBuild Resource IAM User Permission Definition
    """
    codebuild = PacoReference(
        title='CodeBuild Resource Reference',
        required=False,
        schema_constraint='Interface'
    )
    permission = schema.TextLine(
        title='Paco Permission policy',
        constraint = isPacoCodeCommitPermissionPolicyValid,
        required=False,
    )
    console_access_enabled = schema.Bool(
        title='Console Access Boolean',
        required=False,
    )

class IIAMUserPermissionCodeBuild(IIAMUserPermission):
    """
CodeBuild IAM User Permission
    """
    resources = schema.List(
        title='List of CodeBuild resources',
        value_type = schema.Object(IIAMUserPermissionCodeBuildResource),
        required=False
    )

class IIAMUserPermissionCustomPolicy(IIAMUserPermission):
    """
Custom IAM User Permission
    """
    accounts = CommaList(
        title='Comma separated list of Paco AWS account names this user has access to',
        required=False,
    )
    policies = schema.List(
        title="Policies",
        value_type=schema.Object(
            schema=IPolicy
        ),
        required=False
    )

class IIAMUserPermissions(INamed, IMapping):
    """
Container for IAM User Permission objects.
    """
    taggedValue('contains', 'mixed')

class IIAMUser(INamed, IDeployable):
    """
IAM User
    """
    account = PacoReference(
        title="Paco account reference to install this user",
        required=True,
        schema_constraint='IAccount',
    )
    username = schema.TextLine(
        title='IAM Username',
        required=False,
    )
    description=schema.TextLine(
        title='IAM User Description',
        required=False,
    )
    console_access_enabled = schema.Bool(
        title='Console Access Boolean'
    )
    programmatic_access = schema.Object(
        title='Programmatic Access',
        schema = IIAMUserProgrammaticAccess,
        required=False,
    )
    permissions = schema.Object(
        title='Paco IAM User Permissions',
        schema = IIAMUserPermissions,
        required=False,
    )
    account_whitelist = CommaList(
        title='Comma separated list of Paco AWS account names this user has access to',
        required=False,
    )

class IIAMUsers(INamed, IMapping):
    """
Container for `IAMUser`_ objects.
    """
    taggedValue('contains', 'IIAMUser')


class IIAMResource(INamed):
    """
IAM Resource contains IAM Users who can login and have different levels of access to the AWS Console and API.
    """
    users = schema.Object(
        title='IAM Users',
        schema=IIAMUsers,
        required=False,
    )

class IDeploymentPipelineConfiguration(INamed):
    """
Deployment Pipeline General Configuration
    """
    artifacts_bucket = PacoReference(
        title="Artifacts S3 Bucket Reference",
        description="",
        required=False,
        schema_constraint=IS3Bucket,
    )
    account = PacoReference(
        title="The account where Pipeline tools will be provisioned.",
        required=False,
        schema_constraint=IAccount
    )

class IDeploymentPipelineStageAction(INamed, IDeployable, IMapping):
    """
Deployment Pipeline Source Stage
    """
    taggedValue('contains', 'mixed')
    type = schema.TextLine(
        title='The type of DeploymentPipeline Source Stage',
        required=False,
    )
    run_order = schema.Int(
        title='The order in which to run this stage',
        min=1,
        max=999,
        default=1,
        required=False,
    )

class IDeploymentPipelineSourceCodeCommit(IDeploymentPipelineStageAction):
    """
CodeCommit DeploymentPipeline Source Stage
    """
    taggedValue('contains', 'mixed')
    codecommit_repository = PacoReference(
        title='CodeCommit Respository',
        required=False,
        schema_constraint='ICodeCommitRepository'
    )

    deployment_branch_name = schema.TextLine(
        title="Deployment Branch Name",
        description="",
        default="",
        required=False,
    )

class IDeploymentPipelineBuildCodeBuild(IDeploymentPipelineStageAction):
    """
CodeBuild DeploymentPipeline Build Stage
    """
    taggedValue('contains', 'mixed')
    deployment_environment = schema.TextLine(
        title="Deployment Environment",
        description="",
        default="",
        required=False,
    )
    codebuild_image = schema.TextLine(
        title='CodeBuild Docker Image',
        required=False,
    )
    codebuild_compute_type = schema.TextLine(
        title='CodeBuild Compute Type',
        constraint = isValidCodeBuildComputeType,
        required=False,
    )
    timeout_mins = schema.Int(
        title='Timeout in Minutes',
        min=5,
        max=480,
        default=60,
        required=False,
    )
    role_policies = schema.List(
        title='Project IAM Role Policies',
        value_type=schema.Object(IPolicy),
        required=False,
    )

class IDeploymentPipelineDeployS3(IDeploymentPipelineStageAction):
    """
Amazon S3 Deployment Provider
    """
    taggedValue('contains', 'mixed')
    # BucketName: Required
    bucket = PacoReference(
        title="S3 Bucket Reference",
        required=False,
        schema_constraint='IS3Bucket'
    )
    # Extract: Required: Required if Extract = false
    extract = schema.Bool(
        title="Boolean indicating whether the deployment artifact will be unarchived.",
        default=True,
        required=False,
    )
    # ObjectKey: Required if Extract = false
    object_key = schema.TextLine(
        title="S3 object key to store the deployment artifact as.",
        required=False,
    )
    # KMSEncryptionKeyARN: Optional
    # This is used internally for now.
    #kms_encryption_key_arn = schema.TextLine(
    #    title="The KMS Key Arn used for artifact encryption.",
    #    required=False
    #)
    # : CannedACL: Optional
    # https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl
    # canned_acl =

    # CacheControl: Optional
    # cache_control = schema.TextLine()
    # The CacheControl parameter controls caching behavior for requests/responses for objects
    # in the bucket. For a list of valid values, see the Cache-Control header field for HTTP
    # operations. To enter multiple values in CacheControl, use a comma between each value.
    #
    # You can add a space after each comma (optional), as shown in this example for the CLI:
    #
    # "CacheControl": "public, max-age=0, no-transform"

class IDeploymentPipelineManualApproval(IDeploymentPipelineStageAction):
    """
ManualApproval DeploymentPipeline
    """
    taggedValue('contains', 'mixed')
    manual_approval_notification_email = schema.List(
        title="Manual Approval Notification Email List",
        description="",
        value_type=schema.TextLine(
            title="Manual approval notification email",
            description="",
            default="",
            required=False,
        ),
        required=False
    )

class ICodeDeployMinimumHealthyHosts(INamed):
    """
CodeDeploy Minimum Healthy Hosts
    """
    type = schema.TextLine(
        title="Deploy Config Type",
        default="HOST_COUNT",
        required=False,
    )
    value = schema.Int(
        title="Deploy Config Value",
        default=0,
        required=False,
    )


class IDeploymentPipelineDeployCodeDeploy(IDeploymentPipelineStageAction):
    """
CodeDeploy DeploymentPipeline Deploy Stage
    """
    auto_scaling_group = PacoReference(
        title="ASG Reference",
        required=False,
        schema_constraint='IASG'
    )
    auto_rollback_enabled = schema.Bool(
        title="Automatic rollback enabled",
        description="",
        default=True
    )
    minimum_healthy_hosts = schema.Object(
        title="The minimum number of healthy instances that should be available at any time during the deployment.",
        schema = ICodeDeployMinimumHealthyHosts,
        required=False
    )
    deploy_style_option = schema.TextLine(
        title="Deploy Style Option",
        description="",
        default="WITH_TRAFFIC_CONTROL",
        required=False,
    )
    deploy_instance_role = PacoReference(
        title="Deploy Instance Role Reference",
        required=False,
        schema_constraint='IRole'
    )
    elb_name = schema.TextLine(
        title="ELB Name",
        description="",
        default="",
        required=False,
    )
    alb_target_group = PacoReference(
        title="ALB Target Group Reference",
        required=False,
        schema_constraint='ITargetGroup'
    )

class IDeploymentPipelineSourceStage(INamed, IMapping):
    """
A map of DeploymentPipeline source stage actions
    """
    taggedValue('contains', 'mixed')

class IDeploymentPipelineBuildStage(INamed, IMapping):
    """
A map of DeploymentPipeline build stage actions
    """
    taggedValue('contains', 'mixed')

class IDeploymentPipelineDeployStage(INamed, IMapping):
    """
A map of DeploymentPipeline deploy stage actions
    """
    taggedValue('contains', 'mixed')

class IDeploymentPipeline(IResource):
    """
Code Pipeline: Build and Deploy
    """
    configuration = schema.Object(
        title='Deployment Pipeline General Configuration',
        schema = IDeploymentPipelineConfiguration,
        required=False,
    )
    source = schema.Object(
        title='Deployment Pipeline Source Stage',
        schema = IDeploymentPipelineSourceStage,
        required=False,
    )
    build = schema.Object(
        title='Deployment Pipeline Build Stage',
        schema = IDeploymentPipelineBuildStage,
        required=False,
    )
    deploy = schema.Object(
        title='Deployment Pipeline Deploy Stage',
        schema =IDeploymentPipelineDeployStage,
        required=False,
    )

class IDeploymentGroupS3Location(IParent):
    bucket = PacoReference(
        title="S3 Bucket revision location",
        required=False,
        schema_constraint='IS3Bucket'
    )
    bundle_type = schema.TextLine(
        title="Bundle Type",
        description="Must be one of JSON, tar, tgz, YAML or zip.",
        required=False,
        constraint=isValidDeploymentGroupBundleType
    )
    key = schema.TextLine(
        title="The name of the Amazon S3 object that represents the bundled artifacts for the application revision.",
        required=True
    )

class ICodeDeployDeploymentGroups(INamed, IMapping):
    taggedValue('contains', 'mixed')

class ICodeDeployDeploymentGroup(INamed, IDeployable):
    ignore_application_stop_failures = schema.Bool(
        title="Ignore Application Stop Failures",
        required=False,
    )
    revision_location_s3 = schema.Object(
        title="S3 Bucket revision location",
        required=False,
        schema=IDeploymentGroupS3Location
    )
    autoscalinggroups = schema.List(
        title="AutoScalingGroups that CodeDeploy automatically deploys revisions to when new instances are created",
        required=False,
        value_type=PacoReference(
            title="AutoScalingGroup",
            schema_constraint='IASG'
        )
    )
    role_policies = schema.List(
        title="Policies to grant the deployment group role",
        required=False,
        value_type=schema.Object(IPolicy),
    )

class ICodeDeployApplication(IResource):
    """
CodeDeploy Application creates CodeDeploy Application and Deployment Groups for that application.

This resource can be used when you already have another process in-place to put deploy artifacts
into an S3 Bucket. If you also need to build artifacts, use `DeploymentPipeline`_ instead.

.. sidebar:: Prescribed Automation

    **CodeDeploy Service Role**: The AWS CodeDeploy service needs a Service Role that it is allowed to
    assume to allow the service to run in your AWS Account. Paco will automatically create such a service
    role for every CodeDeploy Application.

.. code-block:: yaml
    :caption: Example CodeDeployApplication resource YAML

    type: CodeDeployApplication
    order: 40
    compute_platform: "Server"
    deployment_groups:
      deployment:
        title: "My Deployment Group description"
        ignore_application_stop_failures: true
        revision_location_s3: paco.ref netenv.mynet.applications.app.groups.deploybucket
        autoscalinggroups:
          - paco.ref netenv.mynet.applications.app.groups.web

It can be convienent to install the CodeDeploy agent on your instances using CloudFormationInit.

.. code-block:: yaml
    :caption: Example ASG configuration for cfn_init to install CodeDeploy agent

    launch_options:
      cfn_init_config_sets:
        - "InstallCodeDeploy"
    cfn_init:
      config_sets:
        InstallCodeDeploy:
          - "InstallCodeDeploy"
      files:
        "/tmp/install_codedeploy.sh":
          source: https://aws-codedeploy-us-west-2.s3.us-west-2.amazonaws.com/latest/install
          mode: '000700'
          owner: root
          group: root
      commands:
        01_install_codedeploy:
          command: "/tmp/install_codedeploy.sh auto > /var/log/cfn-init-codedeploy.log 2>&1"
      services:
        sysvinit:
          codedeploy-agent:
            enabled: true
            ensure_running: true

"""
    compute_platform = schema.TextLine(
        title="Compute Platform",
        description="Must be one of Lambda, Server or ECS",
        constraint=isValidCodeDeployComputePlatform,
        required=True
    )
    deployment_groups = schema.Object(
        title="CodeDeploy Deployment Groups",
        schema=ICodeDeployDeploymentGroups,
        required=True,
    )

class IEFS(IResource):
    """
AWS Elastic File System (EFS) resource.

.. code-block:: yaml
    :caption: Example EFS resource YAML

    type: EFS
    order: 20
    enabled: true
    encrypted: false
    segment: private
    security_groups:
      - paco.ref netenv.mynet.network.vpc.security_groups.cloud.content

    """
    encrypted = schema.Bool(
        title='Encryption at Rest',
        default=False
    )
    security_groups = schema.List(
        title="Security groups",
        description="`SecurityGroup`_ the EFS belongs to",
        value_type=PacoReference(
            title="Paco reference",
            schema_constraint='ISecurityGroup'
        ),
        required=True,
    )
    segment = schema.TextLine(
        title="Segment",
        description="",
        required=False,
    )

# AWS Backup

class IBackupPlanRule(INamed):
    schedule_expression = schema.TextLine(
        title="Schedule Expression",
        description="Must be a valid Schedule Expression.",
        required=False
    )
    lifecycle_delete_after_days = schema.Int(
        title="Delete after days",
        required=False,
        min=1
    )
    lifecycle_move_to_cold_storage_after_days = schema.Int(
        title="Move to cold storage after days",
        description="If Delete after days value is set, this value must be smaller",
        required=False,
        min=1
    )

class IBackupSelectionConditionResourceType(IParent):
    condition_type = schema.TextLine(
        title="Condition Type",
        description="String Condition operator must be one of: StringEquals, StringNotEquals, StringEqualsIgnoreCase, StringNotEqualsIgnoreCase, StringLike, StringNotLike.",
        required=True,
        constraint=isValidStringConditionOperator
    )
    condition_key = schema.TextLine(
        title="Tag Key",
        required=True,
        min_length=1
    )
    condition_value = schema.TextLine(
        title="Tag Value",
        required=True,
        min_length=1
    )

class IBackupPlanSelection(IParent):
    title=schema.TextLine(
        title="Title",
        default="",
        required=True,
    )
    tags = schema.List(
        title="List of condition resource types",
        required=False,
        value_type=schema.Object(IBackupSelectionConditionResourceType)
    )
    resources = schema.List(
        title="Backup Plan Resources",
        value_type=PacoReference(
            title="Resource",
            schema_constraint='Interface'
        ),
        required=False,
    )

class IBackupPlan(IResource):
    """
AWS Backup Plan
    """
    plan_rules = schema.List(
        title="Backup Plan Rules",
        value_type=schema.Object(IBackupPlanRule),
        required=True,
    )
    selections = schema.List(
        title="Backup Plan Selections",
        value_type=schema.Object(IBackupPlanSelection),
        required=False
    )

class IBackupPlans(INamed, IMapping):
    """
Container for `BackupPlan`_ objects.
    """
    taggedValue('contains', 'IBackupPlan')

class IBackupVault(IResource):
    """
An AWS Backup Vault.
    """
    notification_events = schema.List(
        title="Notification Events",
        description="Each notification event must be one of BACKUP_JOB_STARTED, BACKUP_JOB_COMPLETED, RESTORE_JOB_STARTED, RESTORE_JOB_COMPLETED, RECOVERY_POINT_MODIFIED",
        value_type=schema.TextLine(
            title="Notification Event"
        ),
        constraint=isValidBackupNotification,
        required=False
    )
    notification_group = schema.TextLine(
        title="Notification Group",
        required=False
    )
    plans = schema.Object(
        title="Backup Plans",
        schema=IBackupPlans,
        required=False
    )

class IBackupVaults(INamed, IMapping):
    """
Container for `BackupVault` objects.
    """
    taggedValue('contains', 'IBackupVault')

