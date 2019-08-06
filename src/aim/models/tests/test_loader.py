import aim.models.applications
import aim.models.networks
import aim.models.loader
import os
import inspect
import unittest
from aim.models import load_project_from_yaml, schemas
from aim.models.project import Project
from aim.models.networks import SecurityGroup

def fixtures_path():
    # find the project root directory
    # this works for pytest run from VS Code
    parts = []
    for part in os.path.abspath(os.path.dirname(__file__)).split(os.sep):
        if part == 'src':
            parts.append('fixtures')
            break
        parts.append(part)
    path = os.sep.join(parts)
    return path

def cwd_to_fixtures():
    fpath = fixtures_path()
    os.chdir(fpath)
    return fpath

class BaseTestModelLoader(unittest.TestCase):
    project_name = 'config_me'

    def setUp(self):
        # set the fixtures dir
        self.path = fixtures_path()
        self.project = load_project_from_yaml(self.path + os.sep + self.project_name)

class TestAimDemo(BaseTestModelLoader):

    project_name = 'aimdemo'
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
        # Basic aim.ref netenv
        ref_value = demo_env.applications['app'].groups['cicd'].resources['cpbd'].asg_name
        assert ref_value == "aim.ref netenv.aimdemo.demo.us-west-2.applications.app.groups.site.resources.webapp.name"

        # aimsub netenf.ref
        #ref_value = demo_env.iam['app'].roles['instance_role'].policies[1].statement[0].resource[0]
        #assert ref_value == "aim.sub 'arn:aws:s3:::${aim.ref netenv.aimdemo.demo.us-west-2.applications.app.groups.cicd.resources.cpbd.artifacts_bucket.name}/*'"

        # netenf.ref in a List
        ref_value = demo_env.applications['app'].groups['site'].resources['alb'].security_groups[0]
        assert ref_value == "aim.ref netenv.aimdemo.demo.us-west-2.network.vpc.security_groups.app.lb.id"

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

    def test_logging(self):
        demo_env = self.project['ne']['aimdemo']['demo']['us-west-2']
        demo_webapp = demo_env['applications']['app'].groups['site'].resources['webapp']

        # test log_set has loaded
        assert demo_webapp.monitoring.log_sets['amazon_linux']['linux']['audit'].log_stream_name, "{instance_id}"

        # override log source settings
        assert demo_webapp.monitoring.log_sets['amazon_linux']['linux']['audit'].log_group_name, "puppydog"

    def test_instantiate_resources(self):
        # Route53
        assert self.project['route53'].hosted_zones['aimdemo'].domain_name, 'aimdemo.example.com'
        # CodeCommit
        assert self.project['codecommit'].repository_groups['aimdemo']['app'].account, 'aim.ref accounts.data'
        # EC2
        assert self.project['ec2'].keypairs['aimdemo_dev'].account, 'aim.ref accounts.dev'

    def test_resource_account(self):
        dev_env = self.project['ne']['aimdemo']['dev']['us-west-2']
        bastion = dev_env['applications']['app'].groups['bastion'].resources['instance']
        account = bastion.get_account()
        assert account.name, 'dev'

    def test_notifications(self):
        demo_env = self.project['ne']['aimdemo']['demo']['us-west-2']
        demo_app = demo_env['applications']['app']

        # notifications for applications
        assert schemas.IAlarmNotifications.providedBy(demo_app.notifications)
        assert schemas.IAlarmNotification.providedBy(demo_app.notifications['team_bob'])
        assert demo_app.notifications['team_bob'].classification, 'performance'

        # test application override
        assert demo_app.notifications['team_bob'].groups[0], 'jim_is_the_new_bob'

        # notification for a resource
        webapp = demo_app.groups['site'].resources['webapp']
        notif_group = webapp.monitoring.notifications['santaclaus']
        assert notif_group.groups[0], 'santa'

        # notification for an alarm set
        alarm_set = webapp.monitoring.alarm_sets['instance-health-cwagent']
        assert schemas.IAlarmNotifications.providedBy(alarm_set.notifications)
        assert alarm_set.notifications['alarmsetnotif'].groups[0], 'misterteam'

        # notification for just a single alarm
        alarm_with_notif = alarm_set['SwapPercent-Low']
        assert schemas.IAlarmNotifications.providedBy(alarm_with_notif.notifications)
        assert alarm_with_notif.notifications['singlealarm']

    def test_alarm_notifications(self):
        demo_env = self.project['ne']['aimdemo']['demo']['us-west-2']
        webapp = demo_env['applications']['app'].groups['site'].resources['webapp']

        alarm_set = webapp.monitoring.alarm_sets['instance-health-cwagent']

        # alarm with specific notification
        alarm_one = alarm_set['SwapPercent-Low']
        assert alarm_one.notification_groups, ['oneguygetsthis', 'misterteam', 'santa', 'jim_is_the_new_bob']

        # alarm with alarm set notification
        alarm_two = alarm_set['SwapPercent-Critical']
        assert alarm_two.notification_groups, ['misterteam', 'santa', 'jim_is_the_new_bob']

        # alarm with resource notification
        alarm_set = webapp.monitoring.alarm_sets['launch-health']
        alarm_three = alarm_set['GroupPendingInstances-Low']
        assert alarm_three.notification_groups, ['santa']

        # alarm with no notifications, is filtered out of on severity and performance
        alarm_four = alarm_set['GroupPendingInstances-Critical']
        assert len(alarm_four.notification_groups) == 0

        # alarm with only app notification
        alarm_set = webapp.monitoring.alarm_sets['instance-health-core']
        alarm_five = alarm_set['CPUTotal-Low']
        assert alarm_five.notification_groups, ['santa']

    def test_notification_groups(self):
        groups = self.project['notificationgroups']
        assert schemas.INotificationGroups.providedBy(groups)
        assert groups.region, 'eu-central-1'
        assert groups.account, 'aim.ref accounts.master'
        assert groups['bobs_team'].subscriptions[0].endpoint, 'http://example.com/yes'
        assert len(groups['bobs_team'].subscriptions), 2
        bob = groups['bob']
        assert bob.subscriptions[0].protocol, 'http'
        assert bob.subscriptions[0].endpoint, 'http://example.com/yes'
        assert bob.subscriptions[1].endpoint, 'https://example.com/orno'
        assert bob.subscriptions[2].endpoint, 'bob@example.com'
        assert bob.subscriptions[3].endpoint, 'bob@example.com'
        assert bob.subscriptions[4].endpoint, '555-555-5555'
        assert bob.subscriptions[5].endpoint, 'arn:aws:sqs:us-east-2:444455556666:queue1'
        assert bob.subscriptions[6].endpoint, 'arn:aws:sqs:us-east-2:444455556666:queue1'
        assert bob.subscriptions[7].endpoint, 'arn:aws:lambda:us-east-1:123456789012:function:my-function'

    def test_lambda(self):
        demo_env = self.project['ne']['aimdemo']['demo']['us-west-2']
        lmbda = demo_env['applications']['notification'].groups['lambda'].resources['function']
        assert schemas.ILambda.providedBy(lmbda)
        assert lmbda.handler, 'notification.lambda_handler'
        assert lmbda.memory_size, 128
        assert len(lmbda.layers), 1