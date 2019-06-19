"""
Cloud accounts
"""
from aim.models.base import Name, Named, Deployable
from aim.models import schemas
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

@implementer(schemas.IAdminIAMUser)
class AdminIAMUser(Deployable):
    """
    Object attrs:
        -
    """
    username = FieldProperty(schemas.IAdminIAMUser["username"])

@implementer(schemas.IAccounts)
class Accounts(Named, dict):
    pass

@implementer(schemas.IAccount)
class Account(Named, dict):
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

    @property
    def admin_delegate_role_arn(self):
        return 'arn:aws:iam::' + self.account_id + ':role/' + self.admin_delegate_role_name


