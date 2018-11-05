from __future__ import division
import pandas as pd
import pd_util as pdu
import scoretool as st
import openpyxl,math
import dimension

def create_from_excel(file_name,ref_file_name):
    table = pd.read_excel(file_name, sheet_name='应用流水金额', header=1)
    mb_table = pd.read_excel(ref_file_name)
    return ZeroHours(table,mb_table)

class ZeroHours(dimension.Dimension):

    def __init__(self,source_table,mb_table,showTempInfo=False):
        dimension.Dimension.__init__(self,source_table,showTempInfo)
        self.name = '零收入小时'
        self.condition_income = 1000
        self.mb_table = mb_table
        self.mb_table[self.sec_index] = self.mb_table[self.sec_index].map(lambda x : str(x))
        self.output_header = ['日期', '应用名称', '应用ID', 'AP代码', 'AP名称','零小时个数','零小时数评分']

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
        table['总收入'] = table[list(range(0, 24))].apply(lambda x: x.sum(), axis=1)
        table['零小时个数'] = table[list(range(0, 24))].apply(lambda x: self.__count_zero(x), axis=1)
        self.table = table
        return self

    def data_analysis(self):
        self.table['零小时数评分'] = self.table[(self.table['计费点类型'] != '包时长') & (self.table['总收入'] >= self.condition_income)]['零小时个数'].map(lambda x: self.__score_proportion(x))
        self.ep_table = self.table[self.table['零小时数评分']>0].copy()
    
    def __count_zero(self,x):
        count = 0
        for c in x:
            if c == 0:
                count = count + 1
        return count

    def __score_proportion(self, x):
        score = st.score_add(x, st.points_0_income_hours)
        return score 
    
  