import logging
from multiprocessing import Queue, Process
from time import sleep
from task import task_nc
from task.task_process import TaskProcess


# 多进程执行任务
def start(input_path, cpus):
    # 任务队列
    task_queue = Queue()
    # 任务执行进程数组
    pool = []

    # 异步任务加载
    logging.info("开始加载输出文件...")
    Process(target=task_nc.get_tasks, args=(input_path, task_queue)).start()
    sleep(5)

    logging.info("开始执行输出任务...")
    # 创建任务执行进程
    for i in range(int(cpus)):
        pool.append(TaskProcess(i + 1, task_queue))
    # 启动进程
    for p in pool:
        p.start()
    # 等待进程执行
    for p in pool:
        p.join()
