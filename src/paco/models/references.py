"""
References
"""

import os, pathlib
import zope.schema
from paco.models import vocabulary, schemas
from paco.models.exceptions import InvalidPacoReference
import ruamel.yaml
from ruamel.yaml.compat import StringIO
from zope.schema.interfaces import ITextLine
from zope.interface import implementer, Interface
from operator import itemgetter

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
            if ref.parts[0] in ['iam', 'codecommit', 'ec2', 'notificationgroups', 's3', 'route53', 'resources']:
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
        try:
            next_obj = obj[ref.parts[part_idx]]
        except (TypeError, KeyError):
            next_obj = getattr(obj, ref.parts[part_idx], None)
        if next_obj != None and isinstance(next_obj, str) == False:
            obj = next_obj
        else:
            # ToDo: Should this throw an error instead?
            break

    ref.resource_ref = '.'.join(ref.parts[part_idx:])
    ref.resource = obj
    # If we get a dict here, return that as it is probably looking
    # for it, as is the case wit S3. Real fix is to make a container
    # object for the list of buckets in S3.yaml
    # TODO: Fix S3 bucket container
    if hasattr(obj, 'resolve_ref') != True and type(obj) == dict:
        return obj

    try:
        response = obj.resolve_ref(ref)
    except AttributeError:
        # Check if we have something stored in Outputs
        outputs_value = resolve_ref_outputs(ref, project['home'])
        if outputs_value != None:
            return outputs_value
        raise_invalid_reference(ref, obj, ref.parts[part_idx:][0])
    return response

def resolve_ref_outputs(ref, project_folder):
    key = ref.parts[0]
    outputs_path = pathlib.Path(
            os.path.join(
                project_folder,
                'Outputs',
                key+'.yaml'
            ))
    if outputs_path.exists() == False:
        return None

    yaml = YAML(typ="safe", pure=True)
    yaml.default_flow_sytle = False
    with open(outputs_path, "r") as output_fd:
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
        if ref.parts[1] == 's3':
            ref_value = get_resolve_ref_obj(project, project['resource']['s3'], ref, part_idx_start=2)
        else:
            try:
                ref_value = project['resource'][ref.parts[1]].resolve_ref(ref)
            except KeyError:
                raise_invalid_reference(ref, project['resource'], ref.parts[1])
    elif ref.type == "service":
        ref_value = get_resolve_ref_obj(project, project, ref, part_idx_start=0)
        return ref_value
        part_idx_start = 0
        if ref.parts[2] == 'applications':
            # This is the case if the ref does not contain an account and region
            part_idx_start = 2
        elif ref.parts[4] == 'applications':
            part_idx_start = 4
        if part_idx_start > 0:
            obj = project['service'][ref.parts[1]]
            response = get_resolve_ref_obj(project, obj, ref, part_idx_start=part_idx_start)
            ref_value = response
        else:
            ref_value = project[ref.parts[1]].resolve_ref(ref)
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

    # If the reference returned a Stack, and that Stack has not been
    # modified by checking is_stack_cached(), then check the outputs
    # to see if a value is there and return it. Otherwise continue
    # to deal with waiting for new stack outputs.
    # XXX: Disabled
    if True == False and 'home' in project.keys():
        value_type = "{}".format(type(ref_value))
        if value_type == "<class 'paco.stack_group.stack_group.Stack'>":
            # TODO: This is only useful when we are looking up values
            # for stacks that will not be provisioned. ie. SNS Topic Arns
            # from NotificationGroups referenced by code in Network Environments.
            # XXX: For now we are only looking at cached outputs for stacks
            # outside of NetworkEnvironments.
            # XXX: This check causes a Stack cache check which queries
            # cloudformation which incurs a delay
            if ref.ref.startswith('netenv') == False:
                if ref_value.is_stack_cached():
                    outputs_value = resolve_ref_outputs(ref, project['home'])
                    if outputs_value != None:
                        return outputs_value
    return ref_value


def resolve_function_ref(ref, project, account_ctx):
    if account_ctx == None:
        return None
    if ref.ref.startswith('function.aws.ec2.ami.latest'):
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
        else:
            raise ValueError("Unsupported AMI Name: {}".format(ref.last_part))

        cache_id = ami_name + ami_description
        if cache_id in ami_cache.keys():
            return ami_cache[cache_id]

        ec2_client = account_ctx.get_aws_client('ec2')
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
            'Values': ['137112412989']
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

def resolve_accounts_ref(ref, project):
    "Return an IAccount object from the model."
    try:
        account = project[ref.parts[0]][ref.parts[1]]
    except KeyError:
        raise InvalidPacoReference("Can not resolve the reference '{}'".format(ref.raw))

    return account.resolve_ref(ref)

