"""
All things Resources.
"""

import json
import troposphere.apigateway
from aim.models.base import Named, CFNExport, Deployable, Regionalized, Resource
from aim.models.metrics import Monitorable
from aim.models import references
from aim.models import schemas
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from aim.models import loader
from aim.models.locations import get_parent_by_interface
from aim.models.references import Reference
from aim.models import references

@implementer(schemas.IApiGatewayMethods)
class ApiGatewayMethods(Named, dict):
    pass

@implementer(schemas.IApiGatewayMethodIntegrationResponse)
class ApiGatewayMethodIntegrationResponse(CFNExport):
    content_handling = FieldProperty(schemas.IApiGatewayMethodIntegrationResponse['content_handling'])
    response_parameters = FieldProperty(schemas.IApiGatewayMethodIntegrationResponse['response_parameters'])
    response_templates = FieldProperty(schemas.IApiGatewayMethodIntegrationResponse['response_templates'])
    selection_pattern = FieldProperty(schemas.IApiGatewayMethodIntegrationResponse['selection_pattern'])
    status_code = FieldProperty(schemas.IApiGatewayMethodIntegrationResponse['status_code'])

    troposphere_props = troposphere.apigateway.IntegrationResponse.props
    cfn_mapping = {
        "ContentHandling": 'content_handling',
        "ResponseParameters": 'response_parameters',
        "ResponseTemplates": 'response_templates',
        "SelectionPattern": 'selection_pattern',
        "StatusCode": 'status_code'
    }

@implementer(schemas.IApiGatewayMethodIntegration)
class ApiGatewayMethodIntegration(CFNExport):
    integration_responses = FieldProperty(schemas.IApiGatewayMethodIntegration['integration_responses'])
    request_parameters = FieldProperty(schemas.IApiGatewayMethodIntegration['request_parameters'])
    integration_http_method = FieldProperty(schemas.IApiGatewayMethodIntegration['integration_http_method'])
    integration_type = FieldProperty(schemas.IApiGatewayMethodIntegration['integration_type'])
    integration_lambda = FieldProperty(schemas.IApiGatewayMethodIntegration['integration_lambda'])
    uri = FieldProperty(schemas.IApiGatewayMethodIntegration['uri'])

    @property
    def integration_responses_cfn(self):
        responses = []
        for resp in self.integration_responses:
            responses.append(resp.cfn_export_dict)
        return responses

    troposphere_props = troposphere.apigateway.Integration.props
    cfn_mapping = {
        #"CacheKeyParameters": ([basestring], False),
        #"CacheNamespace": (basestring, False),
        #"ConnectionId": (basestring, False),
        #"ConnectionType": (basestring, False),
        #"ContentHandling": (basestring, False),
        #"PassthroughBehavior": (basestring, False),
        #"RequestTemplates": (dict, False),
        #"TimeoutInMillis": (integer_range(50, 29000), False),
        "IntegrationResponses": 'integration_responses_cfn',
        "IntegrationHttpMethod": 'integration_http_method',
        "RequestParameters": 'request_parameters',
        "Type": 'integration_type',
        #"Credentials": computed in template according to AWS_PROXY Integration Type,
        #"Uri": computed in the template,
    }

@implementer(schemas.IApiGatewayMethodMethodResponseModel)
class ApiGatewayMethodMethodResponseModel():
    content_type = FieldProperty(schemas.IApiGatewayMethodMethodResponseModel['content_type'])
    model_name = FieldProperty(schemas.IApiGatewayMethodMethodResponseModel['model_name'])

@implementer(schemas.IApiGatewayMethodMethodResponse)
class ApiGatewayMethodMethodResponse():
    status_code = FieldProperty(schemas.IApiGatewayMethodMethodResponse['status_code'])
    response_models = FieldProperty(schemas.IApiGatewayMethodMethodResponse['response_models'])

@implementer(schemas.IApiGatewayMethod)
class ApiGatewayMethod(Resource):
    type = "ApiGatewayMethod"
    resource_id = FieldProperty(schemas.IApiGatewayMethod['resource_id'])
    http_method = FieldProperty(schemas.IApiGatewayMethod['http_method'])
    request_parameters = FieldProperty(schemas.IApiGatewayMethod['request_parameters'])
    method_responses = FieldProperty(schemas.IApiGatewayMethod['method_responses'])
    integration = FieldProperty(schemas.IApiGatewayMethod['integration'])

    @property
    def integration_cfn(self):
        return self.integration.cfn_export_dict

    troposphere_props = troposphere.apigateway.Method.props
    cfn_mapping = {
        #"ApiKeyRequired": (bool, False),
        #"AuthorizationScopes": ([basestring], False),
        #"AuthorizerId": (basestring, False),
        #"RequestModels": (dict, False),
        #"RequestValidatorId": (basestring, False),
        "AuthorizationType": 'authorization_type',
        "HttpMethod": 'http_method',
        "Integration": 'integration_cfn',
        #"MethodResponses": 'method_responses',
        "OperationName": 'title',
        "RequestParameters": 'request_parameters',
        # "ResourceId": computed in the template looked up via resource_id
        # "RestApiId": computed in the template
    }

@implementer(schemas.IApiGatewayModels)
class ApiGatewayModels(Named, dict):
    pass

@implementer(schemas.IApiGatewayModel)
class ApiGatewayModel(Resource):
    type = "ApiGatewayModel"
    content_type = FieldProperty(schemas.IApiGatewayModel['content_type'])
    description = FieldProperty(schemas.IApiGatewayModel['description'])
    schema = FieldProperty(schemas.IApiGatewayModel['schema'])

    troposphere_props = troposphere.apigateway.Model.props
    cfn_mapping ={
        "ContentType": 'content_type',
        "Description": 'description',
        "Name": 'name',
        "Schema": 'schema',
    }

@implementer(schemas.IApiGatewayResources)
class ApiGatewayResources(Named, dict):
    pass

@implementer(schemas.IApiGatewayResource)
class ApiGatewayResource(Resource):
    type = "ApiGatewayResource"
    parent_id = FieldProperty(schemas.IApiGatewayResource['parent_id'])
    path_part = FieldProperty(schemas.IApiGatewayResource['path_part'])

    troposphere_props = troposphere.apigateway.Resource.props
    cfn_mapping = {
        # ParentId needs to be computed from the CFNTemplate to inject the Resource's Logical Id into it
        "PathPart": 'path_part',
        # "RestApiId": 'rest_api_id' - Computed to CFNTemplate Logical Id
    }

@implementer(schemas.IApiGatewayStages)
class ApiGatewayStages(Named, dict):
    pass

@implementer(schemas.IApiGatewayStage)
class ApiGatewayStage(Resource):
    deployment_id = FieldProperty(schemas.IApiGatewayStage['deployment_id'])
    description = FieldProperty(schemas.IApiGatewayStage['description'])
    stage_name = FieldProperty(schemas.IApiGatewayStage['stage_name'])

    troposphere_props = troposphere.apigateway.Stage.props
    cfn_mapping = {
        "Description": 'description',
        "StageName": 'stage_name',
    }

@implementer(schemas.IApiGatewayRestApi)
class ApiGatewayRestApi(Resource):
    title = "API Gateway REST API"
    type = "ApiGatewayRestApi"
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
    methods = FieldProperty(schemas.IApiGatewayRestApi['methods'])
    models = FieldProperty(schemas.IApiGatewayRestApi['models'])
    resources = FieldProperty(schemas.IApiGatewayRestApi['resources'])
    stages = FieldProperty(schemas.IApiGatewayRestApi['stages'])
    _body = None

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.methods = ApiGatewayMethods('methods', self)
        self.resources = ApiGatewayResources('resources', self)
        self.stages = ApiGatewayStages('stages', self)

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
                if repo_config.is_enabled() == False:
                    continue
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
class IAMResource(Named):
    users = FieldProperty(schemas.IIAMResource['users'])