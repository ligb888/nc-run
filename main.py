from time import sleep

import utils
import logging
import constants
import os

# 初始化日志
utils.init_log(console=True)
# 获取入参
args = utils.get_args()
# 入参判断
if args.source_dir is None:
    logging.error("source_dir不能为空")

sh = rf"""
cd {args.source_dir}
sed -i '/FLAG_26 =/{{s/#//g}}' make.inc
make clean > make_clean.log
make > make.log
"""
logging.info("make source start")
os.system(sh)
logging.info("make source end")

sh = rf"""
cd {args.source_dir}{constants.surface_forcing}
make clean > make_clean.log
make > make.log
"""
logging.info("make surface_forcing start")
os.system(sh)
logging.info("make surface_forcing end")

sh = rf"""
cd {args.source_dir}{constants.surface_forcing}
./xsurfaceforce --filename=glbwnd.nml > xsurfaceforce.log
"""
logging.info("run xsurfaceforce start")
os.system(sh)
logging.info("run xsurfaceforce end")

sh = rf"""
cd {args.source_dir}
sed -i '/FLAG_26 =/s/^/#/' make.inc
make clean > make_clean.log
make > make.log
"""
logging.info("make source 2 start")
os.system(sh)
logging.info("make source 2 end")

sh = rf"""
cd {args.source_dir}{constants.init_wqm}
make clean > make_clean.log
make > make.log
"""
logging.info("make init_wqm start")
os.system(sh)
logging.info("make init_wqm end")

sh = rf"""
cd {args.source_dir}{constants.init_wqm}
./xinit_file --filename=glbwnd.nml > xinit_file.log 
"""
logging.info("run xinit_file start")
os.system(sh)
logging.info("run xinit_file end")

sh = rf"""
#!/bin/bash
#BSUB -J FVCOM
#BSUB -n 1 
#BSUB -R "span[ptile=1]"
#BSUB -o output_fvcomJ
#BSUB -e errput_fvcomJ
#BSUB -q normal
export OMP_NUM_THREADS=1
export I_MPI_PIN_PROCESSOR_LIST=0-11
export I_MPI_FABRICS=shm:ofa
export I_MPI_FALLBACK=0
export I_MPI_DEBUG=5
mpirun {args.source_dir}/fvcom --casename=TH >> supershuzhou.txt
"""
logging.info("run fvcom start")
os.system(sh)

is_run = True
while is_run:
    is_run = utils.is_running("fvcom")
    logging.info("fvcom running...")
    sleep(10)

logging.info("fvcom finished")


