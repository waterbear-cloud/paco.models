from paco.models import schemas
from paco.models.base import Resource, ApplicationResource, Named
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

@implementer(schemas.IEventTarget)
class EventTarget(Named):
    target = FieldProperty(schemas.IEventTarget['target'])
    input_json = FieldProperty(schemas.IEventTarget['input_json'])

@implementer(schemas.IEventsRule)
class EventsRule(ApplicationResource):
    description = FieldProperty(schemas.IEventsRule['description'])
    schedule_expression = FieldProperty(schemas.IEventsRule['schedule_expression'])
    enabled_state = FieldProperty(schemas.IEventsRule['enabled_state'])
    targets = FieldProperty(schemas.IEventsRule['targets'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.targets = []
