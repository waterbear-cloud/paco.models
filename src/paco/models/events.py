from paco.models import schemas
from paco.models.base import Resource, ApplicationResource, Named
from paco.models.metrics import Monitorable
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

@implementer(schemas.IEventTarget)
class EventTarget(Named):
    target = FieldProperty(schemas.IEventTarget['target'])
    input_json = FieldProperty(schemas.IEventTarget['input_json'])

@implementer(schemas.IEventsRuleEventPatternDetail)
class EventsRuleEventPatternDetail(Named, dict):
    pass

@implementer(schemas.IEventsRuleEventPattern)
class EventsRuleEventPattern(Named, dict):
    source = FieldProperty(schemas.IEventsRuleEventPattern['source'])
    detail = FieldProperty(schemas.IEventsRuleEventPattern['detail'])
    detail_type = FieldProperty(schemas.IEventsRuleEventPattern['detail_type'])

@implementer(schemas.IEventsRule)
class EventsRule(ApplicationResource, Monitorable):
    description = FieldProperty(schemas.IEventsRule['description'])
    event_pattern = FieldProperty(schemas.IEventsRule['event_pattern'])
    schedule_expression = FieldProperty(schemas.IEventsRule['schedule_expression'])
    enabled_state = FieldProperty(schemas.IEventsRule['enabled_state'])
    targets = FieldProperty(schemas.IEventsRule['targets'])
    monitoring = FieldProperty(schemas.IEventsRule['monitoring'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.targets = []
