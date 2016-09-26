import requests
from entity import Warranty, DellAsset

l1 = "GetAssetWarrantyResponse"
l2 = "GetAssetWarrantyResult"

api_error_code = { 	
	- 1 : "Unknown error happened",
	1 : "Service Profile Throttle Limit Reached",
	2 : "The number of tags that returned no data exceeded the maximum percentage of incorrect tags",
	3 : "The request has failed due to an internal authorization configuration issue",
	4 : "User Identification failed in Key Management Service" }

def get_value_by_key(json_data, key_L):
	# Given a json dict data, and a list of keys, find the value of the last key by levels
	for key in key_L:
		if json_data is not None and type(json_data) is dict and key in json_data:
			json_data = json_data[key]
		else:
			return None
	return json_data

def verify_response_code(respon):
	# Check if response is valid or not
	if str(respon.status_code) != '200':
		content = str(respon.content)
		for k, v in api_error_code.items():
			if content.find(v) > 0:
				return k
	else:
		# In rare case, the Faults is not None but there could still be DellAsset JSON data
		if type(respon.json()) is dict:
			fault_json = get_value_by_key(respon.json(), [l1, l2, "Faults"])
			da_json = get_value_by_key(respon.json(), [l1, l2, "Response", "DellAsset"])
			if fault_json is None or da_json is not None:
				return 0
	return -1
	
def json_value_transform(data, key):
	return str(data[key]).replace(',', ' ') if data is not None and type(data) is dict and key in data else ""

def get_response_batch(req_url, logger):
	# Assuming the svctags are all valid, if the response has an exception, keep on trying until step is 0
	respon = requests.get(req_url)
	code = verify_response_code(respon)
	step = 3
	while code != 0 and step > 0:
		respon = requests.get(req_url)
		code = verify_response_code(respon)
		step - 1
	if code == 0:
		return respon.json()
	else:
		logger.error(api_error_code[code])
		return None

def json_to_entities(json_data, logger):
	# Given a JSON format data, return a list of DellAsset objects
	dell_asset_L = get_value_by_key(json_data, [l1, l2, "Response", "DellAsset"])
	if dell_asset_L is None:
		logger.warn("No Dell Asset exists:\n" + json_data)
		return []
	if type(dell_asset_L) == dict:
		dell_asset_L = [dell_asset_L]
	dell_asset_object_L = []
	has_None_DA = False
	for da in dell_asset_L:
		has_None_W = False
		if da is not None:
			w_response = get_value_by_key(da, ["Warranties", "Warranty"])
			warranty_L = []
			if w_response is not None:
				if type(w_response) == dict:
					w_response = [w_response]
				for w in w_response:
					start_date = json_value_transform(w, "StartDate")
					end_date = json_value_transform(w, "EndDate")
					service_en = json_value_transform(w, "ServiceLevelDescription")
					is_provider = json_value_transform(w, "ServiceProvider") if "@nil" not in w["ServiceProvider"] else "DELL"
					warranty_L.append(Warranty(start_date=start_date, end_date=end_date, service_en=service_en, is_provider=is_provider))
				machine_id = json_value_transform(da, "MachineDescription")
				svctag = json_value_transform(da, "ServiceTag")
				ship_date = json_value_transform(da, "ShipDate")
				dell_asset_object_L.append(DellAsset(machine_id=machine_id, svctag=svctag, ship_date=ship_date, warranty_L=warranty_L))
			else:
				has_None_W = True
		else:
			has_None_DA = True
		if has_None_W:
			logger.warn("Warranty response is None:\n %s" % da)
	if has_None_DA:	
		logger.warn("Dell Asset has None value:\n %s" % json_data)
	return dell_asset_object_L

def api_entities_batch(target_svc_L, api_url, logger):
	api_entities_L = []
	logger.info("======Begin calling API...")
	for svc in target_svc_L:
		req_url = api_url + svc
		logger.info("svctags="svc)
		json_data = get_response_batch(req_url, logger)
		if json_data is not None and type(json_data) is dict:
			api_entities_L.extend(json_to_entities(json_data, logger))
	return api_entities_L
