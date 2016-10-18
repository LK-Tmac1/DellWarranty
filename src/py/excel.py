# -*- coding: utf-8 -*-
import xlwt, sys
from entity import Warranty, DellAsset
reload(sys)
sys.setdefaultencoding('utf8')

def test():
    wbk = xlwt.Workbook(encoding="utf-8")
    sheet = wbk.add_sheet('sheet1')
    w = Warranty("Next Business Day", "下一工作日(服务)", "2015年5月29日", "2018年5月30日", "DELL")
    item_L = str(w).split(",")
    for i in xrange(0, len(item_L)):
        sheet.write(0, i, item_L[i])
        
    wbk.save("test.xls")

