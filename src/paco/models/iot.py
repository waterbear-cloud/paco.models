"""
All things IoT
"""

from paco.models import schemas
from paco.models.base import Parent, Named, Resource, ApplicationResource, md5sum
from paco.models.metrics import Monitorable
from paco.models.locations import get_parent_by_interface
from paco.models.formatter import smart_join
from paco.models.exceptions import InvalidModelObject
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


# IoT Analytics

@implementer(schemas.IStorageRetention)
class StorageRetention():
    expire_events_after_days = FieldProperty(schemas.IStorageRetention['expire_events_after_days'])

@implementer(schemas.IIotAnalyticsStorage)
class IotAnalyticsStorage(Named, StorageRetention):
    bucket = FieldProperty(schemas.IIotAnalyticsStorage['bucket'])
    key_prefix = FieldProperty(schemas.IIotAnalyticsStorage['key_prefix'])

@implementer(schemas.IAttributes)
class Attributes(Named, dict):
    pass

@implementer(schemas.IIoTPipelineActivity)
class IoTPipelineActivity(Named):
    activity_type = FieldProperty(schemas.IIoTPipelineActivity['activity_type'])
    attributes = FieldProperty(schemas.IIoTPipelineActivity['attributes'])
    attribute_list = FieldProperty(schemas.IIoTPipelineActivity['attribute_list'])
    batch_size = FieldProperty(schemas.IIoTPipelineActivity['batch_size'])
    filter = FieldProperty(schemas.IIoTPipelineActivity['filter'])
    function = FieldProperty(schemas.IIoTPipelineActivity['function'])
    math = FieldProperty(schemas.IIoTPipelineActivity['math'])
    thing_name = FieldProperty(schemas.IIoTPipelineActivity['thing_name'])

@implementer(schemas.IIoTPipelineActivities)
class IoTPipelineActivities(Named, dict):
    pass

@implementer(schemas.IDatasetVariable)
class DatasetVariable(Named):
    double_value = FieldProperty(schemas.IDatasetVariable['double_value'])
    output_file_uri_value = FieldProperty(schemas.IDatasetVariable['output_file_uri_value'])
    string_value = FieldProperty(schemas.IDatasetVariable['string_value'])

@implementer(schemas.IDatasetVariables)
class DatasetVariables(Named, dict):
    pass

@implementer(schemas.IDatasetContainerAction)
class DatasetContainerAction(Named):
    image_arn = FieldProperty(schemas.IDatasetContainerAction['image_arn'])
    resource_compute_type = FieldProperty(schemas.IDatasetContainerAction['resource_compute_type'])
    resource_volume_size_gb = FieldProperty(schemas.IDatasetContainerAction['resource_volume_size_gb'])
    variables = FieldProperty(schemas.IDatasetContainerAction['variables'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.variables = DatasetVariables('variables', self)

@implementer(schemas.IDatasetQueryAction)
class DatasetQueryAction(Named):
    filters = FieldProperty(schemas.IDatasetQueryAction['filters'])
    sql_query = FieldProperty(schemas.IDatasetQueryAction['sql_query'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.filters = []

@implementer(schemas.IDatasetS3Destination)
class DatasetS3Destination(Named):
    bucket = FieldProperty(schemas.IDatasetS3Destination['bucket'])
    key = FieldProperty(schemas.IDatasetS3Destination['key'])

@implementer(schemas.IDatasetContentDeliveryRule)
class DatasetContentDeliveryRule(Named):
    s3_destination = FieldProperty(schemas.IDatasetContentDeliveryRule['s3_destination'])

@implementer(schemas.IDatasetContentDeliveryRules)
class DatasetContentDeliveryRules(Named, dict):
    pass

@implementer(schemas.IDatasetTrigger)
class DatasetTrigger(Parent):
    schedule_expression = FieldProperty(schemas.IDatasetTrigger['schedule_expression'])
    triggering_dataset = FieldProperty(schemas.IDatasetTrigger['triggering_dataset'])

@implementer(schemas.IIoTDataset)
class IoTDataset(Named, StorageRetention):
    container_action = FieldProperty(schemas.IIoTDataset['container_action'])
    query_action = FieldProperty(schemas.IIoTDataset['query_action'])
    content_delivery_rules = FieldProperty(schemas.IIoTDataset['content_delivery_rules'])
    triggers = FieldProperty(schemas.IIoTDataset['triggers'])
    version_history = FieldProperty(schemas.IIoTDataset['version_history'])

@implementer(schemas.IIoTDatasets)
class IoTDatasets(Named, dict):
    pass

@implementer(schemas.IIoTAnalyticsPipeline)
class IoTAnalyticsPipeline(ApplicationResource, Monitorable):
    channel_storage = FieldProperty(schemas.IIoTAnalyticsPipeline['channel_storage'])
    datastore_name = FieldProperty(schemas.IIoTAnalyticsPipeline['datastore_name'])
    datastore_storage = FieldProperty(schemas.IIoTAnalyticsPipeline['datastore_storage'])
    pipeline_activities = FieldProperty(schemas.IIoTAnalyticsPipeline['pipeline_activities'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.channel_storage = IotAnalyticsStorage('channel_storage', self)
        self.pipeline_activities = IoTPipelineActivities('pipeline_activities', self)
        self.datastore_storage = IotAnalyticsStorage('dataset_storage', self)
        self.datasets = IoTDatasets('datasets', self)

    def resolve_ref(self, ref):
        return self.stack

@implementer(schemas.IIoTTopicRuleIoTAnalyticsAction)
class IoTTopicRuleIoTAnalyticsAction(Parent):
    pipeline = FieldProperty(schemas.IIoTTopicRuleIoTAnalyticsAction['pipeline'])

# IoT Core

@implementer(schemas.IIoTPolicy)
class IoTPolicy(ApplicationResource):
    policy_json = FieldProperty(schemas.IIoTPolicy['policy_json'])
    variables = FieldProperty(schemas.IIoTPolicy['variables'])

    def get_aws_name(self):
        "Name of the IoT Policy in AWS"
        # NetworkEnvironment or Service name
        name_list = []
        ne = get_parent_by_interface(self, schemas.INetworkEnvironment)
        if ne == None:
            service = get_parent_by_interface(self, schemas.IService)
            if service == None:
                raise InvalidModelObject("""Unable to find an INetworkEnvironment or IService model object.""")
            name_list.append('Service')
            name_list.append(service.name)
        else:
            name_list.append('ne')
            name_list.append(ne.name)

        # Environment name or Blank if one does not exist
        env = get_parent_by_interface(self, schemas.IEnvironment)
        if env != None:
            name_list.append(env.name)
        name_list.append('app')
        app = get_parent_by_interface(self, schemas.IApplication)
        name_list.append(app.name)
        group = get_parent_by_interface(self, schemas.IResourceGroup)
        name_list.append(group.name)
        name_list.append(self.name)
        aws_name = smart_join('-', name_list)
        aws_name = aws_name.replace('_', '-').lower()

        # If the generated policy name is > 128 chars, then prefix a hash of the name
        if len(aws_name) > 128:
            name_hash = md5sum(str_data=aws_name)[:8]
            copy_size = -(128 - 9)
            if aws_name[copy_size] != '-':
                name_hash += '-'
            aws_name = name_hash + aws_name[copy_size:]

        return aws_name


@implementer(schemas.IIoTVariables)
class IoTVariables(Named, dict):
    pass

@implementer(schemas.IIoTTopicRuleLambdaAction)
class IoTTopicRuleLambdaAction(Parent):
    function = FieldProperty(schemas.IIoTTopicRuleLambdaAction['function'])

@implementer(schemas.IIoTTopicRuleAction)
class IoTTopicRuleAction(Parent):
    awslambda = FieldProperty(schemas.IIoTTopicRuleAction['awslambda'])
    iotanalytics = FieldProperty(schemas.IIoTTopicRuleAction['iotanalytics'])

@implementer(schemas.IIoTTopicRule)
class IoTTopicRule(ApplicationResource, Monitorable):
    actions = FieldProperty(schemas.IIoTTopicRule['actions'])
    aws_iot_sql_version = FieldProperty(schemas.IIoTTopicRule['aws_iot_sql_version'])
    rule_enabled = FieldProperty(schemas.IIoTTopicRule['rule_enabled'])
    sql = FieldProperty(schemas.IIoTTopicRule['sql'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.actions = []

    def resolve_ref(self, ref):
        return self.stack
