import task.task_main as task_main
from util import utils
import logging


if __name__ == '__main__':
    # 初始化日志
    utils.init_log(name="main", console=True)
    # 获取入参
    args = utils.get_args()
    # 入参判断
    if args.home is None:
        logging.error("home不能为空")
        exit()
    elif args.cpus is None:
        logging.error("cpu数量不能为空")
        exit()
    elif args.casename is None:
        logging.error("实例名称不能为空")
        exit()

    # 编译
    # script.make(args.home)
    # 执行
    # script.run(args.home, args.cpus, args.casename)

    # 读取输出文件
    task_main.start("", cpus=args.cpus)

    logging.info("finished")




