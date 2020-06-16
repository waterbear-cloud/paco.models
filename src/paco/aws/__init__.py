from paco.models import gen_vocabulary
from paco.models.exceptions import UnsupportedFeature


def ami_id(ref, date_and_type, project, account_ctx):
    date, ami_type = date_and_type.split('.')
    if date == 'latest':
        return gen_vocabulary.ami_ids[ref.region][ami_type][0]['ImageId']
    else:
        raise UnsupportedFeature("Only 'latest' is supported for AMI Id date")
