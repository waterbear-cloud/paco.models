import aim.models.apps
import aim.models.networks
import aim.models.loader
import os
import unittest
from aim.tests import fixtures_path
from aim.models import load_project_from_yaml, schemas
from aim.models.project import Project
from aim.models.networks import SecurityGroup


class BaseTestModelLoader(unittest.TestCase):
    project_name = 'config_me'

    def setUp(self):
        # set the fixtures dir
        self.path = fixtures_path()
        # ToDo: temp re-factor or permanent?
        import aim.config.aim_context
        aim_ctx = aim.config.aim_context.AimContext()
        self.project = load_project_from_yaml(aim_ctx, self.path + os.sep + self.project_name)

class TestAimDemo(BaseTestModelLoader):

    project_name = 'waterbear-networks'
    def test_project(self):
        assert isinstance(self.project, Project)
        assert self.project.name == 'waterbear-networks'
        assert self.project.title.startswith('Waterbear Networks')

    def test_network_environment(self):
        ne = self.project['ne']['aimdemo']
        assert ne.availability_zones == 2

    def test_environment_state(self):
        dev_alb_domain = self.project['ne']['aimdemo']['dev']['us-west-2']['applications']['app'].groups['site'].resources['alb'].dns[0].domain_name
        dev_cert_domain = self.project['ne']['aimdemo']['dev']['us-west-2']['applications']['app'].groups['site'].resources['cert'].domain_name
        assert dev_alb_domain == "dev.aimdemo.waterbear.cloud"
        assert dev_cert_domain == "dev.aimdemo.waterbear.cloud"

    def test_cpbd(self):
        cpbd = self.project['ne']['aimdemo']['demo']['us-west-2']['applications']['app'].groups['cicd'].resources['cpbd']
        assert cpbd.asg_name != None

    def test_ne_vpc(self):
        vpc = self.project['ne']['aimdemo'].vpc
        assert vpc.enable_dns_support == True
        assert vpc.nat_gateway['app'].segment == 'public'
        assert vpc.vpn_gateway['app'].enabled == False
        assert vpc.private_hosted_zone.name == 'example.internal'
        assert vpc.segments['database'].enabled == True
        lb_sg = vpc.security_groups['app']['lb']
        assert lb_sg.ingress[0].from_port == 443
        assert lb_sg.ingress[0].name == 'HTTPS'
        assert lb_sg.egress[0].name == 'ANY'

    def test_env_network_merged(self):
        demo_env = self.project['ne']['aimdemo']['demo']
        assert demo_env['us-west-2'].network.availability_zones == 2
        assert isinstance( demo_env['us-west-2']['network'].vpc, aim.models.networks.VPC)
        assert demo_env['default'].network.vpc.cidr == '10.0.0.0/16'
        assert demo_env['default'].network.vpc.segments['webapp'].az1_cidr == '10.0.3.0/24'
        assert demo_env['default'].network.vpc.segments['webapp'].internet_access == False
        assert demo_env['default'].network.vpc.segments['public'].internet_access == True

    def test_asg_iam_roles(self):
        pass
        #iam_role = self.project['ne']['aimdemo']['demo']['us-west-2'].applications['app'].groups['site'].resources['webapp'].instance_iam_role
        #assert iam_role.assume_role_policy.effect == "Allow"
        #assert iam_role.assume_role_policy.service[0] == 'ec2.amazonaws.com'
        #assert iam_role.instance_profile == True
        #assert iam_role.path == '/'
        #assert iam_role.policies[0].name == 'CloudWatchAgent'
        #assert iam_role.policies[0].statement[0].effect == "Allow"
        #assert iam_role.policies[0].statement[0].action[0] == "cloudwatch:PutMetricData"
        #assert iam_role.policies[0].statement[0].resource[0] == "*"

    def test_netenv_refs(self):
        demo_env = self.project['ne']['aimdemo']['demo']['us-west-2']
        # Basic netenv.ref
        ref_value = demo_env.applications['app'].groups['cicd'].resources['cpbd'].asg_name
        assert ref_value == "netenv.ref aimdemo.subenv.demo.us-west-2.applications.app.groups.site.resources.webapp.name"

        # aimsub netenf.ref
        #ref_value = demo_env.iam['app'].roles['instance_role'].policies[1].statement[0].resource[0]
        #assert ref_value == "aim.sub 'arn:aws:s3:::${netenv.ref aimdemo.subenv.demo.us-west-2.applications.app.groups.cicd.resources.cpbd.artifacts_bucket.name}/*'"

        # netenf.ref in a List
        ref_value = demo_env.applications['app'].groups['site'].resources['alb'].security_groups[0]
        assert ref_value == "netenv.ref aimdemo.subenv.demo.us-west-2.network.vpc.security_groups.app.lb.id"

    def test_get_all_nodes(self):
        # check to ensure each node is only visited once
        seen = {}
        for node in aim.models.loader.get_all_nodes(self.project):
            node_id = id(node)
            if node_id in seen:
                # core metric objects are the same
                name = getattr(node, 'name', '')
                if name != 'ec2core':
                    self.fail("Node seen a second time")
            else:
                seen[node_id] = node

    def test_env_override(self):
        dev_env = self.project['ne']['aimdemo']['dev']['us-west-2']
        bastion = dev_env['applications']['app'].groups['bastion'].resources['instance']
        assert bastion.desired_capacity == 0
        #bastion = dev_env['applications']['app']['groups']['bastion']['resources']['bastion']
        #assert bastion['instance_key_pair'] == 'wbsites-dev-us-west-2'
        #assert bastion['desired_capacity'] == 0

    def test_alarms(self):
        dev_env = self.project['ne']['aimdemo']['dev']['us-west-2']
        dev_bastion = dev_env['applications']['app'].groups['bastion'].resources['instance']
        demo_env = self.project['ne']['aimdemo']['demo']['us-west-2']
        demo_bastion = demo_env['applications']['app'].groups['bastion'].resources['instance']
        demo_webapp = demo_env['applications']['app'].groups['site'].resources['webapp']

        # test typical set-up: the dev env does not have Alarms but demo env does
        assert len(dev_bastion.monitoring.alarm_sets.values()) == 0
        assert len(demo_bastion.monitoring.alarm_sets.values()) > 0
        # bastion has the ASG instance-health-core AlarmSet
        # The Loader loads each AlarmSet into an AlarmSets object
        # then it can overrides existing Alarm settings
        assert schemas.ICloudWatchAlarm.providedBy(demo_bastion.monitoring.alarm_sets['instance-health-core']['StatusCheck-Critical'])
        assert demo_bastion.monitoring.alarm_sets['instance-health-cwagent']['SwapPercent-Low'].evaluation_periods == 5
        assert schemas.ICloudWatchAlarm.providedBy(demo_webapp.monitoring.alarm_sets['launch-health']['GroupPendingInstances-Low'])
        assert demo_webapp.monitoring.alarm_sets['instance-health-cwagent']['SwapPercent-Low'].evaluation_periods == 15


class TestMatchaLatteDemo(BaseTestModelLoader):
    project_name = 'waterbear-kt'

    def test_project(self):
        assert isinstance(self.project, Project)

    def test_monitoring(self):
        env_reg = self.project['ne']['ml']['dev']['eu-central-1']
        asg = env_reg.applications['ml'].groups['app'].resources['webapp']
        assert isinstance(asg, aim.models.resources.ASG)
        assert asg.monitoring.collection_interval == 60
        assert asg.monitoring.metrics[0].measurements[0] == 'CPUUtilization'
