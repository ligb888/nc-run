import calendar
import csv
import logging
import os
import time
import traceback
from multiprocessing import Process, Pool
from netCDF4 import Dataset
from util import utils
import matplotlib.pyplot as plt


def out_excel(file_path, data):
    utils.init_log(name="out_"+str(os.getpid()), console=True)
    try:
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
    except:
        logging.info("生成csv出错" + traceback.format_exc())


def out_img(file_path, x, y, var, data):
    utils.init_log(name="out_"+str(os.getpid()), console=True)
    try:
        if len(data.shape) == 2:
            data = data[0]
        plt.figure(figsize=(9.6, 7.2))
        plt.title(var)
        plt.scatter(x, y, s=10, alpha=0.8, c=data, cmap='jet', linewidth=0)
        plt.colorbar()
        plt.savefig(file_path)
    except:
        logging.info("生成图片出错" + traceback.format_exc())
    finally:
        plt.close()


class TaskNcProcess(Process):
    # 获取任务
    def __init__(self, cpus, input_path, task_queue, out_dir="./out"):
        self.cpus = cpus
        self.input_path = input_path
        self.task_queue = task_queue
        self.out_dir = out_dir
        super().__init__()

    def run(self) -> None:
        try:
            utils.init_log(name="task_nc", console=True)
            # 进程池
            pool = Pool(self.cpus)
            # 数据读入
            nc = Dataset(self.input_path)
            # 所有字段
            logging.info(rf"nc loaded, keys = {nc.variables.keys()}")
            # data字段数组
            data_var = []
            data_var_type = []
            # xy数组长度
            length = len(nc.variables["x"])
            # xcyc数组长度
            length_c = len(nc.variables["xc"])
            x = nc.variables["x"][:]
            y = nc.variables["y"][:]
            xc = nc.variables["xc"][:]
            yc = nc.variables["yc"][:]
            # 判断哪些是data字段，放入data数组
            for var in nc.variables.keys():
                data = nc.variables[var]
                try:
                    if len(data.shape) == 2:
                        if data.shape[1] == length:
                            data_var.append(var)
                            data_var_type.append("2")
                        elif data.shape[1] == length_c:
                            data_var.append(var)
                            data_var_type.append("2_c")
                    elif len(data.shape) == 3:
                        if data.shape[2] == length:
                            data_var.append(var)
                            data_var_type.append("3")
                        elif data.shape[2] == length_c:
                            data_var.append(var)
                            data_var_type.append("3_c")
                except():
                    pass

            # 创建输出文件夹
            if not os.path.exists(self.out_dir):
                os.makedirs(self.out_dir)
            # 通过时间戳创建输出文件夹
            home_dir = self.out_dir + "/" + str(calendar.timegm(time.gmtime()))
            if not os.path.exists(home_dir):
                os.makedirs(home_dir)

            logging.info("开始下发任务...")
            # 遍历数据
            for i in range(len(data_var)):
                var = data_var[i]
                var_type = data_var_type[i]
                data = nc.variables[var]
                curr_dir = home_dir + "/" + var
                if not os.path.exists(curr_dir):
                    os.makedirs(curr_dir)
                for j in range(len(data)):
                    excel_path = curr_dir + "/" + str(j) + ".csv"
                    img_path = curr_dir + "/" + str(j) + ".png"
                    curr_x = x if var_type == "2" or var_type == "3" else xc
                    curr_y = y if var_type == "2" or var_type == "3" else yc
                    pool.apply_async(out_excel, args=(excel_path, data[j],))
                    pool.apply_async(out_img, args=(img_path, curr_x, curr_y, var, data[j],))

            pool.close()
            pool.join()
            nc.close()
            logging.info("任务下发完成")
        except:
            logging.error("获取任务失败" + traceback.format_exc())

