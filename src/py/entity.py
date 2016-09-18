# -*- coding: utf-8 -*-

from constant import history_DA_file_format, service_ch_placeholder
from utility import read_file, parse_str_date, save_object_to_path, is_path_existed
import sys  

reload(sys)
sys.setdefaultencoding('utf8')

class Warranty(object):
	header = "保修服务(英),保修服务(中),开始日期,结束日期,提供商"
	header_num = len(header.split(","))
	def __init__(self, start_date="", end_date="", service_en="", is_provider="", service_ch=None, warranty_str=None):
		if warranty_str is None:
			self.start_date = start_date
			self.end_date = end_date
			self.service_en = service_en
			self.is_provider = is_provider
			self.set_service_ch(service_ch)
		else:
			L = warranty_str.split(',')
			self.service_en = L[0] if len(L) > 0 else ""
			self.set_service_ch(L[1] if len(L) > 1 else "")
			self.start_date = L[2] if len(L) > 2 else ""
			self.end_date = L[3] if len(L) > 3 else ""
			self.is_provider = L[4] if len(L) > 4 else ""
			# Used for de-serailzation of warranty from .csv files
	def __repr__(self):
		start_D = parse_str_date(self.start_date)
		end_D = parse_str_date(self.end_date)
		return "%s,%s,%s,%s,%s" % (self.service_en, self.service_ch, start_D, end_D, self.is_provider)
	def set_service_ch(self, service_ch):
		if service_ch is not None and service_ch != "" and service_ch != "None":
			self.service_ch = service_ch.encode('utf-8')
		else:
			self.service_ch = service_ch_placeholder


class DellAsset(object):
	header = "机器型号,服务标签,发货日期"
	header_num = len(header.split(","))
	def __init__(self, machine_id="", svctag="", ship_date="", warranty_L=None, dellasset_str=None):
		if dellasset_str is None:
			self.machine_id = machine_id
			self.svctag = svctag
			self.ship_date = ship_date
			self.warranty_L = warranty_L
		else:
			L = dellasset_str.split(',')
			self.machine_id = L[0] if len(L) > 0 else ""
			self.svctag = L[1] if len(L) > 1 else ""
			self.ship_date = L[2] if len(L) > 2 else ""
			self.warranty_L = []
			# Used for de-serailzation of dell asset from .csv files
		self.is_translation_updated = False
	def __repr__(self):
		dell_asset = "%s,%s\n" % (DellAsset.header, Warranty.header)
		dell_asset += "%s,%s,%s" % (self.machine_id, self.svctag, parse_str_date(self.ship_date))
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
	@staticmethod
	def save_dell_asset_to_file(dell_asset_L, parent_path, logger):
		for da in dell_asset_L:
			output_path = "%s%s%s" % (parent_path, da.svctag, history_DA_file_format)
			if is_path_existed:
				# If output exists, check if necessary to overwrite the dell asset
				if da.is_translation_updated:
					save_object_to_path([str(da)], output_path)
					logger.info("######Update %s as existing dell asset" % da.svctag)
			else:
				# If there is no such output path, can only save it
				save_object_to_path([str(da)], output_path)
				logger.info("######Save %s as existing dell asset" % da.svctag)
	@staticmethod
	def parse_dell_asset_file(dell_asset_path):
		lines = read_file(dell_asset_path, isYML=False, isURL=False).split('\n')
		if len(lines) > 1:
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
	def parse_dell_asset_file_batch(dell_asset_path, target_svc_S, logger=None):
		da_L = []
		for svc in target_svc_S:
			path = "%s%s%s" % (dell_asset_path, svc, history_DA_file_format)
			if logger is not None:
				logger.info("Read and parse dell asset of " + svc)
			da = DellAsset.parse_dell_asset_file(path)
			if da is not None:
				da_L.append(da)
			elif logger is not None:
				logger.error("Parsing dell asset of %s failed" % path)
		return da_L
