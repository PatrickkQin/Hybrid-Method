import sys
import numpy as np
import mikeio
import time
import os
import xlrd
import datetime
import xlsxwriter
import warnings
import shutil
import pandas as pd


warnings.filterwarnings('ignore')


# Change the number of time steps and the name of the output in the MIKE zero data manager file.
def __update_file__(file, old_str, new_str):
    """
    Replacing strings in a file
    :param file: Filename.
    :param old_str: String to be replaced.
    :param new_str: Replaceing String.
    :return: Nothing.
    """
    file_data = ""
    with open(file, "r", encoding="ISO-8859-1") as f:
        for line in f:
            if old_str in line:
                line = line.replace(old_str, new_str)
            file_data += line
    with open(file, "w", encoding="ISO-8859-1") as f:
        f.write(file_data)


# Calculate the penetration rate of the difference
def __inter_value__(dist1, dist2, v1, v2):
    """
    Suitable for 2 point interpolation
    :param dist1: Distance between the first station and element.
    :param dist2: Distance between the second station and element.
    :param v1: Value of the first station.
    :param v2: Value of the second station.
    :return: The calculated infiltration value of the element.
    """
    v = (v1 / (dist1 ** 2) + v2 / (dist2 ** 2)) / (1 / (dist1 ** 2) + 1 / (dist2 ** 2))
    return v


# Calculate the distance between two points
def __distance__(station, element):
    """
    :param station: A stations' location.
    :param element: An element's position.
    :return: Distance between them.
    """
    dist = ((station[0] - element[0]) ** 2 + (station[1] - element[1]) ** 2) ** 0.5
    return dist


# Calculate the penetration rate of the difference
def __inter_f__(dist, ff):
    """
    :param dist: Distance between the stations and elements.
    :param ff: Infiltration value of stations.
    :return: The calculated infiltration value of the element.
    """
    f_inter = (ff[0] / (dist[0] ** 2) + ff[1] / (dist[1] ** 2) + ff[2] / (dist[2] ** 2) + ff[3] / (dist[3] ** 2)) / (
            1 / (dist[0] ** 2) + 1 / (dist[1] ** 2) + 1 / (dist[2] ** 2) + 1 / (dist[3] ** 2))
    return f_inter


# Weighted calculation of penetration rate
def __get_infil__(element_num, wl_location, infil_value, point_location, group_num):
    """
    :param element_num: Number of mesh elements.
    :param wl_location: Water logging measuring stations' location.
    :param infil_value: Water logging measuring stations' infiltration value.
    :param point_location: All the location of mesh elements.
    :param group_num: Combination of stations
    :return: A list, the infiltration value should be added into the dfsu file.
    """
    infil = np.zeros(element_num)
    for loop in range(element_num):
        dist0 = __distance__(wl_location[group_num[0] - 1, :], point_location[loop, :])
        dist1 = __distance__(wl_location[group_num[1] - 1, :], point_location[loop, :])
        dist2 = __distance__(wl_location[group_num[2] - 1, :], point_location[loop, :])
        dist3 = __distance__(wl_location[group_num[3] - 1, :], point_location[loop, :])
        distance = [dist0, dist1, dist2, dist3]
        infil[loop] = __inter_f__(distance, infil_value)
    return infil


def __add_infil__(old_value, add_value, timestamp):
    """
    :param old_value: The whole ndarray of the old file waiting for refreshing.
    :param add_value: New data should be added into the file.
    :param timestamp: Literal meaning.
    :return: The refreshed old_value.
    """
    old_value[timestamp, :] = add_value
    return old_value


# Check if the file is generated
def __check_file__(num):
    time.sleep(1)  # Need to wait a bit for the software to run
    counter = 0
    while 1:
        if num < 11:
            if os.path.exists("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\"
                              "small3_C(i=0).m21fm - Result Files\\" + str(num) + ".dfs0"):
                time.sleep(0.5)
                fp = "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).m21fm - Result Files\\" + str(
                    num) + ".dfs0"
                try:
                    dfswd = mikeio.open(fp)
                except:
                    time.sleep(2)
                    try:
                        dfswd = mikeio.open(fp)
                    except:
                        time.sleep(5)
                        dfswd = mikeio.open(fp)
                dswd = dfswd.read(items='ngn: Total water depth')
                if dswd.shape[0] == num + 1:
                    break
            else:
                counter += 1
                time.sleep(0.5)
                if counter == 30:
                    os.chdir("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run")
                    os.startfile("startMIKE_C(i=0).bat")
                    counter = 0
        else:
            if os.path.exists("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm - Result Files"
                              "\\" + str(num) + ".dfs0"):
                time.sleep(0.5)
                fp = "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm - Result Files\\" + str(num) + ".dfs0"
                try:
                    dfswd = mikeio.open(fp)
                except:
                    time.sleep(2)
                    try:
                        dfswd = mikeio.open(fp)
                    except:
                        time.sleep(5)
                        dfswd = mikeio.open(fp)
                dswd = dfswd.read(items='ngn: Total water depth')
                if dswd.shape[0] == 11:
                    break
            else:
                counter += 1
                time.sleep(0.5)
                if counter == 30:
                    os.chdir("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run")
                    os.startfile("startMIKE_C.bat")
                    counter = 0


def __change_dfsu__(infil_list, timestamp):
    """
    :param infil_list: All elements' infiltration value list. One by one, listed by the element code.
    :return:
    """
    dire0 = 'C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\chicago infiltration.dfsu'

    infil_dfsu0 = mikeio.open(dire0)
    infil_ds0 = infil_dfsu0.read(items='infiltration')
    infil_ds0.infiltration.values[timestamp, :] = infil_list
    infil_ds0.to_dfs("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\chicago infiltration.dfsu")


def __get_h10__(timestamp, station_num):
    """
    :param timestamp: loop number.
    :param station_num: Index of water logging stations.
    :return:
    """
    dire0 = 'C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).m21fm - Result Files\\' + str(timestamp) + '.dfs0'
    try:
        h_dfs0 = mikeio.open(dire0)
    except():
        time.sleep(5)
        try:
            h_dfs0 = mikeio.open(dire0)
        except():
            time.sleep(5)
            h_dfs0 = mikeio.open(dire0)
    while 1:
        item_name = ['ngb', 'ng', 'kgm', 'sdk', 'xhj', 'ngn']
        name = item_name[station_num] + ': Total water depth'
        h_ds = h_dfs0.read(items=name)
        if h_ds.n_timesteps == (timestamp + 1):
            if station_num == 0:
                n = h_ds.ngb_Total_water_depth.values[timestamp].round(5)
            elif station_num == 1:
                n = h_ds.ng_Total_water_depth.values[timestamp].round(5)
            elif station_num == 2:
                n = h_ds.kgm_Total_water_depth.values[timestamp].round(5)
            elif station_num == 3:
                n = h_ds.sdk_Total_water_depth.values[timestamp].round(5)
            elif station_num == 4:
                n = h_ds.xhj_Total_water_depth.values[timestamp].round(5)
            else:
                n = h_ds.ngn_Total_water_depth.values[timestamp].round(5)
            if str(n) == 'nan':
                n = 0
            return n
        else:
            continue


def __get_h__(timestamp, station_num):
    """
    :param timestamp: loop number.
    :param station_num: Index of water logging stations.
    :return:
    """
    dire0 = 'C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm - Result Files\\' + str(timestamp) + '.dfs0'
    try:
        h_dfs0 = mikeio.open(dire0)
    except():
        time.sleep(5)
        try:
            h_dfs0 = mikeio.open(dire0)
        except():
            time.sleep(5)
            h_dfs0 = mikeio.open(dire0)
    while 1:
        item_name = ['ngb', 'ng', 'kgm', 'sdk', 'xhj', 'ngn']
        name = item_name[station_num] + ': Total water depth'
        h_ds = h_dfs0.read(items=name)
        if h_ds.n_timesteps == 11:
            if station_num == 0:
                n = h_ds.ngb_Total_water_depth.values[10].round(5)
            elif station_num == 1:
                n = h_ds.ng_Total_water_depth.values[10].round(5)
            elif station_num == 2:
                n = h_ds.kgm_Total_water_depth.values[10].round(5)
            elif station_num == 3:
                n = h_ds.sdk_Total_water_depth.values[10].round(5)
            elif station_num == 4:
                n = h_ds.xhj_Total_water_depth.values[10].round(5)
            else:
                n = h_ds.ngn_Total_water_depth.values[10].round(5)
            return n
        else:
            continue


def __time_str__():
    curr_time = datetime.datetime.now()
    time_str = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H-%M-%S')
    return time_str


def __data_write__(datas, folder_num):
    ti = __time_str__()
    if folder_num == 0:
        file = xlsxwriter.Workbook(
            "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).m21fm - Result Files\\r-f-" + ti + ".xlsx")
    else:
        file = xlsxwriter.Workbook(
            "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm - Result Files\\r-f-" + ti + ".xlsx")

    sheet1 = file.add_worksheet()
    ii = 0
    for data0 in datas:
        for jj in range(len(data0)):
            sheet1.write(ii, jj, data0[jj])
        ii = ii + 1
    file.close()


def __cal_hms__(loop_num):
    sec = loop_num % 60
    min0 = loop_num // 60
    min1 = min0 % 60
    hour = min0 // 60
    return hour, min1, sec


def __get_time4mike__(num):
    if num == 0:
        ff = open("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).log", encoding="ISO-8859-1")
    else:
        ff = open("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.log", encoding="ISO-8859-1")
    keyword = "Total              "
    while True:
        line = ff.readline()
        if line:
            if keyword in line:
                print(line)
                timee = line[-5:-1]
                timee = float(timee)
                return timee
        else:
            break
    ff.close()


rain_allfile = ["C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\2a_rain.xls",
                "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\5a_rain.xls",
                "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\10a_rain.xls",
                "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\20a_rain.xls",
                "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\50a_rain.xls",
                "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\100a_rain.xls"]
wd_allfile = ["C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\2a_wd.xls",
              "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\5a_wd.xls",
              "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\10a_wd.xls",
              "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\20a_wd.xls",
              "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\50a_wd.xls",
              "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\100a_wd.xls"]
fn_all = ["C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\2a_rain_20s.dfsu",
          "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\5a_rain_20s.dfsu",
          "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\10a_rain_20s.dfsu",
          "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\20a_rain_20s.dfsu",
          "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\50a_rain_20s.dfsu",
          "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\100a_rain_20s.dfsu"]
need2be = [r"file_name = |.\2a_rain_20s.dfsu|", r"file_name = |.\5a_rain_20s.dfsu|",
           r"file_name = |.\10a_rain_20s.dfsu|", r"file_name = |.\20a_rain_20s.dfsu|",
           r"file_name = |.\50a_rain_20s.dfsu|", r"file_name = |.\100a_rain_20s.dfsu|"]
period = ["2a", "5a", "10a", "20a", "50a", "100a"]

# Locate the loop by identifying the file
q = 0
for qq in range(6):
    if os.path.isdir(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm - Result Files(return period=" + period[qq] + ")"):
        q = qq + 1
        if q == 6:
            sys.exit()
    else:
        break
loop = q

start_time = __time_str__()
# Calculate the difference between the water depth after runoff and the actual water depth and output the f value that should be entered.
# First: reading rainfall files

rain_file = xlrd.open_workbook(rain_allfile[loop])
r_table = rain_file.sheets()[0]
r_dapaotai = np.array(r_table.col_values(0, start_rowx=0, end_rowx=None))
r_haishi = np.array(r_table.col_values(1, start_rowx=0, end_rowx=None))
print("Rainfall file reading complete")

wd_file = xlrd.open_workbook(wd_allfile[loop])
wd_real0 = wd_file.sheets()[0]
neigang_real = wd_real0.col_values(0, start_rowx=0, end_rowx=None)
neigangbei_real = wd_real0.col_values(1, start_rowx=0, end_rowx=None)
neigangnan_real = wd_real0.col_values(2, start_rowx=0, end_rowx=None)
xiahuanjie_real = wd_real0.col_values(3, start_rowx=0, end_rowx=None)
sidakou_real = wd_real0.col_values(4, start_rowx=0, end_rowx=None)
kanggongmiao_real = wd_real0.col_values(5, start_rowx=0, end_rowx=None)
lenght = len(kanggongmiao_real)
wl_real = np.array(
    [neigangbei_real, neigang_real, kanggongmiao_real, sidakou_real, xiahuanjie_real, neigangnan_real]) \
    .astype("float")
print("Water logging depth file reading complete")

fn = fn_all[loop]
# Third: Getting the underlying global variables
dfs = mikeio.open(fn)
ds = dfs.read(items='rain')
element_number = ds.rain.values.shape[1]  # Get the number of grid elements
element_location = dfs.element_coordinates[:, 0:2]  # Getting the position of the grid

station_location = np.array([[19728.836, 18765.928], [19714.014, 18600.935], [19826.955, 18438.579],
                             [19523.554, 17974.719], [19436.905, 17631.302], [19309.053, 17733.999]])
station_distance = np.array([[657, 1690], [596, 1436], [487, 1425], [906, 917], [1129, 532], [1232, 582]])
# This is the distance from each of the 6 stations to the two rainfall stations at Fortress and Marine.

groups = np.array([[1, 2, 4, 5], [1, 2, 4, 6], [1, 2, 5, 6],
                   [1, 3, 4, 5], [1, 3, 4, 6], [1, 3, 5, 6],
                   [2, 3, 4, 5], [2, 3, 4, 6], [2, 3, 5, 6]])
# Reorganized Configuration

k = 5
# Assuming the fifth Reorganized Configuration is best
h = np.zeros((2101, 4))
f = np.zeros((2101, 4))
r_inter = np.array([0, 0, 0, 0])
timestep = 20 * 10
final_loop = 360
delta_time = np.zeros((final_loop, 3))

infil_all = np.zeros((final_loop, element_number))
dire = "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\chicago infiltration.dfsu"

infil_dfsu = mikeio.open(dire)
infil_ds = infil_dfsu.read(items='infiltration')
infil_ds.infiltration.values[:final_loop, :] = infil_all
infil_ds.to_dfs("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\chicago infiltration.dfsu")

for i in range(final_loop):
    time_a = datetime.datetime.now()
    r_inter[0] = __inter_value__(station_distance[groups[k, 0] - 1, 0], station_distance[groups[k, 0] - 1, 1],
                                 r_dapaotai[i], r_haishi[i])
    r_inter[1] = __inter_value__(station_distance[groups[k, 1] - 1, 0], station_distance[groups[k, 1] - 1, 1],
                                 r_dapaotai[i], r_haishi[i])
    r_inter[2] = __inter_value__(station_distance[groups[k, 2] - 1, 0], station_distance[groups[k, 2] - 1, 1],
                                 r_dapaotai[i], r_haishi[i])
    r_inter[3] = __inter_value__(station_distance[groups[k, 3] - 1, 0], station_distance[groups[k, 3] - 1, 1],
                                 r_dapaotai[i], r_haishi[i])
    print("Completed the rainfall interpolation")

    f[i, 0] = (h[i, 0] - wl_real[groups[k, 0] - 1, i + 1]) * 1000 * 3600 / timestep + r_inter[0]
    f[i, 1] = (h[i, 1] - wl_real[groups[k, 1] - 1, i + 1]) * 1000 * 3600 / timestep + r_inter[1]
    f[i, 2] = (h[i, 2] - wl_real[groups[k, 2] - 1, i + 1]) * 1000 * 3600 / timestep + r_inter[2]
    f[i, 3] = (h[i, 3] - wl_real[groups[k, 3] - 1, i + 1]) * 1000 * 3600 / timestep + r_inter[3]
    print("Completed the infiltration calculation")
    add_data = __get_infil__(element_number, station_location, f[i, :], element_location, groups[k, :])
    print("Completed calculation of new data in grids")
    # Renew the dfsu file
    __change_dfsu__(add_data, i)
    print("Completed supplement of the dfsu file")

    if i == 0:
        old_h, old_m, old_s = __cal_hms__((final_loop - 10) * 20)
        old_time = '2000, 1, 1, ' + str(old_h) + ', ' + str(old_m) + ', ' + str(old_s)
        hours, minutes, seconds = __cal_hms__(i)
        new_time = '2000, 1, 1, ' + str(hours) + ', ' + str(minutes) + ', ' + str(seconds)
        __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm", "start_time = " + old_time,
                        "start_time = " + new_time)
        __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm", str(final_loop) + ".dfs0",
                        "10.dfs0")

        __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).m21fm",
                        "number_of_time_steps = 10", "number_of_time_steps = 1")  # Here's where the start time is replaced
        __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).m21fm", "10.dfs0", "1.dfs0")

    if i < 10:
        __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).m21fm",
                        "number_of_time_steps = "
                        + str(i), "number_of_time_steps = " + str(i + 1))
        __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).m21fm", "last_time_step = "
                        + str(i), "last_time_step = " + str(i + 1))
        __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).m21fm", str(i) + ".dfs0",
                        str(i + 1) + ".dfs0")

        # run the .bat file for auto calculation
        time1 = datetime.datetime.now()
        os.chdir("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run")
        os.startfile("startMIKE_C(i=0).bat")
        print('MIKE on going')

    else:
        # Renew the start timestamp
        old_h, old_m, old_s = __cal_hms__((i - 10) * 20)
        old_time = '2000, 1, 1, ' + str(old_h) + ', ' + str(old_m) + ', ' + str(old_s)
        hours, minutes, seconds = __cal_hms__((i - 9) * 20)

        new_time = '2000, 1, 1, ' + str(hours) + ', ' + str(minutes) + ', ' + str(seconds)
        __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm", "start_time = " + old_time,
                        "start_time = " + new_time)
        __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm", str(i) + ".dfs0",
                        str(i + 1) + ".dfs0")

        # run the .bat file for auto calculation
        time1 = datetime.datetime.now()
        os.chdir("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run")
        os.startfile("startMIKE_C.bat")
        print('MIKE on going')

    # Check if the file is generated
    __check_file__(i + 1)
    # Record the time.
    time2 = datetime.datetime.now()
    end_time = __time_str__()
    time4mike = (time2 - time1).total_seconds()
    delta_time[i, 0] = time4mike
    # Extracting data for the next moment
    if i < 10:
        # Extract the generated cumulus file to obtain h(i+1)
        h[i + 1, 0] = __get_h10__(i + 1, groups[k, 0] - 1)
        h[i + 1, 1] = __get_h10__(i + 1, groups[k, 1] - 1)
        h[i + 1, 2] = __get_h10__(i + 1, groups[k, 2] - 1)
        h[i + 1, 3] = __get_h10__(i + 1, groups[k, 3] - 1)
        print("MIKE waterlogging depth Reading Success")
        data = np.hstack([f, h])
        __data_write__(data, 0)
        print("MIKE waterlogging depth saving Success")
        delta_time[i, 1] = __get_time4mike__(0)
    else:
        h[i + 1, 0] = __get_h__(i, groups[k, 0] - 1)
        h[i + 1, 1] = __get_h__(i, groups[k, 1] - 1)
        h[i + 1, 2] = __get_h__(i, groups[k, 2] - 1)
        h[i + 1, 3] = __get_h__(i, groups[k, 3] - 1)
        print("MIKE waterlogging depth Reading Success")
        # Archive it.
        data = np.hstack([f, h])
        __data_write__(data, 1)
        print("MIKE waterlogging depth saving Success")
        delta_time[i, 1] = __get_time4mike__(1)

    # Record the overall run time
    time_b = datetime.datetime.now()
    time4all = (time_b - time_a).total_seconds()
    delta_time[i, 2] = time4all

    if i == 9:
        # rename the small3_C(i=0) folder
        os.rename("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).m21fm - Result Files",
                  "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm - Result Files")
        print("Folder name changed successfully")

    # Store delta_time into excel.：
    if i == final_loop - 1:
        delta_time_pd = pd.DataFrame(delta_time, columns=["time4mike", "cal4mike", "time4all"])
        with pd.ExcelWriter(
                'C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm - Result Files\\time' + str(k + 1)
                + '.xlsx') as writer:
            delta_time_pd.to_excel(writer, sheet_name='Sheet1', float_format='%.6f')

# Change the name of the big folder before the next combination
os.rename("C:\\Users\\DHI MIKE 2021\Desktop\\JT run\\small3_C.m21fm - Result Files",
          "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm - Result Files(return period=" + period[loop] + ")")
print("Resulting folder renamed successfully")

# Save infiltration's dfsu file
shutil.copyfile("C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\chicago infiltration.dfsu",
                "C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm - Result Files"
                "(return period=" + period[loop] + ")\\chicago infiltration.dfsu")

print("Infiltration dfsu file copying successful")

# Replacement of rainfall files
if loop < 5:
    __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C(i=0).m21fm", need2be[loop],
                    need2be[loop+1])
    __update_file__(r"C:\\Users\\DHI MIKE 2021\\Desktop\\JT run\\small3_C.m21fm", need2be[loop],
                    need2be[loop+1])

    print("Restart the program to maintain computational efficiency")
    os.system('python "C:\\Users\\DHI MIKE 2021\\PycharmProjects\\pythonProject\\MIKE Chicago.py"')
