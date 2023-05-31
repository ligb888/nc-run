import os
from util import constants, utils
import subprocess
from time import sleep

# 初始化日志
logger = utils.get_logger(name="main", console=True)


# 编译
def make(home):
    sh = rf"""
    cd {home}{constants.source}
    sed -i '/FLAG_26 =/{{s/#//g}}' make.inc
    make clean > make_clean.log
    make > make.log
    """
    logger.info("make source start")
    os.system(sh)
    logger.info("make source end")

    sh = rf"""
    cd {home}{constants.surface_forcing}
    make clean > make_clean.log
    make > make.log
    """
    logger.info("make surface_forcing start")
    os.system(sh)
    logger.info("make surface_forcing end")

    sh = rf"""
    cd {home}{constants.surface_forcing}
    ./xsurfaceforce --filename=glbwnd.nml > xsurfaceforce.log
    """
    logger.info("run xsurfaceforce start")
    os.system(sh)
    logger.info("run xsurfaceforce end")

    sh = rf"""
    cd {home}{constants.source}
    sed -i '/FLAG_26 =/s/^/#/' make.inc
    make clean > make_clean.log
    make > make.log
    """
    logger.info("make source 2 start")
    os.system(sh)
    logger.info("make source 2 end")

    sh = rf"""
    cd {home}{constants.init_wqm}
    make clean > make_clean.log
    make > make.log
    """
    logger.info("make init_wqm start")
    os.system(sh)
    logger.info("make init_wqm end")

    sh = rf"""
    cd {home}{constants.init_wqm}
    ./xinit_file --filename=glbwnd.nml > xinit_file.log
    """
    logger.info("run xinit_file start")
    os.system(sh)
    logger.info("run xinit_file end")


def run(home, cpus, casename):
    # 执行CPU列表
    p_list = "0-" + str(cpus - 1)

    sh = rf"""\
cd {home}{constants.run}
#!/bin/bash
#BSUB -J FVCOM
#BSUB -n 1
#BSUB -R "span[ptile=1]"
#BSUB -o output_fvcomJ
#BSUB -e errput_fvcomJ
#BSUB -q normal
export OMP_NUM_THREADS=1
export I_MPI_PIN_PROCESSOR_LIST={p_list}
export I_MPI_FABRICS=shm:ofa
export I_MPI_FALLBACK=0
export I_MPI_DEBUG=5
mpirun ..{constants.source}/fvcom --casename={casename} >> supershuzhou.txt
exit 0
"""

    logger.info(rf"run fvcom start")
    p = subprocess.Popen(sh, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

    while p.poll() != 0:
        logger.info("fvcom running...")
        sleep(30)

    logger.info("run fvcom end")