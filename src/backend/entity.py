# -*- coding: utf-8 -*-
from utility import read_file, parse_str_date, save_object_to_path, is_path_existed
from constant import history_DA_file_format, service_ch_placeholder


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

    def get_start_date(self):
        return parse_str_date(self.start_date)

    def get_end_date(self):
        return parse_str_date(self.end_date)

    def get_w_header(self):
        return [self.service_en, self.service_ch,
                self.get_start_date(), self.get_end_date(), self.is_provider]

    def __repr__(self):
        return "%s,%s,%s,%s,%s" % (self.service_en, self.service_ch,
                                   self.get_start_date(), self.get_end_date(), self.is_provider)


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
        self.warranty_L = warranty_L
        self.is_translation_updated = False

    def get_ship_date(self):
        return parse_str_date(self.ship_date)

    def get_da_header(self):
        return [self.machine_id, self.svctag, self.get_ship_date()]

	def __repr__(self):
		dell_asset = "%s,%s\n" % (DellAsset.header, Warranty.header)
		dell_asset += "%s,%s,%s" % (self.machine_id, self.svctag, self.get_ship_date())
		if len(self.warranty_L) > 0:
			dell_asset += "," + str(self.warranty_L[0]) + "\n"
			for w in xrange(1, len(self.warranty_L)):
				dell_asset += "," * DellAsset.header_num + str(self.warranty_L[w]) + "\n"
		else:
			dell_asset += "," * Warranty.header_num
		return dell_asset
	def set_warranty_L(self, warranty_L):
		self.warranty_L = warranty_L
	def get_warranty(self):
		return self.warranty_L
	def __lt__(self, other):
		return self.svctag < other.svctag
	@staticmethod
	def parse_dell_asset_file(dell_asset_path):
		lines = read_file(dell_asset_path, isYML=False, isURL=False, lines=True)
		if lines is not None and len(lines) > 1:
			da = DellAsset(dellasset_str=','.join(lines[1].split(',')[0:DellAsset.header_num]))
			warranty_L = []
			for i in xrange(1, len(lines)):
				if lines[i] != "":
					warranty_L.append(Warranty(warranty_str=','.join(lines[i].split(',')[DellAsset.header_num:])))
			da.set_warranty_L(warranty_L)
			return da
		else:
			return None
	@staticmethod
	def parse_dell_asset_file_batch(dell_asset_path, target_svc_S, file_format=history_DA_file_format, logger=None):
		# Parse dell asset object with target svctag from files in the dell_asset_path
		# Each file contains a single dell asset object
		da_L = []
		for svc in target_svc_S:
			path = "%s%s%s" % (dell_asset_path, svc, file_format)
			da = DellAsset.parse_dell_asset_file(path)
			if da is not None:
				da_L.append(da)
			elif logger is not None:
				logger.error("Parsing dell asset of %s failed" % path)
		return da_L
	@staticmethod
	def parse_dell_asset_multiple(dell_asset_multiple_path):
		# Parse multiple dell asset object in a single path
		da_L = []
		lines = read_file(dell_asset_multiple_path, isYML=False, isURL=False, lines=True)
		if lines is not None:
			i = 0
			while i < len(lines):
				while  i < len(lines) and (lines[i] == "" or lines[i].find(DellAsset.header) == 0):
					i += 1
				if  i < len(lines):
					da = DellAsset(dellasset_str=','.join(lines[i].split(',')[0:DellAsset.header_num]))
					warranty_L = []
					while i < len(lines) and lines[i] != "" and lines[i].find(DellAsset.header) < 0:
						new_w = Warranty(warranty_str=','.join(lines[i].split(',')[DellAsset.header_num:]))
						warranty_L.append(new_w)
						i += 1
					da.set_warranty_L(warranty_L)
					da_L.append(da)
		return da_L
	@staticmethod
	def parse_dell_asset_multiple_batch(dell_asset_multiple_path, output_path):
		output_dell_asset_L = DellAsset.parse_dell_asset_multiple(dell_asset_multiple_path)
		for da in output_dell_asset_L:
			if da is not None and da.svctag != "":
				temp_path = output_path + da.svctag + history_DA_file_format
				save_object_to_path(value=da, output_path=temp_path)
		# print len(output_dell_asset_L), "results generated"
