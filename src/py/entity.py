# -*- coding: utf-8 -*-

from constant import history_DA_file_format
from utility import read_file, parse_str_date

class Warranty(object):
	header = "保修服务(英),保修服务(中),开始日期,结束日期,提供商"
	def __init__(self, start_date, end_date, service_en, is_provider, service_ch=None):
		self.start_date = start_date
		self.end_date = end_date
		self.service_en = service_en
		self.is_provider = is_provider
		self.set_service_ch(service_ch)
	def __repr__(self):
		start_D = parse_str_date(self.start_date)
		end_D = parse_str_date(self.end_date)
		return "%s,%s,%s,%s,%s" % (self.service_en, self.service_ch, start_D, end_D, self.is_provider)
	def set_service_ch(self, service_ch):
		self.service_ch = service_ch
		if self.service_ch is not None:
			self.service_ch = self.service_ch.encode('utf-8')

class DellAsset(object):
	header = "机器型号,服务标签,发货日期"
	def __init__(self, machine_id, svctag, ship_date, warranty_L):
		self.machine_id = machine_id
		self.svctag = svctag
		self.ship_date = ship_date
		self.warranty_L = warranty_L
	def __repr__(self):
		dell_asset = "%s,%s\n%s,%s,%s" % (DellAsset.header, Warranty.header, self.machine_id, self.svctag, parse_str_date(self.ship_date))
		if len(self.warranty_L) > 0:
			dell_asset += "," + str(self.warranty_L[0]) + "\n"
			for w in xrange(1, len(self.warranty_L)):
				dell_asset += ",,," + str(self.warranty_L[w]) + "\n"
		return dell_asset
	def set_machine_id(self, machine_id):
		self.machine_id = machine_id
	def set_ship_date(self, ship_date):
		self.ship_date = ship_date
	def set_svctag(self, svctag):
		self.svctag = svctag
	def set_warranty_L(self, warranty_L):
		self.warranty_L = warranty_L
	def get_warranty(self):
		return self.warranty_L
	@staticmethod
	def load_dell_asset(dell_asset_path, history_svc_S):
		for svc in history_svc_S:
			da_full_name = dell_asset_path + svc + history_DA_file_format
			lines = read_file(da_full_name, isYML=False, isURL=False).split('\n')
			da_header_num = len(DellAsset.header.split(','))
			da_header_L = lines[1].split(',')[0:da_header_num]
			warranty_L = lines[1].split(',')[da_header_num:]
			da = DellAsset(da_header_L[0], da_header_L[1], da_header_L[2], warranty_L)

				
		return []


# w1 = Warranty("2013-12-22T17:59:59", "2013-12-22T17:59:59","ABC", "DELL")
