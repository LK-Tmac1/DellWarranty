import requests
from entity import Warranty, DellAsset
from email_job import send_email


l1 = "GetAssetWarrantyResponse"
l2 = "GetAssetWarrantyResult"

def get_value_by_key(json_data, key_L):
	# Given a json dict data, and a list of keys, find the value of the last key
	temp_data = json_data
	while temp_data is not None:
		for key in key_L:
			if temp_data is not None and key in temp_data:
				temp_data = temp_data[key]
			else:
				return None
		return temp_data
	return "None"

def check_response_valid(respon):
	# Check if response is valid or not due to "internal authorization configuration", Code=503
	# {u"GetAssetWarrantyResponse": {u"GetAssetWarrantyResult": {u"Faults": {u"FaultException": 
	# 	{u"Message": u"The request has failed due to an internal authorization configuration issue.", 
	# 	u"Code": 503}}, u"Response": None}}}
	if str(respon.status_code) == '200':
		json_response = respon.json()
		if type(json_response) is dict:
			if get_value_by_key(json_response, [l1, l2, "Faults"]) is None or \
				get_value_by_key(json_response, [l1, l2, "Response", "DellAsset"]) is not None:
				return True
	return False

def get_response(req_url, step):
	# Assuming the svctags are all valid, if the response is an exception, then keep on trying until step is 0
	respon = requests.get(req_url)
	exceed_quote = "User application has exceeded the allotted usage quota for the day"
	if str(respon.content).find(exceed_quote) > 0:
		return 1
	if not check_response_valid(respon):
		if step > 0:
			return get_response(req_url, step - 1)
		else:
			return 2
	return respon.json()
	
def json_value_transform(data):
	return str(data).replace(',', ' ')

def json_to_entities(json_data, config):
	# Given a JSON format data, return a list of DellAsset objects
	# print json_data, "\n~~~~~~~~~~~~~~~~~"
	dell_asset_L = get_value_by_key(json_data, [l1, l2, "Response", "DellAsset"])
	dell_asset_object_L = []
	if dell_asset_L is None:
		return []
	if type(dell_asset_L) == dict:
		dell_asset_L = [dell_asset_L]
	for da in dell_asset_L:
		if da is not None:
			w_response = get_value_by_key(da, ["Warranties", "Warranty"])
			warranty_L = []
			if w_response is not None:
				if type(w_response) == dict:
					w_response = [w_response]
				#print da, "\n######"
				for w in w_response:
					start_date = json_value_transform(w["StartDate"])
					end_date = json_value_transform(w["EndDate"])
					service_en = json_value_transform(w["ServiceLevelDescription"])
					is_provider = "DELL"
					if "@nil" not in w["ServiceProvider"]:
						is_provider = json_value_transform(w["ServiceProvider"])
					warranty_L.append(Warranty(start_date=start_date, end_date=end_date, service_en=service_en, is_provider=is_provider))
			machine_id = json_value_transform(da["MachineDescription"])
			svctag = json_value_transform(da["ServiceTag"])
			ship_date = json_value_transform(da["ShipDate"])
			dell_asset_object_L.append(DellAsset(machine_id=machine_id, svctag=svctag, ship_date=ship_date, warranty_L=warranty_L))
			#print dell_asset_object_L[-1], "\n>>>>>>>>>>>>>>>"
	return dell_asset_object_L

def get_entities_batch(svctag_L, url, config):
	global_entities_L = []
	for svctag in svctag_L:
		req_url = url + svctag
		json_data = get_response(req_url, step=10)
		if type(json_data) is not dict:
			text = ""
			subject = ""
			if json_data == 1:
				subject = config['email_subject_error']
				text = "Service Profile Throttle Limit Reached\nURL=" + req_url	
			elif json_data == 2:
				subject = config['email_subject_warning']
				text = "Unkown reasons for failing to get response\nURL=" + req_url
			send_email(subject=subject, text=text, config=config)
		else:
			global_entities_L.extend(json_to_entities(json_data, config))
	return global_entities_L
