import logging
import traceback
from time import sleep
from multiprocessing import Process, Queue

from task import task_nc
from util import utils


# 输出执行线程，循环获取输出任务进行执行
class TaskProcess(Process):
    def __init__(self, number, queue: Queue):
        self.queue = queue
        self.fail_count = 0
        self.task_args = None
        self.number = number
        super().__init__()

    def run(self) -> None:
        # 初始化日志
        utils.init_log(name="out_" + str(self.number), console=True)
        # 循环输出任务，失败一定次数后结束
        while self.fail_count < 5:
            try:
                self.task_args = self.queue.get_nowait()
            except:
                self.fail_count += 1
                sleep(1)
                continue

            # 执行获取到的任务
            try:
                task_nc.run(self.task_args)
            except:
                logging.error("任务执行失败" + traceback.format_exc())
                continue
        logging.info("进程结束")
