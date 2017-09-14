# -*- coding: utf-8 -*-
import sys, xlsxwriter
from entity import Warranty, DellAsset
from utility import list_file_name_in_dir

reload(sys)
sys.setdefaultencoding('utf8')

def save_dell_asset_excel(output_dell_asset_L, dell_asset_output_path):
    wbk = xlsxwriter.Workbook(filename=dell_asset_output_path)
    sheet = wbk.add_worksheet('sheet1')
    row = 0
    col = 0
    while col < DellAsset.header_num:
        sheet.write(row, col, DellAsset.header_L[col])
        col += 1
    while col < DellAsset.header_num + Warranty.header_num:
        sheet.write(row, col, Warranty.header_L[col - DellAsset.header_num])
        col += 1
    row = 1
    for da in output_dell_asset_L:
        col = 0
        for h in da.get_da_header():
            sheet.write(row, col, h)
            col += 1
        w_L = da.get_warranty()
        if w_L is not None and len(w_L) > 0:
            for w in w_L:
                for h in w.get_w_header():
                    sheet.write(row, col, h)
                    col += 1
                col = DellAsset.header_num
                row += 1
            row += 1
    wbk.close()
    return True

def txt_to_excel_batch(txt_file_path, excel_output_path):
    txt_file_path = "/Users/Kun/Desktop/excel2/"
    excel_output_path = "/Users/Kun/Desktop/?_?_?_B_K_7_2.xlsx"
    target_svc_S = set(list_file_name_in_dir(input_path=txt_file_path))
    dell_asset_L = DellAsset.parse_dell_asset_file_batch(txt_file_path, target_svc_S)
    return save_dell_asset_excel(dell_asset_L, excel_output_path)