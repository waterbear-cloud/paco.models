"""
References
"""

import re
import zope.schema
from zope.schema.interfaces import ITextLine
from zope.interface import implementer, Interface
from operator import itemgetter

class AimReference():

    def is_ref(self, aim_ref):
        ref_types = ["netenv.ref", "service.ref", "config.ref", "function.ref"]
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

    def constraint(self, value):
        """
        Limit text to the format 'word.ref chars_here.more-chars.finalchars100'
        """
        match = re.match("(\w+)\.ref\s+(.*)", value)
        if match:
            ref_type, ref_value = match.groups()
            if ref_type not in ('service','netenv','config'):
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


def resolve_ref(value, project, account_ctx=None):
    #return '' # XXX until we rework where ref values are stored to avoid schema conflicts
    aim_ref = AimReference()
    if aim_ref.is_ref(value) == False:
        return None

    ref = Reference(value)
    if ref.type == "service":
        if ref.parts[0] == 'ec2':
            return project['ec2'].resolve_ref(ref)
        return project[ref.parts[0]].resolve_ref_obj.resolve_ref(ref)
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
        for part_idx in range(4, len(ref.parts)):
            try:
                obj = obj[ref.parts[part_idx]]
            except (TypeError, KeyError):
                attr_obj = getattr(obj, ref.parts[part_idx], None)
                if attr_obj and not isinstance(attr_obj, str):
                    obj = attr_obj
                else:
                    break

        if isinstance(obj, str):
            pass
        ref.resource_ref = '.'.join(ref.parts[part_idx:])
        ref.resource = obj
        return obj.resolve_ref(ref)

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
    return project[ref.parts[0]][ref.parts[1]].account_id