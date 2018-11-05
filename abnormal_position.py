from __future__ import division
import pandas as pd
import pd_util as pdu
import scoretool as st
import openpyxl,math
import dimension

def create_from_excel(file_name):
    table = pd.read_excel(file_name, header=2)
    table.columns = dimension.sourceHeader
    return AbnormalPosition(table)

class AbnormalPosition(dimension.Dimension):

    def __init__(self,source_table,showTempInfo=False):
        dimension.Dimension.__init__(self,source_table,showTempInfo)
        self.name = '位置校验'
        self.condition_income = 1000
        self.condition_num = 30
        self.output_header = ['日期', '应用名称', '应用ID', 'AP代码', 'AP名称','位置异常率','位置评分']

    def start(self):
        self.data_clean().data_handle().data_analysis()

    def data_clean(self):
        self.table = self.table.drop_duplicates()
        return self

    def data_handle(self):
        self.table['位置异常率'] = self.table['位置校验异常次数'] / self.table['强联网订购次数']
        return self

    def data_analysis(self):
        self.table['位置评分'] = self.table[(self.table['当日总订购金额']>=self.condition_income) & (self.table['强联网订购次数'] >= self.condition_num)]['位置异常率'].apply(lambda x : self.__score_proportion(x))
        self.ep_table = self.table[self.table['位置评分'] > 0].copy()
    
    def __score_proportion(self, x):
        score = st.score_add(x, st.points_abnormal_position)
        return score 
    
  