import itertools, requests, os
from utility import read_file, save_object_to_path
from constant import api_offset, file_valid_svc_name

per = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def load_valid_svctag_set(parent_path):
	svc_file = read_file(parent_path + file_valid_svc_name, isYML=False)
	svc_set = set(svc_file.split("\n"))
	svc_set.remove('')
	return svc_set

def check_letter_valid(letter):
	if letter == "" or letter.upper() not in per:
		return False
	return True

def count_empty_letter(svc_L):
	d = 0
	for s in svc_L:
		if not check_letter_valid(s):
			d += 1
	return d

def get_empty_index_L(svc_L):
	index_L = []
	for i in xrange(0, len(svc_L)):
		if not check_letter_valid(svc_L[i]):
			index_L.append(i)
	return index_L

def svctags_generator(svc_L):
	d = count_empty_letter(svc_L)
	result_T = itertools.product(per, repeat=d)
	result_L = []
	index_L = get_empty_index_L(svc_L)
	for r_T in result_T:
		j = 0
		for i in index_L:
			svc_L[i] = r_T[j]
			j += 1
		result_L.append("".join(svc_L))
	for i in index_L:
		svc_L[i] = ""
	return result_L

def keep_unchecked_svctag(svc_L, valid_svc_set, output_svc_set):
	# remove those valid svctags, and also those svctag already in output 
	# keep those unchecked svctags remained
	uncheck_set = set([])
	svc_set = set(svc_L)
	for s in svc_set:
		if s not in valid_svc_set and s not in output_svc_set:
			uncheck_set.add(s)
	return list(uncheck_set)

def svctags_flatten(valid_svc_L, offset=api_offset):
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
			temp_svc = "|".join(L)
			if temp_svc[len(temp_svc) - 1] == "|":
				temp_svc = temp_svc[0:len(temp_svc) - 2]
			result_L.append(temp_svc)
	return result_L

def check_svctag_valid(svctag, dell_support_url):
	resp_suffix = requests.get(dell_support_url + svctag).url
	return True if str(resp_suffix).endswith(svctag) else False

def filter_invalid_svctags(svctags_L, dell_support_url):
	valid_svc_L = []
	for svc in svctags_L:
		if check_svctag_valid(svctag=svc, dell_support_url=dell_support_url):
			valid_svc_L.append(svc)
	return valid_svc_L

def valid_svctags_batch(dell_support_url, suffix, valid_svctag_path, d):
	# If the valid_svctag_path is already there, no need to regenerate valid svctags
	valid_svc_L = []
	if not os.path.exists(valid_svctag_path):
		svctags_random_L = svctags_generator(d, suffix)
		valid_svc_L = filter_invalid_svctags(svctags_random_L, dell_support_url)
		save_object_to_path(object_L=valid_svc_L, output_path=valid_svctag_path)
	else:
		valid_svc_L = read_file(valid_svctag_path, isYML=False).split("\n")
	
	return svctags_flatten(valid_svc_L=valid_svc_L)
