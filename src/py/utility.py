# -*- coding: utf-8 -*-

import yaml, requests, datetime, os
from constant import letters, history_DA_file_format
from dateutil.parser import parse

def parse_str_date(str_date):
	try:
		date_object = parse(str_date)
		return "%s年%s月%s日" % (date_object.year, date_object.month, date_object.day)
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
		if svc.strip() != "" and svc.upper() not in letters:
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

def list_file_name_in_dir(input_path):
	if not os.path.exists(input_path):
		return None
	names = []
	for n in set(os.listdir(input_path)):
		if n.endswith(history_DA_file_format):
			names.append(n[0:len(n) - len(history_DA_file_format)])
	return names
	
def load_file_as_set(valid_svctag_path):
	_file = read_file(valid_svctag_path, isYML=False)
	_set = set(_file.split("\n"))
	_set.remove('')
	return _set

class Logger(object):
	def __init__(self):
		self.info_header = "[INFO] "
		self.warn_header = "[WARN] "
		self.error_header = "[ERROR] "
		self.message_Q = {0 : self.info_header + "Start logging"}
		self.message_count = 1
		self.has_error = False
		self.has_warn = False
		self.info_index_L = []
		self.warn_index_L = []
		self.error_index_L = []
		self.message_type_D = {"ERROR" : self.error_index_L,
							   "WARN" : self.warn_index_L,
							   "INFO" : self.info_index_L}
	def add_message(self, message, message_index_L, header):
		self.message_Q[self.message_count] = header + message
		message_index_L.append(self.message_count)
		self.message_count += 1
	def info(self, info):
		self.add_message(header=self.info_header, message=info, message_index_L=self.info_index_L)
	def warn(self, warn):
		self.add_message(header=self.warn_header, message=warn, message_index_L=self.warn_index_L)
		self.has_warn = True
	def error(self, error):
		self.add_message(header=self.error_header, message=error, message_index_L=self.error_index_L)
		self.has_error = True
	def __repr__(self):
		temp_L = []
		for i in xrange(0, self.message_count):
			temp_L.append(self.message_Q[i])
		return "\n".join(temp_L)
	def get_message_by_type(self, message_type):
		temp_message_L = []
		message_index_L = self.message_type_D[message_type]
		for i in message_index_L:
			temp_message_L.append(self.message_Q[i])
		return "\n".join(temp_message_L)
	def get_error_only(self):
		return self.get_message_by_type("ERROR")
	def get_warn_only(self):
		return self.get_message_by_type("WARN")
	def get_info_only(self):
		return self.get_message_by_type("INFO")