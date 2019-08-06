"""
All things Resources.
"""

from aim.models.base import Named, Deployable, Regionalized
from aim.models.metrics import Monitorable
from aim.models import schemas
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from aim.models import loader
from aim.models.locations import get_parent_by_interface
from aim.models.references import Reference
from aim.models import references


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