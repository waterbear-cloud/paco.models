from aim.models import schemas
from aim.models.resources import Resource
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from aim.models.base import Named, Deployable, Regionalized


@implementer(schemas.IRDS)
class RDS(Resource):
    pass

@implementer(schemas.ICodeCommitRepository)
class CodeCommitRepository(Named, Deployable, dict):
    account = FieldProperty(schemas.ICodeCommitRepository["account"])
    region = FieldProperty(schemas.ICodeCommitRepository["region"])
    description = FieldProperty(schemas.ICodeCommitRepository["description"])

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
