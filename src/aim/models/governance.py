"""
Governance Services
"""

import aim.models.apps
import aim.models.iam
from aim.models.base import Name, Named, Deployable
from aim.models import schemas
from aim.models import vocabulary
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@implementer(schemas.IGovernanceServices)
class GovernanceServices(Named, dict):
    pass

@implementer(schemas.IGovernanceService)
class GovernanceService(Named, Deployable, dict):
    aws_account = FieldProperty(schemas.IGovernanceService["aws_account"])
    aws_region = FieldProperty(schemas.IGovernanceService["aws_region"])
    resources = FieldProperty(schemas.IGovernanceService["resources"])

@implementer(schemas.IGovernance)
class Governance(Named):
    services = FieldProperty(schemas.IGovernance["services"])

@implementer(schemas.IGovernanceMonitoring)
class GovernanceMonitoring(GovernanceService):
    """
    Governance Monitoring Service
    """
