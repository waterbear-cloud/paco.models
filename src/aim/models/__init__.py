from aim.models.loader import ModelLoader


def load_project_from_yaml(aim_ctx, path):
    """
    Reads a project directory of YAML files and
    returns a complete set of model instances.
    """
    loader = ModelLoader(aim_ctx, path)
    loader.load_all()
    return loader.project
