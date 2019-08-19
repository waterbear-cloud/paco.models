import aim.models.exceptions
import aim.models.services
import json
from aim.models import schemas, vocabulary
from aim.models.base import Deployable, Named, Name, Resource, ServiceAccountRegion
from aim.models.formatter import get_formatted_model_context
from aim.models.logging import CloudWatchLogSets
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

    def get_alarm_actions(self, notificationgroups):
        """Return a list of SNS Topic alarm actions.
        This will by default be a list of SNS Topics that the alarm is subscribed to.
        However, if a plugin is registered, it will provide the actions instead.
        """
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
            notificationgroups[group].resource_name for group in self.notification_groups
        ]
        if len(notification_arns) > 5:
            raise aim.models.exceptions.InvalidAimProjectFile("""
    Alarm {} has {} actions, but CloudWatch Alarms allow a maximum of 5 actions.

    {}""".format(self.name, len(notification_arns), get_formatted_model_context(self))
            )

        return notification_arns

    def get_alarm_description(self, topic_arns):
        """Create an Alarm Description in JSON format with AIM Alarm information"""
        netenv = get_parent_by_interface(self, schemas.INetworkEnvironment)
        env = get_parent_by_interface(self, schemas.IEnvironment)
        envreg = get_parent_by_interface(self, schemas.IEnvironmentRegion)
        app = get_parent_by_interface(self, schemas.IApplication)
        group = get_parent_by_interface(self, schemas.IResourceGroup)
        resource = get_parent_by_interface(self, schemas.IResource)

        # Base alarm info - used for standalone alarms not part of an application
        description = {
            "alarm_name": self.name,
            "classification": self.classification,
            "severity": self.severity,
            "topic_arns": topic_arns
        }

        # conditional fields:
        if self.description:
            description['description'] = self.description
        if self.runbook_url:
            description['runbook_url'] = self.runbook_url

        if app != None:
            # Service applications and apps not part of a NetEnv
            description["app_name"] = app.name
            description["app_title"] = app.title
            description["resource_group_name"] = group.name
            description["resource_group_title"] = group.title
            description["resource_name"] = resource.name
            description["resource_title"] = resource.title

        if netenv != None:
            # NetEnv information
            description["netenv_name"] = netenv.name
            description["netenv_title"] = netenv.title
            description["env_name"] = env.name
            description["env_title"] = env.title
            description["envreg_name"] = env.name
            description["envreg_title"] = env.title

        return json.dumps(description)

@implementer(schemas.IDimension)
class Dimension():
    name = FieldProperty(schemas.IDimension["name"])
    value = FieldProperty(schemas.IDimension["value"])

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
