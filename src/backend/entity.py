# -*- coding: utf-8 -*-
from utility import parse_str_date
import xlsxwriter


class Warranty(object):
    header = "保修服务(英),保修服务(中),开始日期,结束日期,提供商"
    header_L = header.split(",")
    header_num = len(header_L)

    @staticmethod
    def init_warranty_string(warranty_str):
        # Used for de-serailzation of warranty from .csv files
        L = warranty_str.split(',')
        service_en = L[0] if len(L) > 0 else ""
        service_ch = L[1] if len(L) > 1 else ""
        start_date = L[2] if len(L) > 2 else ""
        end_date = L[3] if len(L) > 3 else ""
        is_provider = L[4] if len(L) > 4 else ""
        return Warranty(start_date, end_date, service_en, is_provider, service_ch)

    def __init__(self, start_date, end_date, service_en, is_provider, service_ch):
        self.start_date = start_date
        self.end_date = end_date
        self.service_en = service_en
        self.is_provider = is_provider
        self.service_ch = service_ch.encode('utf-8')

    def get_start_date_str(self):
        return parse_str_date(self.start_date)

    def get_end_date_str(self):
        return parse_str_date(self.end_date)

    def get_w_header(self):
        return [self.service_en, self.service_ch,
                self.get_start_date_str(), self.get_end_date_str(), self.is_provider]

    def __repr__(self):
        return "%s,%s,%s,%s,%s" % (self.service_en, self.service_ch,
                                   self.get_start_date_str(), self.get_end_date_str(), self.is_provider)


class DellAsset(object):
    header = "机器型号,服务标签,发货日期"
    header_L = header.split(",")
    header_num = len(header_L)

    @staticmethod
    def init_dell_asset_string(dellasset_str):
        # Used for de-serailzation of dell asset from .csv files
        L = dellasset_str.split(',')
        machine_id = L[0] if len(L) > 0 else ""
        svc_tag = L[1] if len(L) > 1 else ""
        ship_date = L[2] if len(L) > 2 else ""
        return DellAsset(machine_id, svc_tag, ship_date, None)

    def __init__(self, machine_id="", svc_tag="", ship_date="", warranty_L=None):
        self.machine_id = machine_id
        self.svc_tag = svc_tag
        self.ship_date = ship_date
        self.warranty_L = warranty_L if warranty_L else list([])
        self.is_translation_updated = False

    def get_ship_date_str(self):
        return parse_str_date(self.ship_date)

    def get_da_header(self):
        return [self.machine_id, self.svc_tag, self.get_ship_date_str()]

    def add_warranty(self, warranty):
        if warranty:
            self.warranty_L.append(warranty)

    def get_warranty_list(self):
        return self.warranty_L

    @staticmethod
    def save_dell_asset_to_excel(dell_asset_list, excel_output_path):
        wbk = xlsxwriter.Workbook(filename=excel_output_path)
        sheet = wbk.add_worksheet('sheet1')
        col = 0
        while col < DellAsset.header_num:
            sheet.write(0, col, DellAsset.header_L[col])
            col += 1
        while col < DellAsset.header_num + Warranty.header_num:
            sheet.write(0, col, Warranty.header_L[col - DellAsset.header_num])
            col += 1
        row = 1
        for da in dell_asset_list:
            col = 0
            for h in da.get_da_header():
                sheet.write(row, col, h)
                col += 1
            for w in da.get_warranty_list():
                for h in w.get_w_header():
                    sheet.write(row, col, h)
                    col += 1
                col = DellAsset.header_num
                row += 1
            row += 1
        wbk.close()
        return True

