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
	if isYML:
		if isURL:
			resp = requests.get(file_path)
			return yaml.load(resp.content)
		else:
			with open(file_path, "r") as value:
				return yaml.load(value)
	else:
		if os.path.exists(file_path):
			with open(file_path, "r") as value:
				return value.read()
		else:
			return None


def verify_job_parameter(config_path, password, suffix, digit):
	config = read_file(config_path, isYML=True)
	if password != config['password']:
		return 1
	if len(suffix) + int(digit) != 7:
		return 2
	else:
		return 0

def save_object_to_path(object_L, output_path):
	parent_dir = output_path[0:output_path.rfind("/")]
	# If output parent dir does not exist, create it
	if not os.path.exists(parent_dir):
		os.makedirs(parent_dir)
	with open(output_path, 'w') as output:
		for obj in object_L:
			output.write(str(obj) + "\n")
	return True
