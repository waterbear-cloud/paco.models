"""
References
"""

import re
import zope.schema
from aim.models.exceptions import InvalidAimReference
from zope.schema.interfaces import ITextLine
from zope.interface import implementer, Interface
from operator import itemgetter

class AimReference():

    def is_ref(self, aim_ref):
        ref_types = ["netenv.ref", "resource.ref", "config.ref", "function.ref", "service.ref"]
        for ref_type in ref_types:
            if aim_ref.startswith(ref_type):
                return True
        return False

    def parse_netenv_ref(self, aim_ref, ref_parts):
        ref_dict = {}
        ref_dict['subenv_id'] = ""
        ref_dict['netenv_component'] = ""
        ref_dict['subenv_component'] = ""
        if ref_parts[0] == 'this':
            ref_dict['netenv_id'] = self.this_netenv_id
        else:
            ref_dict['netenv_id'] = ref_parts[0]

        if ref_parts[1] == 'subenv':
            ref_dict['subenv_component'] = ref_parts[1]
            ref_dict['subenv_id'] = ref_parts[2]
            ref_dict['subenv_region'] = ref_parts[3]
            ref_dict['netenv_component'] = ref_parts[4]
        else:
            ref_dict['netenv_component'] = ref_parts[1]
        return ref_dict

    def parse_ref(self, aim_ref):
        ref_parts = aim_ref.split(' ')
        if len(ref_parts) != 2:
            raise ValueError("Invalid aim_ref: {}".format(aim_ref))
            #raise StackException(AimErrorCode.Unknown)
        ref_type = ref_parts[0]
        config_ref = ref_parts[1]
        location_parts = ref_parts[1].split('.')
        ref_dict = {}
        if ref_parts[0] == 'netenv.ref':
            ref_dict = self.parse_netenv_ref(aim_ref, location_parts)
        elif self.is_ref(aim_ref):
            pass
        else:
            print(ref_parts[0])
            raise ValueError("Invalid aim_ref: {}".format(aim_ref))
            #raise StackException(AimErrorCode.Unknown)
        ref_dict['type'] = ref_type
        ref_dict['ref'] = config_ref
        ref_dict['ref_parts'] = location_parts
        ref_dict['raw'] = aim_ref

        return ref_dict


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
        if self.str_ok:
            if isinstance(value, str) == False:
                return False
            return True

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
      raw : original reference str : 'netenv.ref aimdemo.network.vpc.security_groups.app.lb'
      type : reference type str : 'netenv'
      parts : list of ref parts : ['aimdemo', 'network', 'vpc', 'security_groups', 'app', 'lb']
      ref : reffered string : 'aimdemo.network.vpc.security_groups.app.lb'
    """

    def __init__(self, value):
        self.raw = value
        match = re.match("(\w+)\.ref\s+(.*)", value)
        self.type, self.ref = match.groups()
        self.parts = self.ref.split('.')
        # resource_ref is the tail end of the reference that is
        # relevant to the Resource it references
        self.resource = None
        self.resource_ref = None

        aim_ref = AimReference()
        if aim_ref.is_ref(self.raw) == False:
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

def get_resolve_ref_obj(obj, ref, value, part_idx_start):
    for part_idx in range(part_idx_start, len(ref.parts)):
        try:
            next_obj = obj[ref.parts[part_idx]]
        except (TypeError, KeyError):
            next_obj = getattr(obj, ref.parts[part_idx], None)
        if next_obj != None and isinstance(next_obj, str) == False:
            obj = next_obj
        else:
            break

    if isinstance(obj, str):
        pass
    ref.resource_ref = '.'.join(ref.parts[part_idx:])
    ref.resource = obj
    try:
        response = obj.resolve_ref(ref)
    except AttributeError:
        raise InvalidAimReference("Invalid AIM Reference for resource: {0}: '{1}'".format(type(obj), value))
    return response

def resolve_ref(value, project, account_ctx=None):
    #return '' # XXX until we rework where ref values are stored to avoid schema conflicts
    aim_ref = AimReference()
    if aim_ref.is_ref(value) == False:
        return None

    ref = Reference(value)
    if ref.type == "resource":
        if ref.parts[0] == 's3':
            return get_resolve_ref_obj(project['s3'], ref, value, 1)
        return project[ref.parts[0]].resolve_ref(ref)
    elif ref.type == "service":
        if ref.parts[3] == 'applications':
            obj = project[ref.parts[0]]
            response = get_resolve_ref_obj(obj, ref, value, 3)
            return response
        return project[ref.parts[0]].resolve_ref(ref)
    elif ref.type == "netenv":
        # examples:
        # netenv.ref aimdemo.applications.app.resources.webapp.name
        # netenv.ref aimdemo.applications.app.resources.alb.dns.ssl_certificate.arn
        # netenv.ref aimdemo.iam.app.roles.instance_role.name
        # netenv.ref aimdemo.iam.app.roles.instance_role.arn
        # netenv.ref aimdemo.iam.app.roles.instance_role.profile
        # netenv.ref aimdemo.network.vpc.security_groups.app.bastion
        # netenv.ref aimdemo.network.vpc.security_groups.app.webapp
        # netenv.ref aimdemo.network.vpc.security_groups.app.webapp
        #
        # first two parts are transposed - flip them around before resolving
        #ref.parts[0], ref.parts[1] = ref.parts[1], ref.parts[0]
        obj = project['ne'][ref.parts[0]][ref.parts[2]][ref.parts[3]]
        return get_resolve_ref_obj(obj, ref, value, 4)


    elif ref.type == "config":
        return get_config_ref_value(ref, project)
    elif ref.type == "function":
        return resolve_function_ref(ref, project, account_ctx)
    else:
        raise ValueError("Unsupported ref type: {}".format(ref.type))

def resolve_function_ref(ref, project, account_ctx):
    if account_ctx == None:
        return None
    if ref.ref.startswith('aws.ec2.ami.latest'):
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

def get_config_ref_value(ref, project):
    # Only config item is accounts at the moment
    try:
        account_id = project[ref.parts[0]][ref.parts[1]].account_id
    except KeyError:
        raise InvalidAimReference("Can not resolve the reference '{}'".format(ref.raw))
    return account_id