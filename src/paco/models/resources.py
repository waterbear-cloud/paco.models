"""
All things Resources.
"""

import troposphere.apigateway
import troposphere.route53
from paco.models.base import Enablable, Parent, Named, CFNExport, Deployable, HasStack, Resource, ApplicationResource, AccountRegions
from paco.models.metrics import SNSTopics
from paco.models import references
from paco.models import schemas
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from paco.models import loader
from paco.models.locations import get_parent_by_interface
from paco.models.applications import DNS
from paco.models.references import Reference
from paco.models import references


@implementer(schemas.ITopics)
class Topics(Named, dict):
    pass

class Computed(Named, dict):
    pass

@implementer(schemas.ISNS)
class SNS(Named, dict):
    default_locations = FieldProperty(schemas.ISNS['default_locations'])
    topics = FieldProperty(schemas.ISNS['topics'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.computed = Computed('computed', self)
        self.topics = Topics('topics', self)

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IApiGatewayBasePathMapping)
class ApiGatewayBasePathMapping(Parent):
    base_path = FieldProperty(schemas.IApiGatewayBasePathMapping['base_path'])
    stage = FieldProperty(schemas.IApiGatewayBasePathMapping['stage'])

@implementer(schemas.IApiGatewayDNS)
class ApiGatewayDNS(DNS):
    base_path_mappings = FieldProperty(schemas.IApiGatewayDNS['base_path_mappings'])
    ssl_certificate = FieldProperty(schemas.IApiGatewayDNS['ssl_certificate'])

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
class ApiGatewayMethodIntegration(Parent, CFNExport):
    integration_http_method = FieldProperty(schemas.IApiGatewayMethodIntegration['integration_http_method'])
    integration_lambda = FieldProperty(schemas.IApiGatewayMethodIntegration['integration_lambda'])
    integration_responses = FieldProperty(schemas.IApiGatewayMethodIntegration['integration_responses'])
    integration_type = FieldProperty(schemas.IApiGatewayMethodIntegration['integration_type'])
    pass_through_behavior = FieldProperty(schemas.IApiGatewayMethodIntegration['pass_through_behavior'])
    request_parameters = FieldProperty(schemas.IApiGatewayMethodIntegration['request_parameters'])
    request_templates = FieldProperty(schemas.IApiGatewayMethodIntegration['request_templates'])
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
        "PassthroughBehavior": 'pass_through_behavior',
        "RequestTemplates": 'request_templates',
        #"TimeoutInMillis": (integer_range(50, 29000), False),
        "IntegrationResponses": 'integration_responses_cfn',
        "IntegrationHttpMethod": 'integration_http_method',
        "RequestParameters": 'request_parameters',
        "Type": 'integration_type',
        #"Credentials": computed in template according to AWS_PROXY Integration Type,
        #"Uri": computed in the template,
    }

@implementer(schemas.IApiGatewayCognitoAuthorizers)
class ApiGatewayCognitoAuthorizers(Named, dict):
    pass

@implementer(schemas.IApiGatewayCognitoAuthorizer)
class ApiGatewayCognitoAuthorizer(Named):
    identity_source = FieldProperty(schemas.IApiGatewayCognitoAuthorizer['identity_source'])
    user_pools = FieldProperty(schemas.IApiGatewayCognitoAuthorizer['user_pools'])

@implementer(schemas.IApiGatewayMethodMethodResponseModel)
class ApiGatewayMethodMethodResponseModel():
    content_type = FieldProperty(schemas.IApiGatewayMethodMethodResponseModel['content_type'])
    model_name = FieldProperty(schemas.IApiGatewayMethodMethodResponseModel['model_name'])

@implementer(schemas.IApiGatewayMethodMethodResponse)
class ApiGatewayMethodMethodResponse():
    status_code = FieldProperty(schemas.IApiGatewayMethodMethodResponse['status_code'])
    response_models = FieldProperty(schemas.IApiGatewayMethodMethodResponse['response_models'])
    response_parameters = FieldProperty(schemas.IApiGatewayMethodMethodResponse['response_parameters'])

@implementer(schemas.IApiGatewayMethod)
class ApiGatewayMethod(Resource):
    type = "ApiGatewayMethod"
    authorization_type = FieldProperty(schemas.IApiGatewayMethod['authorization_type'])
    authorizer = FieldProperty(schemas.IApiGatewayMethod['authorizer'])
    resource_name = FieldProperty(schemas.IApiGatewayMethod['resource_name'])
    http_method = FieldProperty(schemas.IApiGatewayMethod['http_method'])
    request_parameters = FieldProperty(schemas.IApiGatewayMethod['request_parameters'])
    method_responses = FieldProperty(schemas.IApiGatewayMethod['method_responses'])
    integration = FieldProperty(schemas.IApiGatewayMethod['integration'])

    @property
    def integration_cfn(self):
        return self.integration.cfn_export_dict

    def get_resource(self):
        resource = None
        node = get_parent_by_interface(self, schemas.IApiGatewayRestApi).resources
        for part in self.resource_name.split('.'):
            resource = node[part]
            node = resource.child_resources
        return resource

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
class ApiGatewayResource(Named, dict):
    type = "ApiGatewayResource"
    path_part = FieldProperty(schemas.IApiGatewayResource['path_part'])
    enable_cors = FieldProperty(schemas.IApiGatewayResource['enable_cors'])
    # child_resources is not a FieldProperty as it's set during recursion

    @property
    def nested_name(self):
        parent = self
        parts = []
        while not schemas.IApiGatewayRestApi.providedBy(parent):
            parts.append(parent.name)
            parent = parent.__parent__.__parent__
        parts.reverse()
        return '.'.join(parts)

    troposphere_props = troposphere.apigateway.Resource.props
    cfn_mapping = {
        # ParentId: computed in template
        "PathPart": 'path_part',
        # "RestApiId": computed in template
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
class ApiGatewayRestApi(ApplicationResource, HasStack):
    type = "ApiGatewayRestApi"
    api_key_source_type = FieldProperty(schemas.IApiGatewayRestApi['api_key_source_type'])
    binary_media_types = FieldProperty(schemas.IApiGatewayRestApi['binary_media_types'])
    body_file_location = FieldProperty(schemas.IApiGatewayRestApi['body_file_location'])
    body_s3_location = FieldProperty(schemas.IApiGatewayRestApi['body_s3_location'])
    clone_from = FieldProperty(schemas.IApiGatewayRestApi['clone_from'])
    cognito_authorizers = FieldProperty(schemas.IApiGatewayRestApi['cognito_authorizers'])
    description = FieldProperty(schemas.IApiGatewayRestApi['description'])
    dns = FieldProperty(schemas.IApiGatewayRestApi['dns'])
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
        # "Name": supplied by CloudFormation
        "Body": 'body',
        "FailOnWarnings": 'fail_on_warnings',
        "EndpointConfiguration": ("endpoint_configuration", "endpoint_configuration_cfn"),
        "MinimumCompressionSize": 'minimum_compression_size',
        "Parameters": 'parameters',
        "Policy": 'policy',
    }

@implementer(schemas.IEC2KeyPairs)
class EC2KeyPairs(Named, dict):
    pass

@implementer(schemas.IEC2KeyPair)
class EC2KeyPair(Named):
    region = FieldProperty(schemas.IEC2KeyPair['region'])
    account = FieldProperty(schemas.IEC2KeyPair['account'])
    keypair_name = FieldProperty(schemas.IEC2KeyPair['keypair_name'])

@implementer(schemas.IEC2Users)
class EC2Users(Named, dict):
    pass

@implementer(schemas.IEC2User)
class EC2User(Named):
    full_name = FieldProperty(schemas.IEC2User['full_name'])
    email = FieldProperty(schemas.IEC2User['email'])
    public_ssh_key = FieldProperty(schemas.IEC2User['public_ssh_key'])

@implementer(schemas.IEC2Groups)
class EC2Groups(Named, dict):
    pass

@implementer(schemas.IEC2Group)
class EC2Group(Named):
    members = FieldProperty(schemas.IEC2Group['members'])

@implementer(schemas.IEC2Resource)
class EC2Resource(Named):
    keypairs = FieldProperty(schemas.IEC2Resource['keypairs'])

    def resolve_ref(self, ref):
        if ref.parts[2] == 'keypairs':
            keypair_id = ref.parts[3]
            keypair_attr = ref.parts[4]
            try:
                keypair = self.keypairs[keypair_id]
            except KeyError:
                references.raise_invalid_reference(ref, self.keypairs, keypair_id)
            keypair = self.keypairs[keypair_id]
            value = getattr(keypair, keypair_attr, None)
            if value == None:
                references.raise_invalid_reference(ref, keypair, keypair_attr)
            return value

        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IS3Buckets)
class S3Buckets(Named, dict):
    pass

@implementer(schemas.IS3Resource)
class S3Resource(Named):
    buckets = FieldProperty(schemas.IS3Resource['buckets'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.buckets = S3Buckets('buckets', self)

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IRoute53RecordSet)
class Route53RecordSet():
    record_name = FieldProperty(schemas.IRoute53RecordSet["record_name"])
    type = FieldProperty(schemas.IRoute53RecordSet["type"])
    resource_records = FieldProperty(schemas.IRoute53RecordSet["resource_records"])
    ttl = FieldProperty(schemas.IRoute53RecordSet["ttl"])


@implementer(schemas.IRoute53HostedZoneExternalResource)
class Route53HostedZoneExternalResource(Named, Deployable):
    hosted_zone_id = FieldProperty(schemas.IRoute53HostedZoneExternalResource["hosted_zone_id"])
    nameservers = FieldProperty(schemas.IRoute53HostedZoneExternalResource["nameservers"])

@implementer(schemas.IRoute53HostedZone)
class Route53HostedZone(Named, Deployable):
    domain_name = FieldProperty(schemas.IRoute53HostedZone["domain_name"])
    account = FieldProperty(schemas.IRoute53HostedZone["account"])
    record_sets = FieldProperty(schemas.IRoute53HostedZone["record_sets"])
    parent_zone = FieldProperty(schemas.IRoute53HostedZone["parent_zone"])
    external_resource = FieldProperty(schemas.IRoute53HostedZone["external_resource"])
    private_hosted_zone = FieldProperty(schemas.IRoute53HostedZone["private_hosted_zone"])
    vpc_associations = FieldProperty(schemas.IRoute53HostedZone["vpc_associations"])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.record_sets = []

    def has_record_sets(self):
        if self.record_sets != None and len(self.record_sets) > 0:
            return True
        return False

@implementer(schemas.IRoute53Resource)
class Route53Resource(Named):
    name = 'route53'
    hosted_zones = FieldProperty(schemas.IRoute53Resource["hosted_zones"])

    def __init__(self, name, parent, config_dict):
        super().__init__(name, parent)

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

@implementer(schemas.IRoute53HealthCheck)
class Route53HealthCheck(Resource):

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.health_checker_regions = []

    domain_name = FieldProperty(schemas.IRoute53HealthCheck["domain_name"])
    load_balancer = FieldProperty(schemas.IRoute53HealthCheck["load_balancer"])
    health_check_type = FieldProperty(schemas.IRoute53HealthCheck["health_check_type"])
    ip_address = FieldProperty(schemas.IRoute53HealthCheck["ip_address"])
    enable_sni = FieldProperty(schemas.IRoute53HealthCheck["enable_sni"])
    port = FieldProperty(schemas.IRoute53HealthCheck["port"])
    resource_path = FieldProperty(schemas.IRoute53HealthCheck["resource_path"])
    match_string = FieldProperty(schemas.IRoute53HealthCheck["match_string"])
    failure_threshold = FieldProperty(schemas.IRoute53HealthCheck["failure_threshold"])
    request_interval_fast = FieldProperty(schemas.IRoute53HealthCheck["request_interval_fast"])
    latency_graphs = FieldProperty(schemas.IRoute53HealthCheck["latency_graphs"])
    health_checker_regions = FieldProperty(schemas.IRoute53HealthCheck["health_checker_regions"])

    # All of the configuration is nested in the HealthCheckConfig prop
    # cfn_export_dict will be a HealthCheckConfig dict, this needs to be
    # wrapped in cfn_export_dict['HealthCheckConfig'] in the template
    troposphere_props = troposphere.route53.HealthCheckConfiguration.props
    cfn_mapping = {
        # 'AlarmIdentifier': (AlarmIdentifier, False),
        # 'ChildHealthChecks': ([basestring], False),
        'EnableSNI': 'enable_sni',
        'FailureThreshold': 'failure_threshold',
        # 'FullyQualifiedDomainName': computed in template,
        # 'HealthThreshold': ,
        # 'InsufficientDataHealthStatus': (basestring, False),
        # 'Inverted': (boolean, False),
        # 'IPAddress': computed in template,
        'MeasureLatency': 'latency_graphs',
        'Port': 'port',
        'Regions': 'health_checker_regions',
        'RequestInterval': 'request_interval_cfn',
        'ResourcePath': 'resource_path',
        'SearchString': 'match_string',
        'Type': 'type_cfn',
    }

    @property
    def request_interval_cfn(self):
        if self.request_interval_fast:
            return 10
        else:
            return 30

    @property
    def type_cfn(self):
        # ToDo: implement CLOUDWATCH_METRIC and CALCULATED
        if getattr(self, 'match_string', None) != None:
            if self.health_check_type == 'HTTP':
                return 'HTTP_STR_MATCH'
            elif self.health_check_type == 'HTTPS':
                return 'HTTPS_STR_MATCH'
        else:
            return self.health_check_type

@implementer(schemas.ICodeCommitUsers)
class CodeCommitUsers(Named, dict):
    pass

@implementer(schemas.ICodeCommitUser)
class CodeCommitUser(Named):
    username = FieldProperty(schemas.ICodeCommitUser["username"])
    public_ssh_key = FieldProperty(schemas.ICodeCommitUser["public_ssh_key"])
    permissions = FieldProperty(schemas.ICodeCommitUser["permissions"])

@implementer(schemas.ICodeCommitRepository)
class CodeCommitRepository(Named, Deployable):
    repository_name = FieldProperty(schemas.ICodeCommitRepository["repository_name"])
    account = FieldProperty(schemas.ICodeCommitRepository["account"])
    region = FieldProperty(schemas.ICodeCommitRepository["region"])
    description = FieldProperty(schemas.ICodeCommitRepository["description"])
    users = FieldProperty(schemas.ICodeCommitRepository["users"])
    external_resource = FieldProperty(schemas.ICodeCommitRepository["external_resource"])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.users = CodeCommitUsers('users', self)

@implementer(schemas.ICodeCommitRepositoryGroup)
class CodeCommitRepositoryGroup(Named, dict):
    pass

@implementer(schemas.ICodeCommit)
class CodeCommit(Named, dict):

    def __init__(self, name, parent):
        super().__init__(name, parent)

    def gen_repo_by_account(self):
        self.repo_by_account = {}
        for group_id in self.keys():
            group_config = self[group_id]
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

    def repo_list(self):
        "List of all repositories"
        out = []
        for group in self.values():
            for repo in group.values():
                repo.repository_group = group
                out.append(repo)
        return out


@implementer(schemas.IConfig)
class Config(Resource):
    delivery_frequency = FieldProperty(schemas.IConfig["delivery_frequency"])
    global_resources_region = FieldProperty(schemas.IConfig["global_resources_region"])
    locations = FieldProperty(schemas.IConfig["locations"])
    s3_bucket_logs_account = FieldProperty(schemas.IConfig["s3_bucket_logs_account"])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.locations = []

    def get_accounts(self):
        """
        Resolve the locations field for all accounts.
        If locations is empty, then all accounts are returned.
        """
        if self.locations == []:
            return project['accounts'].values()
        accounts = []
        project = get_parent_by_interface(self, schemas.IProject)
        for location in self.locations:
            account = references.get_model_obj_from_ref(location.account, project)
            accounts.append(account)
        return accounts

@implementer(schemas.IConfigResource)
class ConfigResource(Named):
    config = FieldProperty(schemas.IConfigResource["config"])

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
                account = references.get_model_obj_from_ref(account_ref, project)
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

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)


@implementer(schemas.IIAMUserProgrammaticAccess)
class IAMUserProgrammaticAccess(Enablable):
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
class IAMUserPermissionCodeCommitRepository(Parent):
    codecommit = FieldProperty(schemas.IIAMUserPermissionCodeCommitRepository['codecommit'])
    permission = FieldProperty(schemas.IIAMUserPermissionCodeCommitRepository['permission'])
    console_access_enabled = FieldProperty(schemas.IIAMUserPermissionCodeCommitRepository['console_access_enabled'])
    public_ssh_key = FieldProperty(schemas.IIAMUserPermissionCodeCommitRepository['public_ssh_key'])

@implementer(schemas.IIAMUserPermissionCodeCommit)
class IAMUserPermissionCodeCommit(IAMUserPermission):
    repositories = FieldProperty(schemas.IIAMUserPermissionCodeCommit['repositories'])

@implementer(schemas.IIAMUserPermissionCodeBuildResource)
class IAMUserPermissionCodeBuildResource(Parent):
    codebuild = FieldProperty(schemas.IIAMUserPermissionCodeBuildResource['codebuild'])
    permission = FieldProperty(schemas.IIAMUserPermissionCodeBuildResource['permission'])
    console_access_enabled = FieldProperty(schemas.IIAMUserPermissionCodeBuildResource['console_access_enabled'])

@implementer(schemas.IIAMUserPermissionDeploymentPipelines)
class IAMUserPermissionDeploymentPipelines(IAMUserPermission):
    resources = FieldProperty(schemas.IIAMUserPermissionDeploymentPipelines['resources'])
    accounts = FieldProperty(schemas.IIAMUserPermissionDeploymentPipelines['accounts'])

@implementer(schemas.IIAMUserPermissionDeploymentPipelineResource)
class IAMUserPermissionDeploymentPipelineResource(Parent):
    pipeline = FieldProperty(schemas.IIAMUserPermissionDeploymentPipelineResource['pipeline'])
    permission = FieldProperty(schemas.IIAMUserPermissionDeploymentPipelineResource['permission'])
    console_access_enabled = FieldProperty(schemas.IIAMUserPermissionDeploymentPipelineResource['console_access_enabled'])

@implementer(schemas.IIAMUserPermissionCodeBuild)
class IAMUserPermissionCodeBuild(IAMUserPermission):
    resources = FieldProperty(schemas.IIAMUserPermissionCodeBuild['resources'])

@implementer(schemas.IIAMUserPermissionCustomPolicy)
class IAMUserPermissionCustomPolicy(IAMUserPermission):
    accounts = FieldProperty(schemas.IIAMUserPermissionCustomPolicy['accounts'])
    managed_policies = FieldProperty(schemas.IIAMUserPermissionCustomPolicy['managed_policies'])
    policies = FieldProperty(schemas.IIAMUserPermissionCustomPolicy['policies'])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.policies = []
        self.managed_policies = []

@implementer(schemas.IIAMUserPermissions)
class IAMUserPermissions(Named, dict):
    pass

@implementer(schemas.IIAMUser)
class IAMUser(Named, Deployable):
    account = FieldProperty(schemas.IIAMUser['account'])
    username = FieldProperty(schemas.IIAMUser['username'])
    description = FieldProperty(schemas.IIAMUser['description'])
    console_access_enabled = FieldProperty(schemas.IIAMUser['console_access_enabled'])
    programmatic_access = FieldProperty(schemas.IIAMUser['programmatic_access'])
    permissions = FieldProperty(schemas.IIAMUser['permissions'])
    account_whitelist = FieldProperty(schemas.IIAMUser['account_whitelist'])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.permissions = IAMUserPermissions('permissions', self)

@implementer(schemas.IIAMUsers)
class IAMUsers(Named, dict):
    pass

@implementer(schemas.IIAMResource)
class IAMResource(Named):
    users = FieldProperty(schemas.IIAMResource['users'])


@implementer(schemas.ISSMDocuments)
class SSMDocuments(Named, dict):
    pass

@implementer(schemas.ISSMDocument)
class SSMDocument(Resource):
    locations = FieldProperty(schemas.ISSMDocument['locations'])
    content = FieldProperty(schemas.ISSMDocument['content'])
    document_type = FieldProperty(schemas.ISSMDocument['document_type'])

    def add_location(self, account_ref, region):
        "Add an account and region to locations if it does not already exist"
        for location in self.locations:
            if location.account == account_ref:
                for aws_region in location.regions:
                    if region == aws_region:
                        return
                location.regions.append(region)
                return
        # not seen in existing accounts, add new location
        location = AccountRegions(self)
        location.account = account_ref
        location.regions = [region]
        self.locations.append(location)


@implementer(schemas.ISSMResource)
class SSMResource(Named):
    name = 'ssm'
    ssm_documents = FieldProperty(schemas.ISSMResource["ssm_documents"])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.ssm_documents = SSMDocuments('ssm_documents', self)

@implementer(schemas.IGlobalResources)
class GlobalResources(Named, dict):
    "Global Resources"

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self['cloudtrail'] = CloudTrailResource('cloudtrail', self)
        self.cloudtrail = self['cloudtrail']
        self['codecommit'] = CodeCommit('codecommit', self)
        self.codecommit = self['codecommit']
        self['sns'] = SNS('sns', self)
        self.sns = self['sns']
        self['iam'] = IAMResource('iam', self)
        self.iam = self['iam']
