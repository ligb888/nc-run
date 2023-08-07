import math
from multiprocessing import Pool
import numpy as np
from PIL import Image
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.font_manager as fm
from pyproj import Proj
from util import utils
import traceback
import os
import csv
import imageio
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip

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


def out_img(img_path, curr_x, curr_y, vmin, vmax, ctime, var, img_data, unit=""):
    try:
        # 基础设置
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        # 参数处理
        unit_str = ""
        if unit is not None and unit != "":
            unit_str = rf"({unit})"
        # 画图
        plt.figure(figsize=(9.6, 7.2))
        plt.title(f"{var}{unit_str}\n{ctime}", loc="right")
        plt.xlim(-2000, 70000)
        plt.ylim(-2000, 70000)
        # 设置刻度label
        ax = plt.gca()
        ax.set_xticks([9347.05, 25241.15, 41135.25, 57029.35])
        ax.set_xticklabels(["120°0'", "120°10'", "120°20'", "120°30'"], fontsize=12)
        ax.set_yticks([8697.78, 27193.34, 45688.9, 64184.46])
        ax.set_yticklabels(["31°0'", "31°10'", "31°20'", "31°30'"], fontsize=12)
        plt.grid()
        # 设置图片数据
        plt.scatter(curr_x, curr_y, s=16, alpha=0.8, c=img_data, cmap='jet', linewidth=0, vmin=vmin, vmax=vmax)
        plt.colorbar()
        plt.savefig(img_path)
    except:
        logger.info("生成图片出错" + traceback.format_exc())
    finally:
        plt.close()


def out_flow_draw(img_path, curr_x, curr_y, ctime, k, i, angle_arr, speed_arr, speed_min, speed_range):
    try:
        # 基础设置
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        # 图片大小
        plt.figure(figsize=(24, 20))
        # 标题
        plt.title(f"流场图-深度{k}\n{ctime}", loc="right", fontdict=dict(fontsize=36, color='black', weight='bold'))
        ax = plt.gca()

        # 设置字体、边框宽度
        bwidth = 2
        ax.spines['bottom'].set_linewidth(bwidth)
        ax.spines['left'].set_linewidth(bwidth)
        ax.spines['top'].set_linewidth(bwidth)
        ax.spines['right'].set_linewidth(bwidth)

        # 设置坐标系范围
        plt.xlim(-2000, 70000)
        plt.ylim(-2000, 70000)
        # 设置刻度label
        ax.set_xticks([9347.05, 25241.15, 41135.25, 57029.35])
        ax.set_xticklabels(["120°0'", "120°10'", "120°20'", "120°30'"], fontsize=32)
        ax.set_yticks([8697.78, 27193.34, 45688.9, 64184.46])
        ax.set_yticklabels(["31°0'", "31°10'", "31°20'", "31°30'"], fontsize=32)
        plt.grid()

        # 增加标尺
        speed_max = speed_min + speed_range
        label_speed = math.floor(speed_max*100)/100
        label = rf"{label_speed} m/s"
        fontprops = fm.FontProperties(size=24, family='monospace')
        scalebar = AnchoredSizeBar(ax.transData, 2360 * label_speed / speed_max, label, 'upper right',
                                   sep=10, borderpad=2, pad=1, color='b', fontproperties=fontprops, width=10,
                                   size_vertical=100, fill_bar=True)
        ax.add_artist(scalebar)

        for j in range(len(curr_y)):
            if j % 10 != 0:
                continue
            speed = (speed_arr[j] - speed_min) / speed_range
            if speed < 0:
                speed = 0
            elif speed >= 1:
                speed = 0.999
            # speed = 0.4 + 0.6 * speed

            # 颜色表示流速
            # color = plt.cm.jet(speed)
            # color = plt.cm.Blues(speed)
            # color = plt.cm.GnBu(speed)
            color = 'b'
            alpha = 1
            # 透明度表示流速
            # color = "b"
            # alpha = speed

            # 通过长度和三角函数求出箭头终点坐标
            width = 120
            length = 60 + speed * 2000
            if length < width*2:
                width = length / 2
                if width < 60:
                    width = 60
            x_add = length * math.cos(math.radians(angle_arr[j]))
            y_add = length * math.sin(math.radians(angle_arr[j]))
            plt.arrow(curr_x[j], curr_y[j], x_add, y_add, width=width, fc=color, ec=color, alpha=alpha)
        # 保存后清空图
        plt.savefig(rf"{img_path}/{i}.png")
    except:
        logger.info("生成图片出错" + traceback.format_exc())
    finally:
        plt.close()


# 透明背景的流场图
def out_flow_draw2(img_path, curr_x, curr_y, ctime, k, i, angle_arr, speed_arr, speed_min, speed_range):
    try:
        # 基础设置
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        # 图片大小
        plt.figure(figsize=(24, 20))
        # 标题
        plt.title(f"流场图-深度{k}\n{ctime}", loc="right", fontdict=dict(fontsize=36, color='white', weight='bold'))
        ax = plt.gca()

        # 隐藏刻度、标签、周边空白等
        plt.xticks(())
        plt.yticks(())
        ax.spines['top'].set_color('none')
        ax.spines['bottom'].set_color('none')
        ax.spines['left'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        # ax.xaxis.set_major_locator(plt.NullLocator())
        # ax.yaxis.set_major_locator(plt.NullLocator())
        # plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        # plt.margins(0, 0)

        # 设置坐标系范围
        plt.xlim(-2000, 70000)
        plt.ylim(-2000, 70000)

        # 增加标尺
        speed_max = speed_min + speed_range
        label_speed = math.floor(speed_max*100)/100
        label = rf"{label_speed} m/s"
        fontprops = fm.FontProperties(size=24, family='monospace')
        scalebar = AnchoredSizeBar(ax.transData, 2360 * label_speed / speed_max, label, 'upper right',
                                   sep=10, borderpad=2, pad=1, color='white', fontproperties=fontprops, width=10, frameon=False,
                                   size_vertical=100, fill_bar=True)
        ax.add_artist(scalebar)

        for j in range(len(curr_y)):
            if j % 10 != 0:
                continue
            speed = (speed_arr[j] - speed_min) / speed_range
            if speed < 0:
                speed = 0
            elif speed >= 1:
                speed = 0.999
            speed = 0.3 + 0.7 * speed

            # 颜色表示流速
            color = plt.cm.jet(speed)
            # color = plt.cm.Blues(speed)
            # color = plt.cm.GnBu(speed)
            # color = plt.cm.Wistia(speed)
            # color = 'b'
            alpha = 1
            # 透明度表示流速
            # color = "b"
            # alpha = speed

            # 通过长度和三角函数求出箭头终点坐标
            width = 120
            length = 60 + speed * 2000
            if length < width*2:
                width = length / 2
                if width < 60:
                    width = 60
            x_add = length * math.cos(math.radians(angle_arr[j]))
            y_add = length * math.sin(math.radians(angle_arr[j]))
            plt.arrow(curr_x[j], curr_y[j], x_add, y_add, width=width, fc=color, ec=color, alpha=alpha)
        # 保存后清空图
        plt.savefig(rf"{img_path}/{i}.png", transparent=True)
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
                img = imageio.v2.imread(path + "/" + file)
                frames.append(img)
        if len(frames) > 0:
            imageio.v2.mimsave(path + "/0.gif", frames, 'GIF', duration=500, disposal=2)
    except:
        logger.info("转换动图出错" + traceback.format_exc())


def out_mp4(path):
    try:
        path_list = os.listdir(path)
        path_list.sort(key=lambda x: int(x.split('.')[0]))
        image_list = []
        for file in path_list:
            if not os.path.isdir(file) and os.path.splitext(file)[-1] == ".png":
                image_list.append(path + "/" + file)
        clip = ImageSequenceClip(image_list, fps=2)
        clip.write_videofile(path + "/0.mp4", fps=2)
    except:
        logger.info("转换视频出错" + traceback.format_exc())
