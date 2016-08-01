import requests

config_path = "/Users/kunliu/Desktop/work/dell_config.yml"

with open(config_path, "r") as input:
	config = yaml.load(input)

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
	if  a in json_response and b in json_response[a] and c in json_response[a][b]:
		return True if json_response[a][b][c] is None else False
	return False

def get_response_by_valid_tags(svctags, url):
	"""
	Assuming the svctags are all valid, if the response is an exception, then keep on trying
	until step is 0
	"""
	json_resp = requests.get(url).json()
	step = 10
	while not check_response_valid(json_resp) and step > 0:
		json_resp = requests.get(url).json()
		step -= 1
	return json_resp

api_key=config["api_key"]
data_format="json"
svctags_L=["3P3JR32", "G3VG2W1","DCVYWW1","GGVG2W1","GGGG2W1"]
api_url="https://api.dell.com/support/v2/assetinfo/warranty/tags.%s?svctags=%s&apikey=%s"
url = api_url % (data_format, "G3VG2W1|DCVYWW1", api_key)

json_resp = requests.get(url).json()
dell_asset = json_resp["GetAssetWarrantyResponse"]["GetAssetWarrantyResult"]["Response"]["DellAsset"]
"MachineDescription"
"ServiceTag"


if type(dell_asset) == dict:
	dell_asset = [dell_asset]