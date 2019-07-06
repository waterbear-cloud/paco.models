import itertools, os, copy
import ruamel.yaml
import zope.schema
import zope.schema.interfaces
from aim.models.logging import get_logger
from aim.models.exceptions import InvalidAimProjectFile
from aim.models.metrics import MonitorConfig, Metric, ec2core, CloudWatchAlarm, AlarmSet, AlarmSets
from aim.models.metrics import LogSets, LogSet, LogCategory, LogSource, CWAgentLogSource
from aim.models.networks import NetworkEnvironment, Environment, EnvironmentDefault, \
    EnvironmentRegion, Segment, Network, VPC, NATGateway, VPNGateway, PrivateHostedZone, \
    SecurityGroup, IngressRule, EgressRule, Route53, Route53HostedZone
from aim.models.project import Project, Credentials
from aim.models.apps import ApplicationEngines, ApplicationEngine, Application, ResourceGroup
from aim.models.resources import CodePipeBuildDeploy, ASG, Resource, Resources,LBApplication, \
    TargetGroup, Listener, DNS, PortProtocol, EC2, S3Bucket, S3BucketPolicy, \
    AWSCertificateManager, ListenerRule, Lambda, LambdaEnvironment
from aim.models.governance import Governance, GovernanceService, GovernanceMonitoring
from aim.models.iam import IAMs, IAM, ManagedPolicy, Role, Policy, AssumeRolePolicy, Statement
from aim.models.base import get_all_fields
from aim.models.storages import RDS, CodeCommit, CodeCommitRepository
from aim.models.accounts import Account, AdminIAMUser
from aim.models.references import TextReference
from aim.models.vocabulary import aws_regions
from aim.models.references import resolve_ref
from aim.models.services import EC2Service, EC2KeyPair
from aim.models import schemas
from ruamel.yaml.compat import StringIO
from zope.schema.interfaces import ConstraintNotSatisfied, ValidationError


class YAML(ruamel.yaml.YAML):
    def dump(self, data, stream=None, **kw):
        dumps = False
        if stream is None:
            dumps = True
            stream = StringIO()
        ruamel.yaml.YAML.dump(self, data, stream, **kw)
        if dumps:
            return stream.getvalue()

logger = get_logger()

RESOURCES_CLASS_MAP = {
    'ASG': ASG,
    'CodePipeBuildDeploy': CodePipeBuildDeploy,
    'ACM': AWSCertificateManager,
    'RDS': RDS,
    'LBApplication': LBApplication,
    'EC2': EC2,
    'Lambda': Lambda,
    'ManagedPolicy': ManagedPolicy,
    'S3Bucket': S3Bucket
}

SUB_TYPES_CLASS_MAP = {
    # Resource sub-objects
    LBApplication: {
        'target_groups': ('named_dict', TargetGroup),
        'security_groups': ('str_list', TextReference),
        'listeners': ('named_dict', Listener),
        'dns': ('obj_list', DNS),
        'monitoring': ('located_dict', MonitorConfig)
    },
    ASG: {
        'security_groups': ('str_list', TextReference),
        'target_groups': ('str_list', TextReference),
        'monitoring': ('located_dict', MonitorConfig),
        'instance_iam_role': ('unnamed_dict', Role)
    },
    Listener: {
        'redirect': ('unnamed_dict', PortProtocol),
        'rules': ('named_dict', ListenerRule)
    },
    EC2: {
        'security_groups': ('str_list', TextReference)
    },
    MonitorConfig: {
        'metrics': ('obj_list', Metric),
        'alarm_sets': ('alarm_sets', AlarmSets),
        'log_sets': ('log_sets', LogSets),
    },
    CodePipeBuildDeploy: {
        'artifacts_bucket': ('unnamed_dict', S3Bucket),
    },
    S3Bucket: {
        'policy': ('obj_list', S3BucketPolicy)
    },

    # Networking
    NetworkEnvironment: {
        'vpc': ('unnamed_dict', VPC)
    },
    Network: {
        'vpc': ('unnamed_dict', VPC)
    },
    VPC: {
        'nat_gateway': ('named_dict', NATGateway),
        'vpn_gateway': ('named_dict', VPNGateway),
        'private_hosted_zone': ('unnamed_dict', PrivateHostedZone),
        'segments': ('named_dict', Segment),
        'security_groups': ('named_twolevel_dict', SecurityGroup)
    },
    SecurityGroup: {
        'ingress': ('obj_list', IngressRule),
        'egress' : ('obj_list', EgressRule)
    },

    # IAM
    IAM: {
        'roles': ('named_dict', Role)
        #'policies': ('named_dict', ManagedPolicies)
    },
    Role: {
        'policies': ('obj_list', Policy),
        'assume_role_policy': ('unnamed_dict', AssumeRolePolicy)
    },
    Policy: {
        'statement': ('obj_list', Statement)
    },
    Statement: {
        'action': ('str_list', zope.schema.TextLine),
        'resource': ('str_list', zope.schema.TextLine)
    },
    Lambda: {
        'environment': ('obj_list', LambdaEnvironment)
    },
    ManagedPolicy: {
        'roles': ('str_list', zope.schema.TextLine),
        'statement': ('obj_list', Statement)
    },
    # Accounts
    Account: {
        'admin_iam_users': ('named_dict', AdminIAMUser)
    },
    Route53: {
        'hosted_zones': ('named_dict', Route53HostedZone)
    }
}


def merge(base, override):
    """
    Merge two dictionaries of arbitray depth
    """
    if isinstance(base, dict) and isinstance(override, dict):
        new_dict = dict(base)
        new_dict.update(
            {k: merge(base.get(k, None), override[k]) for k in override}
        )
        return new_dict

    if isinstance(base, list) and isinstance(override, list):
        return [merge(x, y) for x, y in itertools.zip_longest(base, override)]

    return copy.deepcopy(base) if override is None else copy.deepcopy(override)

def annotate_base_config(obj, override_config, base_config):
    """
    Adds attributes prefixed with __base__<name> with values from the
    base configuration for every attribute that has been overriden.
    """
    for name in override_config.keys():
        value = getattr(base_config, name, None)
        if value:
            setattr(obj, '__base__' + name, value)

def get_all_nodes(root):
    "Return a list of all nodes in aim.model"
    nodes = []
    stack = [root]
    while stack:
        cur_node = stack[0]
        stack = stack[1:]
        nodes.append(cur_node)
        if type({}) == type(cur_node) or zope.interface.common.mapping.IMapping.providedBy(cur_node):
            for child in cur_node.values():
                stack.insert(0, child)
        # check for obj or dict attributes
        for field_name, field in get_all_fields(cur_node).items():
            # drill down into objects for non-locatable nodes
            if zope.schema.interfaces.IObject.providedBy(field):
                obj = getattr(cur_node, field_name, None)
                if obj:
                    stack.insert(0, obj)
            elif zope.schema.interfaces.IDict.providedBy(field):
                # dicts are model nodes, don't return them - only their values
                obj = getattr(cur_node, field_name, None)
                if obj:
                    for child in obj.values():
                        stack.insert(0, child)
            elif zope.schema.interfaces.IList.providedBy(field):
                # don't drill down into lists of strings - only lists of model objects
                for obj in getattr(cur_node, field_name, None):
                    if type(obj) != type(''):
                        stack.insert(0, obj)
    return nodes

def add_metric(obj, metric):
    """Add metrics to a resource"""
    if not obj.monitoring:
        obj.monitoring = MonitorConfig('monitoring', obj)
    obj.monitoring.metrics.insert(0, metric)


def most_specialized_interfaces(context):
    """Get interfaces for an object without any duplicates.

    Interfaces in a declaration for an object may already have been seen
    because it is also inherited by another interface. Don't return the
    interface twice, as that would result in duplicate names when creating
    the form.
    """
    declaration = zope.interface.providedBy(context)
    seen = []
    for iface in declaration.flattened():
        if interface_seen(seen, iface):
            continue
        seen.append(iface)
    return seen


def interface_seen(seen, iface):
    """Return True if interface already is seen.
    """
    for seen_iface in seen:
        if seen_iface.extends(iface):
            return True
    return False

def apply_attributes_from_config(obj, config, lookup_config=None):
    """
    Iterates through the field an object's schema has
    and applies the values from configuration.

    Also handles loading of sub-types ...
    """
    # all most-specialized interfaces implemented by obj
    for interface in most_specialized_interfaces(obj):
        fields = zope.schema.getFields(interface)
        for name, field in fields.items():
            # Locatable Objects get their name from their key in the config, for example:
            #   environments:
            #     demo:
            # creates an Environment with the name 'demo'.
            # These objects implement the INamed interface.
            # Do not try to find their 'name' attr from the config.
            if name != 'name' or not schemas.INamed.providedBy(obj):
                value = config.get(name, None)

                # YAML loads "1" as an Int, cast to a Float where expected by the schema
                if zope.schema.interfaces.IFloat.providedBy(field):
                    value = float(value)

                if value != None:
                    # is the value a reference?
                    ref_field = TextReference()
                    try:
                        ref_field._validate(value)
                        # some fields are meant to be reference only
                        if schemas.ITextReference.providedBy(field):
                            setattr(obj, name, value)
                        else:
                            # reference - set a special _ref_ attribute for later look-up
                            setattr(obj, '_ref_' + name, copy.deepcopy(value))

                    except (ValidationError, ConstraintNotSatisfied):
                        # not a reference - set the attribute on the object

                        # ToDo: resources could be loaded here?
                        # resources are loaded later based on type
                        if schemas.IApplication.providedBy(obj) and name == 'groups':
                            continue
                        try:
                            if type(obj) in SUB_TYPES_CLASS_MAP:
                                if name in SUB_TYPES_CLASS_MAP[type(obj)]:
                                    value = sub_types_loader(obj, name, value, lookup_config)
                                    setattr(obj, name, value)
                                else:
                                    setattr(obj, name, copy.deepcopy(value))
                            else:
                                setattr(obj, name, copy.deepcopy(value))
                        except ValidationError as exc:
                            raise InvalidAimProjectFile(
                                "Invalid config for {} => {} (Type: {})\n{}: {}\nSchema error: {}".format(
                                    name, type(obj), value, type(exc), exc.__doc__, exc
                                )
                            )

def sub_types_loader(obj, name, value, lookup_config=None):
    """
    Load sub types
    """
    sub_type, sub_class = SUB_TYPES_CLASS_MAP[type(obj)][name]

    if sub_type == 'named_dict':
        sub_dict = {}
        for sub_key, sub_value in value.items():
            sub_obj = sub_class()
            apply_attributes_from_config(sub_obj, sub_value, lookup_config)
            sub_dict[sub_key] = sub_obj
        return sub_dict

    elif sub_type == 'named_twolevel_dict':
        sub_dict = {}
        for first_key, first_value in value.items():
            sub_dict[first_key]  = {}
            for sub_key, sub_value in first_value.items():
                sub_obj = sub_class()
                apply_attributes_from_config(sub_obj, sub_value, lookup_config)
                sub_dict[first_key][sub_key] = sub_obj
        return sub_dict

    elif sub_type == 'unnamed_dict':
        sub_obj = sub_class()
        apply_attributes_from_config(sub_obj, value, lookup_config)
        return sub_obj

    elif sub_type == 'located_dict':
        sub_obj = sub_class(name, obj)
        apply_attributes_from_config(sub_obj, value, lookup_config)
        return sub_obj

    elif sub_type == 'obj_list':
        sub_list = []
        for sub_value in value:
            sub_obj = sub_class()
            apply_attributes_from_config(sub_obj, sub_value, lookup_config)
            sub_list.append(sub_obj)
        return sub_list

    elif sub_type == 'str_list':
        sub_list = []
        for sub_value in value:
            sub_obj = sub_class().fromUnicode(sub_value)
            sub_list.append(sub_obj)
        return sub_list

    elif sub_type == 'log_sets':
        # Special loading for LogSets
        log_sets = LogSets()
        for log_set_name in value.keys():
            # look-up LogSet by name from base config
            log_set = LogSet()
            for log_category_name, log_category_config in lookup_config['logs']['log_sets'][log_set_name].items():
                log_category = LogCategory(name=log_category_name)
                log_set[log_category_name] = log_category
                for log_source_name, log_source_config in log_category_config.items():
                    log_source = CWAgentLogSource(name=log_source_name)
                    apply_attributes_from_config(log_source, log_source_config)
                    log_category[log_source_name] = log_source
            log_sets[log_set_name] = log_set

            # check for and apply overrides
            if value[log_set_name] is not None:
                for log_category_name in value[log_set_name].keys():
                    if value[log_set_name][log_category_name] is not None:
                        for log_source_name in value[log_set_name][log_category_name].keys():
                            for setting_name, setting_value in value[log_set_name][log_category_name][log_source_name].items():
                                setattr(log_sets[log_set_name][log_category_name][log_source_name], setting_name, setting_value)

        return log_sets

    elif sub_type == 'alarm_sets':
        # Special loading for AlarmSets
        alarm_sets = AlarmSets()
        for alarm_set_name in value.keys():
            # look-up AlarmsSet by Resource type and name
            resource_type = obj.__parent__.type
            alarm_set = AlarmSet()
            alarm_set.resource_type = resource_type
            for alarm_name, alarm_config in lookup_config['alarms'][resource_type][alarm_set_name].items():
                alarm = CloudWatchAlarm(name=alarm_name)
                apply_attributes_from_config(alarm, alarm_config)
                alarm_set[alarm_name] = alarm
            alarm_sets[alarm_set_name] = alarm_set

            # check for and apply overrides
            if value[alarm_set_name] is not None:
                for alarm_name in value[alarm_set_name].keys():
                    for setting_name, setting_value in value[alarm_set_name][alarm_name].items():
                        setattr(alarm_sets[alarm_set_name][alarm_name], setting_name, setting_value)

        return alarm_sets

class ModelLoader():
    """
    Loads YAML config files into aim.model instances
    """

    def __init__(self, aim_ref, config_folder, config_processor=None):
        self.aim_ref = aim_ref
        self.config_folder = config_folder
        self.config_subdirs = {
            "MonitorConfig": self.instantiate_monitor_config,
            "Accounts": self.instantiate_accounts,
            "NetworkEnvironments": self.instantiate_network_environments,
            "Governance": self.instantiate_governance,
            "Services": self.instantiate_services
        }
        self.yaml = YAML(typ="safe", pure=True)
        self.yaml.default_flow_sytle = False
        self.config_processor = config_processor
        self.project = None

    def read_yaml(self, sub_dir='', fname=''):
        # default is to load root project.yaml
        if sub_dir == '':
            path = self.config_folder + os.sep + fname
        else:
            path = self.config_folder + os.sep + sub_dir + os.sep + fname
        logger.debug("Loading YAML: %s" % (path))
        # Credential files must be secured. This seems hacky, is there a better way?
        if fname == '.credentials.yaml':
            cred_stat = os.stat(path)
            oct_perm = oct(cred_stat.st_mode)
            if oct_perm != '0o100400':
                raise PermissionError('Credentials file permissions are too relaxed. Run: chmod 0400 %s' % (path))

        # Validate Configuration
        if self.config_processor != None:
            self.config_processor(sub_dir, fname)

        with open(path, 'r') as stream:
            config = self.yaml.load(stream)
        return config

    def load_all(self):
        'Basically does a LOAD "*",8,1'
        # ToDo: clean-up loading order a bit
        self.instantiate_project('project', self.read_yaml('', 'project.yaml'))
        if os.path.isfile(self.config_folder + os.sep + '.credentials.yaml'):
            self.instantiate_project('.credentials', self.read_yaml('', '.credentials.yaml'))
        for subdir, instantiate_method in self.config_subdirs.items():
            for fname in os.listdir(self.config_folder + os.sep + subdir):
                if fname.endswith('.yml') or fname.endswith('.yaml'):
                    if fname.endswith('.yml'):
                        name = fname[:-4]
                    elif fname.endswith('.yaml'):
                        name = fname[:-5]
                    config = self.read_yaml(subdir, fname)
                    instantiate_method(name, config)
        self.load_references()
        try:
            self.load_resource_ids()
        except:
            # ToDo: we should only inspect actual Resources config files
            # and load them so that load_resource_ids fails if there is an actual bug.
            #
            # ITs ok to fail here when new config has been added
            # but it has not yet generated the Resources.yaml for it
            # In this case we need to wait until the new resources have
            # been generated and saved.
            pass
        self.load_core_monitoring()

    def load_references(self):
        """
        Resolves all references
        A reference is a string that refers to another value in the model. The original
        reference string is stored as '_ref_<attribute>' while the resolved reference is
        stored in the attribute.
        """
        # XXX
        return
        # walk the model
        for model in get_all_nodes(self.project):
            for name, field in get_all_fields(model).items():
                # check for lists of refs
                #if zope.schema.interfaces.IList.providedBy(field):

                # check for refs as normal attrs
                if hasattr(model, '_ref_' + name):
                    value = resolve_ref(getattr(model, '_ref_' + name), self.project)
                    setattr(model, name, value)

    def load_core_monitoring(self):
        "Loads monitoring metrics that are built into resources"
        for model in get_all_nodes(self.project):
            # ToDo: only doing metrics for ASG right now
            if schemas.IASG.providedBy(model):
                add_metric(model, ec2core)

    def load_resource_ids(self):
        "Loads resource ids from CFN Outputs"
        ne_resources_path = self.config_folder + os.sep + 'Resources' + os.sep + 'NetworkEnvironments'
        if os.path.isdir(ne_resources_path):
            for rfile in os.listdir(ne_resources_path):
                # parse filename
                info = rfile.split('.')[0]
                ne_name = info.split('-')[0]
                env_name = info.split('-')[1]
                region = info[len(ne_name) + len(env_name) + 2:]

                env_reg = self.project['ne'][ne_name][env_name][region]
                reg_config = self.read_yaml('Resources' + os.sep + 'NetworkEnvironments', rfile)
                if 'applications' in reg_config:
                    for app_name in reg_config['applications'].keys():
                        groups_config = reg_config['applications'][app_name]['groups']
                        for grp_name in groups_config:
                            for res_name in groups_config[grp_name]['resources']:
                                # Standard AWS Resources in an Application's Resource Group
                                resource_config = groups_config[grp_name]['resources'][res_name]
                                resource = env_reg.applications[app_name].groups[grp_name].resources[res_name]
                                resource.resource_name = resource_config['__name__']

                                # CloudWatch Alarms
                                if 'monitoring' in resource_config:
                                    if 'alarm_sets' in resource_config['monitoring']:
                                        for alarm_set_name in resource_config['monitoring']['alarm_sets']:
                                            for alarm_name in resource_config['monitoring']['alarm_sets'][alarm_set_name]:
                                                alarm = resource.monitoring.alarm_sets[alarm_set_name][alarm_name]
                                                alarm.resource_name = resource_config['monitoring']['alarm_sets'][alarm_set_name][alarm_name]['__name__']

    def load_governance_service(self, name):
        "Loads resource ids from CFN Outputs"
        service_yaml_path = "Governance" + os.sep + name
        service_config = self.read_yaml(service_yaml_path, name+".yaml")
        if name == "Monitoring":
            obj = GovernanceMonitoring(name, self.project['governance'].services)
            apply_attributes_from_config(obj, service_config)
        self.project['governance'].services.append(obj)

    def load_resources(self, res_groups, app_config, local_config={}):
        """
        Loads resources for an Application
        """

        if 'groups' not in app_config:
            app_config['groups'] = {}

        # ToDo: this is never called, it can be removed?
        # layer env config over base app config
        if  len(local_config.keys()) > 0:
            merged_config = merge(app_config['groups'], local_config)
        # if no customizations, use only base config
        else:
            merged_config = app_config

        for grp_key, grp_config in merged_config['groups'].items():
            obj = ResourceGroup(grp_key, res_groups)
            apply_attributes_from_config(obj, grp_config)
            res_groups[grp_key] = obj
            for res_key, res_config in grp_config['resources'].items():
                try:
                    klass = RESOURCES_CLASS_MAP[res_config['type']]
                except KeyError:
                    if 'type' not in res_config:
                        raise InvalidAimProjectFile("No type for resource {}".format(res_key))
                    raise InvalidAimProjectFile(
                        "No mapping for type {} for {}".format(res_config['type'], res_key)
                    )
                obj = klass(res_key, res_groups)
                apply_attributes_from_config(obj, res_config, lookup_config=self.monitor_config)
                res_groups[grp_key].resources[res_key] = obj

    def load_iam_group(self, res_groups, app_config, local_config={}):
        """
        Loads resources for IAM
        """

        if 'groups' not in app_config:
            app_config['groups'] = {}

        # layer env config over base app config
        if  len(local_config.keys()) > 0:
            merged_config = merge(app_config['groups'], local_config)
        # if no customizations, use only base config
        else:
            merged_config = app_config

        for grp_key, grp_config in merged_config['groups'].items():
            obj = ResourceGroup(grp_key, res_groups)
            apply_attributes_from_config(obj, grp_config)
            res_groups[grp_key] = obj
            for res_key, res_config in grp_config['resources'].items():
                try:
                    klass = RESOURCES_CLASS_MAP[res_config['type']]
                except KeyError:
                    if 'type' not in res_config:
                        raise InvalidAimProjectFile("No type for resource {}".format(res_key))
                    raise InvalidAimProjectFile(
                        "No mapping for type {} for {}".format(res_config['type'], res_key)
                    )
                obj = klass(res_key, res_groups)
                apply_attributes_from_config(obj, res_config)
                res_groups[grp_key].resources[res_key] = obj

    def create_apply_and_save(self, name, parent, klass, config):
        """
        Helper to create a new model instance
        apply config to it
        and save in the object hierarchy
        """
        obj = klass(name, parent)
        apply_attributes_from_config(obj, config)
        parent[name] = obj
        return obj

    def insert_subenv_ref_aim_sub(self, str_value, subenv_id, region):
        """
        aim.sub substition
        """
        # Isolate string between quotes: aim.sub ''
        sub_idx = str_value.find('aim.sub')
        if sub_idx == -1:
            return str_value
        end_idx = str_value.find('\n', sub_idx)
        if end_idx == -1:
            end_idx = len(str_value)
        str_idx = str_value.find("'", sub_idx, end_idx)
        if str_idx == -1:
            raise StackException(AimErrorCode.Unknown)
        str_idx += 1
        end_str_idx = str_value.find("'", str_idx, end_idx)
        if end_str_idx == -1:
            raise StackException(AimErrorCode.Unknown)

        # Isolate any ${} replacements
        first_pass = True
        while True:
            dollar_idx = str_value.find("${", str_idx, end_str_idx)
            if dollar_idx == -1:
                if first_pass == True:
                    raise StackException(AimErrorCode.Unknown)
                else:
                    break
            rep_1_idx = dollar_idx
            rep_2_idx = str_value.find("}", rep_1_idx, end_str_idx)+1
            netenv_ref_idx = str_value.find(
                "netenv.ref ", rep_1_idx, rep_2_idx)
            if netenv_ref_idx != -1:
                #sub_ref_idx = netenv_ref_idx + len("netenv.ref ")
                sub_ref_idx = netenv_ref_idx
                sub_ref_end_idx = sub_ref_idx+(rep_2_idx-sub_ref_idx-1)
                sub_ref = str_value[sub_ref_idx:sub_ref_end_idx]

                new_ref = self.insert_subenv_ref_str(sub_ref, subenv_id, region)
                sub_var = str_value[sub_ref_idx:sub_ref_end_idx]
                str_value = str_value.replace(sub_var, new_ref)
            else:
                break
            first_pass = False

        return str_value

    def insert_subenv_ref_str(self, str_value, subenv_id, region):
        netenv_ref_idx = str_value.find("netenv.ref ")
        if netenv_ref_idx == -1:
            return str_value

        if str_value.startswith("aim.sub "):
            return self.insert_subenv_ref_aim_sub(str_value, subenv_id, region)

        netenv_ref_raw = str_value
        sub_ref_len = len(netenv_ref_raw)

        netenv_ref = netenv_ref_raw[0:sub_ref_len]
        ref_dict = self.aim_ref.parse_ref(netenv_ref)
        if ref_dict['netenv_component'] == 'subenv':
            return str_value

        ref_dict['ref_parts'][0] = '.'.join([ref_dict['netenv_id'],
                                             'subenv',
                                             subenv_id,
                                             region])

        new_ref_parts = '.'.join(ref_dict['ref_parts'])
        new_ref = ' '.join([ref_dict['type'], new_ref_parts])

        return new_ref

    def normalize_environment_refs(self, env_config, env_name, env_region):
        """
        Resolves all references
        A reference is a string that refers to another value in the model. The original
        reference string is stored as '_ref_<attribute>' while the resolved reference is
        stored in the attribute.
        Inserts the Environment and Region into any netenv.ref references.
        """
        # walk the model
        model_list = get_all_nodes(env_config)
        for model in model_list:
            #continue
            all_fields = get_all_fields(model).items()
            for name, field in all_fields:
                if hasattr(model, name) == False:
                    continue
                if isinstance(field, (str, zope.schema.TextLine, zope.schema.Text)):
                    ref_name = '_ref_' + name
                    if hasattr(model, '_ref_' + name):
                        attr_name = ref_name
                    else:
                        attr_name = name
                    value = getattr(model, attr_name)
                    if value != None and value.find('netenv.ref') != -1:
                        value = self.insert_subenv_ref_str(value, env_name, env_region)
                        setattr(model, attr_name, value)
                elif zope.schema.interfaces.IList.providedBy(field):
                    new_list = []
                    attr_name = name
                    modified = False
                    for item in getattr(model, name):
                        if isinstance(item, (str, zope.schema.TextLine, zope.schema.Text)):
                            value = self.insert_subenv_ref_str(item, env_name, env_region)
                            modified = True
                        else:
                            value = item
                        new_list.append(value)
                    if modified == True:
                        setattr(model, attr_name, new_list)

    def instantiate_project(self, name, config):
        if name == 'project':
            self.project = Project(config['name'], None)
            apply_attributes_from_config(self.project, config)
        elif name == '.credentials':
            apply_attributes_from_config(self.project['credentials'], config)

    def instantiate_governance(self, name, config):
        if name != "Governance":
            return
        return
        # Under Construction
        #for [service_id, service_config] in config['services'].items():
        #    self.load_governance_service(service_id)

    def instantiate_route53(self, config):
        if config == None:
            return
        obj = Route53(config)
        #breakpoint()
        apply_attributes_from_config(obj, config)
        return obj

    def instantiate_codecommit(self, config):
        if config == None:
            return
        codecommit_obj = CodeCommit()
        codecommit_obj.repository_groups = {}
        for group_id in config.keys():
            group_config = config[group_id]
            codecommit_obj.repository_groups[group_id] = {}
            for repo_id in group_config.keys():
                repo_config = group_config[repo_id]
                repo_obj = CodeCommitRepository(repo_config['name'], codecommit_obj)
                apply_attributes_from_config(repo_obj, repo_config)
                codecommit_obj.repository_groups[group_id][repo_id] = repo_obj

        codecommit_obj.gen_repo_by_account()
        return codecommit_obj

    def instantiate_ec2(self, config):
        if config == None or 'keypairs' not in config.keys():
            return
        ec2_obj = EC2Service()
        ec2_obj.keypairs = {}
        for keypair_id in config['keypairs'].keys():
            keypair_config = config['keypairs'][keypair_id]
            keypair_obj = EC2KeyPair(keypair_config['name'], ec2_obj)
            apply_attributes_from_config(keypair_obj, keypair_config)
            ec2_obj.keypairs[keypair_id] = keypair_obj

        return ec2_obj


    def instantiate_services(self, name, config):
        if name == "Route53":
            self.project['route53'] = self.instantiate_route53(config)
        elif name == "CodeCommit":
            self.project['codecommit'] = self.instantiate_codecommit(config)
        elif name == "EC2":
            self.project['ec2'] = self.instantiate_ec2(config)
        return

    def instantiate_monitor_config(self, name, config):
        """
        Loads LogSets and AlarmSets config
        These do not get directly loaded into the model, their config is simply stored
        in Loader and applied to the model when named in alarm_sets: config sections.
        """
        if not hasattr(self, 'monitor_config'):
            self.monitor_config = {}
        if name == 'AlarmSets':
            self.monitor_config['alarms'] = config
        elif name == 'LogSets':
            self.monitor_config['logs'] = config

    def instantiate_accounts(self, name, config):
        accounts = self.project['accounts']
        self.create_apply_and_save(
            name,
            self.project['accounts'],
            Account,
            config
        )

    # Applications and IAM environment config
    # Merged global, region default, and region config
    def instantiate_env_region_config(self,
                                      config_name, # iam, applications
                                      item_klass,
                                      env_region_config,
                                      env_region,
                                      global_config):
        if config_name in env_region_config:
            global_item_config = global_config[config_name]
            for item_name, item_config in env_region_config[config_name].items():
                item = item_klass(item_name, getattr(env_region, config_name))
                if env_region.name == 'default':
                    # merge global with default
                    item_config = merge(global_config[config_name][item_name], env_region_config[config_name][item_name])
                    annotate_base_config(item, item_config, global_item_config[item_name])
                else:
                    # merge global with default, then merge that with local config
                    env_default = global_config['environments'][env_region.__parent__.name]['default']
                    if config_name in env_default:
                        default_region_config = env_default[config_name][item_name]
                        default_config = merge(global_item_config[item_name], default_region_config)
                        item_config = merge(default_config, item_config)
                        annotate_base_config(item, item_config, default_config)
                    # no default config, merge local with global
                    else:
                        item_config = merge(global_item_config[item_name], item_config)
                        annotate_base_config(item, item_config, global_item_config[item_name])

                env_region[config_name][item_name] = item # save
                apply_attributes_from_config(item, item_config)

                if config_name == 'applications':
                    # Load resources for application
                    self.load_resources(item.groups, item_config)
                elif config_name == 'iam':
                    self.load_iam_group(item.groups, item_config)

    def instantiate_network_environments(self, name, config):
        "Instantiates objects for everything in a NetworkEnvironments/some-workload.yaml file"
         # Network Environment
        net_env = self.create_apply_and_save(
            name, self.project['ne'], NetworkEnvironment, config['network']
        )

        # Environments
        if 'environments' in config:
            for env_name, env_config in config['environments'].items():
                env = self.create_apply_and_save(
                    env_name,
                    net_env,
                    Environment,
                    env_config
                )
                # Load the EnvironmentRegion(s) and EnvironmentDefault
                for env_reg_name, env_reg_config in config['environments'][env_name].items():
                    # skip attributes
                    if env_reg_name == 'title': continue
                    # key must be a valid aws region name
                    if env_reg_name != 'default' and env_reg_name not in aws_regions:
                        raise InvalidAimProjectFile(
                            "Environment region name is not valid: {} in {}".format(env_reg_name, env_name)
                        )
                    if env_reg_name is not 'default':
                        env_region_config = merge(env_config['default'], env_reg_config)
                    else:
                        env_region_config = env_config['default']

                    if env_reg_name == 'default':
                        env_region = self.create_apply_and_save(
                            env_reg_name,
                            env,
                            EnvironmentDefault,
                            env_region_config
                        )
                    else:
                        env_region = self.create_apply_and_save(
                            env_reg_name,
                            env,
                            EnvironmentRegion,
                            env_region_config
                        )

                    # Network
                    network = env_region.network
                    # merge default only with base netenv
                    if env_reg_name == 'default':
                        if not 'network' in env_reg_config:
                            raise InvalidAimProjectFile(
                                "Default Environment {} must have base network config".format(env_region.__parent__.name)
                            )
                        net_config = merge(config['network'], env_reg_config['network'])
                    # merge EnvDefault and base network, then merge that with any EnvReg config
                    else:
                        default = config['environments'][env_region.__parent__.name]['default']
                        if not 'network' in default:
                            raise InvalidAimProjectFile(
                                "Default Environment {} must have base network config".format(env_region.__parent__.name)
                            )
                        net_config = merge(
                            config['network'],
                            default['network']
                        )
                        if 'network' in env_reg_config:
                            net_config = merge(net_config, env_reg_config['network'])
                    apply_attributes_from_config(network, net_config)

                    # Applications
                    self.instantiate_env_region_config('applications',
                                                       Application,
                                                       env_region_config,
                                                       env_region,
                                                       config)

                    # IAM
                    #self.instantiate_env_region_config('iam',
                    #                                   IAMGroup,
                    #                                   env_region_config,
                    #                                   env_region,
                    #                                   config)

                    if env_reg_name != 'default':
                        # Insert the environment and region into any Refs
                        self.normalize_environment_refs(env_region, env_name, env_reg_name)
