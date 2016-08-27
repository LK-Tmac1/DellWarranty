import itertools, requests, os
from utility import read_file, save_object_to_path, list_file_name_in_dir, load_file_as_set
from constant import api_offset

per = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def svctags_generator(svc_L):
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
	result_T = itertools.product(per, repeat=count_empty_letter(svc_L))
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

def separate_svctag(svc_L, history_valid_svc_set, history_dellasset_set):
	# remove those valid svctags, and also those svctag already in output 
	# keep those unchecked svctags remained
	uncheck_set = set([])
	svc_set = set(svc_L)
	for s in svc_set:
		if s not in valid_svc_set and s not in history_dellasset_set:
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

def filter_invalid_svctags(svc_L, dell_support_url):
	valid_svc_L = []
	for svc in svc_L:
		resp_suffix = requests.get(dell_support_url + svctag).url
		if str(resp_suffix).endswith(svctag):
			valid_svc_L.append(svc)
	return valid_svc_L

def valid_svctags_batch(svc_L, logging, dell_asset_path, dell_support_url, history_valid_svctag_path):
	history_valid_svc_set = load_file_as_set(history_valid_svctag_path)
	history_dellasset_set = set(list_file_name_in_dir(dell_asset_path, file_suffix='.txt'))
	all_svc_L = svctags_generator(svc_L)
	unchecked_svc_L, checked_svc_L = separate_svctag(all_svc_L, history_valid_svc_set, history_dellasset_set)
	new_target_svc_L = filter_invalid_svctags(unchecked_svc_L, dell_support_url)

	save_object_to_path(object_L=list(history_valid_svc_set).extend(new_target_svc_L), output_path=history_valid_svctag_path)
	
	return svctags_flatten(valid_svc_L=valid_svc_L)
