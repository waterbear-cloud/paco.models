#import paco.models.yaml
import ruamel.yaml
import troposphere
from ruamel.yaml.compat import StringIO
from paco.models.exceptions import TroposphereConversionError


yaml_str_tag = 'tag:yaml.org,2002:str'
yaml_seq_tag = 'tag:yaml.org,2002:seq'
yaml_map_tag = 'tag:yaml.org,2002:map'

def convert_yaml_node_to_troposphere(node):
    if node.tag == '!Sub':
        if type(node.value) == type(str()):
            # ScalarNode - single argument only
            return troposphere.Sub(node.value)
        else:
            values = {}
            for map_node in node.value[1:]:
                if map_node.tag != yaml_map_tag:
                    raise TroposphereConversionError("Substitue variables for !Sub must be mappings.")
                values[map_node.value[0][0].value] = map_node.value[0][1].value
            return troposphere.Sub(
                node.value[0].value,
                **values
            )

    elif node.tag == '!Ref':
        return troposphere.Ref(node.value)
    elif node.tag == '!Join':
        delimiter = node.value[0].value
        values = []
        for node in node.value[1].value:
            values.append(
                convert_yaml_node_to_troposphere(node)
            )
        return troposphere.Join(delimiter, values)

    elif node.tag == yaml_str_tag:
        return node.value
    else:
        raise TroposphereConversionError(
            "Unknown YAML to convert to Troposphere"
        )

def troposphere_constructor(loader, node):
    return convert_yaml_node_to_troposphere(node)

# def troposphere_representer(loader, node):
#     return export_troposphere_to_yaml_node(node)

cfn_tags = [
    '!Ref',
    '!Sub',
    '!Join',
    # '!Base64',
    # '!Cidr',
    # '!FindInMap',
    # '!GetAZs',
    # '!ImportValue',
    # '!Select',
    # '!Split',
    # '!Transform',
]

# ToDo: implement Fn::<Func> style syntax
# from ruamel.yaml.nodes import MappingNode
# from ruamel.yaml.constructor import BaseConstructor

# def construct_mapping(self, node, deep=False):
#     """SafeConstructor mapping that also handles Troposphere keys
#     such as Fn::Join: Fn::Sub: by creating Troposphere objects.
#     """
#     if isinstance(node, MappingNode):
#         self.flatten_mapping(node)
#     return BaseConstructor.construct_mapping(self, node, deep=deep)

# ruamel.yaml.SafeConstructor.construct_mapping = construct_mapping

class ModelYAML(ruamel.yaml.YAML):

    def add_troposphere_constructors(self):
        self.existing_constructors = {}
        for tag, constructor in self.constructor.yaml_constructors.items():
            if tag != None and tag.startswith('!'):
                self.existing_constructors[tag] = constructor
        for cfn_tag in cfn_tags:
            ruamel.yaml.add_constructor(
                cfn_tag,
                troposphere_constructor,
                constructor=ruamel.yaml.SafeConstructor
            )

    def restore_existing_constructors(self):
        for tag, constructor in self.existing_constructors.items():
            self.constructor.yaml_constructors[tag] = constructor

    def dump(self, data, stream=None, **kw):
        dumps = False
        if stream is None:
            dumps = True
            stream = StringIO()
        ruamel.yaml.YAML.dump(self, data, stream, **kw)
        if dumps:
            return stream.getvalue()

