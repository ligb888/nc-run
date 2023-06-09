import math
from multiprocessing import Pool

import numpy as np
from PIL import Image

from util import utils
import traceback
import os
import csv
import imageio
import matplotlib.pyplot as plt

# 初始化日志
logger = utils.get_logger(name="task_nc_out", console=True)


def out_excel(excel_path, data):
    try:
        with open(excel_path, mode='w', newline='' "") as file:
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
        logger.info("生成csv出错" + traceback.format_exc())


def out_img(img_path, curr_x, curr_y, vmin, vmax, j, var, img_data):
    try:
        # 画图
        plt.figure(figsize=(9.6, 7.2))
        plt.title(var + "-" + str(j))
        plt.scatter(curr_x, curr_y, s=16, alpha=0.8, c=img_data, cmap='jet', linewidth=0, vmin=vmin, vmax=vmax)
        plt.colorbar()
        plt.savefig(img_path)
    except:
        logger.info("生成图片出错" + traceback.format_exc())
    finally:
        plt.close()


def out_flow_draw(img_path, curr_x, curr_y, i, angle_arr, speed_arr, speed_min, speed_range):
    try:
        # 字体设置
        plt.rcParams['font.sans-serif'] = ['SimHei']
        # 图片大小
        plt.figure(figsize=(24, 20))
        # 标题
        # plt.title("流场", loc='right', c="white", fontsize=48)

        # 隐藏刻度和标签
        plt.xticks(())
        plt.yticks(())

        # 隐藏坐标轴
        ax = plt.gca()
        ax.spines['top'].set_color('none')
        ax.spines['bottom'].set_color('none')
        ax.spines['left'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        ax.xaxis.set_major_locator(plt.NullLocator())
        ax.yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)

        for j in range(len(curr_y)):
            if j % 6 != 0:
                continue
            speed = (speed_arr[j] - speed_min) / speed_range
            if speed < 0:
                speed = 0
            elif speed >= 1:
                speed = 0.999
            # speed = 0.4 + 0.6 * speed

            # 颜色表示流速
            color = plt.cm.jet(speed)
            # color = plt.cm.Blues(speed)
            # color = plt.cm.GnBu(speed)
            alpha = 1
            # 透明度表示流速
            # color = "b"
            # alpha = speed

            # 通过长度和三角函数求出箭头终点坐标
            width = 100
            length = 700
            x_add = length * math.cos(math.radians(angle_arr[j]))
            y_add = length * math.sin(math.radians(angle_arr[j]))
            plt.arrow(curr_x[j], curr_y[j], x_add, y_add, width=width, fc=color, ec=color, alpha=alpha)
        # 保存后清空图
        plt.savefig(img_path + "/" + str(i) + ".png", transparent=True)
        # plt.savefig(img_path + "/" + str(i) + ".png", bbox_inches='tight', pad_inches=0, transparent=True)
    except:
        logger.info("生成图片出错" + traceback.format_exc())
    finally:
        plt.close()


def out_gif(path):
    try:
        frames = []
        path_list = os.listdir(path)
        path_list.sort(key=lambda x: int(x.split('.')[0]))
        for file in path_list:
            if not os.path.isdir(file) and os.path.splitext(file)[-1] == ".png":
                img = imageio.imread(path + "/" + file)
                frames.append(img)
        if len(frames) > 0:
            imageio.mimsave(path + "/0.gif", frames, 'GIF', duration=500, disposal=2)

        # photo_list = []
        # path_list = os.listdir(path)
        # path_list.sort(key=lambda x: int(x.split('.')[0]))
        # for file in path_list:
        #     img = Image.open(path + "/" + file)
        #     photo_list.append(img)
        # photo_list[0].save(path + "/0.gif", save_all=True, append_images=photo_list[1:], duration=500, transparency=0,
        #                    loop=0, disposal=2)
    except:
        logger.info("转换动图出错" + traceback.format_exc())
