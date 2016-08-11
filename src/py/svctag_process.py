import itertools, requests, os
from utility import create_dir_if_not_exist, read_file, save_object_to_path

def svctags_random(d, suffix, per="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
	# Generate cartisen product of per, say per="ABC", d=3 then
	# AAA, AAB, AAC, ABA, ABB, ABC, ACA...
	# If suffix specified, then add it to each result above.
	result_T = itertools.product(per ,repeat=int(d))
	result_L = []
	for r_T in result_T:
		result_L.append("".join(r_T) + suffix)
	print "=======%s number of random svctag generated" % (len(result_L))
	return result_L

def svctags_flatten(valid_svc_L, offset=100):
	# Given a list of valid service tags, return the concatenated string delimited by "|"
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
		if len(L) == 1:
			result_L.append(L[0])
		elif len(L) > 1:
			result_L.append("|".join(L))
	return result_L

def check_svctag_valid(svctag, dell_support_url):
	resp_suffix = requests.get(dell_support_url+svctag).url
	return True if str(resp_suffix).endswith(svctag) else False

def filter_invalid_svctags(svctags_L, dell_support_url):
	valid_svc_L = []
	i = 0
	for svc in svctags_L:
		i+=1
		if check_svctag_valid(svctag=svc, dell_support_url=dell_support_url):
			valid_svc_L.append(svc)
			print "~~~~~~~~~~~~~Valid tag:", svc, "remained=", str(len(svctags_L) - i)
	return valid_svc_L

def valid_svctags_batch(dell_support_url, suffix, valid_svctag_path, d, update_svc=False):
	# If the valid_svctag_path is already there, no need to regenerate valid svctags
	valid_svc_L = []
	if not os.path.exists(valid_svctag_path) or update_svc:
		svctags_random_L = svctags_random(d, suffix)
		valid_svc_L = filter_invalid_svctags(svctags_random_L, dell_support_url)
		save_object_to_path(object_L=valid_svc_L, output_path=valid_svctag_path)
	else:
		valid_svc_L = read_file(valid_svctag_path, isYML=False).split("\n")
	
	return svctags_flatten(valid_svc_L=valid_svc_L)
