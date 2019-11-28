import paco.models.applications
import paco.models.networks
import paco.models.resources
from paco.models import schemas
from paco.models.base import Named
from paco.models.schemas import IProject
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@implementer(IProject)
class Project(Named, dict):
    """Paco project"""
    paco_project_version = FieldProperty(schemas.IProject["paco_project_version"])
    legacy_flags = FieldProperty(schemas.IProject["legacy_flags"])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.legacy_flags = []

        # Credentials
        self.credentials = paco.models.project.Credentials('credentials', self)
        self.credentials.title = 'Administrator Credentials'
        self.__setitem__('credentials', self.credentials)

        # Network Environments
        self.network_environments = paco.models.networks.NetworkEnvironments('netenv', self)
        self.network_environments.title = 'Network Environments'
        self.__setitem__('netenv', self.network_environments)

        # Services
        self.services = paco.models.services.Services('service', self)
        self.services.title = 'Services'
        self.__setitem__('service', self.services)

        # Accounts
        self.accounts = paco.models.accounts.Accounts('accounts', self)
        self.accounts.title = 'Cloud Accounts'
        self.__setitem__('accounts', self.accounts)

        # Global Resources
        self.resource = paco.models.resources.GlobalResources('resource', self)
        self.resource.title = 'Global Resources'
        self.__setitem__('resource', self.resource)

        # Init an empty S3Resource in-case there is no Resources/S3.yaml
        self.resource['s3'] = paco.models.resources.S3Resource('s3', self.resource)

        # IAM
        self.resource['iam'] = paco.models.resources.IAMResource('iam', self.resource)
        self.resource['iam'].title = 'IAM Resource'


    def find_object_from_cli(self, controller_type, component_name=None, config_name=None):
        found = None
        CONTROLLER_MAPPING = {
            'NetEnv' : 'netenv'
        }
        found = self[CONTROLLER_MAPPING[controller_type]]
        if component_name:
            found = found[component_name]
        if config_name:
            found = found[config_name]
        return found

    def get_all_applications(self):
        """
        Return a list of all applications in the model
        """
        results = []
        for ne in self['netenv'].values():
            for env in ne.values():
                for env_reg in env.env_regions.values():
                    for application in env_reg.applications.values():
                        results.append(application)
        return results

@implementer(schemas.ICredentials)
class Credentials(Named, dict):
    """
    Object attrs:
        - aws_access_key_id : string : AWS Access Key ID
        - aws_secret_access_key : string : AWS Secret Access Key
        - aws_default_region : string : AWS Default Region
        - master_account_id : string : Master AWS Account ID
        - master_admin_iam_username : string : Master Account Admin IAM Username
    """

    aws_access_key_id = FieldProperty(schemas.ICredentials["aws_access_key_id"])
    aws_secret_access_key = FieldProperty(schemas.ICredentials["aws_secret_access_key"])
    aws_default_region = FieldProperty(schemas.ICredentials["aws_default_region"])
    master_account_id = FieldProperty(schemas.ICredentials["master_account_id"])
    master_admin_iam_username = FieldProperty(schemas.ICredentials["master_admin_iam_username"])
    admin_iam_role_name = FieldProperty(schemas.ICredentials["admin_iam_role_name"])
    mfa_session_expiry_secs = FieldProperty(schemas.ICredentials["mfa_session_expiry_secs"])
    assume_role_session_expiry_secs = FieldProperty(schemas.ICredentials["assume_role_session_expiry_secs"])

    @property
    def mfa_role_arn(self):
        return 'arn:aws:iam::' + self.master_account_id + ':mfa/' + self.master_admin_iam_username

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)

