import requests
import yaml

config_path = "/Users/kunliu/Desktop/work/dell_config.yml"

with open(config_path, 'r') as input:
	config = yaml.load(input)

def svctags_flatten(svctags_L):
	"""
	Given a list of service tags, return the concatenated string delimited by "|"
	"""
	if len(svctags_L) == 0:
		return ""
	elif len(svctags_L) == 1:
		return svctags_L[0]
	else:
		return "|".join(svctags_L)



svc_invalid = "V0FDV32"
offset=100
api_key=config['api_key']
data_format="json"
svctags_L=["3P3JR32", "G3VG2W1","DCVYWW1"]
svctags = svctags_flatten(svctags_flatten_L)
home_url="https://api.dell.com/support/v2/assetinfo/warranty/tags.%s?svctags=%s&apikey=%s"
url = home_url % (data_format, svctags, api_key)

warranty = requests.get(url).json()