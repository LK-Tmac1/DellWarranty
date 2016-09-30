import re
from constant import svc_delimitor, existing_dell_asset_dir
from utility import check_letter_valid, list_file_name_in_dir
from entity import DellAsset

def search_existing_dell_asset(svctags):
    if svctags is not None and svctags != "": 
        svc_pattern = ""
        for svc in svctags.split(svc_delimitor):
            if not check_letter_valid(svc):
                svc = "."
            svc_pattern += svc
        pattern = re.compile(svc_pattern)
        existing_dell_asset_svctags = list_file_name_in_dir(existing_dell_asset_dir)
        target_dell_asset_S = set([])
        for da in existing_dell_asset_svctags:
            if pattern.match(da):
                target_dell_asset_S.add(da)
        return DellAsset.parse_dell_asset_file_batch(existing_dell_asset_dir, target_dell_asset_S, logger=None)
    else:
        return []

def sort_dell_asset_svctag(dell_asset_L):
    if dell_asset_L is not None:
        dell_asset_L.sort()
        return dell_asset_L
    return []

def search_history_unexpired(svc_S, search_history_path, date_offset):
    result_S = set([])
    return result_S
    