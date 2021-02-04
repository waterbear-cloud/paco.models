"""
Implementation for Logging model objects
"""
from paco.models import schemas
from paco.models.base import Named
from paco.models.locations import get_parent_by_interface
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

@implementer(schemas.IMetricTransformation)
class MetricTransformation():
    default_value = FieldProperty(schemas.IMetricTransformation["default_value"])
    metric_name = FieldProperty(schemas.IMetricTransformation["metric_name"])
    metric_namespace = FieldProperty(schemas.IMetricTransformation["metric_namespace"])
    metric_value = FieldProperty(schemas.IMetricTransformation["metric_value"])

@implementer(schemas.IMetricFilters)
class MetricFilters(Named, dict):
    pass

@implementer(schemas.IMetricFilter)
class MetricFilter(Named):
    filter_pattern = FieldProperty(schemas.IMetricFilter["filter_pattern"])
    metric_transformations = FieldProperty(schemas.IMetricFilter["metric_transformations"])

@implementer(schemas.ICloudWatchLogGroups)
class CloudWatchLogGroups(Named, dict):
    pass

@implementer(schemas.ICloudWatchLogGroup)
class CloudWatchLogGroup(Named, CloudWatchLogRetention):
    external_resource = FieldProperty(schemas.ICloudWatchLogGroup["external_resource"])
    metric_filters = FieldProperty(schemas.ICloudWatchLogGroup["metric_filters"])
    sources = FieldProperty(schemas.ICloudWatchLogGroup["sources"])
    log_group_name = FieldProperty(schemas.ICloudWatchLogGroup["log_group_name"])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.metric_filters = MetricFilters('metric_filters', self)
        self.sources = CloudWatchLogSources(name, __parent__)

    def get_log_group_name(self):
        "Return log_group_name if set, otherwise return name"
        if self.log_group_name != '':
            return self.log_group_name
        return self.name

    def get_full_log_group_name(self):
        if self.external_resource == True:
            return self.log_group_name
        name = self.get_log_group_name()
        parent = get_parent_by_interface(self, schemas.ICloudWatchLogSet)
        if parent != None:
            return parent.name + '-' + name
        return name

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ICloudWatchLogSets)
class CloudWatchLogSets(Named, dict):
    "Collection of Log Set objects"

    def get_all_log_sources(self):
        "Return a list of all Log Source in these Log Sets"
        results = []
        for log_set in self.values():
            for log_group in self[log_set.name].log_groups.values():
                for log_source in log_group.sources.values():
                    results.append(log_source)
        return results

    def get_all_log_groups(self):
        "Return a list of all Log Groups in these Log Sets"
        results = []
        for log_set in self.values():
            for log_group in self[log_set.name].log_groups.values():
                results.append(log_group)
        return results

@implementer(schemas.ICloudWatchLogSet)
class CloudWatchLogSet(Named):
    "A set of Log Group objects"
    log_groups = FieldProperty(schemas.ICloudWatchLogSet["log_groups"])

@implementer(schemas.ICloudWatchLogging)
class CloudWatchLogging(Named, CloudWatchLogRetention):
    "Contains global defaults for all CloudWatch logging and log sets"
    log_sets = FieldProperty(schemas.ICloudWatchLogging["log_sets"])
