import calendar
import csv
import logging
import os
import time
import traceback
from netCDF4 import Dataset
from util import utils


def out_excel(file_path, data):
    with open(file_path, mode='w', newline='' "") as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if len(data.shape) == 2:
            for i in range(len(data[0])):
                row_arr = []
                for j in range(len(data)):
                    row_arr.append(data[j][i])
                writer.writerow(row_arr)
        else:
            for i in range(len(data)):
                writer.writerow([data[i]])


# 执行任务
def run(args):
    out_excel(args.curr_dir + "/" + str(args.i) + ".csv", args.data)


# 获取任务
def get_tasks(input_path, task_queue, out_dir="./out"):
    try:
        utils.init_log(name="task_nc", console=True)
        # 数据读入
        nc = Dataset(input_path)
        # 所有字段
        logging.info(rf"nc loaded, keys = {nc.variables.keys()}")
        # data字段数组
        data_key_2 = []
        data_key_3 = []
        data_key_2_c = []
        data_key_3_c = []
        # xy数组长度
        length = len(nc.variables["x"])
        # xcyc数组长度
        length_c = len(nc.variables["xc"])
        # 判断哪些是data字段，放入data数组
        for var in nc.variables.keys():
            data = nc.variables[var]
            try:
                if len(data.shape) == 2:
                    if data.shape[1] == length:
                        data_key_2.append(var)
                    elif data.shape[1] == length_c:
                        data_key_2_c.append(var)
                elif len(data.shape) == 3:
                    if data.shape[2] == length:
                        data_key_3.append(var)
                    elif data.shape[2] == length_c:
                        data_key_3_c.append(var)
            except():
                pass

        # 读取的数据量
        logging.info("nc data size:")
        logging.info(rf"data_key_2 = #{len(data_key_2)} ")
        logging.info(rf"data_key_3 = #{len(data_key_3)} ")
        logging.info(rf"data_key_2_c = #{len(data_key_2_c)} ")
        logging.info(rf"data_key_3_c = #{len(data_key_3_c)} ")

        # 创建输出文件夹
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        # 通过时间戳创建输出文件夹
        out_dir = out_dir + "/" + str(calendar.timegm(time.gmtime()))
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # 遍历数据并输出
        for var in data_key_2:
            data = nc.variables[var][:]
            curr_dir = out_dir + "/" + var
            if not os.path.exists(curr_dir):
                os.makedirs(curr_dir)
            for i in range(len(data)):
                task_queue.put({
                    i: i,
                    curr_dir: curr_dir,
                    data: data[i]
                })
    except:
        logging.error("任务执行失败" + traceback.format_exc())
