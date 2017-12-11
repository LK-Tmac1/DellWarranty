# -*- coding: utf-8 -*-

import json, xml, requests, traceback
from entity import DellAsset, Warranty
from collections import deque

api_offset = 50


class APIClient(object):
    # properly handles API response
    base_url = None
    raw_response = None
    dell_asset_response = None
    fault_exception_list = list([])
    quote_full = False

    def __init__(self, api_key):
        self.api_key = str(api_key)

    def response_to_entities(self):
        # parse response to DellAsset entity list
        raise NotImplementedError

    def flatten_svc_parameter(self, api_svc_list):
        raise NotImplementedError

    def handle_response_error(self, response):
        raise NotImplementedError

    def new_response(self, svc_parameter):
        raise NotImplementedError

    def is_response_error(self):
        raise NotImplementedError

    def get_fault_message(self):
        raise NotImplementedError

    @staticmethod
    def build_api_client_queue(configs):
        json_api_key = configs["dell_api_key"].get("json")
        xml_api_key = configs["dell_api_key"].get("xml")
        client_queue = deque([])
        client_queue.append(JSONClient(json_api_key))
        # client_queue.append(XMLClient(xml_api_key))
        return client_queue


class JSONClient(APIClient):
    parent_chain = ["GetAssetWarrantyResponse", "GetAssetWarrantyResult"]
    fault_chain = ["InvalidFormatAssets", "BadAssets"]
    nil_warranty_chain = ["ServiceLevelDescription","ServiceLevelDescription","nil"]

    def __init__(self, api_key):
        APIClient.__init__(self, api_key)
        self.json_response = None
        self.base_url = "https://api.dell.com/support/assetinfo/v4/getassetwarranty/{}?apikey=%s" % self.api_key

    @staticmethod
    def clean_dell_asset_response_nil(data, key, nil_value=""):
        if data and type(data) is dict:
            value = data.get(key)
            if type(value) is dict and "@nil" in value:
                return nil_value
            else:
                return value
        return ""

    def response_to_entities(self):
        # Given a JSON format data, return a list of DellAsset objects
        da_entity_list = list([])
        dell_asset_response = self.dell_asset_response
        if dell_asset_response:
            if type(dell_asset_response) is not list:
                dell_asset_response = list([dell_asset_response])
            for da in dell_asset_response:
                w_response_list = JSONClient.get_value_by_chain(da, ["AssetEntitlementData"])
                if w_response_list:
                    try:
                        warranty_list = list([])
                        if type(w_response_list) is not list:
                            w_response_list = list([w_response_list])
                        for w in w_response_list:
                            if not w or type(w) is not dict or w.get("@nil"):
                                continue
                            service_en = JSONClient.clean_dell_asset_response_nil(w, "ServiceLevelDescription")
                            if not service_en or service_en == "Do Not Generate":
                                # if no warranty description, skip to the next
                                continue
                            start_date = JSONClient.clean_dell_asset_response_nil(w, "StartDate")
                            end_date = JSONClient.clean_dell_asset_response_nil(w, "EndDate")
                            provider = JSONClient.clean_dell_asset_response_nil(w, "ServiceProvider")
                            if provider is None or provider == "None":
                                provider = "DELL"
                            warranty_list.append(Warranty(start_date=start_date,
                                                          end_date=end_date, service_en=service_en, provider=provider))
                        da = da.get("AssetHeaderData")
                        if da:
                            machine_id = da.get("MachineDescription")
                            svc_tag = da.get("ServiceTag")
                            ship_date = JSONClient.clean_dell_asset_response_nil(da, "ShipDate")
                            dell_asset = DellAsset(machine_id, svc_tag, ship_date, warranty_list)
                            da_entity_list.append(dell_asset)
                    except Exception as e:
                        print "发现异常，忽略：%s\n%s" % (e, traceback.format_exc())
        return da_entity_list

    def flatten_svc_parameter(self, api_svc_list):
        # Given a list of service tags, return the concatenated string delimited by "|"
        return "|".join(api_svc_list) if api_svc_list else None

    def is_response_error(self):
        return self.raw_response and self.raw_response.status_code == 200 and not self.fault_exception_list

    def handle_response_error(self, response):
        # Try to recover from error that blocks the ETL flow
        # It is possible that it could not be resolved, or it could be skipped
        resolved = skip = True
        for fault_exception in self.fault_exception_list:
            code, message = fault_exception.get("Code"), fault_exception.get("Message")
            if code == 403 and message == "Rate Limit Exceeded":
                # handles API "quote fully used" exception
                self.quote_full = True
                resolved = skip = False
                break
        return resolved, skip

    def new_response(self, svc_parameter):
        def retrieve_exception(json_response, fault_exception_list):
            if json_response:
                e1 = JSONClient.get_value_by_chain(json_response, ["InvalidFormatAssets", "BadAssets"])
                e2 = JSONClient.get_value_by_chain(json_response, ["InvalidBILAssets", "BadAssets"])
                e3 = JSONClient.get_value_by_chain(json_response, ["ExcessTags", "BadAssets"])
                fault_exception_list.append(e1)
                fault_exception_list.append(e2)
                fault_exception_list.append(e3)
        target_url = self.base_url.format(svc_parameter)
        self.raw_response = requests.get(target_url, headers={"content-type": "application/json"}, verify=False)
        try:
            self.json_response = self.raw_response.json()
        except Exception as e:
            self.json_response = None
        finally:
            retrieve_exception(self.json_response, self.fault_exception_list)
            self.dell_asset_response = JSONClient.get_value_by_chain(self.json_response, ["AssetWarrantyResponse"])
            return self.raw_response is not None

    def get_fault_message(self):
        message_list = []
        if self.fault_exception_list:
            for fault_exception in self.fault_exception_list:
                message_list.append(fault_exception)
        return "\n".join(message_list)

    def __repr__(self):
        return "JSON Client, key=%s" % self.api_key[:5]

    @staticmethod
    def get_value_by_chain(json_data, chain):
        # Given a json dict data, and a list of keys, find the value of the last key by levels
        for key in chain:
            if json_data and type(json_data) is dict:
                json_data = json_data.get(key)
            else:
                return None
        return json_data


class XMLClient(APIClient):
    def __init__(self, api_key):
        APIClient.__init__(self, api_key)
        self.base_url = "https://api.dell.com/support/assetinfo/v4/getassetwarranty/%s?apikey=" + self.api_key

    def response_to_entities(self):
        raise NotImplementedError

    def flatten_svc_parameter(self, api_svc_list):
        return ",".join(api_svc_list)

    def handle_response_error(self, response):
        raise NotImplementedError

    def new_response(self, svc_parameter):
        url = self.base_url % svc_parameter
        self.raw_response = json.load(requests.get(url=url))
        return self.raw_response

    def is_response_error(self):
        raise NotImplementedError

    def get_fault_message(self):
        pass

    def __repr__(self):
        return "XML Client, key=%s" % self.api_key[:5]


def test():
    client = JSONClient(api_key="")

    client.new_response("305MF12,ABCDEF7")
    result = client.response_to_entities()
    for r in result:
        print r
        for w in r.warranty_list:
            print w
        print "-----------"
