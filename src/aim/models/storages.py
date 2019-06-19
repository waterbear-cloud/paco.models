from aim.models import schemas
from aim.models.resources import Resource
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@implementer(schemas.IRDS)
class RDS(Resource):
    pass

