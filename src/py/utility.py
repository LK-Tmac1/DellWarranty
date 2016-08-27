import yaml, requests, datetime, os


def parse_cmd_args(arguments, required_arg_list):
	arg_map = {}
	for iarg in range(1, len(arguments)):
		arg = arguments[iarg]
		for a in required_arg_list:
			if arg.startswith(a):
				arg_map[a[2:-1]] = arg.split("=", 1)[1]
				break
	return arg_map

def get_current_time():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def read_file(file_path, isYML, isURL=False):
	# Read input file in .yml format, either the yml_path is a URL or or local path
	if isURL:
		resp = requests.get(file_path)
		if str(resp.status_code) == '200':
			return yaml.load(resp.content) if isYML else resp.content
	else:
		if os.path.exists(file_path):
			with open(file_path, "r") as value:
				return yaml.load(value) if isYML else value.read()
	return None

def verify_job_parameter(config_path, password, svc_L):
	config = read_file(config_path, isYML=True)
	if config == None:
		return 3
	if password != config['password']:
		return 1
	for svc in svc_L:
		if svc.upper() not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
			return 2
	return 0

def save_object_to_path(object_L, output_path):
	parent_dir = output_path[0:output_path.rfind("/")]
	# If output parent dir does not exist, create it
	if not os.path.exists(parent_dir):
		os.makedirs(parent_dir)
	with open(output_path, 'w') as output:
		for obj in object_L:
			if str(obj) != '':
				output.write(str(obj) + "\n")
	return True

def list_file_name_in_dir(input_path, file_suffix):
	if not os.path.exists(input_path):
		return None
	names = []
	for n in set(os.listdir(input_path)):
		if n.endswith(file_suffix):
			names.append(n[0:len(n)-len(file_suffix)])
	return names
	
def load_file_as_set(valid_svctag_path):
	_file = read_file(valid_svctag_path, isYML=False)
	_set = set(svc_file.split("\n"))
	_set.remove('')
	return _set