from aim.models.base import Deployable, Named, Name
from aim.models import schemas, vocabulary
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


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
class AlarmSet(dict):
    resource_type = FieldProperty(schemas.IAlarmSet["resource_type"])

@implementer(schemas.IAlarmSets)
class AlarmSets(dict):
    "Collection of Alarms"

@implementer(schemas.IAlarm)
class Alarm(Name):
    "Alarm"
    severity = FieldProperty(schemas.IAlarmSet["resource_type"])

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

    def __init__(self, name):
        self.name = name

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

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.alarm_sets = AlarmSets()
        self.log_sets = LogSets()

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
