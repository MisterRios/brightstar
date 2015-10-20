import json
import requests
from itertools import zip_longest
from math import ceil

ALL_SERVICES = {
    "order": ("order", "order"),
    "contact": ("contact", "contact"),
    "postal_addresses": ("contact", "postal-address"),
    "products": ("product", "product"),
    "prices": ("product", "product-price")
    }

class API(object):

    """
    creates API calls to brightpearl
    and creates the beginning of the URI
    as well as the headers based on config parameters
    """

    def __init__(self, config):

        self.datacentre = config['datacentre']
        self.api_version = config['api_version']
        self.account_code = config['account_code']
        self.app_ref = config['brightpearl_app_ref']
        self.authentication_token = None
        self.staff_authentication_token = None

        if 'brightpearl_account_token' in config:
            self.authentication_token = config['brightpearl_account_token']

        self.staff_authentication_headers = {
                "brightpearl-app-ref": self.app_ref,
                "Content-Type": "application/json"
        }

        self.uri = "https://ws-{}.brightpearl.com/{}/{}/".format(
            self.datacentre, self.api_version, self.account_code)

        self.authentication_uri = "https://ws-{}.brightpearl.com/{}/authorise".format(
            self.datacentre, self.account_code)

        self.headers = {
            "brightpearl-app-ref": self.app_ref,
            "brightpearl-account-token": self.authentication_token
        }


    def get_brightpearl_staff_token(self, username, password):
        """
        calls the API to get the staff token
        """

        
        authentication_string = json.dumps(
                {"apiAccountCredentials" : 
                    {"emailAddress":username, "password":password }
                }
                    )
        authentication_data = authentication_string.encode('utf-8')

        response = requests.post(self.authentication_uri, data=authentication_data, headers=self.staff_authentication_headers)

        decoded_data = response.json()

        self.staff_authentication_token = decoded_data['response']

        self.headers = {
            "brightpearl-app-ref": self.app_ref,
            "brightpearl-staff-token": self.staff_authentication_token,
        }


    def get_uri(self, service, resource, reference_number=None):
        """
        service/resource as string: i.e. "orders", "products"
        allows custom uris for calls not included in self.process_uri
        only returns a single uri
        """
        resource_fragment = "{}-service/{}/".format(service, resource)

        if reference_number is None:
            return "{}{}".format(self.uri, resource_fragment)

        return "{}{}{}".format(self.uri, resource_fragment, reference_number)


    def get_service_uri(self, service, reference_number=None):
        """
        generate uri for certain services in ALL_SERVICE
        service and order_numbers must be strings.
        This method is essentially a shortcut for get_uri above.
        """    

        return self.get_uri(ALL_SERVICES[service][0], ALL_SERVICES[service][1], reference_number)


    def get(self, the_uri):
        """
        the function that actually sends the request
        and returns the data
        """
        
        response = requests.get(the_uri, headers=self.headers)
        return response.json()

    def put(self, the_uri, data):
        """
        the function that puts stuff in
        """

        response = requests.put(the_uri, headers=self.headers, data=data)
        return response.json()

    def post(self, the_uri, data):
        """
        the function that posts stuff
        """

        response = requests.post(the_uri, headers=self.headers, data=data)
        return response.json()


    def options(self, the_uri):
        """
        options function
        used to request custom uris for orders and contacts:
        input range, output: range of uris for minimal number of
        api calls
        """ 

        response = requests.options(the_uri, headers=self.headers)
        return response.json()

    def post_by_service(self, service, data):
        """
        shortcut method to post via different services
        """

        service_uri = "{0}{1}-service/{1}".format(self.uri, service)
        return self.post(service_uri, data) 

    def post_goods_out(self, order, data):
        """
        shortcut to post a new goods out note
        response is goods out note reference number
        """

        goods_out_note_uri = "{}warehouse-service/order/{}/goods-note/goods-out".format(
                self.uri, order
                )
        response = self.post(goods_out_note_uri, data)
        return response['response'][0]


    def get_options_uris_by_service(self, service, reference_number):
        """
        Builds a list_of_uris when passed data and pre-defined service type.
        Only needs service name and reference number(s) as string.
        """
        # service uri also serves as stub for uri building at end of method
        service_uri = "{}{}-service".format(self.uri, ALL_SERVICES[service][0])
        
        options_uri = "{}/{}/{}".format(service_uri, ALL_SERVICES[service][1], reference_number)
        options_data = self.options(options_uri)
        response_data = options_data['response']['getUris']

        list_of_uris = list()
        for uri_segment in response_data:
            list_of_uris.append("{}{}".format(service_uri, uri_segment))
        return list_of_uris

    def get_order_data(self, request_range):

        sales_uris = self.get_options_uris_by_service("order", request_range
            )

        orders_data = list()

        for each_uri in sales_uris:
            response_data = self.get(each_uri)
            for each_set_of_sales in range(len(response_data['response'])):
                orders_data.append(response_data['response'][each_set_of_sales])
        
        return orders_data

    def get_products_data(self, request_range, custom=False):

        sales_uris = self.get_options_uris_by_service("products", request_range
            )
        products_data = list()

        for each_uri in sales_uris:
            if custom is True:
                each_uri += "?includeOptional=customFields"
            response_data = self.get(each_uri)
            for each_set_of_products in range(len(response_data['response'])):
                products_data.append(response_data['response'][each_set_of_products])
        
        return products_data

    def get_product_prices(self, request_range, price_list):
        """
        returns a dictionary of product ids and prices
        """

        prices_uris = self.get_options_uris_by_service("prices", request_range)

        prices_data = dict()

        for each_uri in prices_uris:
            price_list_uri = "{}/price-list/{}".format(each_uri, price_list)
            response_data = self.get(price_list_uri)
            if 'errors' in response_data:
                # return empty set if single item called with no prices
                pass 
            else:
                for each_product in range(len(response_data['response'])):
                    if '1' in response_data['response'][each_product]['priceLists'][0]['quantityPrice']:
                        product_id = response_data['response'][each_product]['productId']
                        price = response_data['response'][each_product]['priceLists'][0]['quantityPrice']['1']
                            
                        prices_data[product_id] = price

        return prices_data

    def get_product_suppliers(self, request_range=""):
        # code smell
        suppliers_uri = self.get_options_uris_by_service("products", request_range
            )
        suppliers_data = dict()

        for each_uri in suppliers_uri:
            response_data = self.get(each_uri + "/supplier")
            suppliers_data.update(response_data['response'])
        
        return suppliers_data

    def get_goods_notes(self, orders, note_type="in"):
        """
        Parameter
        ---------
        orders: list of orders to get goods notes for
        note_type: string for goods note type
            "in": (default value) returns goods-in notes
            "out": returns goods-out notes
        """

        goods_note_uri_start ="{}warehouse-service/order/".format(self.uri)
        goods_note_uri_end = "/goods-note/goods-{}/".format(note_type)
        if len(orders) > 200:
            order_chunks = Tools.grouper(orders, chunksize=200)
        else:
            order_chunks = [orders]

        all_responses = {}
        for chunk in order_chunks:
            response = self.get(
                "{}{}{}".format(
                    goods_note_uri_start,
                    Tools.searchstringifier(chunk),
                    goods_note_uri_end
                    )
                )
            all_responses.update(response['response'])
        return all_responses

    def lookup_service(self, service, **kwargs):
        """
        calls on the search functionality to lookup a product
        and return all information including product ID
        Will lookup sku by default
        """
        methods = set()
        the_uri = '{0}{1}-service/{1}-search?'.format(self.uri, service)
            
        for key, value in kwargs.items():
            the_uri += '{}={}'.format(key, value)
            if len(kwargs) > 1:
                the_uri += '&'
        print(key)
        methods.add(key)       
        response = self.get(the_uri)
        
        if response['response']['results'] != []:
            
            line_items = response['response']['results'][0]

            if "sku" in methods or "ean" in methods:
                data = {
                    'product_id': line_items[0],
                    'product_name': line_items[1],
                    'sku': line_items[2],
                    'EAN': line_items[4],
                    'stock_tracked': line_items[7],
                    'category_code': line_items[11],
                    'product_group_id': line_items[12],
                }
                return data
        else:
            raise KeyError("response returned no data")

        return response['response']['results']


    def sku_lookup(self, sku_number):
        return self.lookup_service("product", sku=sku_number)

    def ean_lookup(self, ean_number):
        return self.lookup_service("product", ean=ean_number)

    def order_lookup(self, kwargs):
        return self.lookup_service("order", **kwargs)
    
    def product_lookup(self, kwargs):
        return self.lookup_service("product", **kwargs)

    def get_stock_levels(self, request_range):
        """
        returns stock levels for products
        comma separated or range
        """

        warehouse_service_uri = "{}warehouse-service/product-availability/{}".format(self.uri, request_range)
        return self.get(warehouse_service_uri)


class Tools(object):

    def list_of_request_ranges(self, request_range):
        """
        Used when OPTIONS cannot be requested.
        Splits request range into 200 item chunks for use within
        brightpearl request limit.
        """
        
        request_numbers = request_range.split("-")

        #for single item requests
        if len(request_numbers) == 1:
            return [request_range]

        begin = int(request_numbers[0])
        end = int(request_numbers[1])


        request_ranges = list()
        while begin < end:
            uri_request = "-".join((str(begin), str(begin+199)))
            begin += 200
            request_ranges.append(uri_request)

        request_ranges.pop()  

        if begin == end:
            last = str(begin)

        else:
            last = "-".join((str(begin-200), str(end)))

        request_ranges.append(last)

        return request_ranges

    def grouper(iterable, chunks=None, chunksize=None, fillvalue=None):
        """
        Parameters
        ----------
        iterable: iterable oblect to be split up 
        chunks: integer denoting how many chunks to produce
            default: None
            notes: overrides chunksize if listed
        chunksize: integer denoting max size of each chunk
            default: None
        fillvalue: string or integer to fill extra places in list with
            default: None

        Returns
        -------
        cleaned_list: list of cleaned lists with None fillvalue removed 
        
        Source
        ------
        https://docs.python.org/3/library/itertools.html#itertools-recipes
        """

        if chunks is None and chunksize is None:
            raise KeyError("Please enter either chunks or chunksize Parameter")

        if chunks is not None:
            chunksize = int(ceil(len(iterable) / chunks))

        args = [iter(iterable)] * chunksize
        list_of_chunks = list(zip_longest(*args, fillvalue=fillvalue))
        cleaned_list = [[item for item in one_list if item is not None] 
                for one_list in list_of_chunks ]

        return cleaned_list

    def searchstringifier(a_list):
        """
        Parameter
        ---------
        a_list: list of items to convert into one comma separated string

        Returns
        -------
        string comma separated
        """

        return ','.join([str(item) for item in a_list])