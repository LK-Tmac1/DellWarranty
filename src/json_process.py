import requests

"""
{u'GetAssetWarrantyResponse': 
	{u'GetAssetWarrantyResult': 
		{u'Faults': {u'FaultException': 
			{u'Message': u'The request has failed due to an internal authorization configuration issue.', u'Code': 503}}, u'Response': None}}}
"""

config_path = "/Users/kunliu/Desktop/work/dell_config.yml"

with open(config_path, 'r') as input:
	config = yaml.load(input)

api_key=config['api_key']
data_format="json"
svctags_L=["3P3JR32", "G3VG2W1","DCVYWW1","GGVG2W1","GGGG2W1"]
api_url="https://api.dell.com/support/v2/assetinfo/warranty/tags.%s?svctags=%s&apikey=%s"
url = api_url % (data_format, svctags_L[0], api_key)

json_resp = requests.get(url).json()
dell_asset = json_resp['GetAssetWarrantyResponse']['GetAssetWarrantyResult']['Response']['DellAsset']