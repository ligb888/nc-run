import logging
from multiprocessing import Queue
from task.task_nc import TaskNcProcess


# 多进程执行任务
def start(input_path, cpus: int):
    # 任务队列
    task_queue = Queue()

    # 多进程任务处理
    task_p = TaskNcProcess(cpus, input_path, task_queue)
    task_p.start()
    task_p.join()

