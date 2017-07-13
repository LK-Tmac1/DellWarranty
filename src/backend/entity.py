# -*- coding: utf-8 -*-
from utility import parse_str_date
import xlsxwriter


class Warranty(object):
    def __init__(self, service_en, service_ch, start_date, end_date, is_provider):
        self.start_date = start_date
        self.end_date = end_date
        self.service_en = service_en
        self.is_provider = is_provider
        self.service_ch = service_ch

    def excel_data(self):
        return [self.service_en, self.service_ch,
                parse_str_date(self.start_date), parse_str_date(self.end_date), self.is_provider]

    def __repr__(self):
        return "%s,%s,%s,%s,%s" % (self.service_ch, self.service_en,
                                   self.start_date, self.end_date, self.is_provider)

    @staticmethod
    def deserialize_txt(warranty_line):
        if warranty_line:
            items = warranty_line.split(",")
            if len(items) >= 5:
                service_ch = items[1]
                service_en = items[0]
                start_date = items[2]
                end_date = items[3]
                is_provider = items[4]
                return Warranty(service_en, service_ch, start_date, end_date, is_provider)
        return None


class DellAsset(object):
    headers = "服务标签,机器型号,发货日期,保修(中),保修(英),开始日期,结束日期,提供商".split(",")

    def __init__(self, machine_id, svc_tag, ship_date, warranty_L=None):
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

    def __repr__(self):
        return "%s,%s,%s" % (self.svc_tag, self.machine_id, self.ship_date)

    def serialize_txt(self):
        contents = list([str(self)])
        for w in self.warranty_L:
            contents.append(str(w))
        return "\n".join(contents)

    @staticmethod
    def deserialize_txt(lines):
        if lines:
            items = lines[0].split(",")
            svc_tag, machine_id, ship_date = items[0], items[1], items[2]
            warranty_list = list([])
            for warranty_line in lines[1:]:
                warranty_list.append(Warranty.deserialize_txt(warranty_line))
            return DellAsset(machine_id, svc_tag, ship_date, warranty_list)

    @staticmethod
    def deserialize_csv(lines):
        # Used for de-serailzation of a dell asset from .csv files
        if not lines or len(lines) < 2:
            return None
        warranty_list = list([])
        for line in lines[1:]:
            line = line.split(",")[3:]
            warranty_line = ",".join(line)
            w = Warranty.deserialize_txt(warranty_line)
            if w:
                warranty_list.append(w)
        items = lines[1].split(",")
        if len(items) >= 3:
            machine_id, svc_tag, ship_date = items[0], items[1], items[2]
            return DellAsset(machine_id, svc_tag, ship_date, warranty_list)
        return None

    @staticmethod
    def save_dell_asset_to_excel(dell_asset_list, excel_output_path):
        wbk = xlsxwriter.Workbook(filename=excel_output_path)
        sheet = wbk.add_worksheet('sheet1')
        for i in xrange(len(DellAsset.headers)):
            sheet.write(0, i, DellAsset.headers[i])
        row = 1
        for da in dell_asset_list:
            col = 0
            for d in da.get_da_data():
                sheet.write(row, col, d)
                col += 1
            for w in da.get_warranty_list():
                for d in w.excel_data():
                    sheet.write(row, col, d)
                    col += 1
                col = DellAsset.header_num
                row += 1
            row += 1
        wbk.close()
        return True

