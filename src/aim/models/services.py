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

    def resolve_ref(self, ref):
        if ref.parts[1] == 'keypairs':
            keypair_id = ref.parts[2]
            keypair_attr = 'name'
            if len(ref.parts) > 3:
                keypair_attr = ref.parts[3]
            keypair = self.keypairs[keypair_id]
            if keypair_attr == 'name':
                return keypair.name
            elif keypair_attr == 'region':
                return keypair.region
            elif keypair_attr == 'account':
                return keypair.account

        return self.resolve_ref_obj.resolve_ref(ref)

