from paco.models import schemas
from paco.models.base import Named, Deployable
from zope.interface import implementer
import os
import pkg_resources


@implementer(schemas.IServices)
class Services(Named, dict):
    pass


def list_enabled_services(paco_home):
    """
    Return an ordered dict of Services enabled in this Paco Project.
    Sorted according to the SERVICE_INITIALIZATION_ORDER for each Service.
    """
    load_order = []
    services_dir_name = 'service'
    count = 1000 # services with no initialization order start at 1000
    for entry_point in pkg_resources.iter_entry_points('paco.services'):
        # Legacy directory name
        if os.path.isdir(paco_home / 'Services'):
            services_dir_name = 'Services'
        services_dir = paco_home / services_dir_name
        fname = None
        if (services_dir / f'{entry_point.name}.yml').is_file():
            fname = entry_point.name + '.yml'
        elif (services_dir / f'{entry_point.name}.yaml').is_file():
            fname = entry_point.name + '.yaml'
        if fname:
            module = entry_point.load()
            if not hasattr(module, 'SERVICE_INITIALIZATION_ORDER'):
                module.initialization_order = count
                count += 1
            load_order.append((module.SERVICE_INITIALIZATION_ORDER, entry_point.name, module, fname))
    load_order = sorted(load_order)
    entry_point_dict = {}
    for item in load_order:
        # The Service name is lower-cased
        entry_point_dict[item[1]] = {'name': item[1].lower(), 'module': item[2], 'filename': item[3]}
    return entry_point_dict
