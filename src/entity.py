from dateutil.parser import parse
from datetime import datetime


class Warranty(object):
	header = "保修服务,开始日期,结束日期,提供商"
	def __init__(self, start_date, end_date, service_en, is_provider, service_ch=None):
		self.start_date = start_date
		self.end_date = end_date
		self.service_en = service_en
		self.is_provider = True if str(is_provider).lower() == 'true' else False
		self.service_ch = service_ch
	def __repr__(self):
		start_D = parse(self.start_date)
		end_D = parse(self.end_date)
		temp = "%s,%s年%s月%s日,%s年%s月%s日," % (self.service_ch,start_D.year, start_D.month, start_D.day, end_D.year, end_D.month, end_D.day)
		return temp + "DELL" if self.is_provider else temp + "其它"

class DellAsset(object):
	header = "机器型号,服务标签,发货日期"
	def __init__(self, machine_id, svctag, ship_date, warranty_L):
		self.machine_id = machine_id
		self.svctag = svctag
		self.ship_date = ship_date
		self.warranty_L = warranty_L
	def __repr__(self):
		ship_D = parse(self.ship_date)
		dell_asset = DellAsset.header + "," + Warranty.header + "\n"
		dell_asset += "%s,%s,%s年%s月%s日" %(self.machine_id,self.svctag,ship_D.year,ship_D.month,ship_D.day)
		if len(self.warranty_L) > 0:
			dell_asset += "," + str(self.warranty_L[0]) + "\n"
			for w in xrange(1, len(self.warranty_L)):
				dell_asset += ",,,"+str(self.warranty_L[w]) + "\n"
		return dell_asset
	def get_warranty(self):
		return self.warranty_L
