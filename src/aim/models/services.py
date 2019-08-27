import pkg_resources
from aim.models import schemas
from aim.models.base import Named, Deployable
from zope.interface import implementer

@implementer(schemas.IServices)
class Services(Named, dict):
    pass

def list_service_plugins():
    """Return a dict of Service plugins"""
    return {
        entry_point.name: entry_point.load()
        for entry_point
        in pkg_resources.iter_entry_points('aim.services')
    }