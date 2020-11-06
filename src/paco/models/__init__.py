import copy
from paco.models.loader import ModelLoader


def load_project_from_yaml(path, warn=None, validate_local_paths=False):
    """
    Reads a project directory of YAML files and
    returns a complete set of model instances.
    """
    loader = ModelLoader(path, warn, validate_local_paths)
    loader.load_all()
    return loader.project

def deepcopy_except_parent(obj):
    """Returns a deepcopy on on the object, but does not recurse up the
    __parent__ attribute to prevent copying the entire model.
    """
    if not hasattr(obj, '__parent__'):
        return copy.deepcopy(obj)

    # set __parent__ to None, copy the object, then restore __parent__
    parent = getattr(obj, '__parent__', None)
    obj.__parent__ = None
    copy_obj = copy.deepcopy(obj)
    obj.__parent__ = parent
    return copy_obj
