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
        test_instance = API(TEST_CONFIG)

    def test_successful_instance(self):
        pass




if __name__ == '__main__':
    unittest.main()