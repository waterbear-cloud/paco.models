"""
All things network.
"""

import aim.models.apps
import aim.models.iam
from aim.models.base import Name, Named, Deployable
from aim.models import schemas
from aim.models import vocabulary
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from aim.models import loader
from aim.models import references

@implementer(schemas.INetworkEnvironments)
class NetworkEnvironments(Named, dict):
    pass


@implementer(schemas.INetworkEnvironment)
class NetworkEnvironment(Named, Deployable, dict):
    """
    Object attrs:
        - environments : dict : Network Environment
        - vpc : obj : instance of VPC model class
        - segments : obj : what are these?

    Container:
        - Dictionary of Environment objects
    """
    availability_zones = FieldProperty(schemas.INetworkEnvironment["availability_zones"])
    vpc = FieldProperty(schemas.INetworkEnvironment["vpc"])

    def environment_pairs(self):
        "Returns a List of Tuples of sorted Environment pairs"
        # used to build UI
        pairs = []
        count = 0
        temp_env = None
        envs = list(self.values())
        for env in envs:
            if count == 0:
                temp_env = env
                count += 1
            else:
                pairs.append( (temp_env, env) )
                count = 0
        if count == 1: # got a left-over
            pairs.append( (temp_env, None))
        return pairs

    @property
    def environments(self):
        return self


@implementer(schemas.IEnvironment)
class Environment(Named, dict):

    @property
    def env_regions(self):
        """Filter out the default and only return EnvironmentRegion instances"""
        results = {}
        for k, v in self.items():
            if k != 'default':
                results[k] = v
        return results


@implementer(schemas.IEnvironmentDefault)
class EnvironmentDefault(Named, dict):

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)

        # applications
        self.applications = aim.models.apps.ApplicationEngines(
            name='applications',
            __parent__=self
        )
        self.applications.title = 'Applications'
        self.__setitem__('applications', self.applications)

        # network
        self.network = Network(
            name='network',
            __parent__=self
        )
        self.network.title = 'Network'
        self.__setitem__('network', self.network)

        # IAM
        self.iam = aim.models.iam.IAMs(
            name='iam',
            __parent__=self
        )
        self.iam.title = 'Identity and Access Management'
        self.__setitem__('iam', self.iam)


@implementer(schemas.IEnvironmentRegion)
class EnvironmentRegion(EnvironmentDefault, Deployable, dict):

    @property
    def title_or_name(self):
        return self.region_full_name

    @property
    def region(self):
        # an EnvironmentRegion *must* always be a valid region name
        return self.__name__

    @property
    def region_full_name(self):
        return vocabulary.aws_regions[self.__name__]['full_name']

@implementer(schemas.INetwork)
class Network(NetworkEnvironment):
    aws_account = FieldProperty(schemas.INetwork["aws_account"])

    def resolve_ref(self, ref):
        if ref.resource_ref == 'aws_account':
            return self.aws_account
        return None

@implementer(schemas.IVPC)
class VPC():
    "VPC"
    cidr = FieldProperty(schemas.IVPC["cidr"])
    enable_dns_hostnames = FieldProperty(schemas.IVPC["enable_dns_hostnames"])
    enable_dns_support = FieldProperty(schemas.IVPC["enable_dns_support"])
    enable_internet_gateway = FieldProperty(schemas.IVPC["enable_internet_gateway"])
    nat_gateway = FieldProperty(schemas.IVPC["nat_gateway"])
    vpn_gateway = FieldProperty(schemas.IVPC["vpn_gateway"])
    private_hosted_zone = FieldProperty(schemas.IVPC["private_hosted_zone"])
    security_groups = FieldProperty(schemas.IVPC["security_groups"])
    segments = FieldProperty(schemas.IVPC["segments"])

@implementer(schemas.IInternetGateway)
class InternetGateway(Deployable):
    pass

@implementer(schemas.INATGateway)
class NATGateway(Deployable, dict):
    availability_zone = FieldProperty(schemas.INATGateway["availability_zone"])
    segment = FieldProperty(schemas.INATGateway["segment"])
    default_route_segments = FieldProperty(schemas.INATGateway["default_route_segments"])

@implementer(schemas.IVPNGateway)
class VPNGateway(Deployable, dict):
    pass

@implementer(schemas.IPrivateHostedZone)
class PrivateHostedZone(Deployable):
    name = FieldProperty(schemas.IPrivateHostedZone["name"])

#@implementer(schemas.ISecurityGroups)
#class SecurityGroups(dict):
#    pass

@implementer(schemas.ISecurityGroup)
class SecurityGroup():
    group_name = FieldProperty(schemas.ISecurityGroup["group_name"])
    group_description = FieldProperty(schemas.ISecurityGroup["group_description"])
    ingress = FieldProperty(schemas.ISecurityGroup["ingress"])
    egress = FieldProperty(schemas.ISecurityGroup["egress"])

    def resolve_ref(self, ref):
        return ref.resource.resolve_ref_obj.resolve_ref(ref)


@implementer(schemas.ISecurityGroupRule)
class SecurityGroupRule():
    name = FieldProperty(schemas.ISecurityGroupRule["name"])
    cidr_ip = FieldProperty(schemas.ISecurityGroupRule["cidr_ip"])
    cidr_ip_v6 = FieldProperty(schemas.ISecurityGroupRule["cidr_ip_v6"])
    description = FieldProperty(schemas.ISecurityGroupRule["description"])
    from_port = FieldProperty(schemas.ISecurityGroupRule["from_port"])
    protocol = FieldProperty(schemas.ISecurityGroupRule["protocol"])
    to_port = FieldProperty(schemas.ISecurityGroupRule["to_port"])
    source_security_group_id = FieldProperty(schemas.ISecurityGroupRule["source_security_group_id"])

@implementer(schemas.IIngressRule)
class IngressRule(SecurityGroupRule):
    pass

@implementer(schemas.IEgressRule)
class EgressRule(SecurityGroupRule):
    pass

@implementer(schemas.ISegment)
class Segment(Deployable):
    internet_access = FieldProperty(schemas.ISegment["internet_access"])
    az1_cidr = FieldProperty(schemas.ISegment["az1_cidr"])
    az2_cidr = FieldProperty(schemas.ISegment["az2_cidr"])
    az3_cidr = FieldProperty(schemas.ISegment["az3_cidr"])
    az4_cidr = FieldProperty(schemas.ISegment["az4_cidr"])
    az5_cidr = FieldProperty(schemas.ISegment["az5_cidr"])
    az6_cidr = FieldProperty(schemas.ISegment["az6_cidr"])

    def resolve_ref(self, ref):
        if ref.resource_ref == 'az1_cidr':
            return self.az1_cidr
        #elif ref_parts[1] == 'subnet_id':
        else:
            # XXX: Load az1.subnet_id from Resources YAML
            # XXX: If not in Resources YAML return the Engine Object
            # else return the Stack() for future StackOutput retrieval. The stack still needs
            # to be created.
            stack = self.resolve_ref_obj.resolve_ref(ref)
            if stack == None:
                raise StackException(AimErrorCode.Unknown)
            else:
                return stack
        return None

@implementer(schemas.IRoute53HostedZone)
class Route53HostedZone(Deployable):
    domain_name = FieldProperty(schemas.IRoute53HostedZone["domain_name"])
    account = FieldProperty(schemas.IRoute53HostedZone["account"])

    def has_record_sets(self):
        return False

@implementer(schemas.IRoute53)
class Route53():

    hosted_zones = FieldProperty(schemas.IRoute53["hosted_zones"])

    def __init__(self, config_dict):
        super().__init__()

        self.zones_by_account = {}
        loader.apply_attributes_from_config(self, config_dict)

        for zone_id in self.hosted_zones.keys():
            hosted_zone = self.hosted_zones[zone_id]
            aws_account_ref = hosted_zone.account
            aim_ref = references.AimReference()
            ref_dict = aim_ref.parse_ref(aws_account_ref)
            account_name = ref_dict['ref_parts'][1]
            if account_name not in self.zones_by_account:
                self.zones_by_account[account_name] = []
            self.zones_by_account[account_name].append(zone_id)

    def get_hosted_zones_account_names(self):
        return sorted(self.zones_by_account.keys())

    def get_zone_ids(self, account_name=None):
        if account_name != None:
            return self.zones_by_account[account_name]
        return sorted(self.hosted_zones.keys())

    def account_has_zone(self, account_name, zone_id):
        if zone_id in self.zones_by_account[account_name]:
            return True
        return False


