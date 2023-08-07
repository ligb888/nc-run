from task import task_main
import calendar
import time

if __name__ == '__main__':
    task_main.start("./input/TH_0001_0530.nc", 6, rf"./output/{calendar.timegm(time.gmtime())}")
