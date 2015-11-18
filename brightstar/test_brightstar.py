import unittest
import responses
import json
from brightpearl import API
from brightpearl import Tools

TEST_CONFIG = { 'datacentre': 'eu1',
                'api_version': 'public-api',
                'account_code': 'testcompany',
                'brightpearl_app_ref': 'testcompany_testapp',
                'brightpearl_account_token': 'f4dtgpjl89z0aftgpj89z0a',
                }



class InstantiationTest(unittest.TestCase):

    def setUp(self):
        self.instance = API(TEST_CONFIG)

    def test_successful_instance(self):

        self.assertEqual(self.instance.datacentre, 'eu1')
        self.assertEqual(self.instance.api_version, 'public-api')
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
                'https://ws-eu1.brightpearl.com/public-api/testcompany/'
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

    @responses.activate
    def test_get(self):

        responses.add(responses.GET,
            'https://ws-eu1.brightpearl.com/public-api/testcompany/',
            body= json.dumps({"response": "get_test_body"}),
            status= 200,
                )

        self.assertEqual(
            self.instance.get(self.instance.uri),
            {"response": "get_test_body"}
            )

    @responses.activate
    def test_put(self):
        responses.add(responses.PUT,
            'https://ws-eu1.brightpearl.com/public-api/testcompany/',
            body= json.dumps({"response": "put_it"}),
            status= 200,
                )

        self.assertEqual(
            self.instance.put(self.instance.uri, data={"first":"second"}),
            {"response": "put_it"}
            )

    @responses.activate
    def test_post(self):
        responses.add(responses.POST,
            'https://ws-eu1.brightpearl.com/public-api/testcompany/',
            body= json.dumps({"response": "postt_it"}),
            status= 200,
                )

        self.assertEqual(
            self.instance.post(self.instance.uri, data={"first":"second"}),
            {"response": "postt_it"}
            )

    @responses.activate
    def test_options(self):
        responses.add(responses.OPTIONS,
            'https://ws-eu1.brightpearl.com/public-api/testcompany/',
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

    @responses.activate
    def test_get_brightpearl_staff_token(self):

        responses.add(
            responses.POST,
            "https://ws-eu1.brightpearl.com/testcompany/authorise",
            body=json.dumps({"response": "St4ffT0K3n"})
            )

        self.instance.get_brightpearl_staff_token("username", "password")

        self.assertEqual(
            self.instance.headers,
            {"brightpearl-app-ref": "testcompany_testapp",
            "brightpearl-staff-token": "St4ffT0K3n"}
            )


    def test_get_uri(self):
        """
        This is not an actual get request.
        Instead, the method builds uris based on given parameters.
        """

        product_251_uri = self.instance.get_uri("product", "product", 251)
        self.assertEqual(
            product_251_uri,
            "https://ws-eu1.brightpearl.com/public-api/testcompany/product-service/product/251")

        order_500500_uri = self.instance.get_uri("order", "order", "500500-500570")
        self.assertEqual(
            order_500500_uri,
            "https://ws-eu1.brightpearl.com/public-api/testcompany/order-service/order/500500-500570"
            )

        base_contact_uri = self.instance.get_uri("contact", "contact")
        self.assertEqual(
            base_contact_uri,
            "https://ws-eu1.brightpearl.com/public-api/testcompany/contact-service/contact/"
            )


    def test_get_service_uri(self):
        order_uri = self.instance.get_service_uri("order")
        self.assertEqual(
            order_uri,
            self.instance.uri + "order-service/order/"
            )

        order_uri_500500 = self.instance.get_service_uri("order", 500500)
        self.assertEqual(
            order_uri_500500,
            self.instance.uri + "order-service/order/500500"
            )

        contact_uri = self.instance.get_service_uri("contact")
        self.assertEqual(
            contact_uri,
            self.instance.uri + "contact-service/contact/")

        postal_addresses_uri = self.instance.get_service_uri("postal_addresses")
        self.assertEqual(
            postal_addresses_uri,
            self.instance.uri + "contact-service/postal-address/")

        products_uri = self.instance.get_service_uri("products")
        self.assertEqual(
            products_uri,
            self.instance.uri + "product-service/product/"
            )

        prices_uri = self.instance.get_service_uri("prices")
        self.assertEqual(
            prices_uri,
            self.instance.uri + "product-service/product-price/"
            )

class OrderSearchTest(unittest.TestCase):

    def setUp(self):
        self.instance = API(TEST_CONFIG)

    @responses.activate
    def test_order_lookup(self):
        responses.add(responses.GET,
            'https://ws-eu1.brightpearl.com/public-api/testcompany/order-service/order-search?orderTypeId=2',
            body= json.dumps(
                {"reference": {},
                 "response": {
                    "metaData": {
                        "resultsAvailable": 200,
                        "resultsReturned": 200
                    },
                    "results": [[100001, 2, 120], [100002, 2, 121]]
                 }
                }
            ),
            status= 200,
            match_querystring=True,
        )

        expected_results = [[100001, 2, 120], [100002, 2, 121]]
        searched_orders = self.instance.order_lookup({'orderTypeId': 2})
        assert searched_orders == expected_results


class TestGrouper:

    def test_grouper_one_chunk(self):
        test_list = [1, 2, 3, 4, 5, 6]
        expected_chunks = [[1, 2, 3, 4, 5, 6]]
        returned_chunks = Tools.grouper(test_list, chunks=1)
        assert expected_chunks == returned_chunks


    def test_grouper_two_chunks(self):
        test_list = [1, 2, 3, 4, 5, 6]
        expected_chunks = [[1, 2, 3], [4, 5, 6]]
        returned_chunks = Tools.grouper(test_list, chunks=2)
        assert expected_chunks == returned_chunks

    def test_grouper_three_chunks(self):
        test_list = [1, 2, 3, 4, 5, 6]
        expected_chunks = [[1, 2], [3, 4], [5, 6]]
        returned_chunks = Tools.grouper(test_list, chunks=3)
        assert expected_chunks == returned_chunks


    def test_grouper_one_chunk_odd_items(self):
        test_list = [1, 2, 3, 4, 5, 6, 7]
        expected_chunks = [[1, 2, 3, 4, 5, 6, 7]]
        returned_chunks = Tools.grouper(test_list, chunks=1)
        assert expected_chunks == returned_chunks

    def test_grouper_two_chunks_seven_items(self):
        test_list = [1, 2, 3, 4, 5, 6, 7]
        expected_chunks = [[1, 2, 3, 4], [5, 6, 7]]
        returned_chunks = Tools.grouper(test_list, chunks=2)
        assert expected_chunks == returned_chunks

    def test_grouper_three_chunks_ten_items(self):
        test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        expected_chunks = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10]]
        returned_chunks = Tools.grouper(test_list, chunks=3)
        assert expected_chunks == returned_chunks


    def test_grouper_chunksize_two(self):
        test_list = [1, 2, 3, 4, 5, 6, 7]
        expected_chunks = [[1, 2], [3, 4], [5, 6], [7]]
        returned_chunks = Tools.grouper(test_list, chunksize=2)
        assert expected_chunks == returned_chunks

    def test_grouper_chunksize_five(self):
        test_list = [1, 2, 3, 4, 5, 6, 7]
        expected_chunks = [[1, 2, 3, 4, 5], [6, 7]]
        returned_chunks = Tools.grouper(test_list, chunksize=5)
        assert expected_chunks == returned_chunks

    def test_grouper_chunksize_ten(self):
        test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        expected_chunks = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
        returned_chunks = Tools.grouper(test_list, chunksize=10)
        assert expected_chunks == returned_chunks


class TestSearchStringifier:

    def test_searchstringifier_five_strings(self):
        test_list = ['one', 'two', 'three', 'four', 'five']
        expected_string = 'one,two,three,four,five'
        returned_string = Tools.searchstringifier(test_list)
        assert expected_string == returned_string

    def test_searchstringifier_five_integers(self):
        test_list = [1, 2, 3, 4, 5]
        expected_string = '1,2,3,4,5'
        returned_string = Tools.searchstringifier(test_list)
        assert expected_string == returned_string


class TestGetProductPrices(unittest.TestCase):

    def setUp(self):
        self.instance = API(TEST_CONFIG)

    @responses.activate
    def test_one_product_id_one_price(self):
        responses.add(responses.OPTIONS,
            "{}{}{}".format(
                "https://ws-eu1.brightpearl.com/public-api/testcompany/",
                "product-service/product-price/",
                "1001"
            ),
            body= json.dumps(
                                {
                                    "response": {
                                        "getUris": [
                                            "/product-price/1001",
                                        ]
                                    }
                                }
                            ),
            status= 200,
            match_querystring=True,
        )

        responses.add(responses.GET,
            "{}{}{}".format(
                "https://ws-eu1.brightpearl.com/public-api/testcompany/",
                "product-service/product-price/",
                "1001/price-list/0"
            ),
            body= json.dumps(
                {
                    "response": [
                        {
                            "productId": 1001,
                            "priceLists": [
                                {
                                    "priceListId": 0,
                                    "currencyCode": "EUR",
                                    "currencyId": 1,
                                    "sku": "10001",
                                    "quantityPrice": {
                                        "1": "5.00",
                                    }
                                }
                            ]
                        }
                    ]
                }
            ),
            status= 200,
            match_querystring=True,
        )

        test_product_id = 1001
        test_prices = self.instance.get_product_prices(test_product_id, price_list=0)
        expected_results = {1001: {0: "5.00"}}

        assert test_prices == expected_results

    @responses.activate
    def test_one_product_id_all_prices(self):
        test_product_id = 10001
        test_prices = self.instance.get_product_prices(test_product_id)
        expected_results = {1001: {0: "5.00", 1: "10.0", 2: "10.0"}}

        assert test_prices == expected_results

    @responses.activate
    def test_many_product_ids_one_price(self):
        test_product_ids = "10001-10002"
        test_prices = self.instance.get_product_prices(test_product_ids, price_list=0)
        expected_results = {
                1001: {0: "5.00"},
                1002: {0: "6.00"},
        }

        assert test_prices == expected_results

    @responses.activate
    def test_many_product_ids_all_prices(self):
        test_product_ids = "10001-10002"
        test_prices = self.instance.get_product_prices(test_product_ids)
        test_product_ids = "10001-10002"
        expected_results = {
                1001: {0: "5.00", 1: "10.0", 2: "10.0"},
                1002: {0: "6.00", 1: "10.0", 2: "10.0"},
        }

        assert test_prices == expected_results

    @responses.activate
    def test_split_product_ids_one_price(self):
        test_product_ids = "10001-10004"
        test_prices = self.instance.get_product_prices(test_product_ids, price_list=0)
        expected_results = {
                1001: {0: "5.00"},
                1002: {0: "6.00"},
                1003: {0: "7.00"},
                1004: {0: "8.00"},
        }

        assert test_prices == expected_results

    @responses.activate
    def test_split_product_ids_all_prices(self):
        test_product_ids = "10001-10004"
        test_prices = self.instance.get_product_prices(test_product_ids)
        expected_results = {
                1001: {0: "5.00", 1: "10.0", 2: "10.0"},
                1002: {0: "6.00", 1: "10.0", 2: "10.0"},
                1003: {0: "7.00", 1: "10.0", 2: "10.0"},
                1004: {0: "8.00", 1: "10.0", 2: "10.0"},
        }

        assert test_prices == expected_results

