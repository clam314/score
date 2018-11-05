from __future__ import division
import pandas as pd
import pd_util as pdu
import scoretool as st
import openpyxl,math
import dimension

def create_from_excel(file_name):
    table = pd.read_excel(file_name, sheet_name='应用流水金额', header=1)
    return EhoursIncome(table)

class EhoursIncome(dimension.Dimension):

    def __init__(self,source_table,showTempInfo=False):
        dimension.Dimension.__init__(self,source_table,showTempInfo)
        self.name = '闲时集中度'
        self.condition_income = 1000
        self.output_header = ['日期', '应用名称', '应用ID', 'AP代码', 'AP名称','闲时占比','闲时评分']

    def start(self):
        self.data_clean().data_handle().data_analysis()

    def data_clean(self):
        self.table = self.table.drop_duplicates()
        return self

    def data_handle(self):
        table = self.table
        table['闲时收入'] = table[list(range(1, 6))].apply(lambda x: x.sum(), axis=1)
        table['总收入'] = table[list(range(0, 24))].apply(lambda x: x.sum(), axis=1)
        table['闲时占比'] = table['闲时收入'] / table['总收入']
        self.table = table
        return self

    def data_analysis(self):
        self.table['闲时评分'] = self.table[self.table['总收入'] >= self.condition_income]['闲时占比'].map(lambda x: self.__score_proportion(x))
        self.ep_table = self.table[self.table['闲时评分']>0].copy()
    
   
    def __score_proportion(self, x):
        score = st.score_add(x, st.points_early_morning)
        return score 
    
  