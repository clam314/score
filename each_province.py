from __future__ import division
import pandas as pd
import openpyxl, time,math
import pd_util as pdu
import dimension
import scoretool as st

sourceHeader = [
        '日期', '省份', '应用名称', '应用ID', 'AP代码', 'AP名称', '前日订购人数', '前日订单数',
        '前日计费金额', '当日订购人数', '当日订单数', '当日计费金额'
    ]

incomeHeader = [
        '日期', '应用名称', '应用ID', 'AP代码', 'AP名称', '前日订购人数', '前日订单数', '前日金额',
        '当日订购人数', '当日订单数', '总金额'
    ]

def create_from_excel(file_name,ref_file_name):
    table = pd.read_excel(file_name, sheet_name='分省分应用流水', header=1)
    table.columns = sourceHeader
    income_table = pd.read_excel(ref_file_name,sheet_name='全国', header=1)
    income_table.columns = incomeHeader
    return ProvinceIncome(table, income_table)

class ProvinceIncome(dimension.Dimension):

    def __init__(self,source_table,income_table,showTempInfo=False):
        dimension.Dimension.__init__(self,source_table,showTempInfo)
        self.name = '分省集中度'
        self.condition_income = 5000
        self.income_table = income_table
        self.income_table[self.index] = self.income_table[['日期','应用ID']].apply(lambda x: '%s&%s' % (x[0],x[1]),axis = 1)
        self.output_header = ['日期', '应用名称', '应用ID', 'AP代码', 'AP名称','计费省份个数','TOP省份占比',"分省评分"]
        print(self.income_table.head())
        print(self.table.head())

    def start(self):
        self.data_clean().data_handle().data_analysis()

    def data_clean(self):
        self.table = self.table.drop_duplicates()
        self.table = self.table[(self.table['省份'] != '未知') & (self.table['当日计费金额'] > 0)]
        return self

    def data_handle(self):
        table = self.table
        #通关匹配当日收入最大值类选出收入最高的省份
        max_tb = pdu.get_tb_after_groupby(table, self.index, '当日计费金额', 'max', 'MAX金额')
        max_tb = pdu.vlookup(table, max_tb, self.index)
        max_tb = max_tb[max_tb['当日计费金额'] == max_tb['MAX金额']].drop(['MAX金额'], axis=1)
        #求省份个数
        count_tb = pdu.get_tb_after_groupby(table, self.index, '省份', 'count', '计费省份个数')
        max_tb = pdu.vlookup(max_tb, count_tb, self.index)
        #匹配总收入
        max_tb = pdu.vlookup(max_tb, self.income_table[[self.index,'总金额']], self.index)
        max_tb = max_tb[max_tb['总金额'] > 0]
        max_tb['TOP省份占比'] = max_tb['当日计费金额'] / max_tb['总金额']
        self.table = max_tb
        return self

    def data_analysis(self):
        self.table['分省评分'] = self.table[self.table['总金额'] >= self.condition_income][['计费省份个数','TOP省份占比']].apply(lambda x: self.__score_proportion(x),axis = 1)
        self.ep_table = self.table[self.table['分省评分']>0]
        return self
    
   
    def __score_proportion(self, x):
        score = 0
        num = x[0]
        p = x[1]
        if num >= 5 and num <= 6 :
            score = st.score_add(p,st.points_province_5_6)
        elif num >= 7 and num <= 9:
            score = st.score_add(p,st.points_province_7_9)
        elif num >= 10 and num <= 13:
            score = st.score_add(p,st.points_province_10_13)
        elif num >= 14 and num <= 18:
            score = st.score_add(p,st.points_province_14_18)
        elif num >= 19 and num <= 31:
            score = st.score_add(p,st.points_province_19_31)
        return score 

