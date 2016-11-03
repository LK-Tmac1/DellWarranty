import re
from constant import svc_delimitor, existing_dell_asset_dir, parent_path, file_config_name, config_translation_url, svc_placeholder
from utility import check_letter_valid, list_file_name_in_dir, read_file, get_current_datetime, save_object_to_path
from entity import DellAsset
from translate import update_dell_warranty_translation

def compile_svc_pattern(svctags):
    if svctags is not None and svctags != "": 
        svc_pattern = ""
        for svc in svctags.split(svc_delimitor):
            if not check_letter_valid(svc):
                svc = "."
            svc_pattern += svc
        return re.compile(svc_pattern)
    return None

def search_existing_dell_asset(svctags, update_translation=True):
    result = []
    possible_file_count = 0
    for s in svctags:
        if s == svc_placeholder:
            possible_file_count += 1
    possible_file_count = 36 ** possible_file_count
    pattern = compile_svc_pattern(svctags)
    if pattern is not None:
        existing_dell_asset_svctags = list_file_name_in_dir(existing_dell_asset_dir)
        target_dell_asset_S = set([])
        target_count = 0
        for svc in existing_dell_asset_svctags:
            if pattern.match(svc):
                target_dell_asset_S.add(svc)
                target_count += 1
            if target_count == possible_file_count:
                break
        result = DellAsset.parse_dell_asset_file_batch(existing_dell_asset_dir, target_dell_asset_S, logger=None)
    if update_translation:
        config = read_file(parent_path + file_config_name, isYML=True, isURL=False)
        result = update_dell_warranty_translation(config[config_translation_url] , result, existing_dell_asset_dir)[0]
    return result


def sort_dell_asset_svctag(dell_asset_L):
    if dell_asset_L is not None:
        dell_asset_L.sort()
        return dell_asset_L
    return []

def update_search_history(search_history_path, new_search_svctags_S):
    existing_search_dict = read_file(search_history_path, isYML=True, isURL=False)
    new_search_dict = {}
    current_date = get_current_datetime(is_format=False, is_date=True)
    for svc in new_search_svctags_S:
        if svc is not None and svc != "":
            new_search_dict[svc] = current_date
    existing_search_dict.update(new_search_dict)
    return save_object_to_path(existing_search_dict, search_history_path, isYML=True)

# search_history_path = "/Users/Kun/dell/search_history.yml"
# new_search_svctags_S = set(["ABCD???", "ABC?111", "ACSDAWW"])
# update_search_history(search_history_path, new_search_svctags_S)
