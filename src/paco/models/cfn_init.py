"""
All things CloudFormation Init.
"""

from paco.models.base import Named
from paco.models import schemas
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
import troposphere.cloudformation


def export_attrs_as_dicts(obj, attrs):
    out = {}
    for name in attrs:
        value = getattr(obj, name, None)
        if value:
            out[name] = dict(value)
    return out

@implementer(schemas.ICloudFormationParameters)
class CloudFormationParameters(Named, dict):
    pass

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

@implementer(schemas.ICloudFormationInitGroup)
class CloudFormationInitGroup(Named):
    gid = FieldProperty(schemas.ICloudFormationInitGroup['gid'])

    def export_as_troposphere(self):
        out = {}
        for name in ('gid'):
            value = getattr(self, name, None)
            if value != None:
                out[name] = value
        return out

@implementer(schemas.ICloudFormationInitGroups)
class CloudFormationInitGroups(Named, dict):

    def export_as_troposphere(self):
        out = {}
        for key, value in self.items():
            out[key] = self[key].export_as_troposphere()
        return out

@implementer(schemas.ICloudFormationInitUser)
class CloudFormationInitUser(Named):
    groups = FieldProperty(schemas.ICloudFormationInitUser['groups'])
    uid = FieldProperty(schemas.ICloudFormationInitUser['uid'])
    home_dir = FieldProperty(schemas.ICloudFormationInitUser['home_dir'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.groups = []

    def export_as_troposphere(self):
        out = {}
        for name in ('groups', 'uid', 'home_dir'):
            value = getattr(self, name, None)
            if name == 'home_dir':
                name = 'homeDir'
            if name == 'uid':
                value = str(value)
            if value != None:
                out[name] = value
        return out

@implementer(schemas.ICloudFormationInitUsers)
class CloudFormationInitUsers(Named, dict):

    def export_as_troposphere(self):
        out = {}
        for key, value in self.items():
            out[key] = self[key].export_as_troposphere()
        return out

@implementer(schemas.ICloudFormationInitSources)
class CloudFormationInitSources(Named, dict):

    def export_as_troposphere(self):
        out = {}
        for key, value in self.items():
            out[key] = value
        return out

@implementer(schemas.ICloudFormationInitFiles)
class CloudFormationInitFiles(Named, dict):

    def export_as_troposphere(self):
        out = {}
        for key, value in self.items():
            out[key] = self[key].export_as_troposphere()
        return out

@implementer(schemas.ICloudFormationInitFile)
class CloudFormationInitFile(Named):
    content_cfn_file = FieldProperty(schemas.ICloudFormationInitFile['content_cfn_file'])
    content_file = FieldProperty(schemas.ICloudFormationInitFile['content_file'])
    source = FieldProperty(schemas.ICloudFormationInitFile['source'])
    encoding = FieldProperty(schemas.ICloudFormationInitFile['encoding'])
    group = FieldProperty(schemas.ICloudFormationInitFile['group'])
    owner = FieldProperty(schemas.ICloudFormationInitFile['owner'])
    mode = FieldProperty(schemas.ICloudFormationInitFile['mode'])
    authentication = FieldProperty(schemas.ICloudFormationInitFile['authentication'])
    context = FieldProperty(schemas.ICloudFormationInitFile['context'])
    _content = None

    @property
    def content(self):
        "Return a string or a Troposphere CFN Function object"
        if self.content_file:
            return self.content_file
        elif self.content_cfn_file:
            return self.content_cfn_file
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

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
                if name == 'ignore_errors':
                    name = 'ignoreErrors'
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

@implementer(schemas.ICloudFormationInitService)
class CloudFormationInitService(Named, dict):
    ensure_running = FieldProperty(schemas.ICloudFormationInitService['ensure_running'])
    enabled = FieldProperty(schemas.ICloudFormationInitService['enabled'])
    files = FieldProperty(schemas.ICloudFormationInitService['files'])
    sources = FieldProperty(schemas.ICloudFormationInitService['sources'])
    packages = FieldProperty(schemas.ICloudFormationInitService['packages'])
    commands = FieldProperty(schemas.ICloudFormationInitService['commands'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.files = []
        self.packages = {}
        self.commands = []
        self.sources = []

@implementer(schemas.ICloudFormationInitServiceCollection)
class CloudFormationInitServiceCollection(Named, dict):

    def export_as_troposphere(self):
        out = {}
        for key, service_obj in self.items():
            service_dict = {}
            for name in ('ensure_running', 'enabled', 'files', 'sources', 'packages', 'commands'):
                value = getattr(service_obj, name)
                if name == 'ensure_running':
                    name = 'ensureRunning'
                if value != None:
                    service_dict[name] = value
            out[key] = service_dict
        return out

@implementer(schemas.ICloudFormationInitServices)
class CloudFormationInitServices(Named):
    sysvinit = FieldProperty(schemas.ICloudFormationInitServices['sysvinit'])
    windows = FieldProperty(schemas.ICloudFormationInitServices['windows'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.sysvinit = CloudFormationInitServiceCollection('sysvinit', self)
        self.windows = CloudFormationInitServiceCollection('windows', self)

    def export_as_troposphere(self):
        out = {}
        if self.sysvinit:
            out['sysvinit'] = self.sysvinit.export_as_troposphere()
        if self.windows:
            out['windows'] = self.windows.export_as_troposphere()
        return out

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
        self.services = CloudFormationInitServices('services', self)
        self.sources = CloudFormationInitSources('sources', self)
        self.groups = CloudFormationInitGroups('groups', self)
        self.users = CloudFormationInitUsers('users', self)

    def export_as_troposphere(self):
        out = {}
        for name in ('packages', 'files', 'commands', 'services', 'sources', 'groups', 'users'):
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