"""
IAM: Identity and Access Managment land
"""

from paco.models.base import Parent, Named, Deployable
from paco.models import schemas
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from paco.models import loader


@implementer(schemas.IIAM)
class IAM(Named):
    roles = FieldProperty(schemas.IIAM["roles"])
    #policies = FieldProperty(schemas.IIAM["policies"])

    def add_roles(self, roles_config_dict):
        roles_dict = {
            'roles': roles_config_dict
        }
        loader.apply_attributes_from_config(self, roles_dict)

@implementer(schemas.IRole)
class Role(Named, Deployable):
    instance_profile = FieldProperty(schemas.IRole["instance_profile"])
    path = FieldProperty(schemas.IRole["path"])
    managed_policy_arns = FieldProperty(schemas.IRole["managed_policy_arns"])
    max_session_duration = FieldProperty(schemas.IRole["max_session_duration"])
    permissions_boundary = FieldProperty(schemas.IRole["permissions_boundary"])
    assume_role_policy = FieldProperty(schemas.IRole["assume_role_policy"])
    role_name = FieldProperty(schemas.IRole["role_name"])
    global_role_name = FieldProperty(schemas.IRole["global_role_name"])
    policies = FieldProperty(schemas.IRole["policies"])

    def __init__(self, __name__, __parent__):
        super().__init__(__name__, __parent__)
        self.policies = []

    def apply_config(self, config_dict):
        loader.apply_attributes_from_config(self, config_dict)

    def set_assume_role_policy(self, policy_config_dict):
        policy_config = AssumeRolePolicy(self)
        loader.apply_attributes_from_config(policy_config, policy_config_dict)
        self.assume_role_policy = policy_config

    def add_policy(self, policy_config_dict):
        policy_config = Policy(self)
        loader.apply_attributes_from_config(policy_config, policy_config_dict)
        self.policies.append(policy_config)

    def get_arn(self):
        return self.resolve_ref_obj.get_role_arn()

    def resolve_ref(self, ref):
        return ref.resource.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IPolicy)
class Policy(Parent):
    name = FieldProperty(schemas.IPolicy["name"])
    statement = FieldProperty(schemas.IPolicy["statement"])

@implementer(schemas.IAssumeRolePolicy)
class AssumeRolePolicy(Parent):
    effect = FieldProperty(schemas.IAssumeRolePolicy["effect"])
    aws = FieldProperty(schemas.IAssumeRolePolicy["aws"])
    service = FieldProperty(schemas.IAssumeRolePolicy["service"])


@implementer(schemas.IStatement)
class Statement(Named):
    effect = FieldProperty(schemas.IStatement["effect"])
    action = FieldProperty(schemas.IStatement["action"])
    resource = FieldProperty(schemas.IStatement["resource"])

    def __init__(self, __name__, __parent__):
        super().__init__(__name__, __parent__)
        self.action = []
        self.resource = []

#@implementer(schemas.IManagedPolicy)
#class ManagedPolicies(Named, dict):
#    pass

@implementer(schemas.IManagedPolicy)
class ManagedPolicy(Named, Deployable):
    name = FieldProperty(schemas.IManagedPolicy["name"])
    statement = FieldProperty(schemas.IManagedPolicy["statement"])
    roles = FieldProperty(schemas.IManagedPolicy["roles"])
    users = FieldProperty(schemas.IManagedPolicy["users"])
    path = FieldProperty(schemas.IManagedPolicy["path"])