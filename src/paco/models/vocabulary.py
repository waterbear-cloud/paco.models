"""
Vocabularies

https://docs.plone.org/develop/plone/forms/vocabularies.html
"""

from zope.schema.vocabulary import SimpleVocabulary

aws_policy_condition_strings = [
    "ArnEquals",
    "ArnNotEquals",
    "ArnLike",
    "ArnNotLike",
    "Bool",
    "DateEquals",
    "DateNotEquals",
    "DateLessThan",
    "DateLessThanEquals",
    "DateGreaterThan",
    "DateGreaterThanEquals",
    "IpAddress",
    "NotIpAddress",
    "Null",
    "NumericEquals",
    "NumericNotEquals",
    "NumericLessThan",
    "NumericLessThanEquals",
    "NumericGreaterThan",
    "NumericGreaterThanEquals",
    "StringEquals",
    "StringNotEquals",
    "StringEqualsIgnoreCase",
    "StringNotEqualsIgnoreCase",
    "StringLike",
    "StringNotLike",
]

aws_config_delivery_frequencies = SimpleVocabulary.fromValues([
 'One_Hour', 'Six_Hours', 'Three_Hours', 'Twelve_Hours','TwentyFour_Hours',
])

codecommit_permissions = SimpleVocabulary.fromValues([
  'ReadWrite',
  'ReadOnly',
])

network_protocols = SimpleVocabulary.fromValues([
  'tcp',
  'udp',
])

log_levels = SimpleVocabulary.fromValues([
	'crit',
	'error',
	'warn',
	'info',
	'debug',
])

dynamodb_attribute_types = SimpleVocabulary.fromValues([
	'S',
	'N',
	'B',
])

dynamodb_key_types = SimpleVocabulary.fromValues([
	'HASH',
	'RANGE',
])

dynamodb_project_types = SimpleVocabulary.fromValues([
	'ALL',
	'INCLUDE',
	'KEYS_ONLY',
])

dynamodb_billing_modes = SimpleVocabulary.fromValues([
	'provisioned',
	'pay_per_request',
])

ecr_permissions = SimpleVocabulary.fromValues([
	'Push',
	'Pull',
	'PushAndPull',
])

ecs_network_modes = SimpleVocabulary.fromValues([
	'awsvpc',
	'bridge',
	'host',
	'none',
])

ecs_deployment_types = SimpleVocabulary.fromValues([
	'ecs',
	'code_deploy',
	'external'
])

ecs_log_drivers = SimpleVocabulary.fromValues([
    'awsfirelens',
    'awslogs',
    'fluentd',
    'gelf',
    'journald',
    'json-file',
    'splunk',
    'syslog'
])

ecs_container_conditions = SimpleVocabulary.fromValues([
	'COMPLETE',
	'HEALTHY',
	'START',
	'SUCCESS',
])

ecs_docker_security_options = SimpleVocabulary.fromValues([
	"no-new-privileges",
	"apparmor:PROFILE",
	"label:value",
	"credentialspec:CredentialSpecFilePath"
])

ecs_ulimit = SimpleVocabulary.fromValues([
	'core',
	'cpu',
	'data',
	'fsize',
	'locks',
	'memlock',
	'msgqueue',
	'nice',
	'nofile',
	'nproc',
	'rss',
	'rtprio',
	'rttime',
	'sigpending',
	'stack',
])

ecs_predefined_metrics = SimpleVocabulary.fromValues([
	"ALBRequestCountPerTarget", "ECSServiceAverageMemoryUtilization", "ECSServiceAverageCPUUtilization",
])

ecs_launch_types = SimpleVocabulary.fromValues([
	"EC2", "Fargate",
])

apigateway_pass_through_behaviors = SimpleVocabulary.fromValues([
	"WHEN_NO_MATCH", "NEVER", "WHEN_NO_TEMPLATES",
])

cognito_mfa_configuration = SimpleVocabulary.fromValues([
	"off", "on", "optional",
])

cognito_schema_datatype = SimpleVocabulary.fromValues([
	"boolean", "datetime", "number", "string",
])

cognito_allowed_oauth_flows = SimpleVocabulary.fromValues([
	"code", "implicit", "client_credentials",
])

cognito_identity_providers = SimpleVocabulary.fromValues([
	"cognito", "facebook", "google", "amazon",
])

cognito_mfa_methods = SimpleVocabulary.fromValues([
	"sms", "software_token",
])

cloudfront_event_types = SimpleVocabulary.fromValues([
	"origin-request", "origin-response", "viewer-request", "viewer-response",
])

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

rds_cluster_engine_mode = SimpleVocabulary.fromValues([
	'provisioned',
	'serverless',
	'parallelquery',
	'global',
	'multimaster'
])

rds_restore_types = SimpleVocabulary.fromValues([
	'full-copy',
	'copy-on-write',
])

rds_cluster_event_categories = SimpleVocabulary.fromValues([
	"maintenance",
	"failover",
	"notification",
	"creation",
	"failure",
	"deletion",
])

rds_instance_event_categories = SimpleVocabulary.fromValues([
	"backup",
	"maintenance",
	"failover",
	"creation",
	"configuration change",
	"recovery",
	"deletion",
	"restoration",
	"failure",
	"read replica",
	"availability",
	"low storage",
	"notification",
	"backtrack",
])

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
	'ECSCluster': {
		'dimension': 'ClusterName',
		'namespace': 'AWS/ECS',
	},
	'ECSServices': {
		'dimension': 'ClusterName',
		'namespace': 'AWS/ECS',
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
	'RDSMysqlAurora': {
		'dimension': 'DBInstanceIdentifier',
		'namespace': 'AWS/RDS'
	},
	'RDSPostgresql': {
		'dimension': 'DBInstanceIdentifier',
		'namespace': 'AWS/RDS'
	},
	'RDSPostgresqlAurora': {
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
    ['HTTP','HTTPS', 'TCP']
)
target_group_health_check_protocol = SimpleVocabulary.fromValues(
    ['HTTP','HTTPS', 'TCP']
)

target_group_target_types = SimpleVocabulary.fromValues(
    ['instance', 'ip', 'lambda']
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

ami_types = [
    'amazon',
    'amazon_ecs',
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
