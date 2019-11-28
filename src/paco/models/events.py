from paco.models import schemas
from paco.models.base import Resource
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@implementer(schemas.IEventsRule)
class EventsRule(Resource):
    title = "CloudWatch Event Rule"
    description = FieldProperty(schemas.IEventsRule['description'])
    schedule_expression = FieldProperty(schemas.IEventsRule['schedule_expression'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.targets = []
