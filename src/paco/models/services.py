from paco.models import schemas
from paco.models.base import Named, match_allowed_paco_filenames
from zope.interface import implementer
import pkg_resources


@implementer(schemas.IServices)
class Services(Named, dict):

    enabled_services = []


def list_enabled_services(paco_home):
    """
    Return an ordered dict of Services enabled in this Paco Project.
    Sorted according to the SERVICE_INITIALIZATION_ORDER for each Service.
    """
    load_order = []
    # ToDo: 'services' should be legacy and only support 'service' ... ?
    services_dir_names = ('service', 'services')
    count = 1000 # services with no initialization order start at 1000
    for entry_point in pkg_resources.iter_entry_points('paco.services'):
        # # Legacy directory name
        # if os.path.isdir(paco_home / 'Services'):
        #     services_dir_name = 'Services'
        # services_dir = paco_home / services_dir_name
        # fname = None
        for service_dirname in services_dir_names:
            yaml_path = match_allowed_paco_filenames(paco_home, service_dirname, entry_point.name)
            if yaml_path != None:
                module = entry_point.load()
                if not hasattr(module, 'SERVICE_INITIALIZATION_ORDER'):
                    module.SERVICE_INITIALIZATION_ORDER = count
                    count += 1
                load_order.append((module.SERVICE_INITIALIZATION_ORDER, entry_point.name, module, yaml_path))
    load_order = sorted(load_order)
    entry_point_dict = {}
    for item in load_order:
        # The Service name is lower-cased
        entry_point_dict[item[1]] = {'name': item[1].lower(), 'module': item[2], 'yaml_path': item[3]}
    return entry_point_dict
