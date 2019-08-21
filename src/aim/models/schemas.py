from zope.interface import Interface, Attribute, invariant, Invalid
from zope.interface.common.mapping import IMapping
from zope.interface.common.sequence import ISequence
from zope import schema
from zope.schema.fieldproperty import FieldProperty
from aim.models import vocabulary
from aim.models.references import TextReference
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

class InvalidHealthCheckTypeError(schema.ValidationError):
    __doc__ = 'Not a valid health check type (can only be EC2 or ELB).'

def isValidHealthCheckType(value):
    if value not in ('EC2', 'ELB'):
        raise InvalidHealthCheckTypeError
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

class InvalidPeriod(schema.ValidationError):
    __doc__ = 'Period must be one of: 10, 30, 60, 300, 900, 3600, 21600, 90000'

def isValidPeriod(value):
    """
    CloudWatch Period is limited to fixed intervals.
    These are the same intervals offered by the AWS Console.
    If you want to allow another value, need to ensrue the CloudWatchAlarm class
    can represent a human-readable value of it.
    """
    if value not in (10, 30, 60, 300, 900, 3600, 21600, 90000):
        raise InvalidPeriod
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
# Here be Schemas!
#

class INamed(Interface):
    """
    A locatable resource
    """
    __parent__ = Attribute("Object reference to the parent in the object hierarchy")
    name = schema.TextLine(
        title="Name",
        default=""
    )
    title = schema.TextLine(
        title="Title",
        default="",
        required=False
    )

class IDeployable(Interface):
    enabled = schema.Bool(
        title="Enabled",
        description = "Could be deployed to AWS",
        default=False
    )

class IName(Interface):
    """
    A resource which has a name but is not locatable
    """
    name = schema.TextLine(
        title="Name",
        default=""
    )


class ITextReference(Interface):
    """A field containing a reference an aim model object or attribute"""
    pass
# work around a circular import
from zope.interface import classImplements
classImplements(TextReference, ITextReference)

class IAdminIAMUser(IDeployable):
    """An AWS Account Administerator IAM User"""
    username = schema.TextLine(
        title = "IAM Username",
        default = ""
    )

class IAccounts(IMapping):
    "Collection of Accounts"
    pass

class IAccount(INamed):
    "Cloud account information"
    account_type = schema.TextLine(
        title = "Account Type",
        description = "Supported types: 'AWS'",
        default = "AWS"
    )
    account_id = schema.TextLine(
        title = "Account ID",
        description = "Can only contain digits.",
        required = True,
        constraint = isOnlyDigits
    )
    admin_delegate_role_name = schema.TextLine(
        title = "Administrator delegate IAM Role name for the account",
        description = "",
        default = ""
    )
    is_master = schema.Bool(
        title = "Boolean indicating if this a Master account",
        default = False
    )
    region = schema.TextLine(
        title = "Region to install AWS Account specific resources",
        default = "no-region-set",
        missing_value = "no-region-set",
        required = True,
        description = 'Must be a valid AWS Region name',
        constraint = isValidAWSRegionName
    )
    root_email = schema.TextLine(
        title = "The email address for the root user of this account",
        required = True,
        description = 'Must be a valid email address.',
        constraint = isValidEmail
    )
    organization_account_ids = schema.List(
        title = "A list of account ids to add to the Master account's AWS Organization",
        value_type = schema.TextLine(),
        required = False,
        default = [],
        description = 'Each string in the list must contain only digits.'
    )
    admin_iam_users = schema.Dict(
        title="Admin IAM Users",
        value_type = schema.Object(IAdminIAMUser),
        required = False
    )


class ISecurityGroupRule(IName):

    @invariant
    def cidr_v4_or_v6(obj):
        if obj.cidr_ip == '' and obj.cidr_ip_v6 == '' and not getattr(obj, 'source_security_group', None):
            raise Invalid("cidr_ip, cidr_ip_v6 and source_security_group can not all be blank")

    cidr_ip = schema.TextLine(
        title = "CIDR IP",
        default = "",
        description = "A valid CIDR v4 block or an empty string",
        constraint = isValidCidrIpv4orBlank
    )
    cidr_ip_v6 = schema.TextLine(
        title = "CIDR IP v6",
        description = "A valid CIDR v6 block or an empty string",
        default = ""
    )
    description = schema.TextLine(
        title = "Description",
        default = "",
        description = "Max 255 characters. Allowed characters are a-z, A-Z, 0-9, spaces, and ._-:/()#,@[]+=;{}!$*."
    )
    from_port = schema.Int(
        title = "From port",
        description = "A value of -1 indicates all ICMP/ICMPv6 types. If you specify all ICMP/ICMPv6 types, you must specify all codes.",
        default = -1
    )
    protocol = schema.TextLine(
        title = "IP Protocol",
        description = "The IP protocol name (tcp, udp, icmp, icmpv6) or number."
    )
    to_port = schema.Int(
        title = "To port",
        description = "A value of -1 indicates all ICMP/ICMPv6 types. If you specify all ICMP/ICMPv6 types, you must specify all codes.",
        default = -1
    )
    source_security_group = TextReference(
        title = "Source Security Group Reference",
        required = False,
        description = "An AIM Reference to a SecurityGroup"
    )

class IIngressRule(ISecurityGroupRule):
    "Security group ingress"

class IEgressRule(ISecurityGroupRule):
    "Security group egress"

class ISecurityGroup(Interface):
    """
    AWS Resource: Security Group
    """
    group_name = schema.TextLine(
        title = "Group name",
        default = "",
        description = "Up to 255 characters in length. Cannot start with sg-."
    )
    group_description = schema.TextLine(
        title = "Group description",
        default = "",
        description = "Up to 255 characters in length"
    )
    ingress = schema.List(
        title = "Ingress",
        value_type=schema.Object(schema=IIngressRule),
        default = [],
        description = "Every list item must be an IngressRule"
    )
    egress = schema.List(
        title = "Egress",
        value_type=schema.Object(schema=IEgressRule),
        default = [],
        description = "Every list item must be an EgressRule"
    )


class IApplicationEngines(INamed, IMapping):
    "A collection of Application Engines"
    pass

class IResource(INamed, IDeployable):
    """
    AWS Resource to support an Application
    """
    type = schema.TextLine(
        title = "Type of Resources",
        description = "A valid AWS Resource type: ASG, LBApplication, etc."
    )
    resource_name = schema.TextLine(
        title = "AWS Resource Name",
        description = "",
        default = ""
    )
    resource_fullname = schema.TextLine(
        title = "AWS Resource Fullname",
        description = "",
        default = ""
    )
    order = schema.Int(
        title = "The order in which the resource will be deployed",
        description = "",
        min = 0,
        default = 0,
        required = False
    )


class IServiceAccountRegion(Interface):
    "An account and region for a service"
    account = TextReference(
        title = "Account Reference",
        required = False
    )
    region = schema.TextLine(
        title = "AWS Region",
        description = "Must be a valid AWS Region name",
        default = "no-region-set",
        missing_value = "no-region-set",
        required = True,
        constraint = isValidAWSRegionName
    )

class IServiceEnvironment(IServiceAccountRegion, INamed):
    "A service composed of one or more applications"
    applications = schema.Object(
        title = "Applications",
        schema = IApplicationEngines,
    )

class IResources(INamed, IMapping):
    "A collection of Application Resources"
    pass

class IResourceGroup(INamed, IMapping):
    "A collection of Application Resources"
    title = schema.TextLine(
        title="Title",
        default = ""
    )
    type = schema.TextLine(
        title="Type"
    )
    order = schema.Int(
        title = "The order in which the group will be deployed",
        description = "",
        min = 1,  # 0 is loading ad NoneType
        required = True
    )
    resources = schema.Object(schema=IResources)


class IResourceGroups(INamed, IMapping):
    "A collection of Application Resource Groups"
    pass

# Alarm and notification schemas

class IAlarmNotifications(IMapping):
    """
    Alarm Notifications
    """

class IAlarmNotification(Interface):
    """
    Alarm Notification
    """
    groups = schema.List(
        title = "List of groups",
        value_type=schema.TextLine(
            title="Group"
        ),
        required = True
    )
    classification = schema.TextLine(
        title = "Classification filter",
        description = "Must be one of: 'performance', 'security', 'health' or ''.",
        constraint = isValidAlarmClassificationFilter,
        default = ''
    )
    severity = schema.TextLine(
        title = "Severity filter",
        constraint = isValidAlarmSeverityFilter,
        description = "Must be one of: 'low', 'critical'"
    )

class INotifiable(Interface):
    """
    A notifiable object
    """
    notifications = schema.Object(
        title = "Alarm Notifications",
        schema = IAlarmNotifications,
    )

class IAlarmSet(INamed, IMapping, INotifiable):
    """
    A collection of Alarms
    """
    resource_type = schema.TextLine(
        title = "Resource type",
        description = "Must be a valid AWS resource type"
    )


class IAlarmSets(INamed, IMapping):
    """
    A collection of AlarmSets
    """

class IDimension(Interface):
    """
    A dimension of a metric
    """
    name = schema.TextLine(
        title = "Dimension name"
    )
    value = schema.TextLine(
        title = "Value to look-up dimension"
    )

class IAlarm(INamed, IDeployable, IName, INotifiable):
    """
    An Alarm
    """
    classification = schema.TextLine(
        title = "Classification",
        description = "Must be one of: 'performance', 'security' or 'health'",
        constraint = isValidAlarmClassification,
        required = True,
        default = 'unset',
        missing_value = 'unset'
    )
    description = schema.TextLine(
        title = "Description",
    )
    notification_groups = schema.List(
        readonly = True,
        title = "List of notificationn groups the alarm is subscribed to.",
        value_type=schema.TextLine(title="Notification group name")
    )
    runbook_url = schema.TextLine(
        title = "Runbook URL",
    )
    severity = schema.TextLine(
        title = "Severity",
        default = "low",
        constraint = isValidAlarmSeverity,
        description = "Must be one of: 'low', 'critical'"
    )

class ICloudWatchAlarm(IAlarm):
    """
    A CloudWatch Alarm
    """
    comparison_operator = schema.TextLine(
        title = "Comparison operator",
        constraint = isComparisonOperator,
        description = "Must be one of: 'GreaterThanThreshold','GreaterThanOrEqualToThreshold', 'LessThanThreshold', 'LessThanOrEqualToThreshold'"
    )
    dimensions = schema.List(
        title = "Dimensions",
        value_type = schema.Object(schema=IDimension),
        default = []
    )
    evaluate_low_sample_count_percentile = schema.TextLine(
        title = "Evaluate low sample count percentile"
    )
    evaluation_periods = schema.Int(
        title = "Evaluation periods"
    )
    extended_statistic = schema.TextLine(
        title = "Extended statistic"
    )
    metric_name = schema.TextLine(
        title = "Metric name",
        required = True
    )
    namespace = schema.TextLine(
        title = "Namespace"
    )
    period = schema.Int(
        title = "Period in seconds",
        constraint = isValidPeriod,
        description = "Must be one of: 10, 30, 60, 300, 900, 3600, 21600, 90000"
    )
    statistic = schema.TextLine(
        title = "Statistic"
    )
    threshold = schema.Float(
        title = "Threshold"
    )
    treat_missing_data = schema.TextLine(
        title = "Treat missing data"
    )

class INotificationGroups(IServiceAccountRegion):
    "Container for Notification Groups"

# Logging schemas

class ICloudWatchLogRetention(Interface):
    expire_events_after_days = schema.TextLine(
        title = "Expire Events After. Retention period of logs in this group",
        description = "",
        default = "",
        constraint = isValidCloudWatchLogRetention
    )

class ICloudWatchLogSources(INamed, IMapping):
    """
    A collection of Log Sources
    """

class ICloudWatchLogSource(INamed, ICloudWatchLogRetention):
    """
    Log source for a CloudWatch agent
    """
    encoding = schema.TextLine(
        title = "Encoding",
        default = "utf-8"
    )
    log_stream_name = schema.TextLine(
        title = "Log stream name",
        description = "CloudWatch Log Stream name",
        default = ""
    )
    multi_line_start_pattern = schema.Text(
        title = "Multi-line start pattern",
        default = ""
    )
    path = schema.TextLine(
        title = "Path",
        default = "",
        required = True,
        description = "Must be a valid filesystem path expression. Wildcard * is allowed."
    )
    timestamp_format = schema.TextLine(
        title = "Timestamp format",
        default = "",
    )
    timezone = schema.TextLine(
        title = "Timezone",
        default = "Local",
        constraint = isValidCWAgentTimezone,
        description = "Must be one of: 'Local', 'UTC'"
    )

class IMetricTransformation(Interface):
    """
    Metric Transformation
    """
    default_value = schema.Float(
        title = "The value to emit when a filter pattern does not match a log event.",
        required = False,
    )
    metric_name = schema.TextLine(
        title = "The name of the CloudWatch Metric.",
        required = True,
    )
    metric_namespace = schema.TextLine(
        title = "The namespace of the CloudWatch metric.",
        required = True,
        max_length = 255,
    )
    metric_value = schema.TextLine(
        title = "The value that is published to the CloudWatch metric.",
        required = True,
    )

class IMetricFilters(INamed, IMapping):
    """
    Metric Filters
    """

class IMetricFilter(INamed):
    """
    Metric filter
    """
    filter_pattern = schema.Text(
        title = "Filter pattern",
        default = ""
    )
    metric_transformations = schema.List(
        title = "Metric transformations",
        value_type=schema.Object(
            title="Metric Transformation",
            schema=IMetricTransformation
        ),
        default = []
    )

class ICloudWatchLogGroups(INamed, IMapping):
    """
    A collection of Log Group objects
    """

class ICloudWatchLogGroup(INamed, ICloudWatchLogRetention):
    """
    A CloudWatchLogGroup is responsible for retention, access control and metric filters
    """
    metric_filters = schema.Object(
        title = "Metric Filters",
        schema = IMetricFilters
    )
    sources = schema.Object(
        title = "A CloudWatchLogSources container",
        schema = ICloudWatchLogSources
    )
    log_group_name = schema.TextLine(
        title = "Log group name. Can override the LogGroup name used from the name field.",
        description = "",
        default = ""
    )

class ICloudWatchLogSets(INamed, IMapping):
    """
    A collection of information about logs to collect.
    A mapping of ILogSet objects.
    """

class ICloudWatchLogSet(INamed, ICloudWatchLogRetention, IMapping):
    """
    A set of Log Group objects
    """
    log_groups = schema.Object(
        title = "A CloudWatchLogGroups container",
        schema = ICloudWatchLogGroups
    )

class ICloudWatchLogging(INamed, ICloudWatchLogRetention):
    """
    CloudWatch Logging configuration
    """
    log_sets = schema.Object(
        title = "A CloudWatchLogSets container",
        schema = ICloudWatchLogSets
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
        title = "Metric(s) group name"
    )
    measurements = schema.List(
        title = "Measurements",
        value_type=schema.TextLine(title="Metric measurement name")
    )
    collection_interval = schema.Int(
        title = "Collection interval",
        description = "",
        min = 1,
        required=False
    )

class IMonitorConfig(IDeployable, INamed, INotifiable):
    """
    A set of metrics and a default collection interval
    """
    collection_interval = schema.Int(
        title = "Collection interval",
        min = 1,
        default=60
    )
    metrics = schema.List(
        title = "Metrics",
        value_type=schema.Object(IMetric),
        default = []
    )
    asg_metrics = schema.List(
        title = "ASG Metrics",
        value_type=schema.TextLine(),
        default= [],
        constraint = isValidASGMetricNames,
        description = "Must be one of: 'GroupMinSize', 'GroupMaxSize', 'GroupDesiredCapacity', 'GroupInServiceInstances', 'GroupPendingInstances', 'GroupStandbyInstances', 'GroupTerminatingInstances', 'GroupTotalInstances'"
    )
    alarm_sets = schema.Object(
        title="Sets of Alarm Sets",
        schema=IAlarmSets,
    )
    log_sets = schema.Object(
        title="Sets of Log Sets",
        schema=ICloudWatchLogSets,
    )


class IMonitorable(Interface):
    """
    A monitorable resource
    """
    monitoring = schema.Object(
        schema = IMonitorConfig,
        required = False
    )

class IS3BucketPolicy(Interface):
    """
    S3 Bucket Policy
    """
    action = schema.List(
        title="List of Actions",
        value_type=schema.TextLine(
            title="Action"
        ),
        required = True
    )
    aws = schema.List(
        title = "List of AWS Principles.",
        description = "Either this field or the principal field must be set.",
        value_type = schema.TextLine(
            title = "AWS Principle"
        ),
        default = [],
        required = False
    )
    condition = schema.Dict(
        title = "Condition",
        description = 'Each Key is the Condition name and the Value must be a dictionary of request filters. e.g. { "StringEquals" : { "aws:username" : "johndoe" }}',
        default = {},
        required = False,
        # ToDo: add a constraint to check for valid conditions. This is a pretty complex constraint though ...
        # https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition.html
    )
    principal = schema.Dict(
        title = "Prinicpals",
        description = "Either this field or the aws field must be set. Key should be one of: AWS, Federated, Service or CanonicalUser. Value can be either a String or a List.",
        default = {},
        required = False
    )
    effect = schema.TextLine(
        title="Effect",
        default="Deny",
        required = True,
        description = "Must be one of: 'Allow', 'Deny'"
    )
    resource_suffix = schema.List(
        title="List of AWS Resources Suffixes",
        value_type=schema.TextLine(
            title="Resources Suffix"
        ),
        required = True
    )
    @invariant
    def aws_or_principal(obj):
        if obj.aws == [] and obj.principal == {}:
            raise Invalid("Either the aws or the principal field must not be blank.")
        if obj.aws != [] and obj.principal != {}:
            raise Invalid("Can not set bot the aws and the principal fields.")


class IS3Bucket(IResource, IDeployable):
    """
    S3 Bucket : A template describing an S3 Bbucket
    """
    bucket_name = schema.TextLine(
        title = "Bucket Name",
        description = "A short unique name to assign the bucket.",
        default = "",
        required = True
    )
    account = TextReference(
        title = "Account Reference"
    )
    deletion_policy = schema.TextLine(
        title = "Bucket Deletion Policy",
        default = "delete",
        required = False
    )
    policy = schema.List(
        title="List of S3 Bucket Policies",
        description="",
        value_type=schema.Object(IS3BucketPolicy),
        default=[]
    )
    region = schema.TextLine(
        title = "Bucket region",
        default = None,
        required = False
    )
    cloudfront_origin = schema.Bool(
        title = "Creates and listens for a CloudFront Access Origin Identity",
        required = False,
        default = False
    )
    external_resource = schema.Bool(
        title='Boolean indicating whether the S3 Bucket already exists or not',
        default = False
    )

class IS3Resource(INamed):
    """
    EC2 Resource Configuration
    """
    buckets = schema.Dict(
        title = "Group of EC2 Key Pairs",
        value_type = schema.Object(IS3Bucket),
        default = {}
    )

class IApplicationEngine(INamed, IDeployable, INotifiable):
    """
    Application Engine : A template describing an application
    """
    groups = schema.Object(IResourceGroups)


class IApplication(IApplicationEngine, IMapping):
    """
    Application : An Application Engine configuration to run in a specific Environment
    """

#class IDeployment(IResource):
#    """
#    An application deployment
#    """

class ICodePipeBuildDeploy(IResource):
    """
    Code Pipeline: Build and Deploy
    """
    deployment_environment = schema.TextLine(
        title = "Deployment Environment",
        description = "",
        default = ""
    )
    deployment_branch_name = schema.TextLine(
        title = "Deployment Branch Name",
        description = "",
        default = ""
    )
    manual_approval_enabled = schema.Bool(
        title = "Manual approval enabled",
        description = "",
        default = False
    )
    manual_approval_notification_email = schema.TextLine(
        title = "Manual approval notification email",
        description = "",
        default = ""
    )
    codecommit_repository = TextReference(
        title = 'CodeCommit Respository'
    )
    asg = TextReference(
        title = "ASG Reference"
    )
    auto_rollback_enabled = schema.Bool(
        title = "Automatic rollback enabled",
        description = "",
        default = True
    )
    deploy_config_type = schema.TextLine(
        title = "Deploy Config Type",
        description = "",
        default = "HOST_COUNT"
    )
    deploy_style_option = schema.TextLine(
        title = "Deploy Style Option",
        description = "",
        default = "WITH_TRAFFIC_CONTROL"
    )
    deploy_config_value = schema.Int(
        title = "Deploy Config Value",
        description = "",
        default = 0
    )
    deploy_instance_role = TextReference(
        title = "Deploy Instance Role Reference"
    )
    elb_name = schema.TextLine(
        title = "ELB Name",
        description = "",
        default = ""
    )
    alb_target_group = TextReference(
        title = "ALB Target Group Reference"
    )
    tools_account = TextReference(
        title = "Tools Account Reference"
    )
    data_account = TextReference(
        title = "Data Account Reference"
    )
    cross_account_support = schema.Bool(
        title = "Cross Account Support",
        description = "",
        default = False
    )
    artifacts_bucket = TextReference(
        title = "Artifacts S3 Bucket Reference",
        description=""
    )

class IEC2KeyPair(INamed):
    """
    EC2 SSH Key Pair
    """
    region = schema.TextLine(
        title = "AWS Region",
        description = "Must be a valid AWS Region name",
        default = "no-region-set",
        missing_value = "no-region-set",
        required = True,
        constraint = isValidAWSRegionName
        )
    account = TextReference(
        title = 'AWS Account Reference'
    )

class IEC2Resource(Interface):
    """
    EC2 Resource Configuration
    """
    keypairs = schema.Dict(
        title = "Group of EC2 Key Pairs",
        value_type = schema.Object(IEC2KeyPair)
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
        default=False
    )
    instance_iam_profile = Attribute("Instance IAM Profile")
    instance_ami = schema.TextLine(
        title="Instance AMI",
        description="",
    )
    instance_key_pair = TextReference(
        title = "Instance key pair reference",
        description=""
    )
    instance_type = schema.TextLine(
        title = "Instance type",
        description="",
    )
    segment = schema.TextLine(
        title="Segment",
        description="",
    )
    security_groups = schema.List(
        title="Security groups",
        description="",
        value_type=TextReference(
            title="AIM Reference"
        )
    )
    root_volume_size_gb = schema.Int(
        title="Root volume size GB",
        description="",
        default=8,
        min=8
    )
    disable_api_termination = schema.Bool(
        title="Disable API Termination",
        description="",
        default=False
    )
    private_ip_address = schema.TextLine(
        title="Private IP Address",
        description=""
    )
    user_data_script = schema.Text(
        title="User data script",
        description="",
        default=""
    )


class INetworkEnvironments(INamed, IMapping):
    """
    A collection of NetworkEnvironments
    """
    pass

class IProject(INamed, IMapping):
    "Project : the root node in the config for an AIM Project"
    aim_project_version = schema.TextLine(
        title = "AIM Project version",
        default = ""
    )

class IInternetGateway(IDeployable):
    """
    AWS Resource: IGW
    """

class INATGateway(IDeployable, IMapping):
    """
    AWS Resource: NAT Gateway
    """
    availability_zone = schema.Int(
        title="Availability Zone",
        description = "",
    )
    segment = schema.TextLine(
        title="Segment",
        description = "",
        default="public"
    )
    default_route_segments = schema.List(
        title="Default Route Segments",
        description = "",
        default=[]
    )

class IVPNGateway(IDeployable, IMapping):
    """
    AWS Resource: VPN Gateway
    """

class IPrivateHostedZone(IDeployable):
    """
    AWS Resource: Private Hosted Zone
    """
    name = schema.TextLine(
        title = "Hosted zone name"
    )

class ISegment(IDeployable):
    """
    AWS Resource: Segment
    """
    internet_access = schema.Bool(
        title = "Internet Access",
        default = False
    )
    az1_cidr = schema.TextLine(
        title = "Availability Zone 1 CIDR",
        default = ""
    )
    az2_cidr = schema.TextLine(
        title = "Availability Zone 2 CIDR",
        default = ""
    )
    az3_cidr = schema.TextLine(
        title = "Availability Zone 3 CIDR",
        default = ""
    )
    az4_cidr = schema.TextLine(
        title = "Availability Zone 4 CIDR",
        default = ""
    )
    az5_cidr = schema.TextLine(
        title = "Availability Zone 5 CIDR",
        default = ""
    )
    az6_cidr = schema.TextLine(
        title = "Availability Zone 6 CIDR",
        default = ""
    )

class IVPCPeeringRoute(Interface):
    """
    VPC Peering Route
    """
    segment = TextReference(
        title = "Segment reference"
    )
    cidr = schema.TextLine(
        title = "CIDR IP",
        default = "",
        description = "A valid CIDR v4 block or an empty string",
        constraint = isValidCidrIpv4orBlank
    )

class IVPCPeering(INamed, IDeployable):
    """
    VPC Peering
    """
    # peer_* is used when peering with an external VPC
    peer_role_name = schema.TextLine(
        title = 'Remote peer role name',
        required = False
    )
    peer_vpcid = schema.TextLine(
        title = 'Remote peer VPC Id',
        required = False
    )
    peer_account_id = schema.TextLine(
        title = 'Remote peer AWS account Id',
        required = False
    )
    peer_region = schema.TextLine(
        title = 'Remote peer AWS region',
        required = False
    )
    # network_environment is used when peering with a network environment
    # local to the project.
    network_environment = TextReference(
        title = 'Network Environment Reference',
        required = False
    )
    # Routes forward traffic to the peering connection
    routing = schema.List(
        title = "Peering routes",
        value_type = schema.Object(IVPCPeeringRoute),
        required = True
    )


class IVPC(Interface):
    """
    AWS Resource: VPC
    """
    cidr = schema.TextLine(
        title = "CIDR",
        description = "",
        default = ""
    )
    enable_dns_hostnames = schema.Bool(
        title = "Enable DNS Hostnames",
        description = "",
        default = False
    )
    enable_dns_support = schema.Bool(
        title="Enable DNS Support",
        description = "",
        default = False
    )
    enable_internet_gateway = schema.Bool(
        title = "Internet Gateway",
        description = "",
        default = False
    )
    nat_gateway = schema.Dict(
        title = "NAT Gateway",
        description = "",
        value_type = schema.Object(INATGateway),
        required = True,
        default = {}

    )
    vpn_gateway = schema.Dict(
        title = "VPN Gateway",
        description = "",
        value_type = schema.Object(IVPNGateway),
        required = True,
        default = {}
    )
    private_hosted_zone = schema.Object(
        title = "Private hosted zone",
        description = "",
        schema = IPrivateHostedZone
    )
    security_groups = schema.Dict(
        # This is a dict of dicts ...
        title = "Security groups",
        default = {},
        description = "Two level deep dictionary: first key is Application name, second key is Resource name."
    )
    segments = schema.Dict(
        title="Segments",
        value_type = schema.Object(ISegment),
        required = False
    )
    peering = schema.Dict(
        title = 'VPC Peering',
        value_type = schema.Object(IVPCPeering),
        required = False
    )

class INetworkEnvironment(INamed, IDeployable, IMapping):
    """
    Network Environment : A template for a Network Environment
    """
    availability_zones = schema.Int(
        title="Availability Zones",
        description = "",
        default=0
    )
    vpc = schema.Object(
        title = "VPC",
        description = "",
        schema=IVPC,
        required=False
    )

class ICredentials(INamed):
    aws_access_key_id = schema.TextLine(
        title = "AWS Access Key ID",
        description = "",
        default = ""
        )
    aws_secret_access_key = schema.TextLine(
        title = "AWS Secret Access Key",
        description = "",
        default = ""
        )
    aws_default_region = schema.TextLine(
        title = "AWS Default Region",
        description = "Must be a valid AWS Region name",
        default = "no-region-set",
        missing_value = "no-region-set",
        required = True,
        constraint = isValidAWSRegionName
        )
    master_account_id = schema.TextLine(
        title = "Master AWS Account ID",
        description = "",
        default = ""
        )
    master_admin_iam_username = schema.TextLine(
        title = "Master Account Admin IAM Username",
        description = "",
        default = ""
        )

class INetwork(INetworkEnvironment):
    aws_account = TextReference(
        title = 'AWS Account Reference'
    )

class IAWSCertificateManager(IResource):
    domain_name = schema.TextLine(
        title = "Domain Name",
        description = "",
        default = ""
    )
    subject_alternative_names = schema.List(
        title = "Subject alternative names",
        description = "",
        value_type=schema.TextLine(
            title="alternative name"
        )
    )

class IPortProtocol(Interface):
    """Port and Protocol"""
    port = schema.Int(
        title = "Port"
    )
    protocol = schema.Choice(
        title="Protocol",
        vocabulary=vocabulary.target_group_protocol
    )

class ITargetGroup(IPortProtocol, IResource):
    """Target Group"""
    health_check_interval = schema.Int(
        title = "Health check interval"
    )
    health_check_timeout = schema.Int(
        title = "Health check timeout"
    )
    healthy_threshold = schema.Int(
        title = "Healthy threshold"
    )
    unhealthy_threshold = schema.Int(
        title = "Unhealthy threshold"
    )
    health_check_http_code = schema.Int(
        title = "Health check HTTP code"
    )
    health_check_path = schema.TextLine(
        title = "Health check path",
        default = "/"
    )
    connection_drain_timeout = schema.Int(
        title = "Connection drain timeout"
    )

class IListenerRule(IDeployable):
    rule_type = schema.TextLine(
        title = "Type of Rule"
    )
    priority = schema.Int(
        title="Forward condition priority",
        required=False,
        default=1
    )
    host = schema.TextLine(
        title = "Host header value"
    )
    # Redirect Rule Variables
    redirect_host = schema.TextLine(
        title="The host to redirect to",
        required=False
    )
    # Forward Rule Variables
    target_group = schema.TextLine(
        title="Target group name",
        required=False
    )

class IListener(IPortProtocol):
    redirect = schema.Object(
        title = "Redirect",
        schema=IPortProtocol,
        required=False
    )
    ssl_certificates = schema.List(
        title = "List of SSL certificate References",
        value_type = TextReference(
            title = "SSL Certificate Reference"
        ),
        required=False,
        default = []
    )
    target_group = schema.TextLine(
        title = "Target group",
        default = "",
        required=False
    )
    rules = schema.Dict(
        title = "Container of listener rules",
        value_type = schema.Object(IListenerRule),
        required=False,
        default=None
    )

class IDNS(Interface):
    hosted_zone = TextReference(
        title = "Hosted Zone Id Reference",
    )
    domain_name = TextReference(
        title = "Domain name",
        required = False,
        str_ok = True
     )
    ssl_certificate = TextReference(
        title = "SSL certificate Reference",
        required = False
    )

class ILBApplication(IResource, IMonitorable, IMapping):
    """Application Load Balancer"""
    target_groups = schema.Dict(
        title = "Target Groups",
        value_type=schema.Object(ITargetGroup)
    )
    listeners = schema.Dict(
        title = "Listeners",
        value_type=schema.Object(IListener)
    )
    dns = schema.List(
        title = "List of DNS for the ALB",
        value_type = schema.Object(IDNS),
        default = []
    )

    scheme = schema.Choice(
        title = "Scheme",
        vocabulary=vocabulary.lb_scheme
    )
    security_groups = schema.List(
        title = "Security Groups",
        value_type=TextReference(
            title="AIM Reference"
        )
    )
    segment = schema.TextLine(
        title = "Id of the segment stack"
    )

class IIAMs(INamed, IMapping):
    "Container for IAM Groups"

class IStatement(Interface):
    effect = schema.TextLine(
        title = "Effect",
        description = "Must be one of: 'Allow', 'Deny'",
        # ToDo: check constraint
        # constraint = vocabulary.iam_policy_effect
    )
    action = schema.List(
        title = "Action(s)",
        value_type=schema.TextLine(),
        default = []
    )
    resource =schema.List(
        title = "Resrource(s)",
        value_type=schema.TextLine(),
        default = []
    )

class IPolicy(Interface):
    name = schema.TextLine(
        title = "Policy name",
        default = ""
    )
    statement = schema.List(
        title = "Statements",
        value_type=schema.Object(
            title="Statement",
            schema=IStatement
        )
    )

class IAssumeRolePolicy(Interface):
    effect = schema.TextLine(
        title = "Effect",
        # ToDo: check constraint
        # constraint = vocabulary.iam_policy_effect
    )
    aws = schema.List(
        title = "List of AWS Principles",
        value_type=schema.TextLine(
            title="AWS Principle",
            default = "",
            required = False
        ),
        default = [],
        required = False
    )
    service = schema.List(
        title = "Service",
        value_type=schema.TextLine(
            title="Service",
            default = "",
            required = False
        ),
        default = [],
        required = False
    )
    # ToDo: what are 'aws' keys for? implement ...

class IRole(IDeployable):
    assume_role_policy = schema.Object(
        title = "Assume role policy",
        schema=IAssumeRolePolicy,
        required = False
    )
    instance_profile = schema.Bool(
        title = "Instance profile",
        default = False,
        required = False
    )
    path = schema.TextLine(
        title = "Path",
        default = "/",
        required = False
    )
    role_name = schema.TextLine(
        title = "Role name",
        default = "",
        required = False
    )
    policies = schema.List(
        title = "Policies",
        value_type=schema.Object(
            schema=IPolicy
        ),
        default = [],
        required = False
    )
    managed_policy_arns = schema.List(
        title = "Managed policy ARNs",
        value_type=schema.TextLine(
            title = "Managed policy ARN"
        ),
        default = [],
        required = False
    )
    max_session_duration = schema.Int(
        title = "Maximum session duration",
        description = "The maximum session duration (in seconds)",
        min = 3600,
        max = 43200,
        default = 3600,
        required = False
    )
    permissions_boundary = schema.TextLine(
        title = "Permissions boundary ARN",
        description = "Must be valid ARN",
        default = "",
        required = False
    )

#class IManagedPolicies(IMapping):
#    """
#    Container of IAM Managed Policices
#    """

class IManagedPolicy(INamed, IMapping):
    """
    IAM Managed Policy
    """

    roles = schema.List(
        title = "List of Role Names",
        value_type=schema.TextLine(
            title="Role Name"
        ),
        default = []
    )
    users = schema.List(
        title = "List of IAM Users",
        value_type=schema.TextLine(
            title = "IAM User name"
        ),
        default = []
    )
    statement = schema.List(
        title = "Statements",
        value_type=schema.Object(
            title="Statement",
            schema=IStatement
        )
    )
    path = schema.TextLine(
        title = "Path",
        default = "/",
        required = False
    )


class IIAM(INamed, IMapping):
    roles = schema.Dict(
        title = "Roles",
        value_type=schema.Object(
            title="Role",
            schema=IRole
        )
    )

    policies = schema.Dict(
        title = "Policies",
        value_type=schema.Object(
            title="ManagedPolicy",
            schema=IManagedPolicy
        )
    )

class IASG(IResource, IMonitorable):
    """
    Auto-scaling group
    """
    desired_capacity = schema.Int(
        title="Desired capacity",
        description="",
        default=1
    )
    min_instances = schema.Int(
        title="Minimum instances",
        description="",
        default=1
    )
    max_instances = schema.Int(
        title="Maximum instances",
        description="",
        default=2
    )
    update_policy_max_batch_size = schema.Int(
        title="Update policy maximum batch size",
        description="",
        default=1
    )
    update_policy_min_instances_in_service = schema.Int(
        title="Update policy minimum instances in service",
        description="",
        default=1
    )
    associate_public_ip_address = schema.Bool(
        title="Associate Public IP Address",
        description="",
        default=False
    )
    cooldown_secs = schema.Int(
        title="Cooldown seconds",
        description="",
        default=300
    )
    ebs_optimized = schema.Bool(
        title="EBS Optimized",
        description="",
        default=False
    )
    health_check_type = schema.TextLine(
        title="Health check type",
        description="Must be one of: 'EC2', 'ELB'",
        default='EC2',
        constraint = isValidHealthCheckType
    )
    health_check_grace_period_secs = schema.Int(
        title="Health check grace period in seconds",
        description="",
        default=300
    )
    instance_iam_role = schema.Object(IRole)
    instance_ami = TextReference(
        title="Instance AMI",
        description="",
        str_ok=True
    )
    instance_key_pair = TextReference(
        title = "Instance key pair reference",
        description=""
    )
    instance_type = schema.TextLine(
        title = "Instance type",
        description="",
        constraint = isValidInstanceSize
    )
    segment = schema.TextLine(
        title="Segment",
        description="",
    )
    termination_policies = schema.List(
        title="Terminiation policies",
        description="",
        value_type=schema.TextLine(
            title="Termination policy",
            description=""
        )
    )
    security_groups = schema.List(
        title="Security groups",
        description="",
        value_type=TextReference(
            title="AIM Reference"
        )
    )
    target_groups = schema.List(
        title="Target groups",
        description="",
        value_type=TextReference(
            title="AIM Reference"
        ),
        default = []
    )
    load_balancers = schema.List(
        title="Target groups",
        description="",
        value_type=TextReference(
            title="AIM Reference"
        ),
        default = []
    )
    termination_policies = schema.List(
        title="Termination policies",
        description="",
        value_type=schema.TextLine(
            title="Termination policy"
        )
    )
    user_data_script = schema.Text(
        title="User data script",
        description="",
        default=""
    )
    instance_monitoring =schema.Bool(
        title="Instance monitoring",
        description="",
        default=False
    )
    scaling_policy_cpu_average = schema.Int(
        title="Average CPU Scaling Polciy",
        # Default is 0 == disabled
        default=0,
        min=0,
        max=100
    )

class IEnvironmentDefault(INamed, IMapping):
    """
    Default values for an Environments configuration
    """

class IEnvironmentRegion(IEnvironmentDefault, IDeployable):
    """
    An actual deployed Environment in a specific region.
    May contains overrides of the IEnvironmentDefault where needed.
    """

class IEnvironment(INamed, IMapping):
    """
    Environment: Logical group of deployments
    """
    #default = schema.Object(IEnvironmentDefault)


class ILambdaVariable(Interface):
    """
    Lambda Environment Variable
    """
    key = schema.TextLine(
        title = 'Variable Name',
        required = True
    )
    value = TextReference(
        title = 'Variable Value',
        required = True,
        str_ok=True
    )

class ILambdaEnvironment(IMapping):
    """
    Lambda Environment
    """
    variables = schema.List(
        title = "Lambda Function Variables",
        value_type = schema.Object(ILambdaVariable),
        default = []
    )

class ILambdaFunctionCode(Interface):
    """The deployment package for a Lambda function."""
    s3_bucket = TextReference(
        title = "An Amazon S3 bucket in the same AWS Region as your function"
    )
    s3_key = schema.TextLine(
        title = "The Amazon S3 key of the deployment package."
    )

class ILambda(IResource, IMonitorable):
    """
    Lambda Function resource
    """
    code = schema.Object(
        title = "The function deployment package.",
        schema = ILambdaFunctionCode,
        required = True
    )
    description = schema.TextLine(
        title = "A description of the function.",
        required = True
    )
    environment = schema.Object(
        title = "Lambda Function Environment",
        schema = ILambdaEnvironment,
        default = None
    )
    iam_role = schema.Object(
        title = "The functions execution IAM role",
        required = True,
        schema = IRole
    )
    layers = schema.List(
        title = "Layers",
        value_type = schema.TextLine(),
        default = [],
        description = "Up to 5 Layer ARNs",
        constraint = isListOfLayerARNs
    )
    handler = schema.TextLine(
        title = "Function Handler",
        required = True
    )
    memory_size = schema.Int(
        title = "Function memory size (MB)",
        min = 128,
        max = 3008,
        default = 128
    )
    reserved_concurrent_executions = schema.Int(
        title = "Reserved Concurrent Executions",
        default = 0
    )
    runtime = schema.TextLine(
        title = "Runtime environment",
        required = True,
        # dotnetcore1.0 | dotnetcore2.1 | go1.x | java8 | nodejs10.x | nodejs8.10 | provided | python2.7 | python3.6 | python3.7 | ruby2.5
        default = 'python3.7'
    )
    # The amount of time that Lambda allows a function to run before stopping it. The default is 3 seconds. The maximum allowed value is 900 seconds.
    timeout = schema.Int(
        title = "Max function execution time in seconds.",
        description = "Must be between 0 and 900 seconds.",
        min = 0,
        max = 900,
    )
    sdb_cache = schema.Bool(
        title = "SDB Cache Domain",
        required=False,
        default=False
    )
    sns_topics = schema.List(
        title = "List of SNS Topic AIM Referenes",
        value_type =  TextReference(
            title = "SNS Topic AIM Reference",
            str_ok=True
        ),
        default = []
    )

class IRoute53HostedZone(IDeployable):
    """
    Route53 Hosted Zone
    """
    domain_name = schema.TextLine(
        title = "Domain Name",
        required = True
    )
    account = TextReference(
        title = "AWS Account Reference",
        required = True
    )

class IRoute53Resource(Interface):
    """
    Route53 Service Configuration
    """
    hosted_zones = schema.Dict(
        title = "Hosted Zones",
        value_type = schema.Object(IRoute53HostedZone),
        default = None
    )

class ICodeCommitUser(Interface):
    """
    CodeCommit User
    """
    username = schema.TextLine(
        title = "CodeCommit Username"
    )
    public_ssh_key = schema.TextLine(
        title = "CodeCommit User Public SSH Key",
        default = None,
        required = False
    )

class ICodeCommitRepository(INamed, IDeployable, IMapping):
    """
    CodeCommit Repository Configuration
    """
    repository_name = schema.TextLine(
        title = "Repository Name"
    )
    account = TextReference(
        title = "AWS Account Reference",
        required = True
    )
    region = schema.TextLine(
        title = "AWS Region"
    )
    description = schema.TextLine(
        title = "Repository Description"
    )
    users = schema.Dict(
        title = "CodeCommit Users",
        value_type = schema.Object(ICodeCommitUser),
        default = None
    )

class ICodeCommit(Interface):
    """
    CodeCommit Service Configuration
    """
    repository_groups = schema.Dict(
        title = "Group of Repositories",
        value_type = schema.Object(ICodeCommitRepository)
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
        title = "Notification protocol",
        default = "email",
        description = "Must be a valid SNS Topic subscription protocol: 'http', 'https', 'email', 'email-json', 'sms', 'sqs', 'application', 'lambda'.",
        constraint = isValidSNSSubscriptionProtocol
    )
    endpoint = TextReference(
        title = "SNS Topic Endpoint",
        str_ok = True
    )

class ISNSTopic(IResource):
    """
    SNS Topic Resource Configuration
    """
    display_name = schema.TextLine(
        title = "Display name for SMS Messages"
    )
    subscriptions = schema.List(
        title = "List of SNS Topic Subscriptions",
        value_type = schema.Object(ISNSTopicSubscription),
        default = []
    )

class ICloudTrail(IResource):
    """
    CloudTrail resource
    """
    accounts = schema.List(
        title = "Accounts to enable this CloudTrail in. Leave blank to assume all accounts.",
        description = "A list of references to AIM Accounts.",
        value_type = TextReference(
            title = "Account Reference",
        ),
        default = []
    )
    cloudwatchlogs_log_group = TextReference(
        title = "A CloudWatch Logs LogGroup to deliver this trail to.",
        required = False
    )
    enable_kms_encryption = schema.Bool(
        title = "Enable KMS Key encryption",
        default = False
    )
    enable_log_file_validation = schema.Bool(
        title = "Enable log file validation",
        default = True
    )
    include_global_service_events = schema.Bool(
        title = "Include global service events",
        default = True
    )
    is_multi_region_trail = schema.Bool(
        title = "Is multi-region trail?",
        default = True
    )
    region = schema.TextLine(
        title = "Region to create the CloudTrail",
        default = "",
        description = 'Must be a valid AWS Region name or empty string',
        constraint = isValidAWSRegionNameOrNone
    )
    s3_key_prefix = schema.TextLine(
        title = "S3 Key Prefix specifies the Amazon S3 key prefix that comes after the name of the bucket.",
        description = "Do not include a leading or trailing / in your prefix. They are provided already.",
        default = "",
        max_length = 200,
        constraint = isValidS3KeyPrefix
    )

class ICloudTrails(INamed, IMapping):
    """
    Container for CloudTrail objects
    """

class ICloudTrailResource(INamed):
    """
    Global CloudTrail configuration
    """
    trails = schema.Object(
        title = "CloudTrails",
        schema = ICloudTrails,
        default = None
    )

class ICloudFrontCookies(Interface):
    forward = schema.TextLine(
        title = "Cookies Forward Action",
        constraint = isValidCloudFrontCookiesForward,
        default = 'all'
    )
    white_listed_names = schema.List(
        title = "White Listed Names",
        value_type = schema.TextLine(),
        default = [],
        required = False
    )

class ICloudFrontForwardedValues(Interface):
    query_string = schema.Bool(
        title = "Forward Query Strings",
        default = True
    )
    cookies = schema.Object(
        title = "Forward Cookies",
        schema = ICloudFrontCookies
    )
    headers = schema.List(
        title = "Forward Headers",
        value_type = schema.TextLine(),
        default = ['*']
    )

class ICloudFrontDefaultCacheBehaviour(Interface):
    allowed_methods = schema.List(
        title = "List of Allowed HTTP Methods",
        value_type = schema.TextLine(),
        default = [ 'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT' ]
    )
    default_ttl = schema.Int(
        title = "Default TTTL",
        # Disable TTL bydefault, just pass through
        default = 0
    )
    target_origin = TextReference(
        title = "Target Origin"
    )
    viewer_protocol_policy = schema.TextLine(
        title = "Viewer Protocol Policy",
        constraint = isValidCFViewerProtocolPolicy,
        default = 'redirect-to-https'
    )
    forwarded_values = schema.Object(
        title = "Forwarded Values",
        schema = ICloudFrontForwardedValues
    )

class ICloudFrontViewerCertificate(IDeployable):
    certificate = TextReference(
        title = "Certificate Reference",
        required = False,
    )
    ssl_supported_method = schema.TextLine(
        title = "SSL Supported Method",
        constraint = isValidCFSSLSupportedMethod,
        required = False,
        default = 'sni-only'
    )
    minimum_protocol_version = schema.TextLine(
        title = "Minimum SSL Protocol Version",
        constraint = isValidCFMinimumProtocolVersion,
        required = False,
        default = 'TLSv1.1_2016'
    )

class ICloudFrontCustomErrorResponse(Interface):
    error_caching_min_ttl = schema.Int(
        title = "Error Caching Min TTL"
    )
    error_code = schema.Int(
        title = "HTTP Error Code"
    )
    response_code = schema.Int(
        title = "HTTP Response Code"
    )
    response_page_path = schema.TextLine(
        title = "Response Page Path"
    )

class ICloudFrontCustomOriginConfig(Interface):
    http_port = schema.Int(
        title = "HTTP Port",
        required = False
    )
    https_port = schema.Int(
        title = "HTTPS Port"
    )
    protocol_policy = schema.TextLine(
        title = "Protocol Policy",
        constraint = isValidCFProtocolPolicy
    )
    ssl_protocols = schema.List(
        title = "List of SSL Protocols",
        value_type = schema.TextLine(),
        constraint = isValidCFSSLProtocol
    )
    read_timeout = schema.Int(
        title = "Read timeout",
        min = 4,
        max = 60,
        default = 30
    )
    keepalive_timeout = schema.Int(
        title = "HTTP Keepalive Timeout",
        min = 1,
        max = 60,
        default = 5
    )

class ICloudFrontOrigin(INamed):
    """
    CloudFront Origin Configuration
    """
    s3_bucket = TextReference(
        title = "Origin S3 Bucket Reference",
        required = False
    )
    domain_name = TextReference(
        title = "Origin Resource Reference",
        str_ok = True,
        required = False
    )
    custom_origin_config = schema.Object(
        title = "Custom Origin Configuration",
        schema = ICloudFrontCustomOriginConfig,
        required = False
    )

class ICloudFrontFactory(INamed):
    """
    CloudFront Factory
    """
    domain_aliases = schema.List(
        title = "List of DNS for the Distribution",
        value_type = schema.Object(IDNS),
        default = []
    )

    viewer_certificate = schema.Object(
        title = "Viewer Certificate",
        schema = ICloudFrontViewerCertificate
    )

class ICloudFront(IResource, IDeployable):
    """
    CloudFront CDN Configuration
    """
    domain_aliases = schema.List(
        title = "List of DNS for the Distribution",
        value_type = schema.Object(IDNS),
        default = []
    )
    default_cache_behavior = schema.Object(
        title = "Default Cache Behavior",
        schema = ICloudFrontDefaultCacheBehaviour
    )
    viewer_certificate = schema.Object(
        title = "Viewer Certificate",
        schema = ICloudFrontViewerCertificate
    )
    price_class = schema.TextLine(
        title = "Price Class",
        constraint = isValidCFPriceClass,
        default = 'All'
    )
    custom_error_responses = schema.List(
        title = "List of Custom Error Responses",
        value_type = schema.Object(ICloudFrontCustomErrorResponse),
        default = []
    )
    origins = schema.Dict(
        title = "Map of Origins",
        value_type = schema.Object(ICloudFrontOrigin)
    )
    webacl_id = schema.TextLine(
        title = "WAF WebACLId"
    )
    factory = schema.Dict(
        title = "CloudFront Factory",
        value_type = schema.Object(ICloudFrontFactory),
        default = None
    )


class IRDS(Interface):
    """
    RDS Common Interface
    """
    engine = schema.TextLine(
        title = "RDS Engine"
    )
    engine_version = schema.TextLine(
        title = "RDS Engine Version"
    )
    db_instance_type = schema.TextLine(
        title = "RDS Instance Type"
    )
    port = schema.Int(
        title = "DB Port"
    )
    segment = TextReference(
        title="Segment"
    )
    storage_type = schema.TextLine(
        title = "DB Storage Type"
    )
    storage_size_gb = schema.Int(
        title = "DB Storage Size in Gigabytes"
    )
    storage_encrypted = schema.Bool(
        title = "Enable Storage Encryption"
    )
    kms_key_id = TextReference(
        title = "Enable Storage Encryption",
        required = False
    )
    allow_major_version_upgrade = schema.Bool(
        title = "Allow major version upgrades"
    )
    allow_minor_version_upgrade = schema.Bool(
        title = "Allow minor version upgrades"
    )
    publically_accessible = schema.Bool(
        title = "Assign a Public IP address"
    )
    master_username = schema.TextLine(
        title = "Master Username"
    )
    master_user_password = schema.TextLine(
        title = "Master User Password"
    )
    backup_preferred_window = schema.TextLine(
        title = "Backup Preferred Window"
    )
    backup_retention_period = schema.Int(
        title = "Backup Retention Period in days"
    )
    maintenance_preferred_window = schema.TextLine(
        title = "Maintenance Preferred Window"
    )
    security_groups = schema.List(
        title = "List of Security Groups",
        value_type = TextReference()
    )
    primary_domain_name = TextReference(
        title = "Primary Domain Name",
        str_ok = True
    )
    primary_hosted_zone = TextReference(
        title = "Primary Hosted Zone"
    )

class IRDSMysql(IResource, IRDS):
    """
    RDS Mysql
    """
    multi_az = schema.Bool(
        title = "MultiAZ Support",
        default = False
    )

class IRDSAurora(IResource, IRDS):
    """
    RDS Aurora
    """
    secondary_domain_name = TextReference(
        title = "Secondary Domain Name",
        str_ok = True
    )
    secondary_hosted_zone = TextReference(
        title = "Secondary Hosted Zone"
    )

class IElastiCache(Interface):
    """
    Base ElastiCache Interface
    """
    engine = schema.TextLine(
        title = "ElastiCache Engine",
        required = False
    )
    engine_version = schema.TextLine(
        title = "ElastiCache Engine Version",
        required = False
    )
    automatic_failover_enabled = schema.Bool(
        title = "Specifies whether a read-only replica is automatically promoted to read/write primary if the existing primary fails"
    )
    number_of_read_replicas = schema.Int(
        title = "Number of read replicas"
    )
    port = schema.Int(
        title = 'Port'
    )
    at_rest_encryption = schema.Bool(
        title = "Enable encryption at rest"
    )
    auto_minor_version_upgrade = schema.Bool(
        title = "Enable automatic minor version upgrades"
    )
    az_mode = schema.TextLine(
        title = "AZ mode",
        constraint = isValidAZMode
    )
    cache_node_type  = schema.TextLine(
        title = "Cache Node Instance type",
        description=""
    )
    maintenance_preferred_window = schema.TextLine(
        title = 'Preferred maintenance window'
    )
    security_groups = schema.List(
        title = "List of Security Groups",
        value_type = TextReference()
    )
    segment = TextReference(
        title="Segment"
    )

class IElastiCacheRedis(IResource, IElastiCache):
    """
    Redis ElastiCache Interface
    """
    cache_parameter_group_family = schema.TextLine(
        title = 'Cache Parameter Group Family',
        constraint = isRedisCacheParameterGroupFamilyValid,
        required = False
    )
    #snapshot_retention_limit_days: 1
    #snapshot_window: 05:00-09:00
