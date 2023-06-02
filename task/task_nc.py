import calendar
import csv
import os
import time
import traceback
from multiprocessing import Process, Pool
import imageio
import numpy as np
from netCDF4 import Dataset
from util import utils
import matplotlib.pyplot as plt

# 初始化日志
logger = utils.get_logger(name="out", console=True)


def out_excel(file_path, data):
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
        logger_out = utils.get_logger(name="out_err_" + str(os.getpid()), console=True)
        logger_out.info("生成csv出错" + traceback.format_exc())


def out_img(file_path, x, y, j, var, data):
    try:
        # 刻度处理
        all_data = []
        img_data = data[j]
        if len(data[j].shape) == 2:
            img_data = data[j][0]
            for item in data:
                all_data.append(item[0])
        else:
            all_data = data
        count = int(len(all_data) * 0.1)
        all_data = np.sort(np.array(all_data).flatten())
        if count > 2:
            all_data = all_data[count:-count]
        vmin = all_data.min()
        vmax = all_data.max()

        # 画图
        plt.figure(figsize=(9.6, 7.2))
        plt.title(var)
        plt.scatter(x, y, s=10, alpha=0.8, c=img_data, cmap='jet', linewidth=0, vmin=vmin, vmax=vmax)
        plt.colorbar()
        plt.savefig(file_path)
    except:
        logger_out = utils.get_logger(name="out_err_" + str(os.getpid()), console=True)
        logger_out.info("生成图片出错" + traceback.format_exc())
    finally:
        plt.close()


def out_gif(path):
    try:
        frames = []
        for file in os.listdir(path):
            if not os.path.isdir(file) and os.path.splitext(file)[-1] == ".png":
                img = imageio.v2.imread(path + "/" + file)
                frames.append(img)
        if len(frames) > 0:
            imageio.v2.mimsave(path + "/0.gif", frames, 'GIF', duration=3000)
    except:
        logger_out = utils.get_logger(name="out_err_" + str(os.getpid()), console=True)
        logger_out.info("转换动图出错" + traceback.format_exc())


class TaskNcProcess(Process):
    # 获取任务
    def __init__(self, cpus, input_path, task_queue, out_dir="./output"):
        self.cpus = cpus
        self.input_path = input_path
        self.task_queue = task_queue
        self.out_dir = out_dir
        super().__init__()

    def run(self) -> None:
        try:
            # 进程池
            pool = Pool(self.cpus)
            # 数据读入
            nc = Dataset(self.input_path)
            # 所有字段
            logger.info(rf"nc loaded, keys = {nc.variables.keys()}")
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

            logger.info("开始下发任务...")
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
                    # 输出excel任务
                    # pool.apply_async(out_excel, args=(excel_path, data[j],))
                    # 输出图片任务
                    pool.apply_async(out_img, args=(img_path, curr_x, curr_y, j, var, data,))

            # 遍历数据，下发输出动态图任务
            for var in data_var:
                curr_dir = home_dir + "/" + var
                pool.apply_async(out_gif, args=(curr_dir,))

            pool.close()
            logger.info("任务下发完成")
            pool.join()
            logger.info("任务执行完成")
            nc.close()
        except:
            logger.error("获取任务失败" + traceback.format_exc())
