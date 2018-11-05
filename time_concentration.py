from __future__ import division
import pandas as pd
import pd_util as pdu
import scoretool as st
import openpyxl,math
import dimension

def create_from_excel(file_name, ref_file_name):
    table = pd.read_excel(file_name, sheet_name='应用流水金额', header=1)
    mb_table = pd.read_excel(ref_file_name)
    return FocusTime(table,mb_table)

class FocusTime(dimension.Dimension):

    def __init__(self,source_table,mb_table,showTempInfo=False):
        dimension.Dimension.__init__(self,source_table,showTempInfo)
        self.name = '时间集中度'
        self.condition_income = 1000
        self.mb_table = mb_table
        self.mb_table[self.sec_index] = self.mb_table[self.sec_index].map(lambda x : str(x))
        self.output_header = ['日期', '应用名称', '应用ID', 'AP代码', 'AP名称','TOP6小时占比','时间段评分']

    def start(self):
        self.data_get().data_clean().data_handle().data_analysis()

    def data_get(self):
        self.table = pdu.vlookup(self.table,self.mb_table[[self.sec_index, "计费点类型"]], self.sec_index)
        self.table['计费点类型'] = self.table['计费点类型'].map( lambda x: x if x == '包时长' else '非包时长')
        return self

    def data_clean(self):
        self.table = self.table.drop_duplicates()
        return self

    def data_handle(self):
        table = self.table
        time_frame = list(range(0, 24))
        table['TOP6小时'] = table[time_frame].apply(lambda x: x.sort_values(ascending=False)[0:6].sum(), axis=1)
        table['总收入'] = table[time_frame].apply(lambda x: x.sum(), axis=1)
        table['TOP6小时占比'] = table['TOP6小时'] / table['总收入']
        self.table = table
        return self

    def data_analysis(self):
        self.table['时间段评分'] = self.table[(self.table['计费点类型'] != '包时长') & (self.table['总收入'] >= self.condition_income)]['TOP6小时占比'].map(lambda x: self.__score_proportion(x))
        self.ep_table = self.table[self.table['时间段评分']>0].copy()
    
   
    def __score_proportion(self, x):
        score = st.score_add(x, st.points_time_concentration)
        return score 
    
  