"""
Implementation for Logging model objects
"""
from aim.models import schemas
from aim.models.base import Named
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@implementer(schemas.ICloudWatchLogRetention)
class CloudWatchLogRetention():
    expire_events_after_days = FieldProperty(schemas.ICloudWatchLogRetention["expire_events_after_days"])

@implementer(schemas.ICloudWatchLogSources)
class CloudWatchLogSources(Named, dict):
    "Collection of Log Sources"

@implementer(schemas.ICloudWatchLogSource)
class CloudWatchLogSource(Named, CloudWatchLogRetention):
    encoding = FieldProperty(schemas.ICloudWatchLogSource["encoding"])
    log_stream_name = FieldProperty(schemas.ICloudWatchLogSource["log_stream_name"])
    multi_line_start_pattern = FieldProperty(schemas.ICloudWatchLogSource["multi_line_start_pattern"])
    path = FieldProperty(schemas.ICloudWatchLogSource["path"])
    timestamp_format = FieldProperty(schemas.ICloudWatchLogSource["timestamp_format"])
    timezone = FieldProperty(schemas.ICloudWatchLogSource["timezone"])

@implementer(schemas.IMetricFilters)
class MetricFilters(dict):
    # ToDo: load these into the model
    pass

@implementer(schemas.IMetricFilter)
class MetricFilter():
    filter_pattern = FieldProperty(schemas.IMetricFilter["filter_pattern"])
    metric_transformations = FieldProperty(schemas.IMetricFilter["metric_transformations"])

@implementer(schemas.ICloudWatchLogGroups)
class CloudWatchLogGroups(Named, dict):
    pass

@implementer(schemas.ICloudWatchLogGroup)
class CloudWatchLogGroup(Named, CloudWatchLogRetention):
    metric_filters = FieldProperty(schemas.ICloudWatchLogGroup["metric_filters"])
    sources = FieldProperty(schemas.ICloudWatchLogGroup["sources"])
    log_group_name = FieldProperty(schemas.ICloudWatchLogGroup["log_group_name"])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.metric_filters = MetricFilters()
        self.sources = CloudWatchLogSources(name, __parent__)

@implementer(schemas.ICloudWatchLogSets)
class CloudWatchLogSets(Named, dict):
    "Collection of Log Set objects"

    def get_all_log_sources(self):
        "Return a list of all Log Sources in these Log Sets"
        # XXX re-work and re-name!
        results = []
        for log_set_name in self.keys():
            for log_cat_name in self[log_set_name].keys():
                for log_source in self[log_set_name][log_cat_name].values():
                    results.append(log_source)
        return results

@implementer(schemas.ICloudWatchLogSet)
class CloudWatchLogSet(Named, dict):
    "A set of Log Group objects"
    log_groups = FieldProperty(schemas.ICloudWatchLogSet["log_groups"])

@implementer(schemas.ICloudWatchLogging)
class CloudWatchLogging(Named, CloudWatchLogRetention):
    "Contains global defaults for all CloudWatch logging and log sets"
    log_sets = FieldProperty(schemas.ICloudWatchLogging["log_sets"])
