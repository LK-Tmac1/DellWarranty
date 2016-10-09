import itertools, requests, time
from utility import check_letter_valid, save_object_to_path, list_file_name_in_dir, load_file_as_set, read_file, get_current_datetime, diff_two_datetime
from constant import api_offset, letters, svc_placeholder
from search import compile_svc_pattern


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


def filter_search_history_expired(svc_S, search_history_path, day_offset):
	expired_S = set([])
	existing_search_dict = read_file(search_history_path, isYML=True, isURL=False)
	current_date = get_current_datetime()
	for svctag, search_date in existing_search_dict.items():
		pattern = compile_svc_pattern(svctag)
		for svc in svc_S:
			if pattern.match(svc) and diff_two_datetime(current_date, search_date, days=True).days < day_offset:
				svc_S.remove(svc)
			else:
				expired_S.add(svc)
	return expired_S


def filter_invalid_svctags_URL(svc_S, dell_support_url, logger, svc_job=False):
	valid_svc_S = set([])
	svc_L = list(svc_S)
	total = len(svc_S)
	logger.info("Beging filtering %s unknown svctags" % total)
	i = 0
	last_error_index = 0
	retry_count = 1
	retry_limit = 5
	logger.info("Valid svctags:")
	while i < len(svc_L):
		try:
			resp_suffix = requests.get(dell_support_url + svc_L[i]).url
			if str(resp_suffix).endswith(svc_L[i]):
				valid_svc_S.add(svc_L[i])
				logger.info(svc_L[i])
			i += 1
		except requests.exceptions.ConnectionError:
			if last_error_index == i:
				retry_count += 1
				if retry_count == retry_limit:
					retry_count = 1
					i += 1
					logger.warn("Retried maximum times of %s for svc %s, move to the next" % (svc_L[i], retry_limit))
			else:
				# The first time this error happens for svc_L[i]
				last_error_index = i
				retry_count = 1
			sleep_time = 10 * retry_count
			time.sleep(sleep_time)
			logger.warn("ConnectionError, sleep %s seconds and restart %s..." % (sleep_time, svc_L[i]))
	return valid_svc_S


def target_svctags_batch(svc_L, dell_support_url, history_dell_asset_path, history_valid_svctag_path, logger, search_history_path, svc_job=False):
	logger.info("Begin svctags processing batch")
	history_valid_svc_S = load_file_as_set(history_valid_svctag_path)
	logger.info("Load %s known valid svctag" % len(history_valid_svc_S))
	history_dellasset_S = set(list_file_name_in_dir(history_dell_asset_path))
	logger.info("Read %s history dell asset" % len(history_dellasset_S))
	all_svc_S = set(svctags_generator(svc_L))
	logger.info("Generate %s possible svctags" % len(all_svc_S))
	unknown_S, valid_S, existing_S = classify_svctags(all_svc_S, history_valid_svc_S, history_dellasset_S)
	logger.info("Classify into %s unknown, %s known as valid but not existed, and %s existing svctags" % (len(unknown_S), len(valid_S), len(existing_S)))
	search_expried_svc_S = unknown_S  # filter_search_history_expired(unknown_S, search_history_path, 30)
	logger.info("Remove %s svctags with search date still effective" % (len(unknown_S) - len(search_expried_svc_S)))
	target_svc_S = filter_invalid_svctags_URL(search_expried_svc_S, dell_support_url, logger).union(valid_S)
	invalid_count = len(all_svc_S) - len(target_svc_S)
	if invalid_count < len(all_svc_S):
		logger.info("Filter out %s invalid, and combine with those valid as target svctags" % invalid_count)
		update_valid_svc_L = list(target_svc_S.union(history_valid_svc_S).union(history_dellasset_S))
		save_object_to_path(value=update_valid_svc_L, output_path=history_valid_svctag_path)
	else:
		logger.warn("No target svctags in this job")
	logger.info("Update %s new valid svctags" % (len(all_svc_S) - invalid_count))
	return svctags_flatten(valid_svc_L=list(target_svc_S)), existing_S

