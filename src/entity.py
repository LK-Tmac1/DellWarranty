# -*- coding: utf-8 -*-

from utility import DateTimeUtil, FileUtil
import xlsxwriter, os
import sys

reload(sys)
sys.setdefaultencoding('utf8')
translation_url = "https://raw.githubusercontent.com/liukun1016/DellWarranty/master/translation.yml"


class Warranty(object):
    translation = FileUtil.read_file(file_path=translation_url, isYML=True, isURL=True)

    def __init__(self, service_en, start_date, end_date, provider, service_ch=None):
        self.start_date = DateTimeUtil.parse_str_date(start_date)
        self.end_date = DateTimeUtil.parse_str_date(end_date)
        self.service_en = str(service_en)
        self.service_en.replace(",", " ")
        self.provider = provider
        self.service_ch = service_ch
        if not service_ch or service_ch == "?":
            self.service_ch = Warranty.translation.get(service_en, "?")

    def to_excel_data(self):
        return [self.service_ch, self.service_en, self.start_date,self.end_date, self.provider]

    def __repr__(self):
        return "%s,%s,%s,%s,%s" % (self.service_ch,self.service_en,self.start_date,self.end_date,self.provider)

    @staticmethod
    def deserialize_txt(warranty_line):
        if warranty_line:
            items = warranty_line.split(",")
            if len(items) >= 5:
                if items[1] or items[0]:
                    return Warranty(service_ch=items[0], service_en=items[1],
                                    start_date=items[2], end_date=items[3], provider=items[4])
        return None


class DellAsset(object):
    headers = "服务标签,机器型号,发货日期,保修(中),保修(英),开始日期,结束日期,提供商".split(",")

    def __init__(self, machine_id, svc_tag, ship_date, warranty_list=None):
        self.machine_id = str(machine_id).replace(",", " ")
        self.svc_tag = svc_tag
        self.ship_date = DateTimeUtil.parse_str_date(ship_date)
        self.warranty_list = warranty_list if warranty_list else list([])
        self.is_translation_updated = False

    def to_excel_data(self):
        return [self.svc_tag, self.machine_id, self.ship_date]

    def add_warranty(self, warranty):
        if warranty:
            self.warranty_list.append(warranty)

    def __repr__(self):
        return "%s,%s,%s" % (self.svc_tag, self.machine_id, self.ship_date)

    def serialize_txt(self):
        contents = list([self.__repr__()])
        for w in self.warranty_list:
            contents.append(w.__repr__())
        return "\n".join(contents)

    @staticmethod
    def serialize_txt_batch(dell_asset_list, output_dir):
        # Serialize each dell asset as one text file under the output directory
        # Return all the output file names under the dir in a list for reference
        output_path_list = list([])
        for da in dell_asset_list:
            file_name = "%s.txt" % da.svc_tag
            output_path_list.append(os.path.join(output_dir, file_name))
            FileUtil.save_object_to_path(da.serialize_txt(), output_path_list[-1])
        return output_path_list

    @staticmethod
    def deserialize_txt(text_content):
        lines = text_content.split("\n")
        if lines:
            items = lines[0].split(",")
            if len(items) >= 3:
                svc_tag, machine_id, ship_date = items[0], items[1], items[2]
                warranty_list = list([])
                for warranty_line in lines[1:]:
                    warranty = Warranty.deserialize_txt(warranty_line)
                    if warranty:
                        warranty_list.append(warranty)
                return DellAsset(machine_id, svc_tag, ship_date, warranty_list)
        return None

    @staticmethod
    def save_as_excel_batch(dell_asset_list, excel_output_path):
        wbk = xlsxwriter.Workbook(filename=excel_output_path)
        sheet = wbk.add_worksheet('sheet1')
        for i in xrange(len(DellAsset.headers)):
            sheet.write(0, i, DellAsset.headers[i])
        row = 1
        for da in dell_asset_list:
            if da:
                col = 0
                for d in da.to_excel_data():
                    sheet.write(row, col, d)
                    col += 1
                if not da.warranty_list:
                    row += 1
                for w in da.warranty_list:
                    for d in w.to_excel_data():
                        sheet.write(row, col, d)
                        col += 1
                    col = 3
                    row += 1
                row += 1
        wbk.close()
        return True
