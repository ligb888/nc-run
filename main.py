from run import script
from task import task_main
from util import utils
from util import constants

# 初始化日志
logger = utils.get_logger(name="main", console=True)

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
    cpus = int(args.cpus)

    # 编译
    # script.make(args.home)
    # 执行
    # script.run(args.home, cpus, args.casename)

    # 读取输出文件
    task_main.start(args.home + constants.output + "/" + args.casename + "_0001.nc", cpus)

    # test
    # task_main.start("./input/TH_0001_0530.nc", cpus=6)

    logger.info("finished")
