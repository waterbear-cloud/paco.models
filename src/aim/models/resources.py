"""
All things Resources.
"""

import json
import troposphere.apigateway
from aim.models.base import Named, Deployable, Regionalized, Resource
from aim.models.metrics import Monitorable
from aim.models import references
from aim.models import schemas
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from aim.models import loader
from aim.models.locations import get_parent_by_interface
from aim.models.references import Reference
from aim.models import references


@implementer(schemas.IApiGatewayRestApi)
class ApiGatewayRestApi(Resource):
    title = "API Gateway REST API"
    api_key_source_type = FieldProperty(schemas.IApiGatewayRestApi['api_key_source_type'])
    binary_media_types = FieldProperty(schemas.IApiGatewayRestApi['binary_media_types'])
    body_file_location = FieldProperty(schemas.IApiGatewayRestApi['body_file_location'])
    body_s3_location = FieldProperty(schemas.IApiGatewayRestApi['body_s3_location'])
    clone_from = FieldProperty(schemas.IApiGatewayRestApi['clone_from'])
    description = FieldProperty(schemas.IApiGatewayRestApi['description'])
    endpoint_configuration = FieldProperty(schemas.IApiGatewayRestApi['endpoint_configuration'])
    fail_on_warnings = FieldProperty(schemas.IApiGatewayRestApi['fail_on_warnings'])
    minimum_compression_size = FieldProperty(schemas.IApiGatewayRestApi['minimum_compression_size'])
    parameters = FieldProperty(schemas.IApiGatewayRestApi['parameters'])
    policy = FieldProperty(schemas.IApiGatewayRestApi['policy'])
    _body = None

    @property
    def body(self):
        "Return populated string, either body or body_file_location"
        if self.body_file_location:
            return self.body_file_location
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    @property
    def endpoint_configuration_cfn(self):
        "Warp list with a dict with a 'Types' key for CloudFormation"
        return {'Types': self.endpoint_configuration }

    troposphere_props = troposphere.apigateway.RestApi.props
    cfn_mapping = {
        "ApiKeySourceType": 'api_key_source_type',
        "BinaryMediaTypes": 'binary_media_types',
        "CloneFrom": 'clone_from',
        "Description": 'description',
        "Name": 'name',
        "Body": 'body',
        "FailOnWarnings": 'fail_on_warnings',
        "EndpointConfiguration": ("endpoint_configuration", "endpoint_configuration_cfn"),
        "MinimumCompressionSize": 'minimum_compression_size',
        "Parameters": 'parameters',
        "Policy": 'policy',
    }

@implementer(schemas.IEC2KeyPair)
class EC2KeyPair(Named):
    region = FieldProperty(schemas.IEC2KeyPair['region'])
    account = FieldProperty(schemas.IEC2KeyPair['account'])

@implementer(schemas.IEC2Resource)
class EC2Resource():
    keypairs = FieldProperty(schemas.IEC2Resource['keypairs'])

    def resolve_ref(self, ref):
        if ref.parts[2] == 'keypairs':
            keypair_id = ref.parts[3]
            keypair_attr = 'name'
            if len(ref.parts) > 4:
                keypair_attr = ref.parts[4]
            keypair = self.keypairs[keypair_id]
            if keypair_attr == 'name':
                return keypair.name
            elif keypair_attr == 'region':
                return keypair.region
            elif keypair_attr == 'account':
                return keypair.account

        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IS3Resource)
class S3Resource():
    buckets = FieldProperty(schemas.IS3Resource['buckets'])

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)


@implementer(schemas.IRoute53HostedZone)
class Route53HostedZone(Deployable):
    domain_name = FieldProperty(schemas.IRoute53HostedZone["domain_name"])
    account = FieldProperty(schemas.IRoute53HostedZone["account"])

    def has_record_sets(self):
        return False

@implementer(schemas.IRoute53Resource)
class Route53Resource():

    hosted_zones = FieldProperty(schemas.IRoute53Resource["hosted_zones"])

    def __init__(self, config_dict):
        super().__init__()

        self.zones_by_account = {}
        if config_dict == None:
            return
        loader.apply_attributes_from_config(self, config_dict)

        for zone_id in self.hosted_zones.keys():
            hosted_zone = self.hosted_zones[zone_id]
            aws_account_ref = hosted_zone.account
            ref = Reference(aws_account_ref)
            account_name = ref.parts[1]
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

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ICodeCommitUser)
class CodeCommitUser():
    username = FieldProperty(schemas.ICodeCommitUser["username"])
    public_ssh_key = FieldProperty(schemas.ICodeCommitUser["public_ssh_key"])

@implementer(schemas.ICodeCommitRepository)
class CodeCommitRepository(Named, Deployable, dict):
    account = FieldProperty(schemas.ICodeCommitRepository["account"])
    region = FieldProperty(schemas.ICodeCommitRepository["region"])
    description = FieldProperty(schemas.ICodeCommitRepository["description"])
    users = FieldProperty(schemas.ICodeCommitRepository["users"])

@implementer(schemas.ICodeCommit)
class CodeCommit():
    repository_groups = FieldProperty(schemas.ICodeCommit["repository_groups"])

    def gen_repo_by_account(self):
        self.repo_by_account = {}
        for group_id in self.repository_groups.keys():
            group_config = self.repository_groups[group_id]
            for repo_id in group_config.keys():
                repo_config = group_config[repo_id]
                account_dict = {'group_id': group_id,
                                'repo_id': repo_id,
                                #'account_ref': repo_config.account,
                                'aws_region': repo_config.region,
                                'repo_config': repo_config }
                if repo_config.account in self.repo_by_account.keys():
                    if repo_config.region in self.repo_by_account[repo_config.account].keys():
                        self.repo_by_account[repo_config.account][repo_config.region].append(account_dict)
                    else:
                        self.repo_by_account[repo_config.account][repo_config.region] = [account_dict]
                else:
                    self.repo_by_account[repo_config.account] = {repo_config.region: [account_dict]}

    def repo_account_ids(self):
        return self.repo_by_account.keys()

    def account_region_ids(self, account_id):
        return self.repo_by_account[account_id].keys()

    def repo_list_dict(self, account_id, aws_region):
         return self.repo_by_account[account_id][aws_region]

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.ICloudTrail)
class CloudTrail(Resource):
    type = 'CloudTrail'
    accounts = FieldProperty(schemas.ICloudTrail["accounts"])
    enable_kms_encryption = FieldProperty(schemas.ICloudTrail["enable_kms_encryption"])
    enable_log_file_validation = FieldProperty(schemas.ICloudTrail["enable_log_file_validation"])
    include_global_service_events = FieldProperty(schemas.ICloudTrail["include_global_service_events"])
    is_multi_region_trail = FieldProperty(schemas.ICloudTrail["is_multi_region_trail"])
    region = FieldProperty(schemas.ICloudTrail["region"])
    s3_key_prefix = FieldProperty(schemas.ICloudTrail["s3_key_prefix"])

    def get_accounts(self):
        """
        Resolve the CloudTrail.accounts field to a list of IAccount objects from the model.
        If the field is empty, then all accounts are returned.
        """
        project = get_parent_by_interface(self, schemas.IProject)
        if self.accounts == []:
            accounts = project['accounts'].values()
        else:
            accounts = []
            for account_ref in self.accounts:
                # ToDo: when accounts .get_ref returns an object, remove this workaround
                ref = references.Reference(account_ref)
                account = project['accounts'][ref.last_part]
                accounts.append(account)
        return accounts

@implementer(schemas.ICloudTrails)
class CloudTrails(Named, dict):
    pass

@implementer(schemas.ICloudTrailResource)
class CloudTrailResource(Named):

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.trails = CloudTrails('trails', self)

@implementer(schemas.IIAMUserProgrammaticAccess)
class IAMUserProgrammaticAccess(Deployable):
    access_key_1_version = FieldProperty(schemas.IIAMUserProgrammaticAccess['access_key_1_version'])
    access_key_2_version = FieldProperty(schemas.IIAMUserProgrammaticAccess['access_key_2_version'])

@implementer(schemas.IIAMUserPermission)
class IAMUserPermission(Named, Deployable):
    type = FieldProperty(schemas.IIAMUserPermission['type'])


@implementer(schemas.IIAMUserPermissionAdministrator)
class IAMUserPermissionAdministrator(IAMUserPermission):
    accounts = FieldProperty(schemas.IIAMUserPermissionAdministrator['accounts'])
    read_only = FieldProperty(schemas.IIAMUserPermissionAdministrator['read_only'])

@implementer(schemas.IIAMUserPermissionCodeCommitRepository)
class IAMUserPermissionCodeCommitRepository():
    codecommit = FieldProperty(schemas.IIAMUserPermissionCodeCommitRepository['codecommit'])
    permission = FieldProperty(schemas.IIAMUserPermissionCodeCommitRepository['permission'])
    console_access_enabled = FieldProperty(schemas.IIAMUserPermissionCodeCommitRepository['console_access_enabled'])
    public_ssh_key = FieldProperty(schemas.IIAMUserPermissionCodeCommitRepository['public_ssh_key'])

@implementer(schemas.IIAMUserPermissionCodeCommit)
class IAMUserPermissionCodeCommit(IAMUserPermission, IAMUserPermissionCodeCommitRepository):
    repositories = FieldProperty(schemas.IIAMUserPermissionCodeCommit['repositories'])

@implementer(schemas.IIAMUserPermissions)
class IAMUserPermissions(Named, dict):
    pass

@implementer(schemas.IIAMUser)
class IAMUser(Named):
    account = FieldProperty(schemas.IIAMUser['account'])
    username = FieldProperty(schemas.IIAMUser['username'])
    description = FieldProperty(schemas.IIAMUser['description'])
    console_access_enabled = FieldProperty(schemas.IIAMUser['console_access_enabled'])
    programmatic_access = FieldProperty(schemas.IIAMUser['programmatic_access'])
    permissions = FieldProperty(schemas.IIAMUser['permissions'])
    account_whitelist = FieldProperty(schemas.IIAMUser['account_whitelist'])


@implementer(schemas.IIAMResource)
class IAMResource():
    users = FieldProperty(schemas.IIAMResource['users'])