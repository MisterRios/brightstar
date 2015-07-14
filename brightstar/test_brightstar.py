import unittest
import httpretty
import json
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
        self.assertEqual(self.instance.staff_authentication_headers, {
                "brightpearl-app-ref": 'testcompany_testapp',
                "Content-Type": "application/json"
                }
            )

        self.assertEqual(self.instance.uri,
                'https://ws-eu1.brightpearl.com/2.0.0/testcompany/'
                )

        self.assertEqual(self.instance.authentication_uri,
                'https://ws-eu1.brightpearl.com/testcompany/authorise'
                )

        self.assertEqual(
            self.instance.headers, {
                "brightpearl-app-ref": 'testcompany_testapp',
                "brightpearl-account-token": 'f4dtgpjl89z0aftgpj89z0a'
                }
            )

class BasicMethodsTest(unittest.TestCase):

    def setUp(self):
        self.instance = API(TEST_CONFIG)

    @httpretty.activate
    def test_get(self):
        
        httpretty.register_uri(httpretty.GET, 
            'https://ws-eu1.brightpearl.com/2.0.0/testcompany/',
            headers={
                "brightpearl-app-ref": 'testcompany_testapp',
                "brightpearl-account-token": 'f4dtgpjl89z0aftgpj89z0a'
                },
            body= json.dumps({"response": "get_test_body"}),
            status= 200,
                )

        self.assertEqual(
            self.instance.get(self.instance.uri),
            {"response": "get_test_body"}
            )

    @httpretty.activate
    def test_put(self):
        httpretty.register_uri(httpretty.PUT, 
            'https://ws-eu1.brightpearl.com/2.0.0/testcompany/',
            headers={
                "brightpearl-app-ref": 'testcompany_testapp',
                "brightpearl-account-token": 'f4dtgpjl89z0aftgpj89z0a'
                },
            body= json.dumps({"response": "put_it"}),
            status= 200,
                )

        self.assertEqual(
            self.instance.put(self.instance.uri, data={"first":"second"}),
            {"response": "put_it"}
            )

    @httpretty.activate
    def test_post(self):
        httpretty.register_uri(httpretty.POST, 
            'https://ws-eu1.brightpearl.com/2.0.0/testcompany/',
            headers={
                "brightpearl-app-ref": 'testcompany_testapp',
                "brightpearl-account-token": 'f4dtgpjl89z0aftgpj89z0a'
                },
            body= json.dumps({"response": "postt_it"}),
            status= 200,
                )

        self.assertEqual(
            self.instance.post(self.instance.uri, data={"first":"second"}),
            {"response": "postt_it"}
            )

    @httpretty.activate
    def test_options(self):
        httpretty.register_uri(httpretty.OPTIONS, 
            'https://ws-eu1.brightpearl.com/2.0.0/testcompany/',
            headers={
                "brightpearl-app-ref": 'testcompany_testapp',
                "brightpearl-account-token": 'f4dtgpjl89z0aftgpj89z0a'
                },
            body= json.dumps({"response": "options"}),
            status= 200,
                )

        self.assertEqual(
            self.instance.options(self.instance.uri),
            {"response": "options"}
            )

class GetMethodsTest(unittest.TestCase):

    def setUp(self):
        self.instance = API(TEST_CONFIG)

    @httpretty.activate  
    def test_get_brightpearl_staff_token(self):

        httpretty.register_uri(
            httpretty.POST,
            "https://ws-eu1.brightpearl.com/testcompany/authorise",
            body=json.dumps({"response": "St4ffT0K3n"})
            )

        self.instance.get_brightpearl_staff_token("username", "password")

        self.assertEqual(
            self.instance.headers,
            {"brightpearl-app-ref": "testcompany_testapp",
            "brightpearl-staff-token": "St4ffT0K3n"}
            )

    @httpretty.activate
    def test_get_uri(self):
        """this is not an actual get request per se,
        it really only builds uris based on parameters"""

        product_251_uri = self.instance.get_uri("product", "product", 251)
        self.assertEqual(
            product_251_uri,
            "https://ws-eu1.brightpearl.com/2.0.0/testcompany/product-service/product/251")

        order_500500_uri = self.instance.get_uri("order", "order", "500500-500570")
        self.assertEqual(
            order_500500_uri,
            "https://ws-eu1.brightpearl.com/2.0.0/testcompany/order-service/order/500500-500570"
            )

        base_contact_uri = self.instance.get_uri("contact", "contact")
        self.assertEqual(
            base_contact_uri,
            "https://ws-eu1.brightpearl.com/2.0.0/testcompany/contact-service/contact/"
            )

if __name__ == '__main__':
    unittest.main()