import requests
from entity import Warranty, DellAsset


def check_response_valid(json_response):
	"""
	Check if response is valid or not due to "internal authorization configuration", Code=503
	{u"GetAssetWarrantyResponse": 
		{u"GetAssetWarrantyResult": 
			{u"Faults": {u"FaultException": {u"Message": u"The request has failed due to an internal authorization configuration issue.", u"Code": 503}}, u"Response": None}}}
	"""
	a = "GetAssetWarrantyResponse"
	b = "GetAssetWarrantyResult"
	c = "Faults"
	if a in json_response and b in json_response[a] and c in json_response[a][b]:
		return True if json_response[a][b][c] is None else False
	return False

def get_response_by_valid_tags(svctags, url, step=10):
	"""
	Assuming the svctags are all valid, if the response is an exception, then keep on trying
	until step is 0
	"""
	json_resp = requests.get(url).json()
	while not check_response_valid(json_resp) and step > 0:
		json_resp = requests.get(url).json()
		step -= 1
	return json_resp
	
def json_to_entities(json_data):
	# Given a JSON format data, return a list of DellAsset objects
