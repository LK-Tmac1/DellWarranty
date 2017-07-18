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
    fault_exception_list = None
    quote_full = False

    def __init__(self, api_key):
        self.api_key = str(api_key)

    def response_to_entities(self, response):
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
    dell_asset_chain = parent_chain + ["Response", "DellAsset"]
    fault_chain = parent_chain + ["Faults"]
    fault_code_chain = ["FaultException", "Code"]
    fault_message_chain = ["FaultException", "Message"]
    nil_warranty_chain = ["ServiceLevelDescription","ServiceLevelDescription","nil"]

    def __init__(self, api_key):
        APIClient.__init__(self, api_key)
        self.json_response = None
        self.base_url = "https://api.dell.com/support/v2/assetinfo/warranty/tags.json?apikey=%s&svctags=" % self.api_key

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
                w_response_list = JSONClient.get_value_by_chain(da, ["Warranties", "Warranty"])
                if w_response_list:
                    try:
                        warranty_list = list([])
                        if type(w_response_list) is not list:
                            w_response_list = list([w_response_list])
                        for w in w_response_list:
                            if not w or type(w) is not dict or w.get("@nil"):
                                continue
                            service_en = JSONClient.clean_dell_asset_response_nil(w, "ServiceLevelDescription")
                            if not service_en:
                                # if no warranty description, skip to the next
                                continue
                            start_date = JSONClient.clean_dell_asset_response_nil(w, "StartDate")
                            end_date = JSONClient.clean_dell_asset_response_nil(w, "EndDate")
                            provider = JSONClient.clean_dell_asset_response_nil(w, "ServiceProvider", "DELL")
                            warranty_list.append(Warranty(start_date=start_date,
                                                          end_date=end_date, service_en=service_en, provider=provider))
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
        return self.raw_response and self.raw_response.status_code == 200 and self.fault_exception_list is None

    def handle_response_error(self, response):
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
        self.raw_response = requests.get(self.base_url + svc_parameter)
        self.json_response = self.raw_response.json()
        fault_response = JSONClient.get_value_by_chain(self.json_response, JSONClient.fault_chain)
        self.fault_exception_list = list([])
        if type(fault_response) is not list:
            fault_response = list([fault_response])
        if fault_response:
            for fault_exception in fault_response:
                if fault_exception:
                    fault_exception = fault_exception.get("FaultException")
                    if fault_exception:
                        self.fault_exception_list.append(fault_exception)
        self.dell_asset_response = JSONClient.get_value_by_chain(self.json_response, JSONClient.dell_asset_chain)
        return self.raw_response is not None

    def get_fault_message(self):
        if self.fault_exception_list:
            return "\n".join(["Code=%s, Message=%s" % (fault_exception.get("Code"), fault_exception.get("Message"))
                              for fault_exception in self.fault_exception_list])

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

    def response_to_entities(self, response):
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
