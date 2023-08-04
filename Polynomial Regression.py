import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd
import datetime
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import xlsxwriter
import time


def __get_data__(name, sheet, column):
    total_file = pd.read_excel('C:\\Users\\70473\\Desktop\\test4_correct\\' + name + '.xlsx', sheet_name=sheet)
    used_data = total_file.loc[:, column]
    used_data0 = np.array(used_data)
    data = used_data0[1:, :]
    print(name + ' Data extraction complete')
    return data


def stand(a, b):
    a = a.astype(float)
    max1 = a.max()
    min1 = a.min()
    range1 = max1 - min1
    if range1 == 0 and b == 0:
        return [0] * len(a)
    else:
        for ii in range(len(a)):
            a[ii] = (a[ii] - min1) / range1
        if b == 0:
            return a
        elif b == 1:
            return range1
        else:
            return min1


def inv_stand(a, range1, min1):
    a = a.astype(float)
    for ii in range(len(a)):
        a[ii] = a[ii] * range1 + min1
    return a


def val_stand(a, range1, min1):
    if range1 == 0:
        return [0] * len(a)
    else:
        for ii in range(len(a)):
            a[ii] = (a[ii] - min1) / range1
        return a


def __time_str__():
    curr_time = datetime.datetime.now()
    time_str = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H-%M-%S')
    return time_str


def __data_write__(datas):
    ti = __time_str__()
    file = xlsxwriter.Workbook("C:\\Users\\70473\\Desktop\\JT run\\Machine Learning result\\PR" + ti + ".xlsx")
    sheet1 = file.add_worksheet()
    jj = 0
    for ii in range(datas.shape[0]):
        sheet1.write(ii, jj, datas[ii])
    file.close()

used_column = ['wd', '30minR', '1hR', 'intensityR', 'ele-tide']
ngb_train_data = __get_data__('内港北total_from21.6.1except21.6.28', 'Sheet1', used_column)
ngb_vali_data = __get_data__('内港北21.6.28', '21.6.28', used_column)
ng_train_data = __get_data__('内港total', 'Sheet1', used_column)
ng_vali_data = __get_data__('内港21.6.28', '21.6.28', used_column)
kgm_train_data = __get_data__('康公庙total', 'Sheet1', used_column)
kgm_vali_data = __get_data__('康公庙21.6.28', '21.6.28', used_column)
sdk_train_data = __get_data__('司打口total', 'Sheet1', used_column)
sdk_vali_data = __get_data__('司打口21.6.28', '21.6.28', used_column)
xhj_train_data = __get_data__('下环街total', 'Sheet1', used_column)
xhj_vali_data = __get_data__('下环街21.6.28', '21.6.28', used_column)
ngn_train_data = __get_data__('内港南total', 'Sheet1', used_column)
ngn_vali_data = __get_data__('内港南21.6.28', '21.6.28', used_column)

pre_all_station = np.array(())
act_all_station = np.array(())

for loop in range(6):
    if loop == 0:
        data_array0 = ngb_train_data
        vali_data0 = ngb_vali_data
        station_name = 'ngb'
    elif loop == 1:
        data_array0 = ng_train_data
        vali_data0 = ng_vali_data
        station_name = 'ng'
    elif loop == 2:
        data_array0 = kgm_train_data
        vali_data0 = kgm_vali_data
        station_name = 'kgm'
    elif loop == 3:
        data_array0 = sdk_train_data
        vali_data0 = sdk_vali_data
        station_name = 'sdk'
    elif loop == 4:
        data_array0 = xhj_train_data
        vali_data0 = xhj_vali_data
        station_name = 'xhj'
    else:
        data_array0 = ngn_train_data
        vali_data0 = ngn_vali_data
        station_name = 'ngn'

    col = data_array0.shape[1]
    hor = data_array0.shape[0]
    data_array = data_array0.astype(float)
    range0 = [0] * col
    min0 = [0] * col
    max0 = [0] * col

    for i in range(data_array0.shape[1]):
        max0[i] = max(data_array0[:, i])
        min0[i] = min(data_array0[:, i])
        range0[i] = max0[i] - min0[i]
        data_array[:, i] = stand(data_array0[:, i], 0)

    vali_data = vali_data0[1:, :].astype(float)
    for i in range(vali_data.shape[1]):
        vali_data[:, i] = val_stand(vali_data[:, i], range0[i], min0[i])

    v_output = vali_data[:, 0]
    v_output = np.around(v_output, decimals=3)
    v_input = vali_data[:, 1:]
    v_length = len(vali_data)

    poly_reg = PolynomialFeatures(degree=2)    # multivariate polynomial regression
    X_ploy = poly_reg.fit_transform(data_array[:, 1:])
    clf = LinearRegression().fit(X_ploy, data_array[:, 0])
    r_sq = clf.score(X_ploy, data_array[:, 0])
    print('coefficient of determination:', r_sq)    # Returns the predicted coefficient of determination
    print('intercept:', clf.intercept_)
    print('slope:', clf.coef_)

    # y_pred = clf.predict(data_array[:, 1:])
    # print('predicted response:', y_pred, sep='\n')
    V_poly = poly_reg.fit_transform(v_input)
    y_vali = clf.predict(V_poly)
    for kk in range(len(y_vali)):
        if y_vali[kk] < 0:
            y_vali[kk] = 0
    __data_write__(y_vali)
    time.sleep(2)

    if loop == 0:
        pre_all_station = y_vali
        act_all_station = v_output
    else:
        pre_all_station = np.hstack([pre_all_station, y_vali])
        act_all_station = np.hstack([act_all_station, v_output])

r2_final_all = r2_score(act_all_station, pre_all_station)
x1 = range(len(act_all_station))
plt.plot(x1, act_all_station, 'r')
plt.plot(x1, pre_all_station, 'b')
plt.title('All in Average, R2=' + str(r2_final_all))
plt.show()
