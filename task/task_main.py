import logging
from multiprocessing import Queue
from time import sleep
from task.task_nc import TaskNcProcess


# 多进程执行任务
def start(input_path, cpus: int):
    # 任务队列
    task_queue = Queue()

    logging.info("开始进行输出任务...")
    # 多进程任务处理
    task_p = TaskNcProcess(cpus, input_path, task_queue)
    task_p.start()
    while task_p.is_alive():
        logging.info("输出任务进行中...")
        sleep(30)
    task_p.join()


