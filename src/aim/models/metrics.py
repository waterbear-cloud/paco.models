import aim.models.exceptions
import aim.models.services
import json
import troposphere.cloudwatch
from aim.models import schemas, vocabulary
from aim.models.base import Deployable, Named, Name, Resource, AccountRef, Regionalized
from aim.models.formatter import get_formatted_model_context
from aim.models.logging import CloudWatchLogSets
from aim.models.locations import get_parent_by_interface
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@implementer(schemas.INotificationGroups)
class NotificationGroups(AccountRef, Named, dict):
    "Container for NotificationGroups"

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IAlarmNotifications)
class AlarmNotifications(dict):
    "Container of AlarmNotifications"

@implementer(schemas.IAlarmNotification)
class AlarmNotification():
    "AlarmNotification"
    groups = FieldProperty(schemas.IAlarmNotification["groups"])
    classification = FieldProperty(schemas.IAlarmNotification["classification"])
    severity = FieldProperty(schemas.IAlarmNotification["severity"])

@implementer(schemas.IAlarmSet)
class AlarmSet(Named, dict):
    resource_type = FieldProperty(schemas.IAlarmSet["resource_type"])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.notifications = AlarmNotifications()

@implementer(schemas.IAlarmSets)
class AlarmSets(Named, dict):
    "Collection of Alarms"

@implementer(schemas.IAlarm)
class Alarm(Named, Regionalized):
    "Alarm"
    classification = FieldProperty(schemas.IAlarm["classification"])
    description = FieldProperty(schemas.IAlarm["description"])
    runbook_url = FieldProperty(schemas.IAlarm["runbook_url"])
    severity = FieldProperty(schemas.IAlarm["severity"])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.notifications = AlarmNotifications()

    def _add_notifications_to_groups(self, notifications, groups):
        for notification in notifications.values():
            # do not add if it is filtered out
            if notification.classification and self.classification != notification.classification:
                continue
            if notification.severity and self.severity != notification.severity:
                continue
            for group in notification.groups:
                if group not in groups:
                    groups[group] = None
        return groups

    @property
    def notification_groups(self):
        "A unique list of notification groups that an Alarm is subscribed to"
        groups = {}

        # start with any notifications specific to the alarm
        groups = self._add_notifications_to_groups(self.notifications, groups)

        # add on notifications for the AlarmSet
        alarm_set = get_parent_by_interface(self, schemas.IAlarmSet)
        groups = self._add_notifications_to_groups(alarm_set.notifications, groups)

        # For Alarms that belong to an application, check IMonitorConfig and IApplication
        # add on notifications for the Resource
        monitor = get_parent_by_interface(self, schemas.IMonitorConfig)
        if monitor != None:
            groups = self._add_notifications_to_groups(monitor.notifications, groups)

        # add on notifications for the Application
        app = get_parent_by_interface(self, schemas.IApplication)
        if app != None:
            groups = self._add_notifications_to_groups(app.notifications, groups)

        return [key for key in groups.keys()]

    def get_alarm_actions_aim_refs(self, notificationgroups=None):
        """Return a list of alarm actions in the form of aim.ref SNS Topic ARNs, e.g.

        'aim.ref service.notification.applications.notification.groups.lambda.resources.snstopic.arn'

        This will by default be a list of SNS Topics that the alarm is subscribed to.
        However, if a plugin is registered, it will provide the actions instead.
        """
        if not notificationgroups:
            project = get_parent_by_interface(self, schemas.IProject)
            notificationgroups = project['resource']['notificationgroups']

        # if a service plugin provides override_alarm_actions, call that instead
        service_plugins = aim.models.services.list_service_plugins()

        # Error if more than one plugin provides override_alarm_actions
        count = 0
        for plugin_module in service_plugins.values():
            if hasattr(plugin_module, 'override_alarm_actions'):
                count += 1
        if count > 1:
            raise aim.models.exceptions.InvalidAimProjectFile('More than one Service plugin is overriding alarm actions')

        for plugin_name, plugin_module in service_plugins.items():
            if hasattr(plugin_module, 'override_alarm_actions'):
                return plugin_module.override_alarm_actions(None, self)

        # default behaviour is to use notification groups directly
        notification_arns = [
            notificationgroups[group].aim_ref + '.arn' for group in self.notification_groups
        ]
        if len(notification_arns) > 5:
            raise aim.models.exceptions.InvalidAimProjectFile("""
    Alarm {} has {} actions, but CloudWatch Alarms allow a maximum of 5 actions.

    {}""".format(self.name, len(notification_arns), get_formatted_model_context(self))
            )

        return notification_arns

    @property
    def actions_enabled(self):
        if hasattr(self, 'alarm_actions'):
            if len(self.alarm_actions) > 0:
                return True
        return None

@implementer(schemas.IDimension)
class Dimension():
    name = FieldProperty(schemas.IDimension["name"])
    value = FieldProperty(schemas.IDimension["value"])

    def __init__(self, name='', value=''):
        self.name = name
        self.value = value

@implementer(schemas.ISimpleCloudWatchAlarm)
class SimpleCloudWatchAlarm():
    "CloudWatch Alarm"
    alarm_description = FieldProperty(schemas.ICloudWatchAlarm["alarm_description"])
    actions_enabled = FieldProperty(schemas.ICloudWatchAlarm["actions_enabled"])
    metric_name = FieldProperty(schemas.ICloudWatchAlarm["metric_name"])
    namespace = FieldProperty(schemas.ICloudWatchAlarm["namespace"])
    period = FieldProperty(schemas.ICloudWatchAlarm["period"])
    evaluation_periods = FieldProperty(schemas.ICloudWatchAlarm["evaluation_periods"])
    threshold = FieldProperty(schemas.ICloudWatchAlarm["threshold"])
    comparison_operator = FieldProperty(schemas.ICloudWatchAlarm["comparison_operator"])
    statistic = FieldProperty(schemas.ICloudWatchAlarm["statistic"])


@implementer(schemas.ICloudWatchAlarm)
class CloudWatchAlarm(Alarm):
    "CloudWatch Alarm"
    metric_name = FieldProperty(schemas.ICloudWatchAlarm["metric_name"])
    namespace = FieldProperty(schemas.ICloudWatchAlarm["namespace"])
    dimensions = FieldProperty(schemas.ICloudWatchAlarm["dimensions"])
    period = FieldProperty(schemas.ICloudWatchAlarm["period"])
    evaluation_periods = FieldProperty(schemas.ICloudWatchAlarm["evaluation_periods"])
    threshold = FieldProperty(schemas.ICloudWatchAlarm["threshold"])
    comparison_operator = FieldProperty(schemas.ICloudWatchAlarm["comparison_operator"])
    statistic = FieldProperty(schemas.ICloudWatchAlarm["statistic"])
    treat_missing_data = FieldProperty(schemas.ICloudWatchAlarm["treat_missing_data"])
    extended_statistic = FieldProperty(schemas.ICloudWatchAlarm["extended_statistic"])
    evaluate_low_sample_count_percentile = FieldProperty(schemas.ICloudWatchAlarm["evaluate_low_sample_count_percentile"])

    troposphere_props = troposphere.cloudwatch.Alarm.props
    cfn_mapping = {
        # 'AlarmName': computed by CloudFormation service so you can specify updates
        # 'AlarmDescription': computed in template for the SNS Topic ARNs
        # 'AlarmActions': computed in template,
        'ActionsEnabled': 'actions_enabled',
        'ComparisonOperator': 'comparison_operator',
        'EvaluateLowSampleCountPercentile': 'evaluate_low_sample_count_percentile',
        'EvaluationPeriods': 'evaluation_periods',
        'ExtendedStatistic': 'extended_statistic',
        'MetricName': 'metric_name',
        'Namespace': 'namespace',
        'Period': 'period',
        'Statistic': 'statistic',
        'Threshold': 'threshold',
        'TreatMissingData': 'treat_missing_data',
    }
    # Need to be supplied externally
    # 'Dimensions': ([MetricDimension], False),
    #
    # Not yet implemented:
    # 'OKActions': ([basestring], False),
    # 'Unit': (basestring, False),
    # 'InsufficientDataActions': ([basestring], False),
    # 'DatapointsToAlarm': (positive_integer, False),
    #  'Metrics': ([MetricDataQuery], False),

    def threshold_human(self):
        "Human readable threshold"
        comparison = vocabulary.cloudwatch_comparison_operators[self.comparison_operator]
        if self.period < 60:
            period_human = '{} seconds'.format(int(self.period))
        elif self.period < 120:
            period_human = '{} minute'.format(int(self.period / 60))
        elif self.period < 3600:
            period_human = '{} minutes'.format(int(self.period / 60))
        elif self.period < 7200:
            period_human = '{} hour'.format(int(self.period / 3600))
        else:
            period_human = '{} hours'.format(int(self.period / 3600))
        return '{} {} {} for {} datapoints within {}'.format(
            self.metric_name,
            comparison,
            self.threshold,
            self.evaluation_periods,
            period_human
        )

@implementer(schemas.IMonitorable)
class Monitorable():
    monitoring = FieldProperty(schemas.IMonitorable["monitoring"])

@implementer(schemas.IMonitorConfig)
class MonitorConfig(Deployable, Named):
    collection_interval = FieldProperty(schemas.IMonitorConfig["collection_interval"])
    metrics = FieldProperty(schemas.IMonitorConfig["metrics"])
    asg_metrics = FieldProperty(schemas.IMonitorConfig["asg_metrics"])
    notifications = FieldProperty(schemas.IMonitorConfig["notifications"])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.alarm_sets = AlarmSets('alarm_sets', self)
        self.log_sets = CloudWatchLogSets('log_sets', self)
        self.notifications = AlarmNotifications()

@implementer(schemas.IMetric)
class Metric():
    name = FieldProperty(schemas.IMetric["name"])
    measurements = FieldProperty(schemas.IMetric["measurements"])
    collection_interval = FieldProperty(schemas.IMetric["collection_interval"])

ec2core = Metric()
ec2core.name = 'ec2core'
ec2core.collection_interval = 300
ec2core.measurements = [
    'CPUUtilization',
    'DiskReadBytes',
    'DiskReadOps',
    'DiskWriteBytes',
    'DiskWriteOps',
    'NetworkIn',
    'NetworkOut',
    'StatusCheckFailed',
    'StatusCheckFailed_Instance',
    'StatusCheckFailed_System'
]
