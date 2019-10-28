"""
All things CloudFormation Init.
"""

from aim.models.base import Named
from aim.models import schemas
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
import troposphere.cloudformation


def export_attrs_as_dicts(obj, attrs):
    out = {}
    for name in attrs:
        obj = getattr(obj, name, None)
        if obj:
            out[name] = dict(obj)

    return out

@implementer(schemas.ICloudFormationParameters)
class CloudFormationParameters(Named, dict):
    pass

# @implementer(schemas.ICloudFormationParameter)
# class CloudFormationParameter():
#     type = FieldProperty(schemas.ICloudFormationParameter['type'])

# @implementer(schemas.ICloudFormationStringParameter)
# class CloudFormationStringParameter(CloudFormationParameter):
#     default = FieldProperty(schemas.ICloudFormationStringParameter['default'])
#     min_length = FieldProperty(schemas.ICloudFormationStringParameter['min_length'])
#     max_length = FieldProperty(schemas.ICloudFormationStringParameter['max_length'])

# @implementer(schemas.ICloudFormationNumberParameter)
# class CloudFormationNumberParameter(CloudFormationParameter):
#     default = FieldProperty(schemas.ICloudFormationNumberParameter['default'])
#     min_value = FieldProperty(schemas.ICloudFormationNumberParameter['min_value'])
#     max_value = FieldProperty(schemas.ICloudFormationNumberParameter['max_value'])

@implementer(schemas.ICloudFormationConfigSets)
class CloudFormationConfigSets(Named, dict):

    def export_as_troposphere(self):
        # plain dict of list values
        return dict(self)

@implementer(schemas.ICloudFormationConfigurations)
class CloudFormationConfigurations(Named, dict):

    def export_as_troposphere(self):
        out = {}
        for key, value in self.items():
            out[key] = troposphere.cloudformation.InitConfig(
                **self[key].export_as_troposphere()
            )
        return out

@implementer(schemas.ICloudFormationInitVersionedPackageSet)
class CloudFormationInitVersionedPackageSet(dict):
    pass

@implementer(schemas.ICloudFormationInitPathOrUrlPackageSet)
class CloudFormationInitPathOrUrlPackageSet(dict):
    pass

@implementer(schemas.ICloudFormationInitPackages)
class CloudFormationInitPackages(Named):
    apt = FieldProperty(schemas.ICloudFormationInitPackages['apt'])
    msi = FieldProperty(schemas.ICloudFormationInitPackages['msi'])
    python = FieldProperty(schemas.ICloudFormationInitPackages['python'])
    rpm = FieldProperty(schemas.ICloudFormationInitPackages['rpm'])
    rubygems = FieldProperty(schemas.ICloudFormationInitPackages['rubygems'])
    yum = FieldProperty(schemas.ICloudFormationInitPackages['yum'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.apt = CloudFormationInitVersionedPackageSet()
        self.msi = CloudFormationInitPathOrUrlPackageSet()
        self.python = CloudFormationInitVersionedPackageSet()
        self.rpm = CloudFormationInitPathOrUrlPackageSet()
        self.rubygems = CloudFormationInitVersionedPackageSet()
        self.yum = CloudFormationInitVersionedPackageSet()

    def export_as_troposphere(self):
        return export_attrs_as_dicts(
            self,
            ('apt', 'msi', 'python', 'rpm', 'rubygems', 'yum')
        )

@implementer(schemas.ICloudFormationInitGroups)
class CloudFormationInitGroups():
    pass

@implementer(schemas.ICloudFormationInitUsers)
class CloudFormationInitUsers():
    pass

@implementer(schemas.ICloudFormationInitSources)
class CloudFormationInitSources():
    pass

@implementer(schemas.ICloudFormationInitFiles)
class CloudFormationInitFiles(Named, dict):

    def export_as_troposphere(self):
        out = {}
        for key, value in self.items():
            out[key] = self[key].export_as_troposphere()
        return out

@implementer(schemas.ICloudFormationInitFile)
class CloudFormationInitFile(Named):
    content = FieldProperty(schemas.ICloudFormationInitFile['content'])
    source = FieldProperty(schemas.ICloudFormationInitFile['source'])
    encoding = FieldProperty(schemas.ICloudFormationInitFile['encoding'])
    group = FieldProperty(schemas.ICloudFormationInitFile['group'])
    owner = FieldProperty(schemas.ICloudFormationInitFile['owner'])
    mode = FieldProperty(schemas.ICloudFormationInitFile['mode'])
    authentication = FieldProperty(schemas.ICloudFormationInitFile['authentication'])
    context = FieldProperty(schemas.ICloudFormationInitFile['context'])

    def export_as_troposphere(self):
        out = {}
        for name in ('content', 'source', 'encoding', 'group', 'owner', 'mode', 'authentication', 'context'):
            value = getattr(self, name, None)
            if value != None:
                out[name] = value

        return out

@implementer(schemas.ICloudFormationInitCommands)
class CloudFormationInitCommands(Named, dict):

    def export_as_troposphere(self):
        out = {}
        for key, command_obj in self.items():
            command_dict = {}
            for name in ('command', 'env', 'cwd', 'test', 'ignore_errors'):
                value = getattr(command_obj, name)
                if value != None:
                    command_dict[name] = value
            out[key] = command_dict
        return out

@implementer(schemas.ICloudFormationInitCommand)
class CloudFormationInitCommand(Named):
    command = FieldProperty(schemas.ICloudFormationInitCommand['command'])
    env = FieldProperty(schemas.ICloudFormationInitCommand['env'])
    cwd = FieldProperty(schemas.ICloudFormationInitCommand['cwd'])
    test = FieldProperty(schemas.ICloudFormationInitCommand['test'])
    ignore_errors = FieldProperty(schemas.ICloudFormationInitCommand['ignore_errors'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.env = {}

@implementer(schemas.ICloudFormationInitServices)
class CloudFormationInitServices():
    pass

@implementer(schemas.ICloudFormationConfiguration)
class CloudFormationConfiguration(Named):
    packages = FieldProperty(schemas.ICloudFormationConfiguration['packages'])
    groups = FieldProperty(schemas.ICloudFormationConfiguration['groups'])
    users = FieldProperty(schemas.ICloudFormationConfiguration['users'])
    sources = FieldProperty(schemas.ICloudFormationConfiguration['sources'])
    files = FieldProperty(schemas.ICloudFormationConfiguration['files'])
    commands = FieldProperty(schemas.ICloudFormationConfiguration['commands'])
    services = FieldProperty(schemas.ICloudFormationConfiguration['services'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.packages = CloudFormationInitPackages('packages', self)
        self.files = CloudFormationInitFiles('files', self)
        self.commands = CloudFormationInitCommands('commands', self)
        self.groups = CloudFormationInitGroups()
        self.users = CloudFormationInitUsers()
        self.sources = CloudFormationInitSources()
        self.services = CloudFormationInitServices()

    def export_as_troposphere(self):
        out = {}
        for name in ('packages', 'files', 'commands'): #, 'groups', 'users', 'sources', 'services'):
            obj = getattr(self, name, None)
            if obj:
                out[name] = obj.export_as_troposphere()
        return out

@implementer(schemas.ICloudFormationInit)
class CloudFormationInit(Named):
    config_sets = FieldProperty(schemas.ICloudFormationInit['config_sets'])
    configurations = FieldProperty(schemas.ICloudFormationInit['configurations'])
    parameters = FieldProperty(schemas.ICloudFormationInit['parameters'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.parameters = {}

    def export_as_troposphere(self):

        init_resource = troposphere.cloudformation.Init(
            troposphere.cloudformation.InitConfigSets(
                **self.config_sets.export_as_troposphere()
            ),
            **self.configurations.export_as_troposphere()
        )
        return init_resource