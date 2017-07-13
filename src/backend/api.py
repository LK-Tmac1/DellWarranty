import requests, json, xml

dell_json_api_url = "https://api.dell.com/support/v2/assetinfo/warranty/tags.json?"
dell_api_url = "https://api.dell.com/support/v2/assetinfo/warranty/tags.json?"
dell_xml_url = "https://api.dell.com/support/assetinfo/v4/getassetwarranty/"

l1 = "GetAssetWarrantyResponse"
l2 = "GetAssetWarrantyResult"

api_error_code = {
   -1: "Unknown error happened",
    0: "Everything is good",
    1: "Service Profile Throttle Limit Reached",
    2: "The number of tags that returned no data exceeded the maximum percentage of incorrect tags",
    3: "The request has failed due to an internal authorization configuration issue",
    4: "User Identification failed in Key Management Service"
}


class APIClient(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = ""
        self.usedup = False

    def call(self, svc_flatten):
        if not self.usedup:
            call_url = self.base_url + svc_flatten
            return requests.get(url=call_url)
        else:
            raise Exception("%s API quote limit reached" % self.__class__.__name__)

    def response_to_entity(self, response):
        raise NotImplementedError

    @staticmethod
    def verify_response_error_code(response):
        # Check if response is valid or not
        if response.status_code == 200:
            content = str(response.content)
            for k, v in api_error_code.items():
                if content.find(v) > 0:
                    return k
        else:
            pass


class JSONClient(APIClient):

    def __init__(self, api_key):
        APIClient.__init__(api_key)
        self.base_url = "%skey=%s&svctags=" % (dell_json_api_url, self.api_key)


class XMLClient(APIClient):
    def __init__(self, api_key):
        APIClient.__init__(api_key)
        self.base_url = "%skey=%s&svctags=" % (dell_xml_url, self.api_key)
