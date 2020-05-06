"""
Vocabularies

https://docs.plone.org/develop/plone/forms/vocabularies.html
"""

from zope.schema.vocabulary import SimpleVocabulary

ssm_document_types = SimpleVocabulary.fromValues([
    'ApplicationConfigurationSchema'
    'Automation',
    'ChangeCalendar',
    'Command',
    'DeploymentStrategy',
    'Package',
    'Policy',
    'Session',
])

subscription_protocols = [
	'http',
	'https',
	'email',
	'email-json',
	'sms',
	'sqs',
	'application',
	'lambda'
]
application_group_types = [
    'Application',
    'Bastion',
    'Deployment',
]

cloudwatch = {
	'App': {
		'dimension': '',
		'namespace': ''
	},

	'ASG': {
		'dimension': 'AutoScalingGroupName',
		'namespace': 'AWS/AutoScaling'
	},
	'CloudFront': {
		'dimension': 'DistributionId',
		'namespace': 'AWS/CloudFront'
	},
	'ElastiCacheRedis': {
		'dimension': 'CacheClusterId',
		'namespace': 'AWS/ElastiCache'
	},
  'ElasticsearchDomain': {
    'dimension': 'DomainName',
    'namespace': 'AWS/ES',
  },
  'IoTTopicRule': {
      'dimension': 'RuleName',
      'namespace': 'AWS/IoT',
  },
  'IoTAnalyticsPipeline': {
      'dimension': '',
      'namespace': 'AWS/IoTAnalytics',
  },
	'Lambda': {
		'dimension': 'FunctionName',
		'namespace': 'AWS/Lambda'
	},
	'LBApplication': {
		'dimension': 'LoadBalancer',
		'namespace': 'AWS/ApplicationELB'
	},
	'RDSMysql': {
		'dimension': 'DBInstanceIdentifier',
		'namespace': 'AWS/RDS'
	},
	'RDSPostgresql': {
		'dimension': 'DBInstanceIdentifier',
		'namespace': 'AWS/RDS'
	},
    'IoTTopicRule': {
        'dimension': 'RuleName',
        'namespace': 'AWS/IoT',
    },
    'IoTAnalyticsPipeline': {
        'dimension': '',
        'namespace': 'AWS/IoTAnalytics',
    },
	'Route53HealthCheck': {
		'dimension': 'HealthCheckId',
		'namespace': 'AWS/Route53',
	},
}

cloudwatch_log_retention = {
	'1': '1 day',
	'3': '3 days',
	'5': '5 days',
	'7': '1 week',
	'14': '2 weeks',
	'30': '1 month',
	'60': '2 months',
	'90': '3 months',
	'120': '4 months',
	'150': '5 months',
	'180': '6 months',
	'365': '1 year',
	'400': '13 months',
	'545': '18 months',
	'731': '2 years',
	'1827': '5 years',
	'3653': '10 years',
	'Never': 'Never'
}

alarm_classifications = {
	'health': None,
	'performance': None,
	'security': None,
	'unset': None
}

cloudwatch_comparison_operators = {
	'GreaterThanThreshold': '>',
	'GreaterThanOrEqualToThreshold': '>=',
	'LessThanThreshold': '<',
	'LessThanOrEqualToThreshold': '<='
}

asg_metrics = {
	'GroupMinSize': None,
    'GroupMaxSize': None,
    'GroupDesiredCapacity': None,
    'GroupInServiceInstances': None,
    'GroupPendingInstances': None,
    'GroupStandbyInstances': None,
    'GroupTerminatingInstances': None,
    'GroupTotalInstances': None
}

# List of AWS Regions with metadata maintained here:
# https://github.com/jsonmaur/aws-regions
aws_regions = {
    'us-east-2': {
		"name": "Ohio",
		"full_name": "US East (Ohio)",
		"short_name": "use2",
		"code": "us-east-2",
		"public": True,
		"zones": [
			"us-east-2a",
			"us-east-2b",
			"us-east-2c"
		]
	},
    'us-east-1': {
		"name": "N. Virginia",
		"full_name": "US East (N. Virginia)",
		"short_name": "use1",
		"code": "us-east-1",
		"public": True,
		"zones": [
			"us-east-1a",
			"us-east-1b",
			"us-east-1c",
			"us-east-1d",
			"us-east-1e",
			"us-east-1f"
		]
	},
    'us-west-1': {
        "name": "N. California",
        "full_name": "US West (N. California)",
		"short_name": "usw1",
        "code": "us-west-1",
        "public": True,
        "zone_limit": 2,
        "zones": [
            "us-west-1a",
            "us-west-1b",
            "us-west-1c"
        ]
    },
    'us-west-2': {
    	"name": "Oregon",
    	"full_name": "US West (Oregon)",
		"short_name": "usw2",
    	"code": "us-west-2",
    	"public": True,
    	"zones": [
    		"us-west-2a",
    		"us-west-2b",
    		"us-west-2c",
    		"us-west-2d"
    	]
    },
    'us-gov-west-1': {
    	"name": "GovCloud West",
    	"full_name": "AWS GovCloud (US)",
		"short_name": "usgw1",
    	"code": "us-gov-west-1",
    	"public": False,
    	"zones": [
    		"us-gov-west-1a",
    		"us-gov-west-1b",
    		"us-gov-west-1c"
    	]
    },
    'af-south-1': {
    	"name": "Cape Town",
    	"full_name": "Africa (Cape Town)",
		"short_name": "afs1",
    	"code": "af-south-1",
    	"public": True,
    	"zones": [
    		"af-south-1a",
    		"af-south-1b",
    		"af-south-1c",
    	]
    },
    'us-gov-east-1': {
    	"name": "GovCloud East",
    	"full_name": "AWS GovCloud (US-East)",
		"short_name": "usge1",
    	"code": "us-gov-east-1",
    	"public": False,
    	"zones": [
    		"us-gov-east-1a",
    		"us-gov-east-1b",
    		"us-gov-east-1c"
    	]
    },
    'ap-northeast-1': {
    	"name": "Tokyo",
    	"full_name": "Asia Pacific (Tokyo)",
		"short_name": "apne1",
    	"code": "ap-northeast-1",
    	"public": True,
    	"zone_limit": 3,
    	"zones": [
    		"ap-northeast-1a",
    		"ap-northeast-1b",
    		"ap-northeast-1c",
    		"ap-northeast-1d"
    	]
    },
    'ap-northeast-3': {
    	"name": "Osaka",
    	"full_name": "Asia Pacific (Osaka-Local)",
		"short_name": "apne3",
    	"code": "ap-northeast-3",
    	"public": False,
    	"zones": [
    		"ap-northeast-3a"
    	]
    },
    'ap-northeast-2': {
    	"name": "Seoul",
    	"full_name": "Asia Pacific (Seoul)",
		"short_name": "apne2",
    	"code": "ap-northeast-2",
    	"public": True,
    	"zones": [
    		"ap-northeast-2a",
    		"ap-northeast-2c"
    	]
    },
    'ca-central-1': {
    	"name": "Canada",
    	"full_name": "Canada (Central)",
		"short_name": "cac1",
    	"code": "ca-central-1",
    	"public": True,
    	"zones": [
    		"ca-central-1a",
    		"ca-central-1b"
    	]
    },
    'cn-north-1': {
    	"name": "Beijing",
    	"full_name": "China (Beijing)",
		"short_name": "cnn1",
    	"code": "cn-north-1",
    	"public": False,
    	"zones": [
    		"cn-north-1a",
    		"cn-north-1b"
    	]
    },
    'cn-northwest-1': {
    	"name": "Ningxia",
    	"full_name": "China (Ningxia)",
		"short_name": "cnnw1",
    	"code": "cn-northwest-1",
    	"public": False,
    	"zones": [
    		"cn-northwest-1a",
    		"cn-northwest-1b",
    		"cn-northwest-1c"
    	]
    },
    'eu-central-1': {
    	"name": "Frankfurt",
    	"full_name": "EU (Frankfurt)",
		"short_name": "euc1",
    	"code": "eu-central-1",
    	"public": True,
    	"zones": [
    		"eu-central-1a",
    		"eu-central-1b",
    		"eu-central-1c"
    	]
    },
    'eu-west-1': {
    	"name": "Ireland",
    	"full_name": "EU (Ireland)",
		"short_name": "euw1",
    	"code": "eu-west-1",
    	"public": True,
    	"zones": [
    		"eu-west-1a",
    		"eu-west-1b",
    		"eu-west-1c"
    	]
    },
    'eu-west-2': {
    	"name": "London",
    	"full_name": "EU (London)",
		"short_name": "euw2",
    	"code": "eu-west-2",
    	"public": True,
    	"zones": [
    		"eu-west-2a",
    		"eu-west-2b",
    		"eu-west-2c"
    	]
    },
    'eu-south-1': {
    	"name": "Milan",
    	"full_name": "EU (Milan)",
		"short_name": "eus1",
    	"code": "eu-south-1",
    	"public": True,
    	"zones": [
    		"eu-south-1a",
    		"eu-south-1b",
    		"eu-south-1c"
    	]
    },
    'eu-west-3': {
    	"name": "Paris",
    	"full_name": "EU (Paris)",
		"short_name": "euw3",
    	"code": "eu-west-3",
    	"public": True,
    	"zones": [
    		"eu-west-3a",
    		"eu-west-3b",
    		"eu-west-3c"
    	]
    },
    'eu-north-1': {
    	"name": "Stockholm",
    	"full_name": "EU (Stockholm)",
		"short_name": "eun1",
    	"code": "eu-north-1",
    	"public": True,
    	"zones": [
    		"eu-north-1a",
    		"eu-north-1b",
    		"eu-north-1c"
    	]
    },
    'ap-south-1': {
    	"name": "Mumbai",
    	"full_name": "Asia Pacific (Mumbai)",
		"short_name": "aps1",
    	"code": "ap-south-1",
    	"public": True,
    	"zones": [
    		"ap-south-1a",
    		"ap-south-1b"
    	]
    },
    'sa-east-1': {
    	"name": "São Paulo",
    	"full_name": "South America (São Paulo)",
		"short_name": "sae1",
    	"code": "sa-east-1",
    	"public": True,
    	"zone_limit": 2,
    	"zones": [
    		"sa-east-1a",
    		"sa-east-1b",
    		"sa-east-1c"
    	]
    },
	'me-south-1': {
		"name": "Bahrain",
		"full_name": "Middle East (Bahrain)",
		"code": "me-south-1",
		"public": True,
		"zones": [
			"me-south-1a",
			"me-south-1b",
			"me-south-1c"
		]
	},
    'ap-southeast-1': {
    	"name": "Singapore",
    	"full_name": "Asia Pacific (Singapore)",
		"short_name": "apse1",
    	"code": "ap-southeast-1",
    	"public": True,
    	"zones": [
    		"ap-southeast-1a",
    		"ap-southeast-1b",
    		"ap-southeast-1c"
    	]
    },
    'ap-southeast-2': {
    	"name": "Sydney",
    	"full_name": "Asia Pacific (Sydney)",
		"short_name": "apse2",
    	"code": "ap-southeast-2",
    	"public": True,
    	"zones": [
    		"ap-southeast-2a",
    		"ap-southeast-2b",
    		"ap-southeast-2c"
    	]
    },
	'ap-east-1': {
		"name": "Hong Kong",
		"full_name": "Asia Pacific (Hong Kong)",
		"code": "ap-east-1",
		"public": True,
		"zones": [
			"ap-east-1a",
			"ap-east-1b",
			"ap-east-1c"
		]
	},
}

aws_region_names = SimpleVocabulary.fromValues(
    list(aws_regions.keys())
)


instance_size_info = {
	'a1.medium': {
		'cpu': 1,
		'cpu_credits': None,
		'memory': 2,
		'network': 'Up to 10 Gbps'
	},
	'a1.large': {
		'cpu': 2,
		'cpu_credits': None,
		'memory': 4,
		'network': 'Up to 10 Gbps'
	},
	'a1.xlarge': {
		'cpu': 4,
		'cpu_credits': None,
		'memory': 8,
		'network': 'Up to 10 Gbps'
	},
	'a1.2xlarge': {
		'cpu': 8,
		'cpu_credits': None,
		'memory': 16,
		'network': 'Up to 10 Gbps'
	},
	'a1.4xlarge': {
		'cpu': 16,
		'cpu_credits': None,
		'memory': 32,
		'network': 'Up to 10 Gbps'
	},
	't3.nano': {
		'cpu': 2,
		'cpu_credits': 6,
		'memory': '0.5',
		'network': 'Up to 5 Gbps'
	},
	't3.micro': {
		'cpu': 2,
		'cpu_credits': 12,
		'memory': 1,
		'network': 'Up to 5 Gbps'
	},
	't3.small': {
		'cpu': 2,
		'cpu_credits': 24,
		'memory': 2,
		'network': 'Up to 5 Gbps'
	},
	't3.medium': {
		'cpu': 2,
		'cpu_credits': 24,
		'memory': 4,
		'network': 'Up to 5 Gbps'
	},
	't3.large': {
		'cpu': 2,
		'cpu_credits': 36,
		'memory': 8,
		'network': 'Up to 5 Gbps'
	},
	't3.xlarge': {
		'cpu': 4,
		'cpu_credits': 96,
		'memory': 16,
		'network': 'Up to 5 Gbps'
	},
	't3.2xlarge': {
		'cpu': 8,
		'cpu_credits': 192,
		'memory': 32,
		'network': 'Up to 5 Gbps'
	},
	't3a.nano': {
		'cpu': 2,
		'cpu_credits': 6,
		'memory': '0.5',
		'network': 'Up to 5 Gbps'
	},
	't3a.micro': {
		'cpu': 2,
		'cpu_credits': 12,
		'memory': 1,
		'network': 'Up to 5 Gbps'
	},
	't3a.small': {
		'cpu': 2,
		'cpu_credits': 24,
		'memory': 2,
		'network': 'Up to 5 Gbps'
	},
	't3a.medium': {
		'cpu': 2,
		'cpu_credits': 24,
		'memory': 4,
		'network': 'Up to 5 Gbps'
	},
	't3a.large': {
		'cpu': 2,
		'cpu_credits': 36,
		'memory': 8,
		'network': 'Up to 5 Gbps'
	},
	't3a.xlarge': {
		'cpu': 4,
		'cpu_credits': 96,
		'memory': 16,
		'network': 'Up to 5 Gbps'
	},
	't3a.2xlarge': {
		'cpu': 8,
		'cpu_credits': 192,
		'memory': 32,
		'network': 'Up to 5 Gbps'
	},
	't2.nano': {
		'cpu': 1,
		'cpu_credits': 3,
		'memory': '0.5',
		'network': 'Low'
	},
	't2.micro': {
		'cpu': 1,
		'cpu_credits': 6,
		'memory': '1',
		'network': 'Low to Moderate'
	},
	't2.small': {
		'cpu': 1,
		'cpu_credits': 12,
		'memory': 2,
		'network': 'Low to Moderate'
	},
	't2.medium': {
		'cpu': 2,
		'cpu_credits': 24,
		'memory': 4,
		'network': 'Low to Moderate'
	},
	't2.large': {
		'cpu': 2,
		'cpu_credits': 36,
		'memory': 8,
		'network': 'Low to Moderate'
	},
	't2.xlarge': {
		'cpu': 4,
		'cpu_credits': 54,
		'memory': 16,
		'network': 'Moderate'
	},
	't2.2xlarge': {
		'cpu': 8,
		'cpu_credits': 81,
		'memory': 32,
		'network': 'Moderate'
	},
	'm5.large': {
		'cpu': 2,
		'cpu_credits': None,
		'memory': 8,
		'network': 'Up to 10 Gbps'
	},
	'm4.large': {
		'cpu': 2,
		'cpu_credits': None,
		'memory': 8,
		'network': 'Moderate'
	},
	'm4.xlarge': {
		'cpu': 4,
		'cpu_credits': None,
		'memory': 16,
		'network': 'High'
	},
	'c5.xlarge': {
		'cpu': 4,
		'cpu_credits': None,
		'memory': 8,
		'network': 'Up to 10 Gbps'
	},
}

target_group_protocol = SimpleVocabulary.fromValues(
    ['HTTP','HTTPS']
)

lb_ssl_policy = SimpleVocabulary.fromValues([
	'',
	'ELBSecurityPolicy-2016-08',
	'ELBSecurityPolicy-TLS-1-0-2015-04',
	'ELBSecurityPolicy-TLS-1-1-2017-01',
	'ELBSecurityPolicy-TLS-1-2-2017-01',
	'ELBSecurityPolicy-TLS-1-2-Ext-2018-06',
	'ELBSecurityPolicy-FS-2018-06',
	'ELBSecurityPolicy-FS-1-1-2019-08',
	'ELBSecurityPolicy-FS-1-2-2019-08',
	'ELBSecurityPolicy-FS-1-2-Res-2019-08',
])

lb_scheme = SimpleVocabulary.fromValues(
    ['internet-facing','internal']
)

iot_dataset_container_types = SimpleVocabulary.fromValues([
	'ACU_1',
	'ACU_2',
])

iam_policy_effect = SimpleVocabulary.fromValues(
    ['Allow','Deny']
)

# complete list of all AWS Managed Policies as of 2020-04-01
#
# Python script used to generate this list:
#
# #!/usr/bin/env python
# import boto3
# client = boto3.client('iam')
# paginator = client.get_paginator('list_policies')
# response_iterator = paginator.paginate(Scope='AWS')
# for response in response_iterator:
#     for policy in response['Policies']:
#         print("    '{}',".format(policy['PolicyName']))
#
iam_managed_policies = SimpleVocabulary.fromValues([
    'AWSDirectConnectReadOnlyAccess',
    'AmazonGlacierReadOnlyAccess',
    'AWSMarketplaceFullAccess',
    'ClientVPNServiceRolePolicy',
    'AWSSSODirectoryAdministrator',
    'AWSIoT1ClickReadOnlyAccess',
    'AutoScalingConsoleReadOnlyAccess',
    'AmazonDMSRedshiftS3Role',
    'AWSQuickSightListIAM',
    'AWSHealthFullAccess',
    'AlexaForBusinessGatewayExecution',
    'AmazonElasticTranscoder_ReadOnlyAccess',
    'AmazonRDSFullAccess',
    'SupportUser',
    'AmazonEC2FullAccess',
    'SecretsManagerReadWrite',
    'AWSIoTThingsRegistration',
    'AmazonDocDBReadOnlyAccess',
    'AWSElasticBeanstalkReadOnlyAccess',
    'AmazonMQApiFullAccess',
    'AWSElementalMediaStoreReadOnly',
    'AWSCertificateManagerReadOnly',
    'AWSQuicksightAthenaAccess',
    'AWSCloudMapRegisterInstanceAccess',
    'AWSMarketplaceImageBuildFullAccess',
    'AWSCodeCommitPowerUser',
    'AWSCodeCommitFullAccess',
    'IAMSelfManageServiceSpecificCredentials',
    'AmazonEMRCleanupPolicy',
    'AWSCloud9EnvironmentMember',
    'AWSApplicationAutoscalingSageMakerEndpointPolicy',
    'FMSServiceRolePolicy',
    'AmazonSQSFullAccess',
    'AlexaForBusinessReadOnlyAccess',
    'AWSLambdaFullAccess',
    'AWSIoTLogging',
    'AmazonEC2RoleforSSM',
    'AlexaForBusinessNetworkProfileServicePolicy',
    'AWSCloudHSMRole',
    'AWSEnhancedClassicNetworkingMangementPolicy',
    'IAMFullAccess',
    'AmazonInspectorFullAccess',
    'AmazonElastiCacheFullAccess',
    'AWSAgentlessDiscoveryService',
    'AWSXrayWriteOnlyAccess',
    'AWSPriceListServiceFullAccess',
    'AWSKeyManagementServiceCustomKeyStoresServiceRolePolicy',
    'AutoScalingReadOnlyAccess',
    'AmazonForecastFullAccess',
    'AmazonWorkLinkReadOnly',
    'TranslateFullAccess',
    'AutoScalingFullAccess',
    'AmazonEC2RoleforAWSCodeDeploy',
    'AWSFMMemberReadOnlyAccess',
    'AmazonElasticMapReduceEditorsRole',
    'AmazonEKSClusterPolicy',
    'AmazonEKSWorkerNodePolicy',
    'AWSMobileHub_ReadOnly',
    'CloudWatchEventsBuiltInTargetExecutionAccess',
    'AutoScalingServiceRolePolicy',
    'AmazonElasticTranscoder_FullAccess',
    'AmazonCloudDirectoryReadOnlyAccess',
    'CloudWatchAgentAdminPolicy',
    'AWSOpsWorksFullAccess',
    'AWSOpsWorksCMInstanceProfileRole',
    'AWSBatchServiceEventTargetRole',
    'AWSCodePipelineApproverAccess',
    'AWSApplicationDiscoveryAgentAccess',
    'ViewOnlyAccess',
    'AmazonElasticMapReduceRole',
    'ElasticLoadBalancingFullAccess',
    'AmazonRoute53DomainsReadOnlyAccess',
    'AmazonSSMAutomationApproverAccess',
    'AWSOpsWorksRole',
    'AWSSecurityHubReadOnlyAccess',
    'AWSConfigRoleForOrganizations',
    'ApplicationAutoScalingForAmazonAppStreamAccess',
    'AmazonEC2ContainerRegistryFullAccess',
    'AmazonFSxFullAccess',
    'SimpleWorkflowFullAccess',
    'GreengrassOTAUpdateArtifactAccess',
    'AmazonS3FullAccess',
    'AWSStorageGatewayReadOnlyAccess',
    'Billing',
    'QuickSightAccessForS3StorageManagementAnalyticsReadOnly',
    'AmazonEC2ContainerRegistryReadOnly',
    'AWSRoboMakerFullAccess',
    'AmazonElasticMapReduceforEC2Role',
    'DatabaseAdministrator',
    'AmazonRedshiftReadOnlyAccess',
    'AmazonEC2ReadOnlyAccess',
    'CloudWatchAgentServerPolicy',
    'AWSXrayReadOnlyAccess',
    'AWSElasticBeanstalkEnhancedHealth',
    'WellArchitectedConsoleFullAccess',
    'AmazonElasticMapReduceReadOnlyAccess',
    'AWSDirectoryServiceReadOnlyAccess',
    'AWSSSOMasterAccountAdministrator',
    'AmazonGuardDutyServiceRolePolicy',
    'AmazonVPCReadOnlyAccess',
    'AWSElasticBeanstalkServiceRolePolicy',
    'ServerMigrationServiceLaunchRole',
    'AWSCodeDeployRoleForECS',
    'CloudWatchEventsReadOnlyAccess',
    'AWSLambdaReplicator',
    'AmazonAPIGatewayInvokeFullAccess',
    'AWSSSOServiceRolePolicy',
    'AWSLicenseManagerMasterAccountRolePolicy',
    'AmazonKinesisAnalyticsReadOnly',
    'AmazonMobileAnalyticsFullAccess',
    'AWSMobileHub_FullAccess',
    'AmazonAPIGatewayPushToCloudWatchLogs',
    'AWSDataPipelineRole',
    'CloudWatchFullAccess',
    'AmazonMQApiReadOnlyAccess',
    'AWSDeepLensLambdaFunctionAccessPolicy',
    'AmazonGuardDutyFullAccess',
    'AmazonRDSDirectoryServiceAccess',
    'AWSCodePipelineReadOnlyAccess',
    'ReadOnlyAccess',
    'AWSAppSyncInvokeFullAccess',
    'AmazonMachineLearningBatchPredictionsAccess',
    'AWSIoTSiteWiseFullAccess',
    'AlexaForBusinessFullAccess',
    'AWSEC2SpotFleetServiceRolePolicy',
    'AmazonRekognitionReadOnlyAccess',
    'AWSCodeDeployReadOnlyAccess',
    'CloudSearchFullAccess',
    'AWSLicenseManagerServiceRolePolicy',
    'AWSCloudHSMFullAccess',
    'AmazonEC2SpotFleetAutoscaleRole',
    'AWSElasticLoadBalancingServiceRolePolicy',
    'AWSCodeBuildDeveloperAccess',
    'ElastiCacheServiceRolePolicy',
    'AWSGlueServiceNotebookRole',
    'AWSDataPipeline_PowerUser',
    'AWSCodeStarServiceRole',
    'AmazonTranscribeFullAccess',
    'AWSDirectoryServiceFullAccess',
    'AmazonFreeRTOSOTAUpdate',
    'AmazonWorkLinkServiceRolePolicy',
    'AmazonDynamoDBFullAccess',
    'AmazonSESReadOnlyAccess',
    'AmazonRedshiftQueryEditor',
    'AWSWAFReadOnlyAccess',
    'AutoScalingNotificationAccessRole',
    'AmazonMechanicalTurkReadOnly',
    'AmazonKinesisReadOnlyAccess',
    'AWSXRayDaemonWriteAccess',
    'AWSCloudMapReadOnlyAccess',
    'AWSCloudFrontLogger',
    'AWSCodeDeployFullAccess',
    'AWSBackupServiceRolePolicyForBackup',
    'AWSRoboMakerServiceRolePolicy',
    'CloudWatchActionsEC2Access',
    'AWSLambdaDynamoDBExecutionRole',
    'AmazonRoute53DomainsFullAccess',
    'AmazonElastiCacheReadOnlyAccess',
    'AmazonRDSServiceRolePolicy',
    'AmazonAthenaFullAccess',
    'AmazonElasticFileSystemReadOnlyAccess',
    'AWSCloudMapDiscoverInstanceAccess',
    'CloudFrontFullAccess',
    'AmazonConnectFullAccess',
    'AWSCloud9Administrator',
    'AWSApplicationAutoscalingEMRInstanceGroupPolicy',
    'AmazonTextractFullAccess',
    'AWSOrganizationsServiceTrustPolicy',
    'AmazonDocDBFullAccess',
    'AmazonMobileAnalyticsNon-financialReportAccess',
    'AWSCloudTrailFullAccess',
    'AmazonCognitoDeveloperAuthenticatedIdentities',
    'AWSConfigRole',
    'AWSSSOMemberAccountAdministrator',
    'AWSApplicationAutoscalingAppStreamFleetPolicy',
    'AWSCertificateManagerPrivateCAFullAccess',
    'AWSGlueServiceRole',
    'AmazonAppStreamServiceAccess',
    'AmazonRedshiftFullAccess',
    'AWSTransferLoggingAccess',
    'AmazonZocaloReadOnlyAccess',
    'AWSCloudHSMReadOnlyAccess',
    'ComprehendFullAccess',
    'AmazonFSxConsoleFullAccess',
    'SystemAdministrator',
    'AmazonEC2ContainerServiceEventsRole',
    'AmazonRoute53ReadOnlyAccess',
    'AWSMigrationHubDiscoveryAccess',
    'AmazonEC2ContainerServiceAutoscaleRole',
    'AWSAppSyncSchemaAuthor',
    'AlexaForBusinessDeviceSetup',
    'AWSBatchServiceRole',
    'AWSElasticBeanstalkWebTier',
    'AmazonSQSReadOnlyAccess',
    'AmazonChimeFullAccess',
    'AWSDeepRacerRoboMakerAccessPolicy',
    'AWSElasticLoadBalancingClassicServiceRolePolicy',
    'AWSMigrationHubDMSAccess',
    'WellArchitectedConsoleReadOnlyAccess',
    'AmazonKinesisFullAccess',
    'AmazonGuardDutyReadOnlyAccess',
    'AmazonFSxServiceRolePolicy',
    'AmazonECSServiceRolePolicy',
    'AmazonConnectReadOnlyAccess',
    'AmazonMachineLearningReadOnlyAccess',
    'AmazonRekognitionFullAccess',
    'RDSCloudHsmAuthorizationRole',
    'AmazonMachineLearningFullAccess',
    'AdministratorAccess',
    'AmazonMachineLearningRealTimePredictionOnlyAccess',
    'AWSAppSyncPushToCloudWatchLogs',
    'AWSMigrationHubSMSAccess',
    'AWSB9InternalServicePolicy',
    'AWSConfigUserAccess',
    'AWSIoTConfigAccess',
    'SecurityAudit',
    'AWSDiscoveryContinuousExportFirehosePolicy',
    'AmazonCognitoIdpEmailServiceRolePolicy',
    'AWSElementalMediaConvertFullAccess',
    'AWSRoboMakerReadOnlyAccess',
    'AWSResourceGroupsReadOnlyAccess',
    'AWSCodeStarFullAccess',
    'AmazonSSMServiceRolePolicy',
    'AWSDataPipeline_FullAccess',
    'NeptuneFullAccess',
    'AmazonSSMManagedInstanceCore',
    'AWSAutoScalingPlansEC2AutoScalingPolicy',
    'AmazonDynamoDBReadOnlyAccess',
    'AutoScalingConsoleFullAccess',
    'AWSElementalMediaPackageFullAccess',
    'AmazonKinesisVideoStreamsFullAccess',
    'AmazonSNSReadOnlyAccess',
    'AmazonRDSPreviewServiceRolePolicy',
    'AWSEC2SpotServiceRolePolicy',
    'AmazonElasticMapReduceFullAccess',
    'AWSCloudMapFullAccess',
    'AWSDataLifecycleManagerServiceRole',
    'AmazonS3ReadOnlyAccess',
    'AWSElasticBeanstalkFullAccess',
    'AmazonWorkSpacesAdmin',
    'AWSCodeDeployRole',
    'AmazonSESFullAccess',
    'CloudWatchLogsReadOnlyAccess',
    'AmazonRDSBetaServiceRolePolicy',
    'AmazonKinesisFirehoseReadOnlyAccess',
    'GlobalAcceleratorFullAccess',
    'AmazonDynamoDBFullAccesswithDataPipeline',
    'AWSIoTAnalyticsReadOnlyAccess',
    'AmazonEC2RoleforDataPipelineRole',
    'CloudWatchLogsFullAccess',
    'AWSSecurityHubFullAccess',
    'AWSElementalMediaPackageReadOnly',
    'AWSElasticBeanstalkMulticontainerDocker',
    'AmazonPersonalizeFullAccess',
    'AWSMigrationHubFullAccess',
    'AmazonFSxReadOnlyAccess',
    'IAMUserChangePassword',
    'LightsailExportAccess',
    'AmazonAPIGatewayAdministrator',
    'AmazonVPCCrossAccountNetworkInterfaceOperations',
    'AmazonMacieSetupRole',
    'AmazonPollyReadOnlyAccess',
    'AmazonRDSDataFullAccess',
    'AmazonMobileAnalyticsWriteOnlyAccess',
    'AmazonEC2SpotFleetTaggingRole',
    'DataScientist',
    'AWSMarketplaceMeteringFullAccess',
    'AWSOpsWorksCMServiceRole',
    'FSxDeleteServiceLinkedRoleAccess',
    'WorkLinkServiceRolePolicy',
    'AmazonConnectServiceLinkedRolePolicy',
    'AWSPrivateMarketplaceAdminFullAccess',
    'AWSConnector',
    'AWSCodeDeployRoleForECSLimited',
    'AmazonElasticTranscoder_JobsSubmitter',
    'AmazonMacieHandshakeRole',
    'AWSIoTAnalyticsFullAccess',
    'AWSBatchFullAccess',
    'AmazonSSMDirectoryServiceAccess',
    'AmazonECS_FullAccess',
    'AWSSupportServiceRolePolicy',
    'AWSApplicationAutoscalingRDSClusterPolicy',
    'AWSServiceRoleForEC2ScheduledInstances',
    'AWSCodeDeployRoleForLambda',
    'AWSFMAdminReadOnlyAccess',
    'AmazonSSMFullAccess',
    'AWSCodeCommitReadOnly',
    'AmazonEC2ContainerServiceFullAccess',
    'AmazonFreeRTOSFullAccess',
    'AmazonTextractServiceRole',
    'AmazonCognitoReadOnly',
    'AmazonDMSCloudWatchLogsRole',
    'AWSApplicationDiscoveryServiceFullAccess',
    'AmazonRoute53AutoNamingReadOnlyAccess',
    'AWSSSOReadOnly',
    'AmazonVPCFullAccess',
    'AWSCertificateManagerPrivateCAUser',
    'AWSAppSyncAdministrator',
    'AWSEC2FleetServiceRolePolicy',
    'AmazonRoute53AutoNamingFullAccess',
    'AWSImportExportFullAccess',
    'DynamoDBReplicationServiceRolePolicy',
    'AmazonMechanicalTurkFullAccess',
    'AmazonEC2ContainerRegistryPowerUser',
    'AWSSSODirectoryReadOnly',
    'AmazonMachineLearningCreateOnlyAccess',
    'AmazonKinesisVideoStreamsReadOnlyAccess',
    'AWSCloudTrailReadOnlyAccess',
    'WAFRegionalLoggingServiceRolePolicy',
    'AWSLambdaExecute',
    'AWSGlueConsoleSageMakerNotebookFullAccess',
    'AmazonMSKFullAccess',
    'AWSIoTRuleActions',
    'AmazonEKSServicePolicy',
    'AWSQuickSightDescribeRedshift',
    'AmazonElasticsearchServiceRolePolicy',
    'AmazonMQReadOnlyAccess',
    'VMImportExportRoleForAWSConnector',
    'AWSCodePipelineCustomActionAccess',
    'AWSLambdaSQSQueueExecutionRole',
    'AWSCloud9ServiceRolePolicy',
    'AWSApplicationAutoscalingECSServicePolicy',
    'AWSOpsWorksInstanceRegistration',
    'AmazonCloudDirectoryFullAccess',
    'AmazonECSTaskExecutionRolePolicy',
    'AWSStorageGatewayFullAccess',
    'AWSIoTEventsFullAccess',
    'AmazonLexReadOnly',
    'TagPoliciesServiceRolePolicy',
    'AmazonChimeUserManagement',
    'AmazonMSKReadOnlyAccess',
    'AWSDataSyncFullAccess',
    'AWSServiceRoleForIoTSiteWise',
    'CloudwatchApplicationInsightsServiceLinkedRolePolicy',
    'AWSTrustedAdvisorServiceRolePolicy',
    'AWSIoTConfigReadOnlyAccess',
    'AmazonWorkMailReadOnlyAccess',
    'AmazonDMSVPCManagementRole',
    'AWSLambdaKinesisExecutionRole',
    'ComprehendDataAccessRolePolicy',
    'AmazonDocDBConsoleFullAccess',
    'ResourceGroupsandTagEditorReadOnlyAccess',
    'AmazonRekognitionServiceRole',
    'AmazonSSMAutomationRole',
    'CloudHSMServiceRolePolicy',
    'ComprehendReadOnly',
    'AWSStepFunctionsConsoleFullAccess',
    'AWSQuickSightIoTAnalyticsAccess',
    'AWSCodeBuildReadOnlyAccess',
    'LexBotPolicy',
    'AmazonMacieFullAccess',
    'AmazonMachineLearningManageRealTimeEndpointOnlyAccess',
    'CloudWatchEventsInvocationAccess',
    'CloudFrontReadOnlyAccess',
    'AWSDeepLensServiceRolePolicy',
    'AmazonSNSRole',
    'AmazonInspectorServiceRolePolicy',
    'AmazonMobileAnalyticsFinancialReportAccess',
    'AWSElasticBeanstalkService',
    'IAMReadOnlyAccess',
    'AmazonRDSReadOnlyAccess',
    'AWSIoTDeviceDefenderAudit',
    'AmazonCognitoPowerUser',
    'AmazonRoute53AutoNamingRegistrantAccess',
    'AmazonElasticFileSystemFullAccess',
    'LexChannelPolicy',
    'ServerMigrationConnector',
    'AmazonESCognitoAccess',
    'AWSFMAdminFullAccess',
    'AmazonChimeReadOnly',
    'AmazonZocaloFullAccess',
    'AWSLambdaReadOnlyAccess',
    'AWSIoTSiteWiseReadOnlyAccess',
    'AWSAccountUsageReportAccess',
    'AWSIoTOTAUpdate',
    'AmazonMQFullAccess',
    'AWSMarketplaceGetEntitlements',
    'AWSGreengrassReadOnlyAccess',
    'AmazonEC2ContainerServiceforEC2Role',
    'AmazonAppStreamFullAccess',
    'AWSIoTDataAccess',
    'AmazonWorkLinkFullAccess',
    'AmazonTranscribeReadOnlyAccess',
    'AmazonESFullAccess',
    'ServerMigrationServiceRole',
    'ApplicationDiscoveryServiceContinuousExportServiceRolePolicy',
    'AmazonSumerianFullAccess',
    'AWSWAFFullAccess',
    'ElasticLoadBalancingReadOnly',
    'AWSArtifactAccountSync',
    'AmazonKinesisFirehoseFullAccess',
    'CloudWatchReadOnlyAccess',
    'AWSLambdaBasicExecutionRole',
    'ResourceGroupsandTagEditorFullAccess',
    'AWSKeyManagementServicePowerUser',
    'AWSApplicationAutoscalingEC2SpotFleetRequestPolicy',
    'AWSImportExportReadOnlyAccess',
    'CloudWatchEventsServiceRolePolicy',
    'AmazonElasticTranscoderRole',
    'AWSGlueConsoleFullAccess',
    'AmazonEC2ContainerServiceRole',
    'AWSDeviceFarmFullAccess',
    'AmazonSSMReadOnlyAccess',
    'AWSStepFunctionsReadOnlyAccess',
    'AWSMarketplaceRead-only',
    'AWSApplicationAutoscalingDynamoDBTablePolicy',
    'AWSCodePipelineFullAccess',
    'AWSCloud9User',
    'AWSGreengrassResourceAccessRolePolicy',
    'AmazonMacieServiceRolePolicy',
    'NetworkAdministrator',
    'AWSIoT1ClickFullAccess',
    'AmazonWorkSpacesApplicationManagerAdminAccess',
    'AmazonDRSVPCManagement',
    'AmazonRedshiftServiceLinkedRolePolicy',
    'AWSCertificateManagerPrivateCAReadOnly',
    'AWSXrayFullAccess',
    'AWSElasticBeanstalkWorkerTier',
    'AWSDirectConnectFullAccess',
    'AWSCodeBuildAdminAccess',
    'AmazonKinesisAnalyticsFullAccess',
    'AWSSecurityHubServiceRolePolicy',
    'AWSElasticBeanstalkMaintenance',
    'APIGatewayServiceRolePolicy',
    'AWSAccountActivityAccess',
    'AmazonGlacierFullAccess',
    'AmazonFSxConsoleReadOnlyAccess',
    'AmazonWorkMailFullAccess',
    'DAXServiceRolePolicy',
    'ComprehendMedicalFullAccess',
    'AWSMarketplaceManageSubscriptions',
    'AWSElasticBeanstalkCustomPlatformforEC2Role',
    'AWSDataSyncReadOnlyAccess',
    'AWSVPCTransitGatewayServiceRolePolicy',
    'NeptuneReadOnlyAccess',
    'AWSSupportAccess',
    'AmazonElasticMapReduceforAutoScalingRole',
    'AWSElementalMediaConvertReadOnly',
    'AWSLambdaInvocation-DynamoDB',
    'AWSServiceCatalogEndUserFullAccess',
    'IAMUserSSHKeys',
    'AWSDeepRacerServiceRolePolicy',
    'AmazonSageMakerReadOnly',
    'AWSIoTFullAccess',
    'AWSQuickSightDescribeRDS',
    'AWSResourceAccessManagerServiceRolePolicy',
    'AWSConfigRulesExecutionRole',
    'AWSConfigServiceRolePolicy',
    'AmazonESReadOnlyAccess',
    'AWSCodeDeployDeployerAccess',
    'KafkaServiceRolePolicy',
    'AmazonPollyFullAccess',
    'AmazonSSMMaintenanceWindowRole',
    'AmazonRDSEnhancedMonitoringRole',
    'AmazonLexFullAccess',
    'AWSLambdaVPCAccessExecutionRole',
    'AmazonMacieServiceRole',
    'AmazonLexRunBotsOnly',
    'AWSCertificateManagerPrivateCAAuditor',
    'AmazonSNSFullAccess',
    'AmazonEKS_CNI_Policy',
    'AWSServiceCatalogAdminFullAccess',
    'AWSShieldDRTAccessPolicy',
    'CloudSearchReadOnlyAccess',
    'AWSGreengrassFullAccess',
    'NeptuneConsoleFullAccess',
    'AWSCloudFormationReadOnlyAccess',
    'AmazonRoute53FullAccess',
    'AWSLambdaRole',
    'AWSLambdaENIManagementAccess',
    'AWSOpsWorksCloudWatchLogs',
    'AmazonAppStreamReadOnlyAccess',
    'AWSStepFunctionsFullAccess',
    'CloudTrailServiceRolePolicy',
    'AmazonInspectorReadOnlyAccess',
    'AWSOrganizationsReadOnlyAccess',
    'TranslateReadOnly',
    'AWSCertificateManagerFullAccess',
    'AWSDeepRacerCloudFormationAccessPolicy',
    'AWSIoTEventsReadOnlyAccess',
    'AWSRoboMakerServicePolicy',
    'PowerUserAccess',
    'AWSApplicationAutoScalingCustomResourcePolicy',
    'GlobalAcceleratorReadOnlyAccess',
    'AmazonSageMakerFullAccess',
    'WAFLoggingServiceRolePolicy',
    'AWSBackupServiceRolePolicyForRestores',
    'AWSElementalMediaStoreFullAccess',
    'CloudWatchEventsFullAccess',
    'AWSLicenseManagerMemberAccountRolePolicy',
    'AWSOrganizationsFullAccess',
    'AmazonFraudDetectorFullAccessPolicy',
    'AmazonChimeSDK',
    'AWSIoTDeviceTesterForFreeRTOSFullAccess',
    'WAFV2LoggingServiceRolePolicy',
    'AWSNetworkManagerFullAccess',
    'AWSPrivateMarketplaceRequests',
    'AmazonSageMakerMechanicalTurkAccess',
    'AWSNetworkManagerServiceRolePolicy',
    'AWSAppMeshServiceRolePolicy',
    'AWSConfigRemediationServiceRolePolicy',
    'ConfigConformsServiceRolePolicy',
    'AmazonEventBridgeReadOnlyAccess',
    'AWSCodeStarNotificationsServiceRolePolicy',
    'AmazonKendraFullAccess',
    'AWSApplicationAutoscalingCassandraTablePolicy',
    'AWSSystemsManagerAccountDiscoveryServicePolicy',
    'AWSResourceAccessManagerReadOnlyAccess',
    'AmazonEventBridgeFullAccess',
    'CloudWatchSyntheticsReadOnlyAccess',
    'AccessAnalyzerServiceRolePolicy',
    'AmazonRoute53ResolverReadOnlyAccess',
    'AmazonEC2RolePolicyForLaunchWizard',
    'AmazonManagedBlockchainFullAccess',
    'ServiceQuotasFullAccess',
    'AWSIoTSiteWiseMonitorServiceRolePolicy',
    'AWSCloudFormationFullAccess',
    'ElementalAppliancesSoftwareFullAccess',
    'AmazonAugmentedAIHumanLoopFullAccess',
    'AWSDataExchangeReadOnly',
    'AWSMarketplaceSellerProductsFullAccess',
    'AWSIQContractServiceRolePolicy',
    'AmazonLaunchWizardFullaccess',
    'AmazonWorkDocsReadOnlyAccess',
    'AWSGlobalAcceleratorSLRPolicy',
    'EC2InstanceProfileForImageBuilder',
    'AWSServiceRoleForLogDeliveryPolicy',
    'AmazonCodeGuruReviewerFullAccess',
    'AWSVPCS2SVpnServiceRolePolicy',
    'AWSImageBuilderFullAccess',
    'AWSCertificateManagerPrivateCAPrivilegedUser',
    'AWSOpsWorksRegisterCLI_OnPremises',
    'Health_OrganizationsServiceRolePolicy',
    'AmazonMCSReadOnlyAccess',
    'AWSAppMeshPreviewServiceRolePolicy',
    'ServiceQuotasServiceRolePolicy',
    'ComputeOptimizerReadOnlyAccess',
    'AlexaForBusinessPolyDelegatedAccessPolicy',
    'AWSMarketplaceProcurementSystemAdminFullAccess',
    'AmazonEKSFargatePodExecutionRolePolicy',
    'IAMAccessAdvisorReadOnly',
    'AmazonCodeGuruReviewerReadOnlyAccess',
    'AmazonCodeGuruProfilerFullAccess',
    'AmazonElasticFileSystemServiceRolePolicy',
    'AWSResourceAccessManagerFullAccess',
    'AWSIoTDeviceDefenderEnableIoTLoggingMitigationAction',
    'DynamoDBCloudWatchContributorInsightsServiceRolePolicy',
    'AmazonChimeVoiceConnectorServiceLinkedRolePolicy',
    'IAMAccessAnalyzerReadOnlyAccess',
    'AmazonEventBridgeSchemasServiceRolePolicy',
    'AWSIoTDeviceDefenderPublishFindingsToSNSMitigationAction',
    'AmazonQLDBConsoleFullAccess',
    'AmazonElasticFileSystemClientReadWriteAccess',
    'AWSApplicationAutoscalingComprehendEndpointPolicy',
    'AWSIoTDeviceDefenderAddThingsToThingGroupMitigationAction',
    'AmazonQLDBFullAccess',
    'AmazonAugmentedAIFullAccess',
    'AWSIoTDeviceDefenderReplaceDefaultPolicyMitigationAction',
    'AWSAppMeshReadOnly',
    'ComputeOptimizerServiceRolePolicy',
    'AWSElasticBeanstalkManagedUpdatesServiceRolePolicy',
    'AmazonQLDBReadOnly',
    'AWSChatbotServiceLinkedRolePolicy',
    'AWSAppSyncServiceRolePolicy',
    'AWSAppMeshFullAccess',
    'AWSServiceRoleForGammaInternalAmazonEKSNodegroup',
    'ServiceQuotasReadOnlyAccess',
    'EC2FleetTimeShiftableServiceRolePolicy',
    'MigrationHubDMSAccessServiceRolePolicy',
    'AWSServiceCatalogEndUserReadOnlyAccess',
    'AWSIQPermissionServiceRolePolicy',
    'AmazonEKSForFargateServiceRolePolicy',
    'MigrationHubSMSAccessServiceRolePolicy',
    'CloudFormationStackSetsOrgAdminServiceRolePolicy',
    'AmazonEventBridgeSchemasFullAccess',
    'AWSMarketplaceSellerFullAccess',
    'CloudWatchAutomaticDashboardsAccess',
    'AmazonWorkMailEventsServiceRolePolicy',
    'AmazonEventBridgeSchemasReadOnlyAccess',
    'AWSMarketplaceSellerProductsReadOnly',
    'AmazonMCSFullAccess',
    'AWSIoTSiteWiseConsoleFullAccess',
    'AmazonElasticFileSystemClientFullAccess',
    'AWSIoTDeviceDefenderUpdateDeviceCertMitigationAction',
    'AWSForWordPressPluginPolicy',
    'AWSServiceRoleForAmazonEKSNodegroup',
    'AWSBackupOperatorAccess',
    'AWSApplicationAutoscalingLambdaConcurrencyPolicy',
    'AmazonMachineLearningRoleforRedshiftDataSourceV2',
    'AWSIoTDeviceDefenderUpdateCACertMitigationAction',
    'AmazonWorkSpacesServiceAccess',
    'AmazonEKSServiceRolePolicy',
    'AWSConfigMultiAccountSetupPolicy',
    'AmazonElasticFileSystemClientReadOnlyAccess',
    'CloudFormationStackSetsOrgMemberServiceRolePolicy',
    'AWSResourceAccessManagerResourceShareParticipantAccess',
    'AWSBackupFullAccess',
    'AmazonCodeGuruProfilerReadOnlyAccess',
    'AWSNetworkManagerReadOnlyAccess',
    'CloudWatchSyntheticsFullAccess',
    'AWSDataExchangeSubscriberFullAccess',
    'IAMAccessAnalyzerFullAccess',
    'AWSServiceCatalogAdminReadOnlyAccess',
    'AWSQuickSightSageMakerPolicy',
    'AmazonWorkSpacesSelfServiceAccess',
    'AmazonManagedBlockchainServiceRolePolicy',
    'AWSDataExchangeFullAccess',
    'AWSDataExchangeProviderFullAccess',
    'AWSControlTowerServiceRolePolicy',
    'AmazonSageMakerNotebooksServiceRolePolicy',
    'AmazonRoute53ResolverFullAccess',
    'LakeFormationDataAccessServiceRolePolicy',
    'AmazonChimeServiceRolePolicy',
    'AWSTrustedAdvisorReportingServiceRolePolicy',
    'AWSOpsWorksRegisterCLI_EC2',
    'AWSSavingsPlansFullAccess',
    'AWSServiceRoleForImageBuilder',
    'AmazonCodeGuruReviewerServiceRolePolicy',
    'AWSAppMeshPreviewEnvoyAccess',
    'AmazonLambdaRolePolicyForLaunchWizardSAP',
    'MigrationHubServiceRolePolicy',
    'AWSImageBuilderReadOnlyAccess',
    'AWSMarketplaceMeteringRegisterUsage',
    'AmazonManagedBlockchainReadOnlyAccess',
    'AmazonRekognitionCustomLabelsFullAccess',
    'AmazonManagedBlockchainConsoleFullAccess',
    'AWSSavingsPlansReadOnlyAccess',
    'AWSIoTDeviceTesterForGreengrassFullAccess',
    'AWSServiceRoleForSMS',
    'CloudWatch-CrossAccountAccess',
    'AWSLakeFormationDataAdmin',
    'AWSDenyAll',
    'AWSIQFullAccess',
    'EC2InstanceConnect',
    'AWSAppMeshEnvoyAccess',
    'AmazonKendraReadOnlyAccess',
])

# Generated with the script
# #!/usr/bin/env python
# import boto3
# import json
#
# client = boto3.client('rds', region_name='us-west-2')
# paginator = client.get_paginator('describe_db_engine_versions')
#
# rds_engine_versions = {}
# for engine in ['postgres','mysql']:
#     rds_engine_versions[engine] = {}
#     response_iterator = paginator.paginate(
#         Engine=engine
#     )
#     for response in response_iterator:
#         for version in response['DBEngineVersions']:
#             rds_engine_versions[engine][version['EngineVersion']] = {}
#             rds_engine_versions[engine][version['EngineVersion']]['param_group_family'] = version['DBParameterGroupFamily']
#
# print(json.dumps(rds_engine_versions, indent=2))
rds_engine_versions = {
  "postgres": {
    "9.4.7": {
      "param_group_family": "postgres9.4"
    },
    "9.4.9": {
      "param_group_family": "postgres9.4"
    },
    "9.4.11": {
      "param_group_family": "postgres9.4"
    },
    "9.4.12": {
      "param_group_family": "postgres9.4"
    },
    "9.4.14": {
      "param_group_family": "postgres9.4"
    },
    "9.4.15": {
      "param_group_family": "postgres9.4"
    },
    "9.4.17": {
      "param_group_family": "postgres9.4"
    },
    "9.4.18": {
      "param_group_family": "postgres9.4"
    },
    "9.4.19": {
      "param_group_family": "postgres9.4"
    },
    "9.4.20": {
      "param_group_family": "postgres9.4"
    },
    "9.4.21": {
      "param_group_family": "postgres9.4"
    },
    "9.4.23": {
      "param_group_family": "postgres9.4"
    },
    "9.4.24": {
      "param_group_family": "postgres9.4"
    },
    "9.4.25": {
      "param_group_family": "postgres9.4"
    },
    "9.5.2": {
      "param_group_family": "postgres9.5"
    },
    "9.5.4": {
      "param_group_family": "postgres9.5"
    },
    "9.5.6": {
      "param_group_family": "postgres9.5"
    },
    "9.5.7": {
      "param_group_family": "postgres9.5"
    },
    "9.5.9": {
      "param_group_family": "postgres9.5"
    },
    "9.5.10": {
      "param_group_family": "postgres9.5"
    },
    "9.5.12": {
      "param_group_family": "postgres9.5"
    },
    "9.5.13": {
      "param_group_family": "postgres9.5"
    },
    "9.5.14": {
      "param_group_family": "postgres9.5"
    },
    "9.5.15": {
      "param_group_family": "postgres9.5"
    },
    "9.5.16": {
      "param_group_family": "postgres9.5"
    },
    "9.5.18": {
      "param_group_family": "postgres9.5"
    },
    "9.5.19": {
      "param_group_family": "postgres9.5"
    },
    "9.5.20": {
      "param_group_family": "postgres9.5"
    },
    "9.6.1": {
      "param_group_family": "postgres9.6"
    },
    "9.6.2": {
      "param_group_family": "postgres9.6"
    },
    "9.6.3": {
      "param_group_family": "postgres9.6"
    },
    "9.6.5": {
      "param_group_family": "postgres9.6"
    },
    "9.6.6": {
      "param_group_family": "postgres9.6"
    },
    "9.6.8": {
      "param_group_family": "postgres9.6"
    },
    "9.6.9": {
      "param_group_family": "postgres9.6"
    },
    "9.6.10": {
      "param_group_family": "postgres9.6"
    },
    "9.6.11": {
      "param_group_family": "postgres9.6"
    },
    "9.6.12": {
      "param_group_family": "postgres9.6"
    },
    "9.6.14": {
      "param_group_family": "postgres9.6"
    },
    "9.6.15": {
      "param_group_family": "postgres9.6"
    },
    "9.6.16": {
      "param_group_family": "postgres9.6"
    },
    "10.1": {
      "param_group_family": "postgres10"
    },
    "10.3": {
      "param_group_family": "postgres10"
    },
    "10.4": {
      "param_group_family": "postgres10"
    },
    "10.5": {
      "param_group_family": "postgres10"
    },
    "10.6": {
      "param_group_family": "postgres10"
    },
    "10.7": {
      "param_group_family": "postgres10"
    },
    "10.9": {
      "param_group_family": "postgres10"
    },
    "10.10": {
      "param_group_family": "postgres10"
    },
    "10.11": {
      "param_group_family": "postgres10"
    },
    "11.1": {
      "param_group_family": "postgres11"
    },
    "11.2": {
      "param_group_family": "postgres11"
    },
    "11.4": {
      "param_group_family": "postgres11"
    },
    "11.5": {
      "param_group_family": "postgres11"
    },
    "11.6": {
      "param_group_family": "postgres11"
    },
    "12.2": {
      "param_group_family": "postgres12"
    }
  },
  "mysql": {
    "5.5.46": {
      "param_group_family": "mysql5.5"
    },
    "5.5.53": {
      "param_group_family": "mysql5.5"
    },
    "5.5.54": {
      "param_group_family": "mysql5.5"
    },
    "5.5.57": {
      "param_group_family": "mysql5.5"
    },
    "5.5.59": {
      "param_group_family": "mysql5.5"
    },
    "5.5.61": {
      "param_group_family": "mysql5.5"
    },
    "5.6.34": {
      "param_group_family": "mysql5.6"
    },
    "5.6.35": {
      "param_group_family": "mysql5.6"
    },
    "5.6.37": {
      "param_group_family": "mysql5.6"
    },
    "5.6.39": {
      "param_group_family": "mysql5.6"
    },
    "5.6.40": {
      "param_group_family": "mysql5.6"
    },
    "5.6.41": {
      "param_group_family": "mysql5.6"
    },
    "5.6.43": {
      "param_group_family": "mysql5.6"
    },
    "5.6.44": {
      "param_group_family": "mysql5.6"
    },
    "5.6.46": {
      "param_group_family": "mysql5.6"
    },
    "5.7.16": {
      "param_group_family": "mysql5.7"
    },
    "5.7.17": {
      "param_group_family": "mysql5.7"
    },
    "5.7.19": {
      "param_group_family": "mysql5.7"
    },
    "5.7.21": {
      "param_group_family": "mysql5.7"
    },
    "5.7.22": {
      "param_group_family": "mysql5.7"
    },
    "5.7.23": {
      "param_group_family": "mysql5.7"
    },
    "5.7.24": {
      "param_group_family": "mysql5.7"
    },
    "5.7.25": {
      "param_group_family": "mysql5.7"
    },
    "5.7.26": {
      "param_group_family": "mysql5.7"
    },
    "5.7.28": {
      "param_group_family": "mysql5.7"
    },
    "8.0.11": {
      "param_group_family": "mysql8.0"
    },
    "8.0.13": {
      "param_group_family": "mysql8.0"
    },
    "8.0.15": {
      "param_group_family": "mysql8.0"
    },
    "8.0.16": {
      "param_group_family": "mysql8.0"
    },
    "8.0.17": {
      "param_group_family": "mysql8.0"
    }
  }
}

ami_types = [
    'amazon',
    'centos',
    'redhat',
    'suse',
    'suse_12',
    'debian',
    'debian_8',
    'debian_9',
    'ubuntu',
    'ubuntu_14',
    'ubuntu_16',
    'ubuntu_16_386',
    'ubuntu_16',
    'ubuntu_16_snap', # Instances created from Ubuntu Server 16.04 AMIs identified with 20180627, SSM Agent is pre-installed using Snap packages
    'ubuntu_17',
    'ubuntu_18',
    'ubuntu_19',
    'ubuntu_20',
    'microsoft'
]
