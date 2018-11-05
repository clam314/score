from __future__ import division
import pandas as pd
import pd_util as pdu
import scoretool as st
import openpyxl,math

sourceHeader = [
        '日期', '应用ID','应用名称', 'AP代码', 'AP名称', 
        "当日总订购人数" , "当日总订购次数", "当日总订购金额",
        "弱联网订购人数","弱联网订购次数","弱联网订购金额",
        "强联网订购人数","强联网订购次数","强联网订购金额",
        "位置校验异常人数","位置校验异常次数","位置校验异常金额",
        "跨应用拦截人数","跨应用拦截次数","跨应用拦截金额",
        "强联网计费成功用户数","强联网计费成功设备数","有埋点用户数","有埋点设备数"
    ]

output_index = 'INDEX'

# output_statistics_header = [output_index,'日期', '应用ID','应用名称', 'AP代码', 'AP名称']
output_statistics_header = [output_index,'日期', '应用ID','应用名称', 'AP名称']

class Dimension(object):
    
    def __init__(self, source_table, showTempInfo=False):
        self.name = ''
        self.condition_income = 0
        self.condition_num = 0
        self.table = source_table
        self.ep_table = pd.DataFrame()
        self.show = showTempInfo
        self.index = output_index
        self.sec_index = '应用ID'
        self.table[['日期','应用ID']] = self.table[['日期','应用ID']].applymap(lambda x : '%.0f' % x)
        self.table[self.sec_index] = self.table[self.sec_index].map(lambda x : str(x))
        self.table[self.index] = self.table[['日期','应用ID']].apply(lambda x: '%s&%s' % (x[0],x[1]),axis = 1)
        self.output_header = []

    

    def print_table(self,excelWriter):
        self.table.to_excel(excelWriter, encoding='utf-8', sheet_name=self.name, index=False)

    def print_exception_table(self,excelWriter):
        self.ep_table.to_excel(excelWriter, encoding='utf-8', sheet_name=self.name, index=False)

    def outTable(self):
        return self.ep_table[self.getOutputHeader()].copy()

    def outAllTable(self):
        return self.table[self.getOutputHeader()].copy()

    def getOutputHeader(self):
        return [self.index] + self.output_header