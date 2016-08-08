import yaml, requests
from svctag_process import valid_svctags_batch
from json_process import check_response_valid, get_response_by_valid_tags
from entity import Warranty, DellAsset
from utility import load_yaml_config

config_path = "/Users/kunliu/Desktop/work/dell_config.yml"
suffix = "JR32"
digit = 3
csv_output_path = ""


if __name__ == '__main__':
	config = load_yaml_config(config_path)

	api_key=config["dell_api_key"]
	svctags_L=["3P3JR32", "G3VG2W1","DCVYWW1","GGVG2W1","GGGG2W1"]
	api_url=config['dell_api_url']
	url = api_url % ("G3VG2W1|DCVYWW1", api_key)

	json_resp = requests.get(url).json()
	dell_asset = json_resp["GetAssetWarrantyResponse"]["GetAssetWarrantyResult"]["Response"]["DellAsset"]

	if type(dell_asset) == dict:
		dell_asset = [dell_asset]


L = valid_svctags_batch(suffix="3JR32", dell_support_url="http://www.dell.com/support/home/cn/zh/cndhs1/product-support/servicetag/", d=2)

a = Warranty("2012-12-21T13:00:00", "2015-12-22T12:59:59", "Parts Only Warranty", "true","仅限部件保修(POW)")
b = Warranty("2011-01-21T13:00:00", "2012-01-12T12:59:59", "Next Business Day response", "true", "下个工作日送达")
c = Warranty("2014-01-21T13:00:00", "2016-11-22T12:59:59", "Parts Only Warranty (Carry-In Service)", "true","仅限部件保修(送修服务)")

d = DellAsset("XPS 13 L322X", "G3VG2W1", "2012-12-21T13:00:00", [a,b,c])

