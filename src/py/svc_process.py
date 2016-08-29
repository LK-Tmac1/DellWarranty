import itertools, requests
from utility import check_letter_valid, save_object_to_path, list_file_name_in_dir, load_file_as_set
from constant import api_offset, letters, svc_placeholder


def svctags_generator(svc_L):
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
	result_T = itertools.product(letters, repeat=count_empty_letter(svc_L))
	result_L = []
	index_L = get_empty_index_L(svc_L)
	for r_T in result_T:
		j = 0
		for i in index_L:
			svc_L[i] = r_T[j]
			j += 1
		result_L.append("".join(svc_L))
	for i in index_L:
		svc_L[i] = svc_placeholder
	return result_L

def classify_svctags(all_svc_S, history_valid_svc_S, history_dellasset_S):
	# classify those valid and invalid svctags, and also those svctag already in output 
	unknown_S = set([])
	valid_S = set([])
	existing_S = set([])
	for svc in all_svc_S:
		# First check whether there is a historical Dell Asset of this svc so as to reduce work load
		target_S = existing_S if svc in history_dellasset_S else (valid_S if svc in history_valid_svc_S else unknown_S)
		target_S.add(svc)
	return unknown_S, valid_S, existing_S
	
def svctags_flatten(valid_svc_L, offset=api_offset):
	# Given a list of service tags, return the concatenated string delimited by "|"
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

def filter_invalid_svctags(svc_S, dell_support_url):
	valid_svc_S = set([])
	for svc in svc_S:
		resp_suffix = requests.get(dell_support_url + svc).url
		if str(resp_suffix).endswith(svc):
			valid_svc_S.add(svc)
	return valid_svc_S

def target_svctags_batch(svc_L, dell_support_url, history_dell_asset_path, history_valid_svctag_path, logger):
	logger.info("Begin svctags processing batch")
	history_valid_svc_S = load_file_as_set(history_valid_svctag_path)
	logger.info("Load history valid svctag file")
	history_dellasset_S = set(list_file_name_in_dir(history_dell_asset_path, file_suffix='.txt'))
	logger.info("Read history dell asset path")
	all_svc_S = set(svctags_generator(svc_L))
	logger.info("Generate all possible svctags")
	unknown_S, valid_S, existing_S = classify_svctags(all_svc_S, history_valid_svc_S, history_dellasset_S)
	logger.info("Classify all possible svctags into unknown, valid, and existing svctags")
	target_svc_S = filter_invalid_svctags(unknown_S, dell_support_url).union(valid_S)
	logger.info("Filter out invalid, and combine with those valid as target svctags")
	update_valid_svc_L = list(target_svc_S.union(history_valid_svc_S).union(history_dellasset_S))
	save_object_to_path(object_L=update_valid_svc_L, output_path=history_valid_svctag_path)
	logger.info("Update the history valid svctags")
	return svctags_flatten(valid_svc_L=list(target_svc_S)), existing_S