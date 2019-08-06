from aim.models.loader import ModelLoader


def load_project_from_yaml(path, config_processor=None):
    """
    Reads a project directory of YAML files and
    returns a complete set of model instances.
    """
    loader = ModelLoader(path, config_processor)
    loader.load_all()
    return loader.project
