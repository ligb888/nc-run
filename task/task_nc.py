import calendar
import os
import time
import traceback
from multiprocessing import Process, Pool, Manager

import numpy as np
from netCDF4 import Dataset
from task.task_nc_out import out_img, out_gif, out_excel
from util import utils

# 初始化日志
logger = utils.get_logger(name="task_nc", console=True)


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
            # 坐标数据
            x = nc.variables["x"][:]
            y = nc.variables["y"][:]
            xc = nc.variables["xc"][:]
            yc = nc.variables["yc"][:]
            # 本次的输出文件夹
            home_dir = self.out_dir + "/" + str(calendar.timegm(time.gmtime()))
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

            logger.info("开始下发任务...")
            # 遍历数据
            for i in range(len(data_var)):
                var = data_var[i]
                var_type = data_var_type[i]
                data = nc.variables[var]
                curr_dir = home_dir + "/" + var
                if not os.path.exists(curr_dir):
                    os.makedirs(curr_dir)

                # 刻度处理
                all_data = []
                if len(data.shape) == 3:
                    for item in data:
                        all_data.append(item[0])
                else:
                    all_data = data
                all_data = np.sort(np.array(all_data).flatten())
                count = int(len(all_data) * 0.05)
                if count > 2:
                    all_data = all_data[count:-count]
                vmin = all_data.min()
                vmax = all_data.max()

                # 循环时间维度
                for j in range(len(data)):
                    # 入参
                    excel_path = curr_dir + "/" + str(j) + ".csv"
                    img_path = curr_dir + "/" + str(j) + ".png"
                    curr_x = x if var_type == "2" or var_type == "3" else xc
                    curr_y = y if var_type == "2" or var_type == "3" else yc
                    img_data = data[j]
                    if len(data[j].shape) == 2:
                        img_data = data[j][0]
                    # 输出excel任务
                    pool.apply_async(out_excel, args=(excel_path, data[j], ))
                    # 输出图片任务
                    pool.apply_async(out_img, args=(img_path, curr_x, curr_y, vmin, vmax, j, var, img_data,))

            # 遍历数据，下发输出动态图任务
            for var in data_var:
                curr_dir = home_dir + "/" + var
                pool.apply_async(out_gif, args=(curr_dir,))

            # 完成下发
            pool.close()
            logger.info("任务下发完成")
            # 等待执行
            pool.join()
            logger.info("任务执行完成")
            nc.close()
        except:
            logger.error("获取任务失败" + traceback.format_exc())
