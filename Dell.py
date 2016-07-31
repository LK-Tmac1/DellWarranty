import requests
import yaml
import itertools

config_path = "/Users/kunliu/Desktop/work/dell_config.yml"

with open(config_path, 'r') as input:
	config = yaml.load(input)

def svctags_random(per, suffix, d):
	#per = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	result_T = itertools.product(per ,repeat=d)
	result_L = []
	for r_T in result_T:
		result_L.append(''.join(r_T) + suffix)
	return result_L


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

def check_svctag_valid(svctag):
	web_url = "http://www.dell.com/support/home/cn/zh/cndhs1/product-support/servicetag/"+svctag
	resp_suffix = requests.get(web_url).url
	return True if str(resp_suffix).endswith(svctag) else False

def filter_invalid_svctags(svctags_L):
	valid_svc_L = []
	for svc in svctags_L:
		if check_svctag_valid(svc):
			valid_svc_L.append(svc)
	return valid_svc_L

def svctags_generator(svctags_L, offset=100):
	valid_svc_L = filter_invalid_svctags(svctags_L)
	temp_L = []
	turn = 1
	while turn * offset <= len(valid_svc_L):
		begin = (turn - 1) * offset
		end = turn * offset
		temp_L.append(valid_svc_L[begin:end])
		turn += 1
	if turn * offset > len(valid_svc_L):
		begin = (turn - 1) * offset
		temp_L.append(valid_svc_L[begin:])
	result_L = []
	for L in temp_L:
		result_L.append(svctags_flatten(L))
	return result_L



filter_invalid_svctags(svctags_L)
offset=100
api_key=config['api_key']
data_format="json"
svctags_L=["3P3JR32", "G3VG2W1","DCVYWW1", "V0FDV32","GGVG2W1","GGGG2W1"]
api_url="https://api.dell.com/support/v2/assetinfo/warranty/tags.%s?svctags=%s&apikey=%s"
url = api_url % (data_format, svctags, api_key)

warranty = requests.get(url).json()