import requests, os
from entity import Warranty, DellAsset

reload(sys)
sys.setdefaultencoding('utf8')

l1 = "GetAssetWarrantyResponse"
l2 = "GetAssetWarrantyResult"

def get_value_by_key(json_data, key_L):
	temp_data = json_data
	for key in key_L:
		if key in temp_data:
			temp_data = temp_data[key]
		else:
			return None
	return temp_data

def check_response_valid(json_response):
	# Check if response is valid or not due to "internal authorization configuration", Code=503
	# {u"GetAssetWarrantyResponse": {u"GetAssetWarrantyResult": {u"Faults": {u"FaultException": 
	#	{u"Message": u"The request has failed due to an internal authorization configuration issue.", 
	# 	u"Code": 503}}, u"Response": None}}}
	return True if get_value_by_key(json_response, [l1, l2, "Faults"]) is None else False

def get_response(svctags, url, step):
	# Assuming the svctags are all valid, if the response is an exception, then keep on trying until step is 0
	json_resp = requests.get(url+svctags).json()
	while not check_response_valid(json_resp) and step > 0:
		json_resp = requests.get(url).json()
		step -= 1
	return json_resp
	
def json_value_transform(data):
	return str(data).replace(',',' ')

def json_to_entities(json_data):
	# Given a JSON format data, return a list of DellAsset objects
	dell_asset_L = get_value_by_key(json_data, [l1,l2,"Response","DellAsset"])
	dell_asset_object_L = []
	if type(dell_asset_L) == dict:
		dell_asset_L = [dell_asset_L]
	for da in dell_asset_L:
		w_response = get_value_by_key(da, ["Warranties", "Warranty"])
		warranty_L = []
		for w in w_response:
			start_date=json_value_transform(w["StartDate"])
			end_date=json_value_transform(w["EndDate"])
			service_en=json_value_transform(w["ServiceLevelDescription"])
			is_provider=json_value_transform(w["ServiceProvider"]["@nil"])
			warranty_L.append(Warranty(start_date=start_date, end_date=end_date,service_en=service_en, is_provider=is_provider))
		machine_id=json_value_transform(da["MachineDescription"])
		svctag=json_value_transform(da["ServiceTag"])
		ship_date=json_value_transform(da["ShipDate"])
		dell_asset_object_L.append(DellAsset(machine_id=machine_id,svctag=svctag,ship_date=ship_date, warranty_L=warranty_L))
	return dell_asset_object_L

def get_entities_batch(svctag_L, url, step=10):
	global_entities_L = []
	for svctag in svctag_L:
		json_data = get_response(svctag, url, step)
		global_entities_L.extend(json_to_entities(json_data))
	return global_entities_L
