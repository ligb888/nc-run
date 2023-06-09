import calendar
import math
import os
import time
import traceback
from multiprocessing import Process, Pool
import numpy as np
from netCDF4 import Dataset
from task.task_nc_out import out_img, out_gif, out_excel, out_flow_draw
from util import utils

# 初始化日志
logger = utils.get_logger(name="task_nc", console=True)


class TaskNcProcess(Process):
    # 获取任务
    def __init__(self, cpus, input_path, task_queue, out_dir="./output"):
        self.input_path = input_path
        self.task_queue = task_queue
        self.out_dir = out_dir
        self.home_dir = self.out_dir + "/" + str(calendar.timegm(time.gmtime()))
        self.cpus = cpus
        super().__init__()

    def run(self) -> None:
        try:
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

            self.out_flow(nc)
            # 遍历数据
            # for i in range(len(data_var)):
            #     var = data_var[i]
            #     var_type = data_var_type[i]
            #     data = nc.variables[var]
            #     curr_dir = home_dir + "/" + var
            #     if not os.path.exists(curr_dir):
            #         os.makedirs(curr_dir)
            #
            #     # 刻度处理
            #     all_data = []
            #     if len(data.shape) == 3:
            #         for item in data:
            #             all_data.append(item[0])
            #     else:
            #         all_data = data
            #     all_data = np.sort(np.array(all_data).flatten())
            #     count = int(len(all_data) * 0.05)
            #     if count > 2:
            #         all_data = all_data[count:-count]
            #     vmin = all_data.min()
            #     vmax = all_data.max()
            #
            #     # 循环时间维度
            #     for j in range(len(data)):
            #         # 入参
            #         excel_path = curr_dir + "/" + str(j) + ".csv"
            #         img_path = curr_dir + "/" + str(j) + ".png"
            #         curr_x = x if var_type == "2" or var_type == "3" else xc
            #         curr_y = y if var_type == "2" or var_type == "3" else yc
            #         img_data = data[j]
            #         if len(data[j].shape) == 2:
            #             img_data = data[j][0]
            #         # 输出excel任务
            #         self.pool.apply_async(out_excel, args=(excel_path, data[j], ))
            #         # 输出图片任务
            #         self.pool.apply_async(out_img, args=(img_path, curr_x, curr_y, vmin, vmax, j, var, img_data,))

            # 遍历数据，下发输出动态图任务
            # for var in data_var:
            #     curr_dir = home_dir + "/" + var
            #     pool.apply_async(out_gif, args=(curr_dir,))

            # 完成下发
            # self.pool.close()
            # logger.info("任务下发完成")
            # # 等待执行
            # self.pool.join()
            # logger.info("任务执行完成")
        except:
            logger.error("获取任务失败" + traceback.format_exc())
        finally:
            nc.close()

    def out_flow(self, nc):
        logger.info("开始执行流向专题图任务...")
        try:
            pool = Pool(self.cpus)
            img_path = self.home_dir + "/flow"
            if not os.path.exists(img_path):
                os.makedirs(img_path)

            xc = nc.variables["xc"][:]
            yc = nc.variables["yc"][:]
            u = nc.variables["u"][:]
            v = nc.variables["v"][:]

            # 东向和北向转换成数学角度
            all_angle_arr = []
            all_speed_arr = []
            total_speed_arr = []
            for i in range(len(u)):
                # 计算角度、流速
                angle_arr = []
                speed_arr = []
                cu = u[i][0]
                cv = v[i][0]
                for j in range(len(xc)):
                    # 气象角度和数学角度，这里使用数学角度
                    # angle = 180 + math.atan2(cu[i], cv[i]) * 180 / math.pi
                    angle = 90 - math.atan2(cu[j], cv[j]) * 180 / math.pi
                    if angle < 0:
                        angle = angle + 360
                    speed = math.sqrt(cu[j] ** 2 + cv[j] ** 2)
                    angle_arr.append(angle)
                    speed_arr.append(speed)
                    total_speed_arr.append(speed)
                all_angle_arr.append(angle_arr)
                all_speed_arr.append(speed_arr)

            # 为了刻度统一，求出区间
            total_speed_arr.sort()
            count = int(len(total_speed_arr) * 0.05)
            total_speed_arr = total_speed_arr[count:-count]
            speed_min = min(total_speed_arr)
            speed_range = max(total_speed_arr) - speed_min

            # 绘制箭头
            for i in range(len(all_angle_arr)):
                angle_arr = all_angle_arr[i]
                speed_arr = all_speed_arr[i]
                pool.apply_async(out_flow_draw, args=(img_path, xc, yc, i, angle_arr, speed_arr, speed_min, speed_range,))

            # 等待执行完成
            pool.close()
            pool.join()
            # 执行动图任务
            Process(target=out_gif, args=(img_path,)).start()
            logger.info("流向专题图完成。")
        except:
            logger.info("数据处理出错" + traceback.format_exc())
