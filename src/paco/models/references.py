"""
Paco References
"""

from paco.models import vocabulary, schemas
from paco.models.exceptions import InvalidPacoReference
from ruamel.yaml.compat import StringIO
from zope.schema.interfaces import ITextLine
from zope.interface import implementer, Interface
from operator import itemgetter
import importlib
import os
import pathlib
import ruamel.yaml
import zope.schema


ami_cache = {}

class YAML(ruamel.yaml.YAML):
    def dump(self, data, stream=None, **kw):
        dumps = False
        if stream is None:
            dumps = True
            stream = StringIO()
        ruamel.yaml.YAML.dump(self, data, stream, **kw)
        if dumps:
            return stream.getvalue()


class InvalidPacoReferenceString(zope.schema.ValidationError):
    __doc__ = 'PacoReference must be of type (string)'

class InvalidPacoReferenceStartsWith(zope.schema.ValidationError):
    __doc__ = "PacoReference must begin with 'paco.ref'"

class InvalidPacoReferenceRefType(zope.schema.ValidationError):
    __doc__ = "PacoReference 'paco.ref must begin with: netenv | resource | accounts | function | service"

def is_ref(paco_ref, raise_enabled=False):
    """Determines if the string value is a Paco reference"""
    if type(paco_ref) != type(str()):
        if raise_enabled: raise InvalidPacoReferenceString
        return False
    if paco_ref.startswith('paco.ref ') == False:
        if raise_enabled: raise InvalidPacoReferenceStartsWith
        return False
    ref_types = ["netenv", "resource", "accounts", "function", "service"]
    for ref_type in ref_types:
        if paco_ref.startswith('paco.ref %s.' % ref_type):
            return True
    if raise_enabled: raise InvalidPacoReferenceRefType
    return False

class FileReference():
    pass

class StringFileReference(FileReference, zope.schema.Text):
    """Path to a file on the filesystem"""

    def constraint(self, value):
        """
        Validate that the path resolves to a file on the filesystem
        """
        return True
        # ToDo: how to get the PACO_HOME and change to that directory from here?
        #path = pathlib.Path(value)
        #return path.exists()

class YAMLFileReference(FileReference, zope.schema.Object):
    """Path to a YAML file"""

    def __init__(self, **kw):
        self.schema = Interface
        self.validate_invariants = kw.pop('validate_invariants', True)
        super(zope.schema.Object, self).__init__(**kw)

class PacoReference(zope.schema.Text):

    def __init__(self, *args, **kwargs):
        self.str_ok = False
        self.schema_constraint = ''
        if 'str_ok' in kwargs.keys():
            self.str_ok = kwargs['str_ok']
            del kwargs['str_ok']
        # schema_constraint is a string name of an ISchema
        # if a Schema is passed, it is converted to a string
        if 'schema_constraint' in kwargs.keys():
            self.schema_constraint = kwargs['schema_constraint']
            if hasattr(self.schema_constraint, '__name__'):
                self.schema_constraint = self.schema_constraint.__name__
            del kwargs['schema_constraint']
        super().__init__(*args, **kwargs)

    def constraint(self, value):
        """
        Limit text to the format 'word.ref chars_here.more-chars.finalchars100'
        """
        if self.str_ok and is_ref(value) == False:
            if isinstance(value, str) == False:
                raise InvalidPacoReferenceString
                #return False
            return True

        return is_ref(value, raise_enabled=True)


class Reference():
    """
    Reference to something in the paco.models

    attributes:
      raw : original reference str : 'paco.ref netenv.pacodemo.network.vpc.security_groups.app.lb'
      type : reference type str : 'netenv'
      parts : list of ref parts : ['netenv', 'pacodemo', 'network', 'vpc', 'security_groups', 'app', 'lb']
      ref : reffered string : 'netenv.pacodemo.network.vpc.security_groups.app.lb'
    """

    def __init__(self, value):
        self.raw = value
        self.ref = value.split(' ', 2)[1]
        self.parts = self.ref.split('.')
        self.type = self.parts[0]
        # resource_ref is the tail end of the reference that is
        # relevant to the Resource it references
        self.resource = None
        self.resource_ref = None
        self.region = None

        if self.type == 'netenv':
            # do not try to find region for short environment refs like 'paco.ref netenv.mynet.prod'
            if len(self.parts) > 3:
                if self.parts[3] in vocabulary.aws_regions.keys():
                    self.region = self.parts[3]

        if is_ref(self.raw) == False:
            print("Invalid Paco reference: %s" % (value))
            #raise StackException(PacoErrorCode.Unknown)

    @property
    def last_part(self):
        return self.parts[-1]

    def next_part(self, search_ref):
        search_parts = search_ref.split('.')
        first_found = False
        for ref_part in self.parts:
            if first_found == True:
                if search_idx == len(search_parts):
                    return ref_part
                elif ref_part == search_parts[search_idx]:
                    search_idx += 1
            elif ref_part == search_parts[0]:
                first_found = True
                search_idx = 1

        return None

    def sub_part(self, part, value):
        self.raw = self.raw.replace(part, value)
        self.ref = self.ref.replace(part, value)
        self.parts = self.ref.split('.')

    def set_account_name(self, account_name):
        self.sub_part('<account>', account_name)

    def set_environment_name(self, environment_name):
        self.sub_part('<environment>', environment_name)

    def set_region(self, region):
        self.region = region
        self.sub_part('<region>', region)

    def resolve(self, project, account_ctx=None):
        return resolve_ref(
            ref_str=None,
            project=project,
            account_ctx=account_ctx,
            ref=self
        )

def get_model_obj_from_ref(ref, project):
    """Resolves the reference to an object in a model.
    ref can be either a string or a Reference object.
    project is an Project object.
    """
    # ToDo: initial implementation - do we have ref corner cases to consider?
    if isinstance(ref, str):
        ref = Reference(ref)
    obj = project
    for part_idx in range(0, len(ref.parts)):
        # special case for resource.route53 hosted zone look-ups
        if schemas.IRoute53Resource.providedBy(obj):
            obj = obj.hosted_zones
        try:
            next_obj = obj[ref.parts[part_idx]]
        except (TypeError, KeyError):
            next_obj = getattr(obj, ref.parts[part_idx], None)
        if next_obj != None and isinstance(next_obj, str) == False:
            obj = next_obj
        else:
            message = "\nCould not find model at {}\n".format(ref.raw)
            if ref.parts[0] in ['iam', 'codecommit', 'ec2', 'snstopics', 's3', 'route53', 'resources']:
                message += "Did you mean to run:\n"
                message += "paco <command> resource.{}?\n".format(ref.ref)
            raise InvalidPacoReference(message)
    return obj

def get_resolve_ref_obj(project, obj, ref, part_idx_start):
    """
    Traverses the reference parts looking for the last child that
    is a not a string. This object is expected to be a part of the
    model and should have a resolve_ref method that can be called.
    """
    for part_idx in range(part_idx_start, len(ref.parts)):
        # the model can be walked with either obj[name] or obj.name
        # depending on what is being walked
        name = ref.parts[part_idx]
        try:
            next_obj = obj[name]
        except (TypeError, KeyError):
            next_obj = getattr(obj, name, None)
        if next_obj != None and isinstance(next_obj, str) == False:
            obj = next_obj
        else:
            # Given a ref of 'netenv.websites.prod.[...].resources.database.endpoint.address' then
            # after walks to the RDS Resource named '.database' it won't be able to find the next '.endpoint'
            # and will break here
            break

    ref.resource_ref = '.'.join(ref.parts[part_idx:])
    ref.resource = obj
    try:
        response = obj.resolve_ref(ref)
    except AttributeError:
        # Check if we have something stored in Outputs
        outputs_value = resolve_ref_outputs(ref, project['home'])
        if outputs_value != None:
            return outputs_value
        raise_invalid_reference(ref, obj, ref.parts[part_idx:][0])
    return response

def resolve_ref_outputs(ref, project_home_path):
    key = ref.parts[0]
    # ToDo: .paco-work is part of paco not paco.models, refactor?
    output_filepath = pathlib.Path(project_home_path) / '.paco-work' / 'outputs' / key
    output_filepath = output_filepath.with_suffix('.yaml')
    if output_filepath.exists() == False:
        return None

    yaml = YAML(typ="safe", pure=True)
    yaml.default_flow_sytle = False
    with open(output_filepath, "r") as output_fd:
        outputs_dict = yaml.load(output_fd)

    for part in ref.parts:
        if part not in outputs_dict.keys():
            break
        node = outputs_dict[part]
        outputs_dict = node
        if len(list(node.keys())) == 1 and '__name__' in node.keys():
            return node['__name__']

    return None

def raise_invalid_reference(ref, obj, name):
    """Takes the ref attempting to be looked-up,
    an obj that was the last model traversed too,
    the name that failed the next look-up.
    """
    raise InvalidPacoReference("""
Invalid Paco reference:
{}

Reference look-up failed at '{}' trying to find name '{}'.
""".format(ref.raw, obj.paco_ref_parts, name))

def resolve_ref(ref_str, project, account_ctx=None, ref=None):
    """Resolve a reference"""
    if ref == None:
        ref = Reference(ref_str)
    ref_value = None
    if ref.type == "resource":
        try:
            ref_value = project['resource'][ref.parts[1]].resolve_ref(ref)
        except KeyError:
            raise_invalid_reference(ref, project['resource'], ref.parts[1])
    elif ref.type == "service":
        return get_resolve_ref_obj(project, project, ref, part_idx_start=0)
    elif ref.type == "netenv":
        try:
            obj = project['netenv']
            for i in range(1,4):
                obj = obj[ref.parts[i]]
        except KeyError:
            raise_invalid_reference(ref, obj, ref.parts[i])
        ref_value = get_resolve_ref_obj(project, obj, ref, 4)

    elif ref.type == "accounts":
        ref_value = resolve_accounts_ref(ref, project)
    elif ref.type == "function":
        ref_value = resolve_function_ref(ref, project, account_ctx)
    else:
        raise ValueError("Unsupported ref type: {}".format(ref.type))

    return ref_value

def function_ec2_ami_latest(ref, project, account_ctx):
    """EC2 AMI latest"""
    ami_description = None
    ami_name = None
    if ref.last_part == 'amazon-linux-2':
        ami_description = "Amazon Linux 2 AMI*"
        ami_name = 'amzn2-ami-hvm-*'
    elif ref.last_part == 'amazon-linux':
        ami_description = "Amazon Linux AMI*"
        ami_name = 'amzn-ami-hvm-*'
    elif ref.last_part == 'amazon-linux-nat':
        ami_description = "Amazon Linux AMI*"
        ami_name = 'amzn-ami-vpc-nat-hvm-*'
    elif ref.last_part == 'amazon-linux-2-ecs':
        ami_description = "Amazon Linux AMI*"
        ami_name = "amzn2-ami-ecs-hvm-*"
    else:
        raise ValueError("Unsupported AMI Name: {}".format(ref.last_part))

    cache_id = ami_name + ami_description
    if cache_id in ami_cache.keys():
        return ami_cache[cache_id]

    ec2_client = account_ctx.get_aws_client('ec2', aws_region=ref.region)
    filters = [ {
        'Name': 'name',
        'Values': [ami_name]
    },{
        'Name': 'description',
        'Values': [ami_description]
    },{
        'Name': 'architecture',
        'Values': ['x86_64']
    },{
        'Name': 'owner-alias',
        'Values': ['amazon']
    },{
        'Name': 'owner-id',
        'Values': ['*']
    },{
        'Name': 'state',
        'Values': ['available']
    },{
        'Name': 'root-device-type',
        'Values': ['ebs']
    },{
        'Name': 'virtualization-type',
        'Values': ['hvm']
    },{
        'Name': 'hypervisor',
        'Values': ['xen']
    },{
        'Name': 'image-type',
        'Values': ['machine']
    } ]

    ami_list= ec2_client.describe_images(
        Filters=filters,
        Owners=[
            'amazon'
        ]
    )
    # Sort on Creation date Desc
    image_details = sorted(ami_list['Images'],key=itemgetter('CreationDate'),reverse=True)
    ami_id = image_details[0]['ImageId']
    ami_cache[cache_id] = ami_id
    return ami_id

def import_and_call_function(ref, project, account_ctx):
    "Import a module and call a function in it with the Reference, Project and AccountContext"
    module_name = '.'.join(ref.parts[1:-1])
    if module_name.find(':') != -1:
        module_name = module_name.split(':')[0]
        function_name = module_name.split('.')[-1:][0]
        module_name = '.'.join(module_name.split('.')[:-1])
        module = importlib.import_module(module_name)
        extra_context = ref.raw.split(':')[1]
        return getattr(module, function_name)(ref, extra_context, project, account_ctx)
    else:
        function_name = ref.parts[-1:][0]
        module = importlib.import_module(module_name)
        return getattr(module, function_name)(ref, project, account_ctx)

def resolve_function_ref(ref, project, account_ctx):
    if account_ctx == None:
        return None
    if ref.ref.startswith('function.aws.ec2.ami.latest'):
        # ToDo: call this as a proper function ref? migrate it?
        return function_ec2_ami_latest(ref, project, account_ctx)
    else:
        return import_and_call_function(ref, project, account_ctx)

def resolve_accounts_ref(ref, project):
    "Return an IAccount object from the model."
    try:
        account = project[ref.parts[0]][ref.parts[1]]
    except KeyError:
        raise InvalidPacoReference("Can not resolve the reference '{}'".format(ref.raw))

    return account.resolve_ref(ref)

