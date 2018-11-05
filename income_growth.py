from __future__ import division
import pandas as pd
import pd_util as pdu
import scoretool as st
import openpyxl,math
import dimension


sourceHeader = [
        '日期', '应用名称', '应用ID', 'AP代码', 'AP名称', '前日订购人数', '前日订单数', '前日金额','当日订购人数', '当日订单数', '当日金额'
    ]

def create_from_excel(file_name):
    table = pd.read_excel(file_name, sheet_name='全国', header=1)
    table.columns = sourceHeader
    return IncomeGrowth(table)

class IncomeGrowth(dimension.Dimension):

    def __init__(self,source_table,showTempInfo=False):
        dimension.Dimension.__init__(self,source_table,showTempInfo)
        self.name = '收入异增'
        self.condition_income = 5000
        self.output_header = ['日期', '应用名称', '应用ID', 'AP代码', 'AP名称','环比增长率','收入异增评分']

    def start(self):
        self.data_clean().data_handle().data_analysis()

    def data_clean(self):
        self.table = self.table.drop_duplicates()
        return self

    def data_handle(self):
        table = self.table
        table['环比增长率'] = (table['当日金额'] - table['前日金额']) / table['前日金额']
        self.table = table
        return self

    def data_analysis(self):
        self.table['收入异增评分'] = self.table[self.table['前日金额'] >= self.condition_income]['环比增长率'].apply(lambda x : self.__score_proportion(x))
        self.ep_table = self.table[self.table['收入异增评分'] > 0].copy()
    
    #环比增长率评分
    def __score_proportion(self, x):
        score = st.score_add(x, st.points_income_growth)
        return score 
    
  