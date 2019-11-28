import pkg_resources
from paco.models import schemas
from paco.models.base import Named, Deployable
from zope.interface import implementer

@implementer(schemas.IServices)
class Services(Named, dict):
    pass

def list_service_plugins():
    """Return an ordered dict of Service plugins that is
    sorted by the initilization_order variable for each Service.
    """
    load_order = []
    count = 1000 # services with no initialization order start at 1000
    for entry_point in pkg_resources.iter_entry_points('paco.services'):
        module = entry_point.load()
        if not hasattr(module, 'initialization_order'):
            module.initialization_order = count
            count += 1
        load_order.append((module.initialization_order, entry_point.name, module))
    load_order = sorted(load_order)
    entry_point_dict = {}
    for item in load_order:
        entry_point_dict[item[1]] = item[2]
    return entry_point_dict
