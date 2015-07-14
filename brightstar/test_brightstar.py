import unittest
import requests
import httpretty
from brightpearl import API

TEST_CONFIG = { 'datacentre': 'eu1',
                'api_version': '2.0.0',
                'account_code': 'testcompany',
                'brightpearl_app_ref': 'testcompany_testapp',
                'brightpearl_account_token': 'f4dtgpjl89z0aftgpj89z0a',
                }
                


class InstantiationTest(unittest.TestCase):

    def setUp(self):
        self.instance = API(TEST_CONFIG)

    def test_successful_instance(self):
        
        self.assertEqual(self.instance.datacentre, 'eu1')
        self.assertEqual(self.instance.api_version, '2.0.0')
        self.assertEqual(self.instance.account_code, 'testcompany')
        self.assertEqual(self.instance.app_ref, 'testcompany_testapp')
        self.assertEqual(self.instance.authentication_token, 
            'f4dtgpjl89z0aftgpj89z0a')
        self.assertIsNone(self.instance.staff_authentication_token)

        self.assertEqual(
            self.instance.headers, {
            "brightpearl-app-ref": 'testcompany_testapp',
            "brightpearl-account-token": 'f4dtgpjl89z0aftgpj89z0a'
            }
            )




if __name__ == '__main__':
    unittest.main()