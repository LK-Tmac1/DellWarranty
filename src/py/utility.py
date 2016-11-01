# -*- coding: utf-8 -*-

import yaml, requests, datetime, os, time
from constant import letters, history_DA_file_format, datetime_str_format, \
	date_str_format, hour_str_format, date_str_format_search
from dateutil.parser import parse

def is_path_existed(path):
	return os.path.exists(path)

def delete_file(file_path):
	if is_path_existed(file_path):
		os.remove(file_path)

def parse_str_date(str_date):
	if str(str_date).strip() == "" or str_date is None:
		return ""
	try:
		date_object = parse(str_date)
		return date_str_format % (date_object.year, date_object.month, date_object.day)
	except:
		return str_date

def check_letter_valid(letter):
		return letter != "" and letter.upper() in letters

def parse_cmd_args(arguments, required_arg_list):
	arg_map = {}
	for iarg in range(1, len(arguments)):
		arg = arguments[iarg]
		for a in required_arg_list:
			if arg.startswith(a):
				if "=" in arg:
					arg_map[a[2:-1]] = arg.split("=", 1)[1]
				else:
					arg_map[a[2:]] = None
				break
	return arg_map

def get_current_datetime(is_format=True, is_date=False, str_format=datetime_str_format):
	now = datetime.datetime.now()
	if is_format:
		if is_date:
			now = now.strftime(date_str_format_search)
		else:
			now = now.strftime(str_format)
	return now

def diff_two_datetime(time1, time2, date_time=True, days=False):
	t1 = datetime.datetime.strptime(time1, datetime_str_format)
	t2 = datetime.datetime.strptime(time2, datetime_str_format)
	if t1 > t2:
		temp = t1
		t2 = t1
		t1 = temp
	diff = t2 - t1
	if date_time:
		a = time.strftime(hour_str_format, time.gmtime(diff.seconds))
		return a
	elif days:
		return diff.days

def read_file(file_path, isYML, isURL=False, lines=False):
	# Read input file in .yml format, either the yml_path is a URL or or local path
	result = None
	if isURL:
		resp = requests.get(file_path)
		if str(resp.status_code) == '200':
			result = yaml.load(resp.content) if isYML else resp.content
	else:
		if is_path_existed(file_path):
			with open(file_path, "r") as value:
				result = yaml.load(value) if isYML else value.read()
	if lines and result is not None:
		result = result.split("\n")
	return result

def convert_linux_to_win(input_path, output_path):
	with open(input_path, 'r') as value:
		value = value.read()
		value.replace("\n", "\r\n")
		import io
		with io.open(output_path, 'w', newline="\r\n") as output:
			output.write(value)
	return True
input_path = "/Users/Kun/dell/output_1_H_Y_J_R_3_2.txt"
output_path = "/Users/Kun/dell/output.txt"
# convert_linux_to_win(input_path, output_path)

def save_object_to_path(value, output_path, isYML=False):
	parent_dir = output_path[0:output_path.rfind("/")]
	# If output parent dir does not exist, create it
	if not is_path_existed(parent_dir):
		os.makedirs(parent_dir)
	with open(output_path, 'w') as output:
		if not isYML:
			object_L = value
			if type(object_L) is not list:
				object_L = [object_L]
			for obj in object_L:
				if obj is not None and obj != "":
					content = str(obj)
					if content[-1] != '\n':
						content += '\n'
					output.write(content)
		else:
			yaml.safe_dump(value, output)
	return True

def list_file_name_in_dir(input_path, file_format=history_DA_file_format):
	if not is_path_existed(input_path):
		return None
	names = []
	for n in set(os.listdir(input_path)):
		if n.endswith(file_format):
			names.append(n[0:len(n) - len(file_format)])
	return names
	
def load_file_as_set(valid_svctag_path):
	_file = read_file(valid_svctag_path, isYML=False)
	_set = set(_file.split("\n"))
	if '' in _set:
		_set.remove('')
	return _set	

