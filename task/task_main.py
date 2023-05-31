from multiprocessing import Queue
from time import sleep
from task.task_nc import TaskNcProcess
from util import utils

# 初始化日志
logger = utils.get_logger(name="main", console=True)


# 多进程执行任务
def start(input_path, cpus: int):
    # 任务队列
    task_queue = Queue()

    logger.info("开始进行输出任务...")
    # 多进程任务处理
    task_p = TaskNcProcess(cpus, input_path, task_queue)
    task_p.start()
    while task_p.is_alive():
        logger.info("输出任务进行中...")
        sleep(30)
    task_p.join()


