import unittest
import paco.models.exceptions
from paco.models import references


class TestReferenceClass(unittest.TestCase):

    def test_secret_base_ref(self):
        base_ref = 'paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.mydb'
        test_refs = [
            'paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.mydb',
            'paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.mydb.arn',
            'paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.mydb.myjsonfield',
            'paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.mydb.myjsonfield.arn',
        ]
        for test_ref in test_refs:
            ref_obj = references.Reference(test_ref)
            base_ref_obj = ref_obj.secret_base_ref()
            assert base_ref_obj.raw == base_ref
        bogus_ref = 'paco.ref netenv.mynet.dev.eu-central-1.applications.myapp'
        ref_obj = references.Reference(bogus_ref)
        with self.assertRaises(paco.models.exceptions.InvalidPacoReference):
            ref_obj.secret_base_ref()

