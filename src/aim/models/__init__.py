import logging
import ruamel.yaml
import sys
from aim.models.loader import ModelLoader
from ruamel.yaml.compat import StringIO


class YAML(ruamel.yaml.YAML):
    def dump(self, data, stream=None, **kw):
        dumps = False
        if stream is None:
            dumps = True
            stream = StringIO()
        ruamel.yaml.YAML.dump(self, data, stream, **kw)
        if dumps:
            return stream.getvalue()

def get_logger():
    log = logging.getLogger("aim.models")
    log.setLevel(logging.DEBUG)
    return log

def load_project_from_yaml(aim_ctx, path):
    """
    Reads a project directory of YAML files and
    returns a complete set of model instances.
    """
    loader = ModelLoader(aim_ctx, path)
    loader.load_all()
    return loader.project
