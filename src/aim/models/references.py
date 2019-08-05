"""
References
"""

import re
import zope.schema
from aim.models.exceptions import InvalidAimReference
from zope.schema.interfaces import ITextLine
from zope.interface import implementer, Interface
from operator import itemgetter

def is_ref(aim_ref):
    """Determines if the string value is an AIM Reference"""

    if aim_ref.startswith('aim.ref ') == False:
        return False
    ref_types = ["netenv", "resource", "accounts", "function", "service"]
    for ref_type in ref_types:
        if aim_ref.startswith('aim.ref %s.' % ref_type):
            return True
    return False

class TextReference(zope.schema.Text):

    def __init__(self, *args, **kwargs):
        self.str_ok = False
        if 'str_ok' in kwargs.keys():
            self.str_ok = kwargs['str_ok']
            del kwargs['str_ok']
        super().__init__(*args, **kwargs)

    def constraint(self, value):
        """
        Limit text to the format 'word.ref chars_here.more-chars.finalchars100'
        """
#        if value.find('patch.<account>.<region>.applications.patch.groups.lambda.resources.snstopic.arn') != -1:
        if self.str_ok and is_ref(value) == False:
            if isinstance(value, str) == False:
                return False
            return True

        return is_ref(value)

        match = re.match("(\w+)\.ref\s+(.*)", value)
        if match:
            ref_type, ref_value = match.groups()
            if ref_type not in ('resource','service','netenv','config', 'function'):
                return False
            for part in ref_value.split('.'):
                if not re.match("[\w-]+", part):
                    return False
            return True
        else:
            return False

class Reference():
    """
    Reference to something in the aim.model

    attributes:
      raw : original reference str : 'aim.ref netenv.aimdemo.network.vpc.security_groups.app.lb'
      type : reference type str : 'netenv'
      parts : list of ref parts : ['netenv', 'aimdemo', 'network', 'vpc', 'security_groups', 'app', 'lb']
      ref : reffered string : 'netenv.aimdemo.network.vpc.security_groups.app.lb'
    """

    def __init__(self, value):
        self.raw = value
        #match = re.match("aim\.ref\s+(.*)", value)
        self.ref = value.split(' ', 2)[1]
        self.parts = self.ref.split('.')
        self.type = self.parts[0]
        # resource_ref is the tail end of the reference that is
        # relevant to the Resource it references
        self.resource = None
        self.resource_ref = None

        if is_ref(self.raw) == False:
            print("Invalid AIM Reference: %s" % (value))
            #raise StackException(AimErrorCode.Unknown)

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

    def set_region(self, region):
        self.sub_part('<region>', region)

    def resolve(self, project, account_ctx=None):
        return resolve_ref(
            ref_str=None,
            project=project,
            account_ctx=account_ctx,
            ref=self
        )

def get_resolve_ref_obj(obj, ref, value, part_idx_start):
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
            break

    ref.resource_ref = '.'.join(ref.parts[part_idx:])
    ref.resource = obj
    try:
        response = obj.resolve_ref(ref)
    except AttributeError:
        raise InvalidAimReference("Invalid AIM Reference for resource: {0}: '{1}'".format(type(obj), value))
    return response

def resolve_ref(ref_str, project, account_ctx=None, ref=None):
    """Resolve a reference"""
    if ref == None:
        ref = Reference(ref_str)
    if ref.type == "resource":
        if ref.parts[1] == 's3':
            return get_resolve_ref_obj(project['s3'], ref, ref_str, part_idx_start=2)
        return project[ref.parts[1]].resolve_ref(ref)
    elif ref.type == "service":
        if ref.parts[4] == 'applications':
            obj = project[ref.parts[1]]
            response = get_resolve_ref_obj(obj, ref, ref_str, part_idx_start=4)
            return response
        return project[ref.parts[1]].resolve_ref(ref)
    elif ref.type == "netenv":
        # examples:
        # aim.ref netenv.aimdemo.applications.app.resources.webapp.name
        # aim.ref netenv.aimdemo.applications.app.resources.alb.dns.ssl_certificate.arn
        # aim.ref netenv.aimdemo.iam.app.roles.instance_role.name
        # aim.ref netenv.aimdemo.iam.app.roles.instance_role.arn
        # aim.ref netenv.aimdemo.iam.app.roles.instance_role.profile
        # aim.ref netenv.aimdemo.network.vpc.security_groups.app.bastion
        # aim.ref netenv.aimdemo.network.vpc.security_groups.app.webapp
        # aim.ref netenv.aimdemo.network.vpc.security_groups.app.webapp
        #
        # first two parts are transposed - flip them around before resolving
        #ref.parts[0], ref.parts[1] = ref.parts[1], ref.parts[0]
        obj = project['ne'][ref.parts[1]][ref.parts[2]][ref.parts[3]]
        return get_resolve_ref_obj(obj, ref, ref_str, 4)


    elif ref.type == "accounts":
        return get_accounts_ref_value(ref, project)
    elif ref.type == "function":
        return resolve_function_ref(ref, project, account_ctx)
    else:
        raise ValueError("Unsupported ref type: {}".format(ref.type))

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
        else:
            raise ValueError("Unsupported AMI Name: {}".format(ref.last_part))

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
        return ami_id

def get_accounts_ref_value(ref, project):
    try:
        account_id = project[ref.parts[0]][ref.parts[1]].account_id
    except KeyError:
        raise InvalidAimReference("Can not resolve the reference '{}'".format(ref.raw))
    return account_id