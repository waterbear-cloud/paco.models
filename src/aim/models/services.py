from aim.models import schemas
from aim.models.resources import Resource
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from aim.models.base import Named, Deployable, Regionalized


@implementer(schemas.IEC2KeyPair)
class EC2KeyPair(Named):
    region = FieldProperty(schemas.IEC2KeyPair['region'])
    account = FieldProperty(schemas.IEC2KeyPair['account'])

@implementer(schemas.IEC2Service)
class EC2Service():
    keypairs = FieldProperty(schemas.IEC2Service['keypairs'])

