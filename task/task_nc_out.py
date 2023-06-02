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
            imageio.v2.mimsave(path + "/0.gif", frames, 'GIF', duration=3000)
    except:
        logger.info("转换动图出错" + traceback.format_exc())
