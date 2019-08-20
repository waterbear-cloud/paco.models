import copy
from aim.models.loader import ModelLoader


def load_project_from_yaml(path, config_processor=None):
    """
    Reads a project directory of YAML files and
    returns a complete set of model instances.
    """
    loader = ModelLoader(path, config_processor)
    loader.load_all()
    return loader.project

def deepcopy_except_parent(obj):
    """Returns a deepcopy on on the object, but does not recurse up the
    __parent__ attribute to prevent copying the entire model.
    """
    parent = obj.__parent__
    obj.__parent__ = None
    copy_obj = copy.deepcopy(obj)
    obj.__parent__ = parent
    return copy_obj

