import logging
from logging.handlers import TimedRotatingFileHandler
import os
import re
import argparse
import psutil


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=str, help='home directory.')
    parser.add_argument('--cpus', type=str, help='cpu number.')
    parser.add_argument('--casename', type=str, help='case name.')
    return parser.parse_args()


def is_running(process_name):
    pl = psutil.pids()
    result = False
    for pid in pl:
        if psutil.Process(pid).name() == process_name:
            if isinstance(pid, int):
                result = True
    return result


def get_logger(name="project", level=logging.INFO, console=False, path="./logs"):
    logger = logging.getLogger(name)
    if len(logger.handlers) > 0:
        return logger

    if not os.path.exists(path):
        os.makedirs(path)

    formatter = logging.Formatter("%(asctime)s-%(process)d-%(processName)s-%(levelname)s-%(filename)s[:%(lineno)d]-%(message)s")

    handler = TimedRotatingFileHandler(
        filename=path + '/' + name + '.log', encoding="utf-8",
        # when="MIDNIGHT", interval=1, backupCount=10
    )
    # handler.suffix = "%Y%m%d.log"
    # handler.extMatch = re.compile(r"^" + name + "_\d{4}\d{2}\d{2}.log$")
    handler.setLevel(level)
    handler.setFormatter(formatter)

    system_handler = logging.StreamHandler()
    system_handler.setLevel(level)
    system_handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(handler)
    if console:
        logger.addHandler(system_handler)

    # logging.info("logger initialization")
    return logger
