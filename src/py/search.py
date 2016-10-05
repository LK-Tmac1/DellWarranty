import re
from constant import svc_delimitor, existing_dell_asset_dir
from utility import check_letter_valid, list_file_name_in_dir, read_file, get_current_datetime, save_object_to_path
from entity import DellAsset

def compile_svc_pattern(svctags):
    if svctags is not None and svctags != "": 
        svc_pattern = ""
        for svc in svctags.split(svc_delimitor):
            if not check_letter_valid(svc):
                svc = "."
            svc_pattern += svc
        return re.compile(svc_pattern)
    return None

def search_existing_dell_asset(svctags):
    pattern = compile_svc_pattern(svctags)
    if pattern is not None:
        existing_dell_asset_svctags = list_file_name_in_dir(existing_dell_asset_dir)
        target_dell_asset_S = set([])
        for svc in existing_dell_asset_svctags:
            if pattern.match(svc):
                target_dell_asset_S.add(svc)
        return DellAsset.parse_dell_asset_file_batch(existing_dell_asset_dir, target_dell_asset_S, logger=None)
    else:
        return []

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

#search_history_path = "/Users/Kun/dell/search_history.yml"
#new_search_svctags_S = set(["ABCD???", "ABC?111", "ACSDAWW"])
#update_search_history(search_history_path, new_search_svctags_S)








