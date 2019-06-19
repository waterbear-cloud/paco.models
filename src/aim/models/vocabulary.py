"""
Vocabularies

https://docs.plone.org/develop/plone/forms/vocabularies.html
"""

from zope.schema.vocabulary import SimpleVocabulary

application_group_types = [
    'Application',
    'Bastion',
    'Deployment',
]

cloudwatch = {
	'ASG': {
		'dimension': 'AutoScalingGroupName',
		'namespace': 'AWS/AutoScaling'
	},
	'LBApplication': {
		'dimension': 'LoadBalancer',
		'namespace': 'AWS/ApplicationELB'
	}
}

alarm_classifications = {
	'health': None,
	'performance': None,
	'security': None
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
    }
}

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
}

target_group_protocol = SimpleVocabulary.fromValues(
    ['HTTP','HTTPS']
)

lb_scheme = SimpleVocabulary.fromValues(
    ['internet-facing','internal']
)

iam_policy_effect = SimpleVocabulary.fromValues(
    ['Allow','Deny']
)