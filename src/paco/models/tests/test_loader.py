import paco.models.applications
import paco.models.networks
import paco.models.loader
import os
import troposphere
import unittest
from paco.models import load_project_from_yaml, schemas
from paco.models.project import Project

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

    @classmethod
    def setUpClass(cls):
        # set the fixtures dir
        cls.path = fixtures_path()
        cls.project = load_project_from_yaml(cls.path + os.sep + cls.project_name)

class Testpacodemo(BaseTestModelLoader):

    project_name = 'pacodemo'

    def setUp(self):
        self.demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        self.demo_app = self.demo_env['applications']['app']

    def test_project(self):
        assert isinstance(self.project, Project)
        assert self.project.name == 'waterbear-networks'
        assert self.project.title.startswith('Waterbear Networks')

    def test_network_az(self):
        network = self.project['netenv']['pacodemo']['demo']['us-west-2'].network
        assert network.availability_zones == 2

    def test_environment_state(self):
        dev_alb_domain = self.project['netenv']['pacodemo']['dev']['us-west-2']['applications']['app'].groups['site'].resources['alb'].dns[0].domain_name
        dev_cert_domain = self.project['netenv']['pacodemo']['dev']['us-west-2']['applications']['app'].groups['site'].resources['cert'].domain_name
        assert dev_alb_domain == "dev.pacodemo.waterbear.cloud"
        assert dev_cert_domain == "dev.pacodemo.waterbear.cloud"

    def test_deployment_pipeline(self):
        deploy_pipeline = self.project['netenv']['pacodemo']['demo']['us-west-2']['applications']['app'].groups['cicd'].resources['pipeline']
        assert schemas.IDeploymentPipeline.providedBy(deploy_pipeline)
        assert deploy_pipeline.stages['source']['github'].type, 'GitHub.Source'
        ecrpipe = self.project['netenv']['pacodemo']['demo']['us-west-2']['applications']['app'].groups['cicd'].resources['ecrpipe']
        assert ecrpipe.source['ecr'].type, 'ECR.Source'

        # Test CodeBuild
        codebuild = deploy_pipeline.stages['build']['codebuild']
        ecs = codebuild.release_phase.ecs
        assert schemas.IDeploymentPipelineBuildReleasePhase(codebuild.release_phase)
        assert ecs[0].command, 'docker rake:deploy'

    def test_ne_vpc(self):
        vpc = self.project['netenv']['pacodemo']['demo']['us-west-2'].network.vpc
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

    def test_lbapplication(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        alb = demo_env['applications']['app'].groups['site'].resources['alb']
        assert schemas.ILoadBalancer.providedBy(alb)
        assert schemas.IListener.providedBy(alb.listeners['https'])
        assert alb.listeners['https'].rules['app_forward'].name == 'app_forward'
        assert alb.listeners['https'].rules['app_forward'].rule_type == 'forward'

    def test_lbnetwork(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        nlb = demo_env['applications']['app'].groups['site'].resources['nlb']
        assert schemas.INetworkLoadBalancer.providedBy(nlb)
        # assert schemas.IListener.providedBy(alb.listeners['https'])
        # assert alb.listeners['https'].rules['app_forward'].name == 'app_forward'
        # assert alb.listeners['https'].rules['app_forward'].rule_type == 'forward'


    def test_asg(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        asg = demo_env.applications['app'].groups['site'].resources['webapp']

        # rolling_udpate_policy
        assert asg.rolling_update_policy.max_batch_size == 1
        assert asg.rolling_update_policy.min_instances_in_service == 0
        assert asg.rolling_update_policy.pause_time == 'PT1M'
        assert asg.rolling_update_policy.wait_on_resource_signals == False

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

        # Test IAM Role
        assert asg.instance_iam_role.enabled == True
        assert asg.instance_iam_role.name == 'instance_iam_role'

        norole_asg = demo_env.applications['app'].groups['site'].resources['norole']
        assert norole_asg.instance_iam_role.enabled == False

        # SSH Access
        assert asg.ssh_access.users, ['bdobbs']
        assert asg.ssh_access.groups, ['developers']

        # ECS
        ecs_asg = demo_env.applications['app'].groups['container'].resources['ecs_asg']
        assert ecs_asg.ecs.cluster, 'paco.ref netenv.pacodemo.demo.us-west-2.applications.app.groups.container.resources.ecs_cluster'


    def test_netenv_refs(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']

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

    def test_iamuser_resource(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        github_user = demo_env['applications']['app'].groups['cicd'].resources['github_user']
        assert schemas.IIAMUserResource.providedBy(github_user)
        assert github_user.allows[0] == 'paco.ref netenv.pacodemo.demo.us-west-2.app.app.groups.cicd.resources.ecrrepo'

    def test_pinpointapp(self):
        pinpointapp = self.demo_app.groups['market'].resources['pinpointapp']
        assert schemas.IPinpointApplication(pinpointapp)
        assert pinpointapp.email_channel.from_address == 'bob@example.com'
        assert pinpointapp.sms_channel.sender_id == 'MisterId'

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
        assert self.project['resource']['codecommit']['pacodemo']['app'].account, 'paco.ref accounts.data'
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

    def test_sns(self):
        sns = self.project['resource']['sns']
        assert len(sns.default_locations), 1
        assert len(sns.topics), 2

    def test_ec2(self):
        ec2 = self.project['resource']['ec2']
        assert ec2.keypairs['pacodemo_dev'].region, 'us-west-2'
        assert ec2.users['bdobbs'].full_name, 'Bob Dobbs'
        assert ec2.groups['developers'].members, ['Bob Dobbs']

    def test_ecs(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        cluster = demo_env['applications']['app'].groups['container'].resources['ecs_cluster']
        assert schemas.IECSCluster.providedBy(cluster)
        assert cluster.capacity_providers[0].base, 1
        ecs_service_config = demo_env['applications']['app'].groups['container'].resources['ecs_services']

        assert ecs_service_config.setting_groups['app_pool'].secrets[0].name, 'TWO_SECRET'
        assert ecs_service_config.setting_groups['app_pool'].environment[1].value, 'down'

        simple_app_service = ecs_service_config.services['simple_app']
        assert ecs_service_config.services['simple_app'].desired_count, 2
        assert ecs_service_config.services['simple_app'].load_balancers[0].container_name, 'hello'
        hello_def = ecs_service_config.task_definitions['hello_web'].container_definitions['hello']
        assert hello_def.cpu, 10
        assert hello_def.depends_on[0].condition, 'START'
        assert hello_def.health_check.retries, 5
        assert hello_def.ulimits[0].hard_limit, 1000
        assert hello_def.user, 'www-data'
        assert hello_def.secrets[0].value_from, 'paco.ref netenv.pacodemo.secrets_manager.one.two.another'
        assert hello_def.environment[0].name, 'hello'

        assert simple_app_service.target_tracking_scaling_policies['memory'].scale_in_cooldown, 300
        assert simple_app_service.target_tracking_scaling_policies['cpu'].predefined_metric, 'ECSServiceAverageCPUUtilization'
        assert simple_app_service.target_tracking_scaling_policies['cpu'].target, 70

        # Capacity Providers
        assert simple_app_service.capacity_providers[0].base, 1
        assert simple_app_service.capacity_providers[0].weight, 1

    def test_cognito(self):
        auth_app = self.demo_app.groups['auth']
        userpool = auth_app.resources['userpool']
        assert schemas.ICognitoUserPool(userpool)
        assert userpool.app_clients['bob'].generate_secret, True
        assert userpool.user_creation.invite_message_templates.email_message, "Would you like to test the email?"
        assert userpool.lambda_triggers.pre_sign_up.startswith('paco.ref ')
        idp = auth_app.resources['ident']
        assert schemas.ICognitoIdentityPool(idp)

    def test_rds(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        pg_aurora = demo_env['applications']['app'].groups['site'].resources['pg_aurora']
        assert pg_aurora.db_instances['first'].db_instance_type, 'db.t3.small'
        assert pg_aurora.default_instance.db_instance_type, 'db.t3.medium'
        assert pg_aurora.enable_kms_encryption, True
        assert pg_aurora.cluster_event_notifications.groups, ['bob']
        assert pg_aurora.default_instance.event_notifications.event_categories[0], 'availability'
        assert pg_aurora.db_instances['first'].event_notifications.event_categories[0], 'failure'

    def test_lambda(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        lmbda = demo_env['applications']['notification'].groups['lambda'].resources['function']
        assert schemas.ILambda.providedBy(lmbda)
        assert lmbda.handler, 'notification.lambda_handler'
        assert lmbda.memory_size, 128
        assert len(lmbda.layers), 1

    def test_esdomain(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        esdomain = demo_env['applications']['app'].groups['site'].resources['esdomain']
        assert schemas.IElasticsearchDomain.providedBy(esdomain)

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

    def test_config(self):
        config = self.project['resource']['config'].config
        assert config.global_resources_region == 'us-west-2'
        assert config.delivery_frequency == 'Six_Hours'

    def test_api_gateway_rest_api(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        api = demo_env['applications']['app'].groups['restapi'].resources['api_gateway_rest_api']
        assert len(api.body_file_location) > 1
        api.resources['idle'].path_part, '/idle'
        api.resources['idle'].child_resources['view'].path_part, '{view}'
        api.resources['idle'].child_resources['view'].child_resources['one'].path_part, 'one'
        api.resources['idle'].child_resources['view'].child_resources['two'].path_part, 'two'

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

        assert myvault.plans['ebs_daily'].plan_rules[0].copy_actions[0].destination_vault.startswith('arn:aws:backup')
        assert myvault.plans['ebs_daily'].plan_rules[0].copy_actions[1].lifecycle_delete_after_days == 100

    # dashboard_file is not reading correctly? disable for now
    def test_dashboard(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        dashboard = demo_env['applications']['app'].groups['site'].resources['dashboard']
        assert schemas.ICloudWatchDashboard.providedBy(dashboard)
        assert dashboard.title == "Demo-Dashboard"
        assert 'WebAsg.name' in dashboard.variables

    def test_dynamodb(self):
        dynamodb = self.demo_app.groups['storage'].resources['dynamodb']
        assert schemas.IDynamoDB.providedBy(dynamodb)
        assert dynamodb.default_provisioned_throughput.read_capacity_units == 5
        concert = dynamodb.tables['concert']
        assert concert.attribute_definitions[0].name == 'ArtistId'
        assert concert.key_schema[0].type == 'HASH'
        assert concert.global_secondary_indexes[0].index_name == 'GSI'
        assert concert.global_secondary_indexes[0].projection.type == 'KEYS_ONLY'
        assert concert.provisioned_throughput.write_capacity_units == 10
        assert concert.target_tracking_scaling_policy.min_capacity == 5
        discography = dynamodb.tables['discography']
        assert discography.attribute_definitions[1].type == 'S'

    def test_iotcore(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        iottopic = demo_env['applications']['app'].groups['iot'].resources['iottopic']
        assert schemas.IIoTTopicRule.providedBy(iottopic)
        assert iottopic.sql == "SELECT * FROM 'iot/myTestTopic'"

        iotpolicy = demo_env['applications']['app'].groups['iot'].resources['iotpolicy']
        assert schemas.IIoTPolicy.providedBy(iotpolicy)
        assert iotpolicy.variables['sensor_topic_arn'].startswith('paco.ref ')

    def test_iotanalyticspipeline(self):
        demo_env = self.project['netenv']['pacodemo']['demo']['us-west-2']
        iotpipeline = demo_env['applications']['app'].groups['iot'].resources['raw_analysis']
        assert schemas.IIoTAnalyticsPipeline.providedBy(iotpipeline)
        assert iotpipeline.channel_storage.key_prefix == 'raw_input/'
        assert iotpipeline.datastore_storage.expire_events_after_days == 30
        assert iotpipeline.pipeline_activities['extra_bit'].attributes['key1'] == 'heyguy'

        # datasets
        sample = iotpipeline.datasets['sample']
        assert sample.query_action.sql_query == "SELECT * FROM example"
        assert sample.content_delivery_rules['s3dump'].s3_destination.key == "/DataSet/!{iotanalytics:scheduleTime}/!{iotanalytics:versionId}.csv"
        assert sample.version_history == 2
        assert sample.expire_events_after_days == 3

    def test_ssm_documents(self):
        ssm_documents = self.project['resource']['ssm'].ssm_documents
        assert ssm_documents['my_ssm_doc'].locations[0].regions[0] == 'eu-central-1'
        assert ssm_documents['my_ssm_doc'].document_type == 'Command'
