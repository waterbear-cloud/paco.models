"""
AWS Backup models
"""

from aim.models.base import Named, Parent, Resource
from aim.models import schemas
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@implementer(schemas.IBackupPlanRule)
class BackupPlanRule(Named):
    lifecycle_delete_after_days = FieldProperty(schemas.IBackupPlanRule['lifecycle_delete_after_days'])
    lifecycle_move_to_cold_storage_after_days = FieldProperty(schemas.IBackupPlanRule['lifecycle_move_to_cold_storage_after_days'])
    schedule_expression = FieldProperty(schemas.IBackupPlanRule['schedule_expression'])


@implementer(schemas.IBackupSelectionConditionResourceType)
class BackupSelectionConditionResourceType(Parent):
    condition_type = FieldProperty(schemas.IBackupSelectionConditionResourceType['condition_type'])
    condition_key = FieldProperty(schemas.IBackupSelectionConditionResourceType['condition_key'])
    condition_value = FieldProperty(schemas.IBackupSelectionConditionResourceType['condition_value'])


@implementer(schemas.IBackupPlanSelection)
class BackupPlanSelection(Parent):
    tags = FieldProperty(schemas.IBackupPlanSelection['tags'])


@implementer(schemas.IBackupPlan)
class BackupPlan(Resource):
    plan_rules = FieldProperty(schemas.IBackupPlan['plan_rules'])
    selections = FieldProperty(schemas.IBackupPlan['selections'])

@implementer(schemas.IBackupPlans)
class BackupPlans(Named, dict):
    pass

@implementer(schemas.IBackupVault)
class BackupVault(Resource):
    notification_events = FieldProperty(schemas.IBackupVault['notification_events'])
    notification_groups = FieldProperty(schemas.IBackupVault['notification_groups'])
    plans = FieldProperty(schemas.IBackupVault['plans'])

@implementer(schemas.IBackupVaults)
class BackupVaults(Named, dict):
    pass

