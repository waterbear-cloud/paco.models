import os.path
import boto3
import json
import pathlib
from operator import itemgetter


def update_gen_vocabulary():
    gen_vocabulary_path = os.path.dirname(__file__) + os.sep + '..' + os.sep + 'models' + os.sep + 'gen_vocabulary.py'
    gen_vocabulary_path_new = gen_vocabulary_path + '.new'
    print("Updating paco.models generated vocabulary")
    print(f"file path: {gen_vocabulary_path}")
    print()
    with open(gen_vocabulary_path_new, 'w') as f:
        f.write("""# Generated file: do not edit
# see README.md on how to run paco_update_gen_vocabulary to update this with the latest data from AWS

from zope.schema.vocabulary import SimpleVocabulary

""")
        print("Updating EC2 AMI Ids")
        regions = [
            'us-east-2',
            'us-east-1',
            'us-west-1',
            'us-west-2',
            'ca-central-1',
            'eu-central-1',
            'eu-west-1',
            'eu-west-2',
            'eu-west-3',
            'ap-southeast-1',
            'ap-southeast-2',
        ]
        ami_types = [
            {
                'ami_yaml_name': 'amazon-linux-2-ecs',
                'ami_description': "Amazon Linux AMI 2*",
                'ami_name': "amzn2-ami-ecs-hvm-*"
            },
            {
                'ami_yaml_name': 'amazon-linux-2',
                'ami_description': "Amazon Linux 2 AMI*",
                'ami_name': "amzn2-ami-hvm-*"
            },
            {
                'ami_yaml_name': 'amazon-linux-nat',
                'ami_description': "Amazon Linux AMI*",
                'ami_name': "amzn-ami-vpc-nat-hvm-*"
            },
        ]
        ami_images = {}
        for region in regions:
            print(f"Getting AMI Ids for {region}")
            ami_images[region] = {}
            ec2_client = boto3.client('ec2', region_name=region)
            for ami_type in ami_types:
                filters = [ {
                    'Name': 'name',
                    'Values': [ami_type['ami_name']]
                },{
                    'Name': 'description',
                    'Values': [ami_type['ami_description']]
                },{
                    'Name': 'architecture',
                    'Values': ['x86_64']
                },{
                    'Name': 'owner-alias',
                    'Values': ['amazon']
                },{
                    'Name': 'owner-id',
                    'Values': ['*']
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
                ami_list = ec2_client.describe_images(
                    Filters=filters,
                    Owners=[
                        'amazon'
                    ]
                )
                # sorted by newest first
                image_brief = []
                for image_info in sorted(ami_list['Images'], key=itemgetter('CreationDate'), reverse=True):
                    if image_info['State'] == 'available':
                        image_brief.append({
                            'ImageId': image_info['ImageId'],
                            'CreationDate': image_info['CreationDate'],
                        })
                ami_images[region][ami_type['ami_yaml_name']] = image_brief
        f.write("ami_ids = ")
        f.write(json.dumps(ami_images, indent=2))
        f.write("\n\n")

        print("Updating IAM Managed Policies vocabulary")
        client = boto3.client('iam')
        f.write("iam_managed_policies = SimpleVocabulary.fromValues([\n")
        paginator = client.get_paginator('list_policies')
        response_iterator = paginator.paginate(Scope='AWS')
        for response in response_iterator:
            for policy in response['Policies']:
                f.write("    '{}',\n".format(policy['PolicyName']))
        f.write("])\n\n")

        print("Updating RDS Engine Verions vocabulary")
        client = boto3.client('rds', region_name='us-west-2')
        paginator = client.get_paginator('describe_db_engine_versions')
        rds_engine_versions = {}
        for engine in ['postgres','mysql', 'aurora', 'aurora-mysql', 'aurora-postgresql']:
            rds_engine_versions[engine] = {}
            response_iterator = paginator.paginate(
                Engine=engine
            )
            for response in response_iterator:
                for version in response['DBEngineVersions']:
                    rds_engine_versions[engine][version['EngineVersion']] = {}
                    rds_engine_versions[engine][version['EngineVersion']]['param_group_family'] = version['DBParameterGroupFamily']
        f.write("rds_engine_versions = ")
        f.write(json.dumps(rds_engine_versions, indent=2))
        f.write("\n\n")

    pathlib.Path(gen_vocabulary_path_new).rename(gen_vocabulary_path)
    print("Done!")
