from multiprocessing import Process
from flask import Flask, request
from service import whole
from util import utils
import calendar
import time

logger = utils.get_logger(name="api", console=True)
app = Flask(__name__, static_folder='output')
whole_service = None


@app.route('/whole', methods=["POST"])
def world():
    home = request.json.get("home")
    cpus = request.json.get("cpus")
    casename = request.json.get("casename")
    output_path = request.json.get("output_path")

    # 暂时先给默认值
    if home is None:
        home = "/home/water/zhao"
    if cpus is None:
        cpus = "24"
    if casename is None:
        casename = "TH"
    if output_path is None:
        output_path = rf"/output/{str(calendar.timegm(time.gmtime()))}"

    # 入参判断
    if home is None:
        return {"code": 400, "msg": "home文件夹不能为空"}
    elif cpus is None:
        return {"code": 400, "msg": "cpu数量不能为空"}
    elif casename is None:
        return {"code": 400, "msg": "实例名称不能为空"}
    elif output_path is None:
        return {"code": 400, "msg": "输出文件夹不能为空"}
    try:
        cpus = int(cpus)
    except:
        return {"code": 400, "msg": "错误的cpu数量"}

    # 执行
    global whole_service
    if whole_service is not None and whole_service.is_alive():
        return {"code": 406, "msg": "服务正在运行..."}

    whole_service = Process(target=whole, args=(home, cpus, casename, "." + output_path))
    whole_service.start()
    return {"code": 200, "output_path": output_path}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9001)
