from run import script
from task import task_main
from util import utils
from util import constants
import calendar
import time

# 初始化日志
logger = utils.get_logger(name="service", console=True)


def whole(home, cpus: int, casename, output_path):
    # 编译
    script.make(home)
    # 执行
    script.run(home, cpus, casename)
    # 读取输出文件
    task_main.start(home + constants.output + "/" + casename + "_0001.nc", cpus, output_path)

    # 执行完成
    logger.info("finished")


# 通过命令行调用
if __name__ == '__main__':
    # 获取入参
    args = utils.get_args()
    # 入参判断
    if args.home is None:
        logger.error("home不能为空")
        exit()
    elif args.cpus is None:
        logger.error("cpu数量不能为空")
        exit()
    elif args.casename is None:
        logger.error("实例名称不能为空")
        exit()
    try:
        cpus = int(args.cpus)
    except:
        logger.error("错误的cpu数量")

    # 执行
    whole(args.home, cpus, args.casename, rf"./output/{calendar.timegm(time.gmtime())}")
