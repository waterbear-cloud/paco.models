"""
Cloud accounts
"""
from paco.models.base import Name, Named, Deployable
from paco.models import schemas
from paco.models.exceptions import InvalidPacoReference
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

@implementer(schemas.IAdminIAMUsers)
class AdminIAMUsers(Named, dict):
    pass

@implementer(schemas.IAdminIAMUser)
class AdminIAMUser(Named, Deployable):
    username = FieldProperty(schemas.IAdminIAMUser["username"])

@implementer(schemas.IAccounts)
class Accounts(Named, dict):
    pass

@implementer(schemas.IAccount)
class Account(Named, Deployable, dict):
    """
    Object attrs:
        - account_type : string : Cloud account type
        - account_id : string : Cloud account ID
        - admin_delegate_role_name : string : Name of the Administrator IAM Role to assume in the account
    """
    account_type = FieldProperty(schemas.IAccount["account_type"])
    account_id = FieldProperty(schemas.IAccount["account_id"])
    admin_delegate_role_name = FieldProperty(schemas.IAccount["admin_delegate_role_name"])
    is_master = FieldProperty(schemas.IAccount["is_master"])
    region = FieldProperty(schemas.IAccount["region"])
    root_email = FieldProperty(schemas.IAccount["root_email"])
    organization_account_ids = FieldProperty(schemas.IAccount["organization_account_ids"])
    admin_iam_users = FieldProperty(schemas.IAccount["admin_iam_users"])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.enabled = True

    def resolve_ref(self, ref):
        if ref.parts[1] != self.name:
            raise InvalidPacoReference("Ref of {} can not resolve.")
        if len(ref.parts) == 2:
            # This may return an account object in the future
            # but you can use get_model_obj_from_ref for that instead
            return self.account_id
        elif ref.last_part == 'id':
            return self.account_id
        elif ref.last_part == 'name':
            return self.name
        elif ref.last_part == 'region':
            return self.region

    @property
    def admin_delegate_role_arn(self):
        return 'arn:aws:iam::' + self.account_id + ':role/' + self.admin_delegate_role_name


