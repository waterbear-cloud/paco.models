from aim.models import schemas, vocabulary
from aim.models.base import Deployable, Named, Name, Resource, ServiceAccountRegion
from aim.models.locations import get_parent_by_interface
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@implementer(schemas.INotificationGroups)
class NotificationGroups(ServiceAccountRegion, Named, dict):
    "Container for NotificationGroups"

@implementer(schemas.IAlarmNotifications)
class AlarmNotifications(dict):
    "Container of AlarmNotifications"

@implementer(schemas.IAlarmNotification)
class AlarmNotification():
    "AlarmNotification"
    groups = FieldProperty(schemas.IAlarmNotification["groups"])
    classification = FieldProperty(schemas.IAlarmNotification["classification"])
    severity = FieldProperty(schemas.IAlarmNotification["severity"])

@implementer(schemas.ILogSets)
class LogSets(dict):
    "Collections of Log Sets"

@implementer(schemas.ILogSet)
class LogSet(dict):
    "Collection of Log Categories"

@implementer(schemas.ILogCategory)
class LogCategory(dict):
    "Collection of Log Sources"

    def __init__(self, name):
        self.name = name

@implementer(schemas.ILogSource)
class LogSource(Name):
    path = FieldProperty(schemas.ILogSource["path"])

@implementer(schemas.ICWAgentLogSource)
class CWAgentLogSource(LogSource):
    timezone = FieldProperty(schemas.ICWAgentLogSource["timezone"])
    timestamp_format = FieldProperty(schemas.ICWAgentLogSource["timestamp_format"])
    multi_line_start_pattern = FieldProperty(schemas.ICWAgentLogSource["multi_line_start_pattern"])
    encoding = FieldProperty(schemas.ICWAgentLogSource["encoding"])
    log_group_name = FieldProperty(schemas.ICWAgentLogSource["log_group_name"])
    log_stream_name = FieldProperty(schemas.ICWAgentLogSource["log_stream_name"])

    def __init__(self, name):
        self.name = name

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
class Alarm(Named):
    "Alarm"
    classification = FieldProperty(schemas.IAlarm["classification"])
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

        # add on notifications for the Resource
        monitor = get_parent_by_interface(self, schemas.IMonitorConfig)
        groups = self._add_notifications_to_groups(monitor.notifications, groups)

        # add on notifications for the Application
        app = get_parent_by_interface(self, schemas.IApplication)
        groups = self._add_notifications_to_groups(app.notifications, groups)

        return list(groups.keys())

@implementer(schemas.ICloudWatchAlarm)
class CloudWatchAlarm(Alarm):
    "CloudWatch Alarm"
    metric_name = FieldProperty(schemas.ICloudWatchAlarm["metric_name"])
    period = FieldProperty(schemas.ICloudWatchAlarm["period"])
    evaluation_periods = FieldProperty(schemas.ICloudWatchAlarm["evaluation_periods"])
    threshold = FieldProperty(schemas.ICloudWatchAlarm["threshold"])
    comparison_operator = FieldProperty(schemas.ICloudWatchAlarm["comparison_operator"])
    statistic = FieldProperty(schemas.ICloudWatchAlarm["statistic"])
    treat_missing_data = FieldProperty(schemas.ICloudWatchAlarm["treat_missing_data"])
    extended_statistic = FieldProperty(schemas.ICloudWatchAlarm["extended_statistic"])
    evaluate_low_sample_count_percentile = FieldProperty(schemas.ICloudWatchAlarm["evaluate_low_sample_count_percentile"])

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
        self.log_sets = LogSets()
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
