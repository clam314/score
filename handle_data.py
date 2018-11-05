from __future__ import division
import pandas as pd
import openpyxl, time, os, re, configparser
import dimension,income_growth,time_concentration,early_morning,each_province,zero_hours,weak_network,buried_point,interception_rate,abnormal_position
import pd_util as pdu
import common_utils as cu

ref_dir = './reference/'
ref_file = ref_dir+'网页计费全量计费点（包时长）.xlsx'

config_path = ref_dir + r'/config.ini'

source_dir = './source/'

output_dir = './output/'
output_temp_ep_key = '各维度评分不为零的应用%s.xlsx'
output_temp_key = '应用各维度计算数据%s.xlsx'
output_key = '应用评分%s.xlsx'

printTempData = True
printTempEpData = False
printNoTotal = True

key1 = '平台室'
key2 = '能力部'

def printTempDataForOneSheet(sheets,timeStr):
    fileNameTemp = output_dir + output_temp_key % timeStr
    ew = pd.ExcelWriter(fileNameTemp)
    exp_tbs = list()
    [exp_tbs.append(s.outAllTable()) for s in sheets]
    statistics_header = dimension.output_statistics_header
    statistics_tb = exp_tbs[0][statistics_header]
    for i in range(1, len(exp_tbs)):
        statistics_tb = statistics_tb.append(exp_tbs[i][statistics_header])
    statistics_tb = statistics_tb.drop_duplicates()
    statistics_tb.reset_index(drop=True)
    for i in range(0, len(exp_tbs)):
        ll = [dimension.output_index] + sheets[i].getOutputHeader()[6:]
        statistics_tb = pdu.vlookup(statistics_tb, exp_tbs[i][ll],dimension.output_index)
    statistics_tb.to_excel(ew, encoding='utf-8', sheet_name='全量', index=False)
    ew.save()


def handle_excel(r_file_name,r_file_name_1,timeStr):
    sheets = createSheetsByDimension(r_file_name,r_file_name_1)
    
    #计算各维度数据
    [s.start() for s in sheets]

    #输出应用各维度计算数据
    if printTempData:
        # fileNameTemp = output_dir + output_temp_key % timeStr
        # ew = pd.ExcelWriter(fileNameTemp)
        # [s.print_table(ew) for s in sheets]
        # ew.save()
        printTempDataForOneSheet(sheets,timeStr)
    
    #输出各维度评分不为零的应用情况
    if printTempEpData:
        fileName1 = output_dir + output_temp_ep_key % timeStr
        ew = pd.ExcelWriter(fileName1)
        [s.print_exception_table(ew) for s in sheets]
        ew.save()
    
    if printNoTotal:
        return

    ##输出各个应用评分情况
    #汇总各应用各各维度评分
    exp_tbs = list()
    [exp_tbs.append(s.outTable()) for s in sheets]
    statistics_header = dimension.output_statistics_header
    statistics_tb = exp_tbs[0][statistics_header]
    for i in range(1, len(exp_tbs)):
        statistics_tb = statistics_tb.append(exp_tbs[i][statistics_header])
    statistics_tb = statistics_tb.drop_duplicates()
    statistics_tb.reset_index(drop=True)
    for i in range(0, len(exp_tbs)):
        ll = [dimension.output_index] + sheets[i].getOutputHeader()[6:]
        statistics_tb = pdu.vlookup(statistics_tb, exp_tbs[i][ll],dimension.output_index)
    #统计各应用总分
    score_list = list()
    for s in sheets:
        score_list.append(s.getOutputHeader()[-1])
    statistics_tb['评分维度数'] = statistics_tb[score_list].apply(lambda x : countDimension(x), axis=1)
    statistics_tb['评分'] = statistics_tb[score_list].apply(lambda x : x.sum(), axis=1)
    
    w_file_name = output_dir + output_key % timeStr
    s_ew = pd.ExcelWriter(w_file_name)
    statistics_tb.to_excel(s_ew, encoding='utf-8', sheet_name='评分', index=False)

    mb_table = pd.read_excel(ref_file)
    mb_table.to_excel(s_ew, encoding='utf-8', sheet_name="包时长列表", index=False)

    t_table = pd.read_excel(r_file_name, sheet_name='计费类型')
    t_table.to_excel(s_ew, encoding='utf-8', sheet_name="计费类型", index=False)

    s_ew.save()

#按维度创建sheet
def createSheetsByDimension(r_file_name,r_file_name_1):
    sheetList = list()
    #收入异增
    sheetList.append(income_growth.create_from_excel(r_file_name))
    #时间集中度
    sheetList.append(time_concentration.create_from_excel(r_file_name,ref_file))
    #闲时占比
    sheetList.append(early_morning.create_from_excel(r_file_name))
    #分省集中度
    sheetList.append(each_province.create_from_excel(r_file_name,r_file_name))
    #零收入小时数
    sheetList.append(zero_hours.create_from_excel(r_file_name,ref_file))
    #弱联网占比
    sheetList.append(weak_network.create_from_excel(r_file_name_1))
    #埋点采集率
    sheetList.append(buried_point.create_from_excel(r_file_name_1))
    #跨应用拦截率
    sheetList.append(interception_rate.create_from_excel(r_file_name_1))
    #位置校验
    sheetList.append(abnormal_position.create_from_excel(r_file_name_1))
    return sheetList

def countDimension(xx):
    c = 0
    for x in xx:
        if x > 0:
            c = c + 1
    return c

def findDataSourceFile(sourceDir,r_key_1,r_key_2):
    r_file_1 = cu.find_file_in_dir(source_dir,r_key_1)
    r_file_2 = cu.find_file_in_dir(source_dir,r_key_2)
    return r_file_1,r_file_2
    

def readConfig(path):
    global key1,key2
    cf = configparser.ConfigParser()
    cf.read(path,encoding='utf-8')
    key1 = cf.get('file_key','old_dimension')
    key2 = cf.get('file_key','new_dimension')

if __name__ == "__main__":
    startTime = time.time()
    readConfig(config_path)
    r_file_name , r_file_name_1 = findDataSourceFile(source_dir,key1,key2)
    if r_file_name is None or r_file_name_1 is None:
        print("not find source file and exit")
        os._exit(0)
        time.sleep(2)
    name_key = input("输出文件的命名key:")
    print("input = %s \nIn calculation ..." % name_key)
    handle_excel(r_file_name,r_file_name_1,name_key)
    print('finish:',time.time()-startTime)