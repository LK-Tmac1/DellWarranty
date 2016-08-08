import yaml, requests
from svctag_process import valid_svctags_batch
from json_process import check_response_valid, get_response_by_valid_tags

config_path = "/Users/kunliu/Desktop/work/dell_config.yml"

with open(config_path, "r") as value:
	config = yaml.load(value)

api_key=config["dell_api_key"]
svctags_L=["3P3JR32", "G3VG2W1","DCVYWW1","GGVG2W1","GGGG2W1"]
#api_url="https://api.dell.com/support/v2/assetinfo/warranty/tags.json?svctags=%s&apikey=%s"
api_url=config['dell_api_url']
url = api_url % ("G3VG2W1|DCVYWW1", api_key)

json_resp = requests.get(url).json()
dell_asset = json_resp["GetAssetWarrantyResponse"]["GetAssetWarrantyResult"]["Response"]["DellAsset"]
"MachineDescription"
"ServiceTag"


if type(dell_asset) == dict:
	dell_asset = [dell_asset]


L = valid_svctags_batch("3JR32", d=2)
