import yaml, os

def read_translation(file_path):
	# Read input file and return a translation dictionary
	# With key as the service english and value as service chinese
	tran_dict = {}
	if os.path.isfile(file_path):
		with open(file_path, "r") as value:
			tran_dict = yaml.load(value)
	return tran_dict

def write_translation(output_path, tran_dict, overwrite=True):
	# Given a new translation dict, update the translation file
	mode = "w" if overwrite else "a"
	with open(output_path, mode) as output_file:
		output_file.write(yaml.safe_dump(tran_dict, allow_unicode=True, default_flow_style=False))

def separate_translation_dict(tran_dict):
	# Separate those services with/out available Chinese translation from the dict
	NA_dict = {}
	for k, v in tran_dict.items():
		if v is None or v == 'null' or len(v.encode('utf-8')) == 0:
			tran_dict.pop(k)
			NA_dict[k] = None
	return tran_dict, NA_dict

def update_translation(input_path, tran_dict, output_path=""):
	# 1. Update those serivces already translated and overwrite the output
	# 2. For services not translated, append them to the output
	tran_dict = import_translation(input_path)
	print tran_dict
	tran_dict, NA_dict = separate_translation_dict(tran_dict)
	output_path = input_path if output_path == "" else output_path
	write_translation(output_path, tran_dict)
	write_translation(output_path, NA_dict, overwrite=False)