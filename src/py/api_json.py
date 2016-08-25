import requests
from entity import Warranty, DellAsset
from email_job import send_email
from constant import api_json_l1, api_json_l2, api_error_code


def get_value_by_key(json_data, key_L):
	# Given a json dict data, and a list of keys, find the value of the last key
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
		return -1
	else:
		json_response = respon.json()
		if type(json_response) is dict:
			# In rare case, the Faults is not None but there could still be DellAsset JSON data
			if get_value_by_key(json_response, [api_json_l1, api_json_l2, "Faults"]) is None or \
				get_value_by_key(json_response, [api_json_l1, api_json_l2, "Response", "DellAsset"]) is not None:
				return 0
	
def json_value_transform(data, key):
	return str(data[key]).replace(',', ' ') if data is not None and type(data) is dict and key in data else ""

def json_to_entities(json_data, config):
	# Given a JSON format data, return a list of DellAsset objects
	# print json_data, "\n~~~~~~~~~~~~~~~~~"
	dell_asset_L = get_value_by_key(json_data, [api_json_l1, api_json_l2, "Response", "DellAsset"])
	if dell_asset_L is None:
		return []
	if type(dell_asset_L) == dict:
		dell_asset_L = [dell_asset_L]
	dell_asset_object_L = []
	for da in dell_asset_L:
		if da is not None:
			w_response = get_value_by_key(da, ["Warranties", "Warranty"])
			warranty_L = []
			if w_response is not None:
				if type(w_response) == dict:
					w_response = [w_response]
				# print da, "\n######"
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
			print dell_asset_object_L[-1], "\n>>>>>>>>>>>>>>>"
	return dell_asset_object_L

def get_response_batch(req_url, step, config):
	# Assuming the svctags are all valid, if the response is an exception, then keep on trying until step is 0
	respon = requests.get(req_url)
	code = verify_response_code(respon)
	if code == 0:
		return respon.json()
	elif step > 0:
		return get_response_batch(req_url, step - 1, config)
	else:
		subject = config['email_subject_error']
		text = api_error_code[code] + "\n\n" + req_url
		print "Error message:\n", text
		send_email(subject=subject, text=text, config=config)
		return None

def get_entities_batch(svctag_L, url, config):
	global_entities_L = []
	for svctag in svctag_L:
		req_url = url + svctag
		json_data = get_response_batch(req_url, step=10, config=config)
		if json_data is not None and type(json_data) is dict:
			global_entities_L.extend(json_to_entities(json_data, config))
	return global_entities_L
