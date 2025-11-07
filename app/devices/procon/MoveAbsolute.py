import sys
import time
from ctypes import *
from YKCat2 import *

pDll = CDLL("dll\YKCat2.dll")

handle = 0
axisIndex = 0

result = YKM_SysLoadLib(pDll, handle)
if result != YKE_RESULT_CODE.YKE_RET_OK.value:
    print(result)

status = YKS_BusStatus()
while True:
    result = YKM_ReadBusStatus(pDll, handle, YKE_NODE.YKE_ECAT_A.value, status);
    if result != YKE_RESULT_CODE.YKE_RET_OK.value:
        print(result)

    if status.bus_status == YKE_BUS_STATUS.YKE_BUS_STATUS_RUNNING.value:
        break

config = YKS_AxisProfileMotion()
result = YKM_GetAxisProfileMotion(pDll, handle, axisIndex, config)
if result != YKE_RESULT_CODE.YKE_RET_OK.value:
    print(result)

print(config.velocity)

result = YKM_MoveAbsolute(pDll, handle, axisIndex, c_double(100.0))
if result != YKE_RESULT_CODE.YKE_RET_OK.value:
    print(result)

time.sleep(1)

result = YKM_MoveAbsolute(pDll, handle, axisIndex, c_double(-100.0))
if result != YKE_RESULT_CODE.YKE_RET_OK.value:
    print(result)

input("按回车键继续...")




