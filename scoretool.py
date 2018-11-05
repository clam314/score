from __future__ import division

points_income_growth =  [[0.5,0],[1,30],[2,60],[3,100]]

points_time_concentration = [[0.8,0],[0.9,50],[1,100]]

points_early_morning = [[0.1,0],[0.15,50],[0.3,100]]

points_0_income_hours = [[7,0],[11,50],[20,100]]

points_weak_network = [[0.2,0],[0.4,25],[0.8,50],[0.97,75],[1,100]]

points_buried_point = [[0.38,0],[0.18,25],[0.06,50],[0.015,75],[0,100]]

points_interception_rate = [[0.4,0],[0.5,50],[0.75,100]]

points_abnormal_position = [[0.85,0],[0.93,50],[1,100]]

points_province_5_6 = [[0.88,0],[0.93,50],[0.98,100]]

points_province_7_9 = [[0.8,0],[0.86,50],[0.97,100]]

points_province_10_13 = [[0.54,0],[0.61,50],[0.83,100]]

points_province_14_18 = [[0.37,0],[0.4,50],[0.51,100]]

points_province_19_31 = [[0.28,0],[0.32,50],[0.57,100]]

showProgress = False

# 计算正相关的维度评分
def score_add(v,points):
    score = 0
    position = -1
    for i in range(len(points)):
        p = points[i]
        if v <= p[0]:
            position = i
            break
    if showProgress:
        print('V:%s  position:%d ' % (v , position ))
    if position > 0 :
        point0 = points[position-1]
        point1 = points[position]
        score = (v - point0[0]) / (point1[0] - point0[0]) * (point1[1] - point0[1]) + point0[1]
    elif position == 0 :
        score = 0
    elif position == -1 :
        score = 100

    return score

# 计算负相关的维度评分
def score_less(v,points):
    score = 0
    position = -1
    for i in range(len(points)):
        p = points[i]
        if v >= p[0]:
            position = i
            break
    if showProgress:
        print('V:%s  position:%d ' % (v , position ))
    if position > 0 :
        point0 = points[position-1]
        point1 = points[position]
        score = (v - point0[0]) / (point1[0] - point0[0]) * (point1[1] - point0[1]) + point0[1]
    elif position == 0 :
        score = 0
    elif position == -1 :
        score = 100

    return score