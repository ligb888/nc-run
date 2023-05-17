import logging
from logging.handlers import TimedRotatingFileHandler
import os
import re
import argparse
import psutil


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_dir', type=str, help='source directory.')
    return parser.parse_args()


def is_running(process_name):
    pl = psutil.pids()
    result = False
    for pid in pl:
        if psutil.Process(pid).name() == process_name:
            if isinstance(pid, int):
                result = True
    return result


def init_log(name="project", level=logging.INFO, console=False, path="./log"):
    if not os.path.exists(path):
        os.makedirs(path)

    formatter = logging.Formatter("%(asctime)s-%(process)d-%(levelname)s-%(filename)s[:%(lineno)d]-%(message)s")

    handler = TimedRotatingFileHandler(
        filename=path + '/' + name + '.log',
        when="MIDNIGHT", interval=1, backupCount=10, encoding="utf-8"
    )
    handler.suffix = "%Y%m%d.log"
    handler.extMatch = re.compile(r"^" + name + "_\d{4}\d{2}\d{2}.log$")
    handler.setLevel(level)
    handler.setFormatter(formatter)

    system_handler = logging.StreamHandler()
    system_handler.setLevel(level)
    system_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)
    if console:
        logger.addHandler(system_handler)

    logging.info("日志初始化完成")
