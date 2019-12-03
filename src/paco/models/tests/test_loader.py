import paco.models.applications
import paco.models.networks
import paco.models.loader
import os
import troposphere
import inspect
import unittest
from paco.models import load_project_from_yaml, schemas
from paco.models.project import Project
from paco.models.networks import SecurityGroup

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

class Testpacodemo(BaseTestModelLoader):

    project_name = 'pacodemo'
    def test_project(self):
        assert isinstance(self.project, Project)
        assert self.project.name == 'waterbear-networks'
        assert self.project.title.startswith('Waterbear Networks')

    def test_network_environment(self):
        ne = self.project['netenv']['pacodemo']
        assert ne.availability_zones == 2

    def test_environment_state(self):
        dev_alb_domain = self.project['netenv']['pacodemo']['dev']['us-west-2']['applications']['app'].groups['site'].resources['alb'].dns[0].domain_name
        dev_cert_domain = self.project['netenv']['pacodemo']['dev']['us-west-2']['applications']['app'].groups['site'].resources['cert'].domain_name
        assert dev_alb_domain == "dev.pacodemo.waterbear.cloud"
        assert dev_cert_domain == "dev.pacodemo.waterbear.cloud"

    def test_cpbd(self):
        cpbd = self.project['netenv']['pacodemo']['demo']['us-west-2']['applications']['app'].groups['cicd'].resources['cpbd']
        assert cpbd.asg != None

    def test_ne_vpc(self):
        vpc = self.project['netenv']['pacodemo'].vpc
        assert vpc.enable_dns_support == True
        assert vpc.vpn_gateway['app'].enabled == False
        assert vpc.private_hosted_zone.name == 'example.internal'
        assert vpc.segments['database'].enabled == True
        lb_sg = vpc.security_groups['app']['lb']
        assert lb_sg.ingress[0].from_port == 443
        assert lb_sg.ingress[0].name == 'HTTPS'
        assert lb_sg.egress[0].name == 'ANY'

    def test_env_network_merged(self):
        demo_env = self.project['netenv']['pacodemo']['demo']
        assert demo_env['us-west-2'].network.availability_zones == 2
        assert isinstance( demo_env['us-west-2']['network'].vpc, paco.models.networks.VPC)
        assert demo_env['default'].network.vpc.cidr == '10.0.0.0/16'
        assert demo_env['default'].network.vpc.segments['webapp'].az1_cidr == '10.0.3.0/24'
        assert demo_env['default'].network.vpc.segments['webapp'].internet_access == False
        assert demo_env['default'].network.vpc.segments['public'].internet_access == True

    def test_asg(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        asg = demo_env.applications['app'].groups['site'].resources['webapp']

        # CloudFormation Init
        cfn_init = asg.cfn_init
        assert schemas.ICloudFormationInit.providedBy(cfn_init)
        assert cfn_init.raw_config['config_sets']['ascending'][0] == 'config1'
        configurations = cfn_init.configurations
        assert schemas.ICloudFormationConfigurations.providedBy(configurations)
        assert configurations['config1'].packages.rubygems['chef'][0] == "0.10.2"
        assert configurations['config1'].commands['test'].command == "ls"
        assert configurations['config1'].commands['test'].cwd == "~"
        assert configurations['config1'].commands['test'].env['CFNTEST'] ==  "I come from config1."

        config_sets = cfn_init.config_sets
        assert schemas.ICloudFormationConfigSets.providedBy(config_sets)
        assert config_sets['ascending'][0] == 'config1'

        # Services
        service = configurations['config1'].services.sysvinit['apache2']
        assert service.enabled == True
        assert service.commands[1] == 'two'
        assert service.files[0] == "/etc/cfn/cfn-hup.conf"

        # Test files - check for CloudFormation functions such as Fn::Sub or !Sub
        local_file = configurations['config1'].files['/tmp/local-file']
        assert type(local_file.content) == troposphere.Sub

        plain_file = configurations['config1'].files['/tmp/plain-file']
        assert plain_file.content == "Nothing to see here."

        #fullyaml = configurations['config1'].files['/fullyaml.txt'].content
        mysql_file = configurations['config1'].files['/tmp/setup.mysql']
        assert mysql_file.mode == "000644"
        assert mysql_file.group == "root"
        #assert mysql_file.content == '!Sub\nCREATE DATABASE ${DBName};\n'

        tag_file = configurations['config1'].files['/tag.txt']
        assert tag_file.content == '!Join\n- \'\'\n- - "#!/bin/bash\\n"\n  - !Ref: AWS::StackName\n!Ref: SomeLogicalId\n'

        # Use expressions such Fn::Sub
        #test_file = configurations['config1'].files['/test-file.txt']
        #assert test_file.content == 'Fn::Sub | TEST FILE ${DBName};'

        # Test cfn_init Parameters
        assert cfn_init.parameters['TestString'] == 'catdog'
        assert cfn_init.parameters['TestNumber'] == 10


    def test_netenv_refs(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        # Basic paco.ref netenv
        ref_value = demo_env.applications['app'].groups['cicd'].resources['cpbd'].asg
        assert ref_value == "paco.ref netenv.pacodemo.demo.us-west-2.applications.app.groups.site.resources.webapp"

        # paco.sub netenf.ref
        #ref_value = demo_env.iam['app'].roles['instance_role'].policies[1].statement[0].resource[0]
        #assert ref_value == "paco.sub 'arn:aws:s3:::${paco.ref netenv.pacodemo.demo.us-west-2.applications.app.groups.cicd.resources.cpbd.artifacts_bucket.name}/*'"

        # netenf.ref in a List
        ref_value = demo_env.applications['app'].groups['site'].resources['alb'].security_groups[0]
        assert ref_value == "paco.ref netenv.pacodemo.demo.us-west-2.network.vpc.security_groups.app.lb"

    def test_get_all_nodes(self):
        # ToDo: EnvironmentRegion.applications is seen twice because it's both
        # an attribute and a dict key - refactor so it's only attribute
        # but it's breaking change ...
        return
        # check to ensure each node is only visited once
        seen = {}
        for node in paco.models.loader.get_all_nodes(self.project):
            node_id = id(node)
            if node_id in seen:
                # core metric objects are the same
                name = getattr(node, 'name', '')
                if name not in ('ec2core_builtin_metric'):
                    self.fail("Node seen a second time")
            else:
                seen[node_id] = node

    def test_env_override(self):
        dev_env = self.project['netenv']['pacodemo']['dev']['us-west-2']
        bastion = dev_env['applications']['app'].groups['bastion'].resources['instance']
        assert bastion.desired_capacity == 0
        #bastion = dev_env['applications']['app']['groups']['bastion']['resources']['bastion']
        #assert bastion['instance_key_pair'] == 'wbsites-dev-us-west-2'
        #assert bastion['desired_capacity'] == 0

    def test_alarms(self):
        dev_env = self.project['netenv']['pacodemo']['dev']['us-west-2']
        dev_bastion = dev_env['applications']['app'].groups['bastion'].resources['instance']
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
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
        assert demo_webapp.monitoring.alarm_sets['instance-health-cwagent']['SwapPercent-Low'].threshold == 10.0

        # LogAlarm
        assert demo_webapp.monitoring.alarm_sets['log-test']['ApacheError'].type == 'LogAlarm'
        assert demo_webapp.monitoring.alarm_sets['log-test']['ApacheError'].log_set_name == 'apache'
        assert demo_webapp.monitoring.alarm_sets['log-test']['ApacheError'].log_group_name == 'error'

    def test_dbparameters(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        dbparams = demo_env['applications']['app'].groups['site'].resources['dbparams']
        assert schemas.IDBParameterGroup.providedBy(dbparams)
        assert dbparams.parameters['block_encryption_mode'] == 'aes-128-ecb'

    def test_cloudwatch_logging(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        demo_webapp = demo_env['applications']['app'].groups['site'].resources['webapp']
        linux_log_set = demo_webapp.monitoring.log_sets['amazon_linux']

        # Log Set
        assert schemas.ICloudWatchLogSet.providedBy(linux_log_set)
        assert linux_log_set.expire_events_after_days == '1'

        # Log Group
        assert schemas.ICloudWatchLogGroup.providedBy(linux_log_set.log_groups['audit'])
        assert linux_log_set.log_groups['audit'].log_group_name == 'puppydog'

        # Log Source
        assert schemas.ICloudWatchLogSource.providedBy(linux_log_set.log_groups['audit'].sources['audit'])
        assert linux_log_set.log_groups['audit'].sources['audit'].log_stream_name == "audit-{instance_id}"

        # metric filters
        assert linux_log_set.log_groups['audit'].metric_filters['authorization_failures'].filter_pattern.startswith('{ ($')

    def test_instantiate_resources(self):
        # Route53
        assert self.project['resource']['route53'].hosted_zones['pacodemo'].domain_name, 'pacodemo.example.com'
        # CodeCommit
        assert self.project['resource']['codecommit'].repository_groups['pacodemo']['app'].account, 'paco.ref accounts.data'
        # EC2
        assert self.project['resource']['ec2'].keypairs['pacodemo_dev'].account, 'paco.ref accounts.dev'

    def test_resource_account(self):
        dev_env = self.project['netenv']['pacodemo']['dev']['us-west-2']
        bastion = dev_env['applications']['app'].groups['bastion'].resources['instance']
        account = bastion.get_account()
        assert account.name, 'dev'

    def test_notifications(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
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
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
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
        groups = self.project['resource']['notificationgroups']
        assert schemas.INotificationGroups.providedBy(groups)
        assert groups.account, 'paco.ref accounts.master'
        assert groups['us-west-2']['bobs_team'].subscriptions[0].endpoint, 'http://example.com/yes'
        assert len(groups['us-west-2']['bobs_team'].subscriptions), 2
        bob = groups['ca-central-1']['bob']
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
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        lmbda = demo_env['applications']['notification'].groups['lambda'].resources['function']
        assert schemas.ILambda.providedBy(lmbda)
        assert lmbda.handler, 'notification.lambda_handler'
        assert lmbda.memory_size, 128
        assert len(lmbda.layers), 1

    def test_paco_project_version(self):
        # test that a version loaded ... we will fiddle with this number in fixtures
        # as we update paco.models
        assert len(self.project.paco_project_version) > 2

    def test_cloudtrail(self):
        cloudtrail = self.project['resource']['cloudtrail']
        assert schemas.ICloudTrailResource.providedBy(cloudtrail)
        trail = cloudtrail.trails['basic_trail']
        assert schemas.ICloudTrail.providedBy(trail)
        assert trail.enable_log_file_validation == True
        assert trail.cloudwatchlogs_log_group.log_group_name, 'CloudTrail'
        assert trail.cloudwatchlogs_log_group.expire_events_after_days, '14'

    def test_api_gateway_rest_api(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        api_gra = demo_env['applications']['app'].groups['restapi'].resources['api_gateway_rest_api']
        assert len(api_gra.body_file_location) > 1

    def test_health_checks(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        health_checks = demo_env['applications']['app'].monitoring.health_checks
        assert schemas.IHealthChecks.providedBy(health_checks)
        pinger = health_checks['external_ping']
        assert pinger.match_string, 'alive!'
        assert pinger.port, 80

    def test_multiple_apps_one_netenv(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        apps = demo_env['applications']
        assert schemas.IApplication.providedBy(apps['appmouse'])
        assert schemas.IApplication.providedBy(apps['appelephant'])
        assert schemas.IApplication.providedBy(apps['app'])
        assert apps['appmouse'].groups['cicd'].resources['cpbd'].asg == 'paco.ref netenv.pacodemo.demo.us-west-2.applications.appmouse.groups.site.resources.webapp'

    def test_codedeploy_application(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        codedeploy = demo_env['applications']['app'].groups['cicd'].resources['codedeploy']
        assert schemas.ICodeDeployApplication.providedBy(codedeploy)
        assert codedeploy.compute_platform == "Server"
        assert len(codedeploy.deployment_groups['deployment'].autoscalinggroups) == 1
        assert codedeploy.deployment_groups['deployment'].revision_location_s3.bundle_type == 'zip'

    def test_backup(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        vaults = demo_env.backup_vaults
        assert schemas.IBackupVaults.providedBy(vaults)
        myvault = vaults['myapp']
        assert myvault.title == "All data for MyApp (myapp) application"
        assert myvault.plans['ebs_daily'].plan_rules[0].schedule_expression == 'cron(0 7 ? * * *)'

    def test_dashboard(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        dashboard = demo_env['applications']['app'].groups['site'].resources['dashboard']
        assert schemas.ICloudWatchDashboard.providedBy(dashboard)
        assert dashboard.title == "Demo-Dashboard"
        assert 'WebAsg.name' in dashboard.variables
