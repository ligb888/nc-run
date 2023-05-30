from multiprocessing import Queue
from task.task_process import TaskProcess


# 多进程执行任务
def start(input_path, cpus):
    # 任务队列
    task_queue = Queue()
    # 进程数组
    pool = []
    # 创建进程
    for i in range(int(cpus)):
        pool.append(TaskProcess(i + 1, task_queue))
    # 启动进程
    for p in pool:
        p.start()
    # 等待进程执行
    for p in pool:
        p.join()