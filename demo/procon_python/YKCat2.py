from enum import Enum
from ctypes import *
# <summary>
# 系统定义
# </summary>
class YKE_SYSTEM_DEFINE (Enum):
	#/ </summary>
	YKE_MAGIC_FLAG = 0x13575A5A

	#/ </summary>
	YKE_PROCON_VER = 1512

	#/ </summary>
	YKE_DIGITAL_INPUT_NUM = 4096

	#/ </summary>
	YKE_DIGITAL_OUTPUT_NUM = 4096

	#/ </summary>
	YKE_DIGITAL_OUTPUT_CYCLE_NUM = 1024

	#/ </summary>
	YKE_MASTER_NUM = 4

	#/ </summary>
	YKE_OSC_NUM = 8

	#/ </summary>
	YKE_OSC_ITEM_NUM = 64

	#/ </summary>
	YKE_INTER_AXIS_NUM = 32

	#/ </summary>
	YKE_SOFT_COMPARE_NUM = 128

	#/ </summary>
	YKE_SOFT_COMPARE_DEPTH = 512

	#/ </summary>
	YKE_SOFT_PROBE_NUM = 128

	#/ </summary>
	YKE_SOFT_PROBE_DEPTH = 512

	#/ </summary>
	YKE_HARD_PROBE_DEPTH = 512

	#/ </summary>
	YKE_AXIS_SOFT_PROBE_NUM = 4

	#/ </summary>
	YKE_PITCH1D_NUM = 2048

	#/ </summary>
	YKE_PITCH2D_NUM = 512

	#/ </summary>
	YKE_EVENT_NUM = 1024

	#/ </summary>
	YKE_WAIT_NUM = 1024

	#/ </summary>
	YKE_GROUP_NUM = 32

	#/ </summary>
	YKE_GROUP_DEPTH = 4096

	#/ </summary>
	YKE_GROUP_OUTPUT_NUM = 32

	#/ </summary>
	YKE_AXIS_NUM = 1024

	#/ </summary>
	YKE_LOGGER_ITEM = 32

	#/ </summary>
	YKE_EXC_CONDI = 16

	#/ </summary>
	YKE_REGISTER_SIZE = 0x100000

	#/ </summary>
	YKE_EMG_STOP_INPUT_NUM = 8

	#/ </summary>
	YKE_EMG_STOP_OUTPUT_NUM = 4

	#/ </summary>
	YKE_EMG_STOP_NUM = 32

	#/ </summary>
	YKE_PVT_DEPTH = 4096

	#/ </summary>
	YKE_FILE_PATH_SIZE = 512

	#/ </summary>
	YKE_FILE_NAME_SIZE = 64

	#/ </summary>
	YKE_LOGGER_PROCCESS = 32

	#/ </summary>
	YKE_MULTI_AXIS_NUM = 128

	#/ </summary>
	YKE_CIRCLE_ZONE_NUM = 32

	#/ </summary>
	YKE_API_BUFFER_NUM = 512

# <summary>
# 函数返回值定义
# </summary>
class YKE_RESULT_CODE (Enum):
	#/ </summary>
	YKE_RET_OK = 0

	#/ </summary>
	YKE_RET_SYS_LOAD_RTA = 0x0100

	#/ </summary>
	YKE_RET_SYS_OPEN_GW = 0x0101

	#/ </summary>
	YKE_RET_SYS_CONNECT_GW = 0x0102

	#/ </summary>
	YKE_RET_SYS_OPEN_MEM = 0x0103

	#/ </summary>
	YKE_RET_SYS_GW_TIMOUT = 0x0104

	#/ </summary>
	YKE_RET_SYS_LIC = 0x0105

	#/ </summary>
	YKE_RET_SYS_RTOS = 0x0106

	#/ </summary>
	YKE_RET_SYS_EXIT = 0x0107

	#/ </summary>
	YKE_RET_SYS_COLD = 0x0108

	#/ </summary>
	YKE_RET_SYS_ACCESS = 0x0109

	#/ </summary>
	YKE_RET_SYS_MISMATCH = 0x010a

	#/ </summary>
	YKE_RET_SYS_LANG_TEXT = 0x010b

	#/ </summary>
	YKE_RET_SYS_CHN = 0x010c

	#/ </summary>
	YKE_RET_SYS_FUN = 0x010d

	#/ </summary>
	YKE_RET_SYS_DYNC_MEM = 0x010e

	#/ </summary>
	YKE_RET_SYS_COLD_ERR = 0x010f

	#/ </summary>
	YKE_RET_SYS_NODEA_ENA = 0x0110

	#/ </summary>
	YKE_RET_SYS_NODEO = 0x0111

	#/ </summary>
	YKE_RET_SYS_NODEB_ENA = 0x0112

	#/ </summary>
	YKE_RET_SYS_NODEB_RUN = 0x0113

	#/ </summary>
	YKE_RET_SYS_NODEC_ENA = 0x0114

	#/ </summary>
	YKE_RET_SYS_NODEC_RUN = 0x0115

	#/ </summary>
	YKE_RET_SYS_NODED_ENA = 0x0116

	#/ </summary>
	YKE_RET_SYS_NODED_RUN = 0x0117

	#/ </summary>
	YKE_RET_SYS_RUNTIME_STOP = 0x0118

	#/ </summary>
	YKE_RET_SYS_INTIME_MEM = 0x0119

	#/ </summary>
	YKE_RET_SYS_NODE_ENA = 0x011E

	#/ </summary>
	YKE_RET_SYS_NODE_IDX = 0x011F

	#/ </summary>
	YKE_RET_SYS_CREATE_DIR = 0x0120

	#/ </summary>
	YKE_RET_SYS_SIM_CONNECT = 0x0121

	#/ </summary>
	YKE_RET_SYS_NULL = 0x0122

	#/ </summary>
	YKE_RET_YKSRV_NOT_INSTALL = 0x0123

	#/ </summary>
	YKE_RET_SYS_YKSRV_NOT_START = 0x0124

	#/ </summary>
	YKE_RET_YKSRV_OP_FAIL = 0x0125

	#/ </summary>
	YKE_RET_YKSRV_ACCESS = 0x0126

	#/ </summary>
	YKE_RET_SYS_API_VER = 0x012F

	#/ </summary>
	YKE_RET_SYS_LOG_NULL = 0x0130

	#/ </summary>
	YKE_RET_API_BUFFER = 0x140

	#/ </summary>
	YKE_RET_API_BUFFER_N = 0x141

	#/ </summary>
	YKE_RET_SYS_YKCATN_CONNECT = 0x0180

	#/ </summary>
	YKE_RET_SYS_YKCATN_TIMEOUT = 0x0181

	#/ </summary>
	YKE_RET_SYS_YKCATN_HANDLE = 0x0182

	#/ </summary>
	YKE_RET_SYS_YKCATN_SIZE = 0x0183

	#/ </summary>
	YKE_RET_INS_PARA = 0x0200

	#/ </summary>
	YKE_RET_INS_NEG = 0x0201

	#/ </summary>
	YKE_RET_INS_DOUBLE = 0x0202

	#/ </summary>
	YKE_RET_INS_ENUM = 0x0203

	#/ </summary>
	YKE_RET_INS_PTR = 0x0204

	#/ </summary>
	YKE_RET_EMG_HARD = 0x0220

	#/ </summary>
	YKE_RET_EMG_SOFT = 0x0221

	#/ </summary>
	YKE_RET_LIMIT_H = 0x0230

	#/ </summary>
	YKE_RET_LIMIT_S = 0x0231

	#/ </summary>
	YKE_RET_CIRCLE_ZONE = 0x0232

	#/ </summary>
	YKE_RET_IO_REVERSE_BUFFER_OV = 0x0240

	#/ </summary>
	YKE_RET_AXIS_SIM_POS = 0x0300

	#/ </summary>
	YKE_RET_AXIS_SIM_TIM = 0x0301

	#/ </summary>
	YKE_RET_AXIS_SIM_TIMOUT = 0x0302

	#/ </summary>
	YKE_RET_AXIS_OVERRIDE_INVALID = 0x0313

	#/ </summary>
	YKE_RET_AXIS_BUSY = 0x0314

	#/ </summary>
	YKE_RET_AXIS_READY = 0x0315

	#/ </summary>
	YKE_RET_AXIS_INDEX = 0x0316

	#/ </summary>
	YKE_RET_AXIS_MOTION_TYPE = 0x0317

	#/ </summary>
	YKE_RET_AXIS_CSP = 0x0318

	#/ </summary>
	YKE_RET_FOLLOW_MASTER = 0x0400

	#/ </summary>
	YKE_RET_FOLLOW_CAM_MPOS = 0x0401

	#/ </summary>
	YKE_RET_MULTI_AXIS_ACITVE = 0x0420

	#/ </summary>
	YKE_RET_MULTI_AXIS_NUM = 0x0421

	#/ </summary>
	YKE_RET_MULTI_AXIS_NODE = 0x0430

	#/ </summary>
	YKE_RET_PVT_BUFFER_OV = 0x0500

	#/ </summary>
	YKE_RET_PVT_FIRST = 0x0501

	#/ </summary>
	YKE_RET_PVTS_NUM = 0x0502

	#/ </summary>
	YKE_RET_PVTS_DYNC = 0x0503

	#/ </summary>
	YKE_RET_PVTS_TIM = 0x0504

	#/ </summary>
	YKE_RET_GROUP_INIT = 0x0600

	#/ </summary>
	YKE_RET_GROUP_DEINIT = 0x0601

	#/ </summary>
	YKE_RET_GROUP_AXIS_INDEX_REPEAT = 0x0602

	#/ </summary>
	YKE_RET_GROUP_ACTIVE = 0x0603

	#/ </summary>
	YKE_RET_GROUP_BUFFER_FULL = 0x0604

	#/ </summary>
	YKE_RET_GROUP_AXIS_WARN = 0x0605

	#/ </summary>
	YKE_RET_GROUP_WARN = 0x0606

	#/ </summary>
	YKE_RET_GROUP_AXIS_SINGLE = 0x0607

	#/ </summary>
	YKE_RET_GROUP_AXIS_CSP = 0x0608

	#/ </summary>
	YKE_RET_GROUP_AXIS_INDEX_REPEAT2 = 0x0609

	#/ </summary>
	YKE_RET_GROUP_PAUSE = 0x0610

	#/ </summary>
	YKE_RET_GROUP_INC = 0x0611

	#/ </summary>
	YKE_RET_GROUP_STOPPING = 0x0612

	#/ </summary>
	YKE_RET_GROUP_AXIS_GANTRY = 0x0613

	#/ </summary>
	YKE_RET_GROUP_AXIS_NODE = 0x0614

	#/ </summary>
	YKE_RET_PITCH_ENA = 0x0700

	#/ </summary>
	YKE_RET_PITCH_REPEAT = 0x0701

	#/ </summary>
	YKE_RET_PITCH_DATA = 0x0702

	#/ </summary>
	YKE_RET_PITCH_DRV = 0x0703

	#/ </summary>
	YKE_RET_PITCH_USED = 0x0704

	#/ </summary>
	YKE_RET_BUS_INIT = 0x0800

	#/ </summary>
	YKE_RET_BUS_SDO_OV = 0x0801

	#/ </summary>
	YKE_RET_BUS_SDO_U = 0x0802

	#/ </summary>
	YKE_RET_BUS_SDO_OD = 0x0803

	#/ </summary>
	YKE_RET_BUS_SDO_TIMOUT = 0x0804

	#/ </summary>
	YKE_RET_BUS_OD_PDO = 0x0805

	#/ </summary>
	YKE_RET_BUS_OD_SDO = 0x0806

	#/ </summary>
	YKE_RET_BUS_OD_RD = 0x0807

	#/ </summary>
	YKE_RET_BUS_SIM_SCAN = 0x0808

	#/ </summary>
	YKE_RET_BUS_SNAP_UNUSED = 0x0809

	#/ </summary>
	YKE_RET_BUS_SNAP_IDEL = 0x0810

	#/ </summary>
	YKE_RET_ERROR_DRV_WARN = 0x0820

	#/ </summary>
	YKE_RET_PROBE_ACTIVE = 0x0900

	#/ </summary>
	YKE_RET_SOFT_COMPARE_ACTIVE = 0x0a00

	#/ </summary>
	YKE_RET_COMPARE_BUFFER_OV = 0x0a01

	#/ </summary>
	YKE_RET_COMPARE_BUFFER_FIX = 0x0a02

	#/ </summary>
	YKE_RET_NTF_LOAD = 0x0B00

	#/ </summary>
	YKE_RET_NTF_EXIST = 0x0B01

	#/ </summary>
	YKE_RET_WAIT_INIT = 0x0B60

	#/ </summary>
	YKE_RET_WAIT_DEL = 0x0B61

	#/ </summary>
	YKE_RET_WAIT_TIMEOUT = 0x0B62

	#/ </summary>
	YKE_RET_WAIT_FAIL = 0x0B63

	#/ </summary>
	YKE_RET_WAIT_BUSY = 0x0B64

	#/ </summary>
	YKE_RET_WAIT_OPEN = 0x0B65

	#/ </summary>
	YKE_RET_WAIT_SYS_RESET = 0x0B66

	#/ </summary>
	YKE_RET_WAIT_INS_RESET = 0x0B67

	#/ </summary>
	YKE_RET_WAIT_EXIT = 0x0B68

	#/ </summary>
	YKE_RET_PROEN_SHAREM = 0x0C00

	#/ </summary>
	YKE_RET_PROEN_OV = 0x0C01

	#/ </summary>
	YKE_RET_PROEN_EXIST = 0x0C02

	#/ </summary>
	YKE_RET_PROEN_OPEN_FAIL = 0x0C10

	#/ </summary>
	YKE_RET_PROEN_MAGIC_FAIL = 0x0C11

	#/ </summary>
	YKE_RET_PROEN_TIMEOUT = 0x0C12

	#/ </summary>
	YKE_RET_PROEN_FILENAME = 0x0C13

	#/ </summary>
	YKE_RET_PROEN_FILE_EXT = 0x0C14

	#/ </summary>
	YKE_RET_EVENT_NODE = 0x0d00

	#/ </summary>
	YKE_RET_EVENT_BUSY = 0x0d01

	#/ </summary>
	YKE_RET_EVENT_ENCODER = 0x0d02

	#/ </summary>
	YKE_RET_CIRCLE_ZONE_INIT = 0x0d40

	#/ </summary>
	YKE_RET_CIRCLE_ZONE_INDEX = 0x0d41

	#/ </summary>
	YKE_RET_DOGGLE_TIMEOUT = 0x0d80

	#/ </summary>
	YKE_RET_NTF_INIT = 0x0da0

	#/ </summary>
	YKE_RET_NTF_API_BUFFER_INIT = 0x0da1

	#/ </summary>
	YKE_RET_NTF_API_BUFFER_CH_INIT = 0x0da2

	#/ </summary>
	YKE_RET_NTF_API_BUFFER_CH_OV = 0x0da3

	#/ </summary>
	YKE_RET_NTF_API_BUFFER_INS = 0x0da4

# <summary>
# 运动错误代码
# </summary>
class YKE_MC_ERROR (Enum):
	#/ </summary>
	YKE_ERR_MC_OK = 0x0000

	#/ </summary>
	YKE_ERR_MC_SOFT_EMG = 0x0001

	#/ </summary>
	YKE_ERR_MC_HARD_EMG = 0x0002

	#/ </summary>
	YKE_ERR_MC_SYS_STOP = 0x0003

	#/ </summary>
	YKE_ERR_MC_AXIS_READY = 0x0101

	#/ </summary>
	YKE_ERR_MC_LIMIT_HARDP = 0x0102

	#/ </summary>
	YKE_ERR_MC_LIMIT_HARDN = 0x0103

	#/ </summary>
	YKE_ERR_MC_LIMIT_SOFTP = 0x0104

	#/ </summary>
	YKE_ERR_MC_LIMIT_SOFTN = 0x0105

	#/ </summary>
	YKE_ERR_MC_POSITION_LAG = 0x0106

	#/ </summary>
	YKE_ERR_MC_INP = 0x0107

	#/ </summary>
	YKE_ERR_MC_DRV_OP_MODE = 0x0108

	#/ </summary>
	YKE_ERR_MC_DRV_OP_MODE_ACTIVE = 0x0109

	#/ </summary>
	YKE_ERR_MC_AXIS_SLAVE_STOP = 0x010a

	#/ </summary>
	YKE_ERR_MC_GANTRY_LAG = 0x0120

	#/ </summary>
	YKE_ERR_MC_HOME_LIMIT = 0x0150

	#/ </summary>
	YKE_ERR_MC_HOME_HOME = 0x0151

	#/ </summary>
	YKE_ERR_MC_HOME_PROBE = 0x0152

	#/ </summary>
	YKE_ERR_MC_HOME_3537 = 0x0153

	#/ </summary>
	YKE_ERR_MC_HOME_STOP1 = 0x0154

	#/ </summary>
	YKE_ERR_MC_HOME_TOUCH = 0x0155

	#/ </summary>
	YKE_ERR_MC_HOME_OFFLINE = 0x0156

	#/ </summary>
	YKE_ERR_MC_PLS_PROBE_CONFIG = 0x160

	#/ </summary>
	YKE_ERR_MC_PITCH2D_VEL = 0x170

	#/ </summary>
	YKE_ERR_MC_DRV_WARN = 0x0200

	#/ </summary>
	YKE_ERR_MC_DRV_PP = 0x0201

	#/ </summary>
	YKE_ERR_MC_DRV_HM = 0x0202

	#/ </summary>
	YKE_ERR_MC_PV_SDO = 0x0203

	#/ </summary>
	YKE_ERR_MC_PP_SDO = 0x0204

	#/ </summary>
	YKE_ERR_MC_TORQUE_PDO = 0x0208

	#/ </summary>
	YKE_ERR_MC_POWER_ON = 0x0210

	#/ </summary>
	YKE_ERR_MC_CLR_DRV = 0x0211

	#/ </summary>
	YKE_ERR_MC_GROUP_PATH = 0x0250

	#/ </summary>
	YKE_ERR_MC_GROUP_CIR = 0x0251

	#/ </summary>
	YKE_ERR_MC_GROUP_AXIS = 0x0252

	#/ </summary>
	YKE_ERR_MC_GROUP_AXIS_INDEX = 0x0253

	#/ </summary>
	YKE_ERR_MC_GROUP_AXIS_ACTIVE1 = 0x0254

	#/ </summary>
	YKE_ERR_MC_GROUP_AXIS_INPOS = 0x0255

	#/ </summary>
	YKE_ERR_MC_GROUP_AXIS_ACTIVE2 = 0x0256

	#/ </summary>
	YKE_ERR_MC_GROUP_AXIS_READY = 0x0257

	#/ </summary>
	YKE_ERR_MC_GROUP_AXIS_LIMIT = 0x0258

	#/ </summary>
	YKE_ERR_MC_GROUP_HARD_EMG = 0x0259

	#/ </summary>
	YKE_ERR_MC_GROUP_SOFT_EMG = 0x025a

	#/ </summary>
	YKE_ERR_MC_GROUP_CNC_EXT = 0x0260

	#/ </summary>
	YKE_ERR_MC_GROUP_CNC_NUM = 0x0261

	#/ </summary>
	YKE_ERR_MC_GROUP_CNC_LINE = 0x0262

	#/ </summary>
	YKE_ERR_MC_GROUP_CNC_CIR = 0x0263

	#/ </summary>
	YKE_ERR_MC_GROUP_CNC_GCODE = 0x0264

	#/ </summary>
	YKE_ERR_MC_GROUP_CNC_FILE = 0x0265

	#/ </summary>
	YKE_ERR_MC_END = 0x0300

# <summary>
# 系统错误类型
# </summary>
class YKE_SYSTEM_ERROR (Enum):
	#/ </summary>
	YKE_ERR_SYS_APP_NONE = 0x0000

	#/ </summary>
	YKE_ERR_SYS_FILE_VER = 0x0001

	#/ </summary>
	YKE_ERR_SYS_FILE_CFG = 0x0002

	#/ </summary>
	YKE_ERR_SYS_FILE_EXIST = 0x0003

	#/ </summary>
	YKE_ERR_SYS_FILE_READ = 0x0004

	#/ </summary>
	YKE_ERR_SYS_CARD_VER1 = 0x0005

	#/ </summary>
	YKE_ERR_SYS_CARD_VER2 = 0x0006

	#/ </summary>
	YKE_ERR_SYS_BRD_VER = 0x0007

	#/ </summary>
	YKE_ERR_SYS_CLK_BASE = 0x0008

	#/ </summary>
	YKE_ERR_SYS_DC_125US = 0x0009

	#/ </summary>
	YKE_ERR_SYS_YKGROUP_VER = 0x000A

	#/ </summary>
	YKE_ERR_SYS_CARD_UNKNOWN = 0x000B

	#/ </summary>
	YKE_ERR_SYS_APP_INIT_I = 0x0010

	#/ </summary>
	YKE_ERR_SYS_NTF_LOAD = 0x0011

	#/ </summary>
	YKE_ERR_SYS_NTF_INIT = 0x0012

	#/ </summary>
	YKE_ERR_SYS_NODEB_ENA = 0x0013

	#/ </summary>
	YKE_ERR_SYS_NODEC_ENA = 0x0014

	#/ </summary>
	YKE_ERR_SYS_NODED_ENA = 0x0015

	#/ </summary>
	YKE_ERR_SYS_NODEB_FAIL = 0x0016

	#/ </summary>
	YKE_ERR_SYS_NODEC_FAIL = 0x0017

	#/ </summary>
	YKE_ERR_SYS_NODED_FAIL = 0x0018

	#/ </summary>
	YKE_ERR_SYS_NTF_PAYLOAD = 0x0019

	#/ </summary>
	YKE_ERR_SYS_BRD_INIT = 0x0020

	#/ </summary>
	YKE_ERR_SYS_APP_WTD = 0x0030

	#/ </summary>
	YKE_ERR_SYS_LIC = 0x0031

	#/ </summary>
	YKE_ERR_SYS_DYNC_MEM = 0x0032

	#/ </summary>
	YKE_ERR_SYS_APP_CHK_NIC = 0x0040

	#/ </summary>
	YKE_ERR_SYS_SLAVE_CHKNUM = 0x0041

	#/ </summary>
	YKE_ERR_SYS_LINK_ECAT = 0x0042

	#/ </summary>
	YKE_ERR_SYS_DC_SHIFT = 0x0043

	#/ </summary>
	YKE_ERR_SYS_DISCONNECT = 0x0044

	#/ </summary>
	YKE_ERR_SYS_PDO1_WKC = 0x0045

	#/ </summary>
	YKE_ERR_SYS_PDO2_WKC = 0x0046

	#/ </summary>
	YKE_ERR_SYS_PDO3_WKC = 0x0047

	#/ </summary>
	YKE_ERR_SYS_PDO4_WKC = 0x0048

	#/ </summary>
	YKE_ERR_SYS_DATA_TYPE = 0x004a

	#/ </summary>
	YKE_ERR_SYS_NIC_SWAP = 0x004b

	#/ </summary>
	YKE_ERR_SYS_APP_HDCHANGE = 0x0051

	#/ </summary>
	YKE_ERR_SYS_DC_CYCLE = 0x0052

	#/ </summary>
	YKE_ERR_SYS_PLS_OVERFLOW = 0x0060

	#/ </summary>
	YKE_ERR_SYS_PLS_MAX = 0x0061

	#/ </summary>
	YKE_ERR_SYS_APP_BRDCHANGE = 0x0062

	#/ </summary>
	YKE_ERR_SYS_EMG_OFFLINE = 0x070

	#/ </summary>
	YKE_ERR_SYS_EMG_SOFT = 0x071

	#/ </summary>
	YKE_ERR_SYS_EMG_HARD = 0x072

	#/ </summary>
	YKE_ERR_EVENT_START_AXIS = 0x080

	#/ </summary>
	YKE_ERR_EVENT_START_GROUP = 0x081

	#/ </summary>
	YKE_ERR_EVENT_READ_PDO = 0x082

	#/ </summary>
	YKE_ERR_EVENT_WRITE_PDO = 0x083

# <summary>
# 从站错误类型
# </summary>
class YKE_SLAVE_ERROR (Enum):
	#/ </summary>
	YKE_ERR_SLAVE_PDO_NONE = 0x0000

	#/ </summary>
	YKE_ERR_SLAVE_PDO_DTYPE = 0x0100

	#/ </summary>
	YKE_ERR_SLAVE_PDO = 0x0101

	#/ </summary>
	YKE_ERR_SLAVE_VID = 0x0102

	#/ </summary>
	YKE_ERR_SLAVE_PID = 0x0103

	#/ </summary>
	YKE_ERR_SLAVE_TO_INIT = 0x0104

	#/ </summary>
	YKE_ERR_SLAVE_TO_PREOP = 0x0105

	#/ </summary>
	YKE_ERR_SLAVE_TO_SAFEOP = 0x0106

	#/ </summary>
	YKE_ERR_SLAVE_TO_OP = 0x0107

	#/ </summary>
	YKE_ERR_SLAVE_SDO_WRITE = 0x0108

	#/ </summary>
	YKE_ERR_SLAVE_SDO_READ = 0x0109

	#/ </summary>
	YKE_ERR_SLAVE_SDO = 0x010a

	#/ </summary>
	YKE_ERR_SLAVE_SDO_OVER = 0x010b

	#/ </summary>
	YKE_ERR_SLAVE_INDEX = 0x010c

	#/ </summary>
	YKE_ERR_SLAVE_OFFLINE = 0x010d

	#/ </summary>
	YKE_ERR_SLAVE_RST = 0x010e

	#/ </summary>
	YKE_ERR_SLAVE_DRVW = 0x010f

	#/ </summary>
	YKE_ERR_SLAVE_SM_TIMEOUT = 0x0110

# <summary>
# 主站选择
# </summary>
class YKE_NODE (Enum):
	#/ </summary>
	YKE_ECAT_A = 0

	#/ </summary>
	YKE_ECAT_B = 1

	#/ </summary>
	YKE_ECAT_C = 2

	#/ </summary>
	YKE_ECAT_D = 3

	#/ </summary>
	YKE_NODE_E = 4

	#/ </summary>
	YKE_NODE_F = 5

	#/ </summary>
	YKE_NODE_G = 6

	#/ </summary>
	YKE_NODE_H = 7

# <summary>
# 轴物理层类型
# </summary>
class YKE_AXIS_PHY (Enum):
	#/ </summary>
	YKE_AXIS_PHY_VIRTUAL = 0

	#/ </summary>
	YKE_AXIS_PHY_ETHERCAT = 1

	#/ </summary>
	YKE_AXIS_PHY_PULSE = 2

# <summary>
# 数字IO物理层类型
# </summary>
class YKE_DIO_PHY (Enum):
	#/ </summary>
	YKE_DIO_PHY_PCI = 0

	#/ </summary>
	YKE_DIO_PHY_EBUS_DIO = 1

	#/ </summary>
	YKE_DIO_PHY_EBUS_GW = 2

	#/ </summary>
	YKE_DIO_PHY_EBUS_DRV = 3

# <summary>
# 停止类型
# </summary>
class YKE_AXIS_STOP_TYPE (Enum):
	#/ </summary>
	YKE_AXIS_STOP_NONE = 0

	#/ </summary>
	YKE_AXIS_STOP_EMG = 1

	#/ </summary>
	YKE_AXIS_STOP_INS = 2

	#/ </summary>
	YKE_AXIS_STOP_HARD_LIMIT = 3

	#/ </summary>
	YKE_AXIS_STOP_SOFT_LIMIT = 4

	#/ </summary>
	YKE_AXIS_STOP_DRIVER = 5

	#/ </summary>
	YKE_AXIS_STOP_MASTER = 6

	#/ </summary>
	YKE_AXIS_STOP_SLAVE = 7

	#/ </summary>
	YKE_AXIS_STOP_FOLLOW = 8

	#/ </summary>
	YKE_AXIS_STOP_TRIGGER = 9

	#/ </summary>
	YKE_AXIS_STOP_EVENT = 10

	#/ </summary>
	YKE_AXIS_STOP_CIRCLE_ZONE = 11

	#/ </summary>
	YKE_AXIS_STOP_RUNTIME = 20

# <summary>
# 轴等待信号类型
# </summary>
class YKE_AXIS_WAIT_TYPE (Enum):
	#/ </summary>
	YKE_AXIS_WAIT_ACITVE_OFF = 0

	#/ </summary>
	YKE_AXIS_WAIT_ACITVE_ON = 1

# <summary>
# 数字输入等待类型
# </summary>
class YKE_DIGITAL_INPUT_WAIT_TYPE (Enum):
	#/ </summary>
	YKE_DIGITAL_INPUT_WAIT_OFF = 0

	#/ </summary>
	YKE_DIGITAL_INPUT_WAIT_ON = 1

# <summary>
# 事件等待类型
# </summary>
class YKE_EVENT_WAIT_TYPE (Enum):
	#/ </summary>
	YKE_EVENT_WAIT_FINISH = 0

# <summary>
# 运动曲线
# </summary>
class YKE_CURVE_TYPE (Enum):
	#/ </summary>
	YKE_CURVE_S7 = 0

	#/ </summary>
	YKE_CURVE_T7 = 1

	#/ </summary>
	YKE_CURVE_TS = 2

# <summary>
# 开关配置
# </summary>
class YKE_SWITCH_TYPE (Enum):
	#/ </summary>
	YKE_SWITCH_NONE = 0

	#/ </summary>
	YKE_SWITCH_COE_REG = 1

	#/ </summary>
	YKE_SWITCH_GLOBAL_DIO = 2

	#/ </summary>
	YKE_SWITCH_LOCAL_DIO = 3

	#/ </summary>
	YKE_SWITCH_MECHANICAL = 4

# <summary>
# 语言选择
# </summary>
class YKE_LANGUAGE (Enum):
	#/ </summary>
	YKE_LNG_CHN = 0

# <summary>
# 缓冲模式
# </summary>
class YKE_BUFFER_MODE (Enum):
	#/ </summary>
	YKE_BUFFER_NONE = 0x0000

	#/ </summary>
	YKE_BUFFERED = 0x0001

	#/ </summary>
	YKE_BLENDING_LOW = 0x0002

	#/ </summary>
	YKE_BLENDING_PREV = 0x0003

	#/ </summary>
	YKE_BLENDING_NEXT = 0x0004

	#/ </summary>
	YKE_BLENDING_HIGH = 0x0005

# <summary>
# 过渡方式
# </summary>
class YKE_TRANSITION_MODE (Enum):
	#/ </summary>
	YKE_TRANS_NONE = 0x0000

	#/ </summary>
	YKE_CORNER_DISTANCE = 0x0003

	#/ </summary>
	YKE_MAX_CORNER_DEVIATION = 0x0004

# <summary>
# 圆弧辅助点模式
# </summary>
class YKE_CIRCULAR_AUX_MODE (Enum):
	#/ </summary>
	YKE_CIRCULAR_BORDER = 0x0000

	#/ </summary>
	YKE_CIRCULAR_CENTER = 0x0001

# <summary>
# 圆弧路径选择
# </summary>
class YKE_CIRCULAR_PATH_CHOICE (Enum):
	#/ </summary>
	YKE_CIRCULAR_CLOCKWISE = 0x0000

	#/ </summary>
	YKE_CIRCULAR_COUNTERCLOCKWISE = 0x0001

	#/ </summary>
	YKE_CIRCULAR_DEFINED_BY_AUX_POINT = 0x0002

# <summary>
# 运动方向
# </summary>
class YKE_DIRECTION (Enum):
	#/ </summary>
	YKE_DIRECTION_POSITIVE = 0

	#/ </summary>
	YKE_DIRECTION_NEGATIVE = 1

	#/ </summary>
	YKE_DIRECTION_NONE = 2

# <summary>
# 回原点方式
# </summary>
class YKE_HOME_MODE (Enum):
	#/ </summary>
	YKE_HOME_MODE_00 = 0

	#/ </summary>
	YKE_HOME_MODE_01 = 1

	#/ </summary>
	YKE_HOME_MODE_02 = 2

	#/ </summary>
	YKE_HOME_MODE_03 = 3

	#/ </summary>
	YKE_HOME_MODE_04 = 4

	#/ </summary>
	YKE_HOME_MODE_05 = 5

	#/ </summary>
	YKE_HOME_MODE_06 = 6

	#/ </summary>
	YKE_HOME_MODE_07 = 7

	#/ </summary>
	YKE_HOME_MODE_08 = 8

	#/ </summary>
	YKE_HOME_MODE_09 = 9

	#/ </summary>
	YKE_HOME_MODE_10 = 10

	#/ </summary>
	YKE_HOME_MODE_11 = 11

	#/ </summary>
	YKE_HOME_MODE_12 = 12

	#/ </summary>
	YKE_HOME_MODE_13 = 13

	#/ </summary>
	YKE_HOME_MODE_14 = 14

	#/ </summary>
	YKE_HOME_MODE_15 = 15

	#/ </summary>
	YKE_HOME_MODE_16 = 16

	#/ </summary>
	YKE_HOME_MODE_17 = 17

	#/ </summary>
	YKE_HOME_MODE_18 = 18

	#/ </summary>
	YKE_HOME_MODE_19 = 19

	#/ </summary>
	YKE_HOME_MODE_20 = 20

	#/ </summary>
	YKE_HOME_MODE_21 = 21

	#/ </summary>
	YKE_HOME_MODE_22 = 22

	#/ </summary>
	YKE_HOME_MODE_23 = 23

	#/ </summary>
	YKE_HOME_MODE_24 = 24

	#/ </summary>
	YKE_HOME_MODE_25 = 25

	#/ </summary>
	YKE_HOME_MODE_26 = 26

	#/ </summary>
	YKE_HOME_MODE_27 = 27

	#/ </summary>
	YKE_HOME_MODE_28 = 28

	#/ </summary>
	YKE_HOME_MODE_29 = 29

	#/ </summary>
	YKE_HOME_MODE_30 = 30

	#/ </summary>
	YKE_HOME_MODE_31 = 31

	#/ </summary>
	YKE_HOME_MODE_32 = 32

	#/ </summary>
	YKE_HOME_MODE_33 = 33

	#/ </summary>
	YKE_HOME_MODE_34 = 34

	#/ </summary>
	YKE_HOME_MODE_35 = 35

	#/ </summary>
	YKE_HOME_MODE_36 = 36

	#/ </summary>
	YKE_HOME_MODE_37 = 37

	#/ </summary>
	YKE_HOME_MODE_ABS = 38

# <summary>
# 轴停止命令减速度选择
# </summary>
class YKE_STOP_DEC (Enum):
	#/ </summary>
	YKE_STOP_SEL_SMOOTH = 0

	#/ </summary>
	YKE_STOP_SEL_EMG = 1

	#/ </summary>
	YKE_STOP_SEL_INS = 2

# <summary>
# 编码器模式
# </summary>
class YKE_ENCODER_MODE (Enum):
	#/ </summary>
	YKE_ENCODER_MODE_PD = 0

	#/ </summary>
	YKE_ENCODER_MODE_PN = 1

	#/ </summary>
	YKE_ENCODER_MODE_AB4 = 2

# <summary>
# 比较器模式
# </summary>
class YKE_COMPARE_MODE (Enum):
	#/ </summary>
	YKE_COMPARE_MODE_FIX = 0

	#/ </summary>
	YKE_COMPARE_MODE_LINE = 1

	#/ </summary>
	YKE_COMPARE_MODE_FIFO = 2

# <summary>
# 输入信号触发模式
# </summary>
class YKE_TRIG_MODE (Enum):
	#/ </summary>
	YKE_TRIG_MODE_UPEDGE = 0

	#/ </summary>
	YKE_TRIG_MODE_DOWNEDGE = 1

	#/ </summary>
	YKE_TRIG_MODE_HGIHLEVEL = 2

	#/ </summary>
	YKE_TRIG_MODE_LOWLEVEL = 3

	#/ </summary>
	YKE_TRIG_MODE_EDGE = 4

# <summary>
# 示波器触发模式
# </summary>
class YKE_OSC_TRIG_TYPE (Enum):
	#/ </summary>
	YKE_OSC_TRIG_FREE = 0

	#/ </summary>
	YKE_OSC_TRIG_MANUAL = 1

	#/ </summary>
	YKE_OSC_TRIG_UPEDGE = 2

	#/ </summary>
	YKE_OSC_TRIG_DOWNEDGE = 3

	#/ </summary>
	YKE_OSC_TRIG_HIGHLEVEL = 4

	#/ </summary>
	YKE_OSC_TRIG_LOWLEVEL = 5

	#/ </summary>
	YKE_OSC_TRIG_UPDOWN = 6

# <summary>
# 示波器监控对象类型
# </summary>
class YKE_OSC_ITEM_TYPE (Enum):
	#/ </summary>
	YKE_OSC_ITEM_AXIS = 0

	#/ </summary>
	YKE_OSC_ITEM_OD = 1

	#/ </summary>
	YKE_OSC_ITEM_UG = 2

	#/ </summary>
	YKE_OSC_ITEM_DI = 3

	#/ </summary>
	YKE_OSC_ITEM_DO = 4

	#/ </summary>
	YKE_OSC_ITEM_DATA_REG = 5

	#/ </summary>
	YKE_OSC_ITEM_SYS = 6

	#/ </summary>
	YKE_OSC_ITEM_GROUP = 7

	#/ </summary>
	YKE_OSC_ITEM_ENCODER = 8

	#/ </summary>
	YKE_OSC_ITEM_EVENT = 9

	#/ </summary>
	YKE_OSC_ITEM_MULTI_AXIS = 10

	#/ </summary>
	YKE_OSC_ITEM_WAIT = 11

# <summary>
# 轴信息采样数据类型
# </summary>
class YKE_AXIS_ITEM_TYPE (Enum):
	#/ </summary>
	YKE_AXIS_ITEM_CMD_VEL = 0

	#/ </summary>
	YKE_AXIS_ITEM_ACT_VEL = 1

	#/ </summary>
	YKE_AXIS_ITEM_CMD_POS = 2

	#/ </summary>
	YKE_AXIS_ITEM_ACT_POS = 3

	#/ </summary>
	YKE_AXIS_ITEM_CMD_TQ = 4

	#/ </summary>
	YKE_AXIS_ITEM_ACT_TQ = 5

	#/ </summary>
	YKE_AXIS_ITEM_CMD_ACC = 6

	#/ </summary>
	YKE_AXIS_ITEM_CMD_JERK = 7

	#/ </summary>
	YKE_AXIS_ITEM_TARGET_POS = 11

	#/ </summary>
	YKE_AXIS_ITEM_COE_MODE = 12

	#/ </summary>
	YKE_AXIS_ITEM_ENCODER = 13

	#/ </summary>
	YKE_AXIS_ITEM_WARN_ID = 14

	#/ </summary>
	YKE_AXIS_ITEM_PITCH = 15

	#/ </summary>
	YKE_AXIS_ITEM_BACKLASH = 16

	#/ </summary>
	YKE_AXIS_ITEM_CMD_DONE = 20

	#/ </summary>
	YKE_AXIS_ITEM_ACTIVE1 = 21

	#/ </summary>
	YKE_AXIS_ITEM_ACTIVE2 = 22

	#/ </summary>
	YKE_AXIS_ITEM_DONE = 23

	#/ </summary>
	YKE_AXIS_ITEM_POWER_ON = 24

	#/ </summary>
	YKE_AXIS_ITEM_CHANGE = 25

	#/ </summary>
	YKE_AXIS_ITEM_REMAIN_TIM = 30

	#/ </summary>
	YKE_AXIS_ITEM_TOTAL_TIM = 31

	#/ </summary>
	YKE_AXIS_ITEM_COMPLETE_TIM = 32

	#/ </summary>
	YKE_AXIS_ITEM_POS_LAG = 40

	#/ </summary>
	YKE_AXIS_ITEM_POS_LAG_FILTER = 41

	#/ </summary>
	YKE_AXIS_ITEM_GANTRY_CMDERR = 42

	#/ </summary>
	YKE_AXIS_ITEM_GANTRY_ACTERR = 43

	#/ </summary>
	YKE_AXIS_ITEM_HOME = 50

	#/ </summary>
	YKE_AXIS_ITEM_HD_POSITIVE = 51

	#/ </summary>
	YKE_AXIS_ITEM_HD_NEGATIVE = 52

	#/ </summary>
	YKE_AXIS_ITEM_SOFT_POSITIVE = 53

	#/ </summary>
	YKE_AXIS_ITEM_SOFT_NEGATIVE = 54

	#/ </summary>
	YKE_AXIS_ITEM_INPOS1 = 60

	#/ </summary>
	YKE_AXIS_ITEM_INPOS2 = 61

	#/ </summary>
	YKE_AXIS_ITEM_INPOS3 = 62

	#/ </summary>
	YKE_AXIS_ITEM_INPOS4 = 63

	#/ </summary>
	YKE_AXIS_ITEM_INPOS5 = 64

	#/ </summary>
	YKE_AXIS_ITEM_INPOS6 = 65

	#/ </summary>
	YKE_AXIS_ITEM_USER_TEST = 100

# <summary>
# 事件数据类型
# </summary>
class YKE_EVENT_ITEM_TYPE (Enum):
	#/ </summary>
	YKE_EVENT_ITEM_START = 0

	#/ </summary>
	YKE_EVENT_ITEM_STATUS = 1

# <summary>
# 多轴联动数据采集类型
# </summary>
class YKE_MULTI_AXIS_ITEM_TYPE (Enum):
	#/ </summary>
	YKE_MULTI_AXIS_ITEM_ACTIVE = 0

	#/ </summary>
	YKE_MULTI_AXIS_ITEM_DONE = 1

	#/ </summary>
	YKE_MULTI_AXIS_ITEM_REMAIN_TIM = 10

	#/ </summary>
	YKE_MULTI_AXIS_ITEM_TOTAL_TIM = 11

	#/ </summary>
	YKE_MULTI_AXIS_ITEM_ACCELERATION = 21

# <summary>
# 多轴联动数据采集类型
# </summary>
class YKE_WAIT_ITEM_TYPE (Enum):
	#/ </summary>
	YKE_WAIT_ITEM_ACTIVE = 0

# <summary>
# 轴跟随信息
# </summary>
class YKE_AXIS_FOLLOW_TYPE (Enum):
	#/ </summary>
	YKE_AXIS_FOLLOW_CMD_POS = 0

	#/ </summary>
	YKE_AXIS_FOLLOW_ACT_POS = 1

# <summary>
# 轴位置比较模式
# </summary>
class YKE_AXIS_COMPARE_TYPE (Enum):
	#/ </summary>
	YKE_AXIS_COMPARE_CMD_POS = 0

	#/ </summary>
	YKE_AXIS_COMPARE_ACT_POS = 1

# <summary>
# 坐标系跟随信息
# </summary>
class YKE_FOLLOW_GROUP_TYPE (Enum):
	#/ </summary>
	YKE_FOLLOW_GROUP_DIST_2D = 10

	#/ </summary>
	YKE_FOLLOW_GROUP_DIST_3D = 11

# <summary>
# 系统信息采样数据类型
# </summary>
class YKE_SYSTEM_ITEM_TYPE (Enum):
	#/ </summary>
	YKE_SYS_ITEM_MOTICK = 0

	#/ </summary>
	YKE_SYS_ITEM_DC_JITTER = 1

	#/ </summary>
	YKE_SYS_ITEM_DC_ADJUST = 2

	#/ </summary>
	YKE_SYS_ITEM_CPU_FREQ = 3

	#/ </summary>
	YKE_SYS_ITEM_PAYLOAD_YKG = 4

	#/ </summary>
	YKE_SYS_ITEM_PAYLOAD_NTF = 5

	#/ </summary>
	YKE_SYS_ITEM_PAYLOAD_CNC = 6

	#/ </summary>
	YKE_SYS_ITEM_PAYLOAD_ALL = 7

	#/ </summary>
	YKE_SYS_ITEM_TEST1 = 8

# <summary>
# 设置驱动器控制模式,总线轴专用
# </summary>
class YKE_DRV_OP_MODE (Enum):
	#/ </summary>
	YKE_DRV_OP_MODE_NONE = 0

	#/ </summary>
	YKE_DRV_OP_MODE_PP = 1

	#/ </summary>
	YKE_DRV_OP_MODE_PV = 3

	#/ </summary>
	YKE_DRV_OP_MODE_TQ = 4

	#/ </summary>
	YKE_DRV_OP_MODE_HM = 6

	#/ </summary>
	YKE_DRV_OP_MODE_CSP = 8

	#/ </summary>
	YKE_DRV_OP_MODE_CSV = 9

	#/ </summary>
	YKE_DRV_OP_MODE_CST = 10

# <summary>
# 跟随方式
# </summary>
class YKE_AXIS_FOLLOW_MODE (Enum):
	#/ </summary>
	YKE_AXIS_FOLLOW_SCALE = 0

	#/ </summary>
	YKE_AXIS_FOLLOW_ACC = 1

# <summary>
# 传送带同步状态
# </summary>
class YKE_CONVEYOR_SYNC_STATUS (Enum):
	#/ </summary>
	YKE_CONVEYOR_SYNC_SYNC_ACTIVE = 0

	#/ </summary>
	YKE_CONVEYOR_SYNC_FAIL = 1

	#/ </summary>
	YKE_CONVEYOR_SYNC_DONE = 2

# <summary>
# 脉冲模式
# </summary>
class YKE_PULSE_MODE (Enum):
	#/ </summary>
	YKE_PULSE_DIR = 0

	#/ </summary>
	YKE_PULSE_PN = 1

# <summary>
# 捕获源
# </summary>
class YKE_CAPTURE_SOURCE (Enum):
	#/ </summary>
	YKE_CAPTURE_ENCODER = 0

	#/ </summary>
	YKE_CAPTURE_CMD_PULSE = 1

# <summary>
# 凸轮曲线
# </summary>
class YKE_CAM_CURVE (Enum):
	#/ </summary>
	YKE_CAM_CURVE_POLY = 0

	#/ </summary>
	YKE_CAM_CURVE_SPLINE = 1

# <summary>
# 双轴混合模式
# </summary>
class YKE_COMBINE_MODE (Enum):
	#/ </summary>
	YKE_COMBINE_ADD = 0

	#/ </summary>
	YKE_COMBINE_SUB = 1

	#/ </summary>
	YKE_COMBINE_DIST = 10

# <summary>
# 总线从站配置操作内容
# </summary>
class YKE_SLAVE_ITEM (Enum):
	#/ </summary>
	YKE_SLAVE_ITEM_REMOVE = 1

	#/ </summary>
	YKE_SLAVE_ITEM_ENABLE = 2

# <summary>
# 数据类型
# </summary>
class YKE_DATA_TYPE (Enum):
	#/ </summary>
	YKE_INT8 = 0

	#/ </summary>
	YKE_UINT8 = 1

	#/ </summary>
	YKE_INT16 = 2

	#/ </summary>
	YKE_UINT16 = 3

	#/ </summary>
	YKE_INT32 = 4

	#/ </summary>
	YKE_UINT32 = 5

# <summary>
# 布尔数据
# </summary>
class YKE_BOOL (Enum):
	#/ </summary>
	YKE_FALSE = 0

	#/ </summary>
	YKE_TRUE = 1

# <summary>
# 运动模式
# </summary>
class YKE_MOTION_TYPE (Enum):
	#/ </summary>
	YKE_MOTION_NONE = 0

	#/ </summary>
	YKE_MOTION_POSITION = 1

	#/ </summary>
	YKE_MOTION_VELOCITY = 2

	#/ </summary>
	YKE_MOTION_TORQUE = 3

	#/ </summary>
	YKE_MOTION_HOME = 4

	#/ </summary>
	YKE_MOTION_SOFT_FOLLOW = 5

	#/ </summary>
	YKE_MOTION_HARD_FOLLOW = 6

	#/ </summary>
	YKE_MOTION_GROUP = 7

	#/ </summary>
	YKE_MOTION_MULTI_AXIS = 8

	#/ </summary>
	YKE_MOTION_PVT = 9

# <summary>
# 连接错误类型
# </summary>
class YKE_LINK_ERROR (Enum):
	#/ </summary>
	YKE_ERR_LINK_NONE = 0

	#/ </summary>
	YKE_ERR_LINK_WKC = 1

	#/ </summary>
	YKE_ERR_LINK_SEND = 2

	#/ </summary>
	YKE_ERR_LINK_REV = 3

	#/ </summary>
	YKE_ERR_LINK_READREG = 4

	#/ </summary>
	YKE_ERR_LINK_SEND_SIZE = 13

	#/ </summary>
	YKE_ERR_LINK_SEND_QUENE = 14

	#/ </summary>
	YKE_ERR_LINK_REV_QUENE = 15

	#/ </summary>
	YKE_ERR_LINK_ALLOC_REV = 22

	#/ </summary>
	YKE_ERR_LINK_ALLOC_SEND = 23

	#/ </summary>
	YKE_ERR_LINK_DC_ADJUST = 27

	#/ </summary>
	YKE_ERR_LINK_REDUNDANCY = 31

# <summary>
# 总线状态
# </summary>
class YKE_BUS_STATUS (Enum):
	#/ </summary>
	YKE_BUS_STATUS_IDEL = 0

	#/ </summary>
	YKE_BUS_STATUS_INITING = 1

	#/ </summary>
	YKE_BUS_STATUS_ERR = 2

	#/ </summary>
	YKE_BUS_STATUS_RUNNING = 10

# <summary>
# 同步运动模式
# </summary>
class YKE_SYNC_AXIS_MODE (Enum):
	#/ </summary>
	YKE_SYNC_AXIS_LIMIT = 0

	#/ </summary>
	YKE_SYNC_AXIS_SLOWEST = 1

	#/ </summary>
	YKE_SYNC_AXIS_FARTHESET = 2

	#/ </summary>
	YKE_SYNC_FIX_TIME = 3

# <summary>
# 坐标系报警后输出状态
# </summary>
class YKE_GROUP_OUTPUT_IN_WARN (Enum):
	#/ </summary>
	YKE_GROUP_OUTPUT_IN_WARN_KEEP = 0

	#/ </summary>
	YKE_GROUP_OUTPUT_IN_WARN_HIGH = 1

	#/ </summary>
	YKE_GROUP_OUTPUT_IN_WARN_LOW = 2

# <summary>
# 急停信号有效后给轴的控制命令
# </summary>
class YKE_EMG_AXIS_BEGAVIOR (Enum):
	#/ </summary>
	YKE_EMG_AXIS_KEEP = 0

	#/ </summary>
	YKE_EMG_AXIS_STOP = 1

	#/ </summary>
	YKE_EMG_AXIS_POWEROFF = 2

# <summary>
# 坐标系采样数据类型
# </summary>
class YKE_GROUP_ITEM_TYPE (Enum):
	#/ </summary>
	YKE_GROUP_ITEM_ACTIVE = 0

	#/ </summary>
	YKE_GROUP_ITEM_DONE = 1

	#/ </summary>
	YKE_GROUP_ITEM_CUR_LINE = 10

	#/ </summary>
	YKE_GROUP_ITEM_CURMARK = 11

	#/ </summary>
	YKE_GROUP_ITEM_VEL = 12

	#/ </summary>
	YKE_GROUP_ITEM_ACC = 13

	#/ </summary>
	YKE_GROUP_ITEM_JERK = 14

	#/ </summary>
	YKE_GROUP_ITEM_WARN1 = 15

	#/ </summary>
	YKE_GROUP_ITEM_WARN2 = 16

	#/ </summary>
	YKE_GROUP_ITEM_VEL_2D = 20

	#/ </summary>
	YKE_GROUP_ITEM_VEL_3D = 21

	#/ </summary>
	YKE_GROUP_ITEM_DIST_2D = 22

	#/ </summary>
	YKE_GROUP_ITEM_DIST_3D = 23

	#/ </summary>
	YKE_GROUP_ITEM_WORKPIECE_X = 30

	#/ </summary>
	YKE_GROUP_ITEM_WORKPIECE_Y = 31

	#/ </summary>
	YKE_GROUP_ITEM_WORKPIECE_Z = 32

	#/ </summary>
	YKE_GROUP_ITEM_WORKPIECE_A = 33

	#/ </summary>
	YKE_GROUP_ITEM_WORKPIECE_B = 34

	#/ </summary>
	YKE_GROUP_ITEM_WORKPIECE_C = 35

	#/ </summary>
	YKE_GROUP_ITEM_DEBUG1 = 100

	#/ </summary>
	YKE_GROUP_ITEM_DEBUG2 = 101

	#/ </summary>
	YKE_GROUP_ITEM_DEBUG3 = 102

	#/ </summary>
	YKE_GROUP_ITEM_DEBUG4 = 103

	#/ </summary>
	YKE_GROUP_ITEM_DEBUG5 = 104

# <summary>
# 坐标系中位置比较模式
# </summary>
class YKE_GROUP_COMPARE_MODE (Enum):
	#/ </summary>
	YKE_GROUP_COMPARE_START_IMMEDIATELY = 0

	#/ </summary>
	YKE_GROUP_COMPARE_END_IMMEDIATELY = 1

	#/ </summary>
	YKE_GROUP_COMPARE_COMPLETED_TIME = 2

	#/ </summary>
	YKE_GROUP_COMPARE_COMPLETED_DIST = 3

	#/ </summary>
	YKE_GROUP_COMPARE_REMAINING_TIME = 4

	#/ </summary>
	YKE_GROUP_COMPARE_REMAINING_DIST = 5

	#/ </summary>
	YKE_GROUP_COMPARE_COMPLETED_RATE = 6

# <summary>
# 坐标系中数字输出模式
# </summary>
class YKE_GROUP_DO_MODE (Enum):
	#/ </summary>
	YKE_GROUP_DO_SINGLE = 0

	#/ </summary>
	YKE_GROUP_DO_ALTERNATE = 1

	#/ </summary>
	YKE_GROUP_DO_PULSE = 2

# <summary>
# 坐标系中PWM跟随模式
# </summary>
class YKE_GROUP_PWM_MODE (Enum):
	#/ </summary>
	YKE_GROUP_PWM_FIX = 0

	#/ </summary>
	YKE_GROUP_PWM_DUTY = 1

	#/ </summary>
	YKE_GROUP_PWM_FREQ = 2

# <summary>
# 轴类型,coppylia仿真使用
# </summary>
class YKE_AXIS_SIM_TYPE (Enum):
	#/ </summary>
	YKE_AXIS_SIM_LINEAR = 0

	#/ </summary>
	YKE_AXIS_SIM_ROTARY = 1

# <summary>
# 触发类型
# </summary>
class YKE_TRIGGER_TYPE (Enum):
	#/ </summary>
	YKE_TRIGGER_REMAINING_TIME = 0

	#/ </summary>
	YKE_TRIGGER_REMAINGING_DISTANCE = 1

	#/ </summary>
	YKE_TRIGGER_SAMETIME_COMPLETION = 2

	#/ </summary>
	YKE_TRIGGER_COMPLETED_TIME = 3

	#/ </summary>
	YKE_TRIGGER_COMPLETED_DISTANCE = 4

	#/ </summary>
	YKE_TRIGGER_STAGGERED_TIME_COMPLETION = 5

	#/ </summary>
	YKE_TRIGGER_STAGGERED_DISTANCE_COMPLETION = 6

# <summary>
# 信号源
# </summary>
class YKE_SIGNAL_SOURCE_TYPE (Enum):
	#/ </summary>
	YKE_SIGNAL_SOURCE_INPUT = 0

	#/ </summary>
	YKE_SIGNAL_SOURCE_OUTPUT = 1

	#/ </summary>
	YKE_SIGNAL_SOURCE_EVENT = 2

	#/ </summary>
	YKE_SIGNAL_SOURCE_REG = 3

# <summary>
# 两个BIT位合成条件
# </summary>
class YKE_LOGIC_CONDITIONS (Enum):
	#/ </summary>
	YKE_LOGIC_AND = 0

	#/ </summary>
	YKE_LOGIC_OR = 1

	#/ </summary>
	YKE_LOGIC_NAND = 2

	#/ </summary>
	YKE_LOGIC_NOR = 3

# <summary>
# 事件状态
# </summary>
class YKE_EVENT_STATUS_TYTE (Enum):
	#/ </summary>
	YKE_EVENT_STATUS_IDEL = 0

	#/ </summary>
	YKE_EVENT_STATUS_WAIT = 5

	#/ </summary>
	YKE_EVENT_STATUS_RESTART = 10

	#/ </summary>
	YKE_EVENT_STATUS_DELAY = 15

	#/ </summary>
	YKE_EVENT_STATUS_FINISH = 20

# <summary>
# M/H辅助功能相对过渡段执行时间类型
# </summary>
class YKE_CNC_ACTION_TYPE (Enum):
	#/ </summary>
	YKE_CNC_ACTION_INTER = 0

	#/ </summary>
	YKE_CNC_ACTION_PRE = 1

	#/ </summary>
	YKE_CNC_ACTION_POST = 2

# <summary>
# Akima样条过渡切向类型
# </summary>
class YKE_CNC_ASPLINE_TRANS_TYPE (Enum):
	#/ </summary>
	YKE_CNC_ASPLINE_TRANS_AUTO = 0

	#/ </summary>
	YKE_CNC_ASPLINE_TRANS_TANGENTIAL = 1

	#/ </summary>
	YKE_CNC_ASPLINE_TRANS_USER = 2

# <summary>
# HSC_Surface平滑变加速监控类型
# </summary>
class YKE_CNC_CHECK_JERK_TYPE (Enum):
	#/ </summary>
	YKE_CNC_CHECKJERK_NO = 0

	#/ </summary>
	YKE_CNC_CHECKJERK_GEOMERTRIC = 1

	#/ </summary>
	YKE_CNC_CHECKJERK_NOLIEAR = 2

# <summary>
# HSC_Serface平滑圆弧优化类型
# </summary>
class YKE_HSC_CIR_MODE (Enum):
	#/ </summary>
	YKE_HSC_CIR_MODE_CONTOUR = 0

	#/ </summary>
	YKE_HSC_CIR_MODE_NOCONTOUR = 1

	#/ </summary>
	YKE_HSC_CIR_MODE_CONTOUR_LONG = 2

# <summary>
# CNC指令模式
# </summary>
class YKE_CNC_INS_MODE (Enum):
	#/ </summary>
	YKE_CNC_INS_API = 0

	#/ </summary>
	YKE_CNC_INS_FILE = 1

	#/ </summary>
	YKE_CNC_EXTERN = 2

# <summary>
# 日志过滤选择
# </summary>
class YKE_LOGGER_FILTER_TYPE (Enum):
	#/ </summary>
	YKE_LOGGER_FILTER_ALL = 0

	#/ </summary>
	YKE_LOGGER_FILTER_INCLUDE = 1

	#/ </summary>
	YKE_LOGGER_FILTER_EXCLUDE = 2

# <summary>
# 授权状态
# </summary>
class YKE_LICENSE_STATUS (Enum):
	#/ </summary>
	YKE_LICENSE_OK = 0

	#/ </summary>
	YKE_LICENSE_AXIS = 1

	#/ </summary>
	YKE_LICENSE_GROUP = 2

	#/ </summary>
	YKE_LICENSE_VISION = 3

	#/ </summary>
	YKE_LICENSE_ECAM = 4

	#/ </summary>
	YKE_LICENSE_PLC = 5

	#/ </summary>
	YKE_LICENSE_HMI = 6

	#/ </summary>
	YKE_LICENSE_RT = 7

	#/ </summary>
	YKE_LICENSE_NTF = 8

	#/ </summary>
	YKE_LICENSE_SUID = 20

	#/ </summary>
	YKE_LICENSE_TEMP = 21

	#/ </summary>
	YKE_LICENSE_SHELL = 30

# <summary>
# 工程配置数据掩码,按位定义
# </summary>
class YKE_PROJECT_MASK (Enum):
	#/ </summary>
	YKE_PROJECT_GCONFIG = 0x01

	#/ </summary>
	YKE_PROJECT_AXIS = 0x02

	#/ </summary>
	YKE_PROJECT_CARD = 0x04

	#/ </summary>
	YKE_PROJECT_ECAT = 0x08

# <summary>
# 扫描内容
# </summary>
class YKE_SCAN_INFO (Enum):
	#/ </summary>
	YKE_SCAN_NONE = 0x00

	#/ </summary>
	YKE_SCAN_VID = 0x01

	#/ </summary>
	YKE_SCAN_SLOT = 0x02

# <summary>
# 总线初始化状态
# </summary>
class YKE_PDS_PHASE (Enum):
	#/ </summary>
	YKE_PDS_NONE = 0x00

	#/ </summary>
	YKE_PDS_LOAD = 10

	#/ </summary>
	YKE_PDS_ING = 20

	#/ </summary>
	YKE_PDS_EEP = 21

	#/ </summary>
	YKE_PDS_PREOP = 24

	#/ </summary>
	YKE_PDS_SAFEOP = 25

	#/ </summary>
	YKE_PDS_PDO = 30

	#/ </summary>
	YKE_PDS_RUN = 40

# <summary>
# 总线初始化状态
# </summary>
class YKE_DOGGLE_TYPE (Enum):
	#/ </summary>
	YKE_DOGGLE_A = 0

	#/ </summary>
	YKE_DOGGLE_B = 1

# <summary>
# 总线初始化状态
# </summary>
class YKE_PLC_CMD_TYPE (Enum):
	#/ </summary>
	YKE_PLC_CMD_NONE = 0

	#/ </summary>
	YKE_PLC_CMD_PRG_START = 1

	#/ </summary>
	YKE_PLC_CMD_PRG_STOP = 2

	#/ </summary>
	YKE_PLC_CMD_SYS_EXIT = 10

# <summary>
# 3坐标值
# </summary>
class YKS_POINT3 (Structure):
	_fields_ = [
		#/ </summary>
		('x',c_double),

		#/ </summary>
		('y',c_double),

		#/ </summary>
		('z',c_double),
	]

# <summary>
# 输入信号配置
# </summary>
class YKS_AxisSwitchConfig (Structure):
	_fields_ = [
		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('byte_offset',c_uint),

		#/ </summary>
		('bit_offset',c_uint),

		#/ </summary>
		('inv_or_edge',c_uint32),

		#/ </summary>
		('position_error',c_double),

		#/ </summary>
		('hold_time',c_double),

		#/ </summary>
		('res1', c_uint * 8),
	]

# <summary>
# 系统配置
# </summary>
class YKS_SysProfile (Structure):
	_fields_ = [
		#/ </summary>
		('path', c_char * 260),

		#/ </summary>
		('res6',c_uint),

		#/ </summary>
		('config_axis_num',c_uint),

		#/ </summary>
		('config_input_size',c_uint),

		#/ </summary>
		('config_output_size',c_uint),

		#/ </summary>
		('dog_serial_numberA',c_uint),

		#/ </summary>
		('dog_serial_numberB', c_char * 64),

		#/ </summary>
		('dog_mem_sizeA',c_uint),

		#/ </summary>
		('dog_mem_sizeB',c_uint),

		#/ </summary>
		('res0',c_double),

		#/ </summary>
		('dog_axis_num',c_uint),

		#/ </summary>
		('dog_axis_used',c_uint),

		#/ </summary>
		('dog_ecam_num',c_uint),

		#/ </summary>
		('dog_ecam_used',c_uint),

		#/ </summary>
		('dog_vision_num',c_uint),

		#/ </summary>
		('dog_vision_used',c_uint),

		#/ </summary>
		('dog_plc_num',c_uint),

		#/ </summary>
		('dog_plc_used',c_uint),

		#/ </summary>
		('dog_hmi_num',c_uint),

		#/ </summary>
		('dog_hmi_used',c_uint),

		#/ </summary>
		('dog_comm_num',c_uint),

		#/ </summary>
		('dog_comm_used',c_uint),

		#/ </summary>
		('dog_cad_num',c_uint),

		#/ </summary>
		('dog_cad_used',c_uint),

		#/ </summary>
		('dog_group_num',c_uint),

		#/ </summary>
		('dog_group_used',c_uint),

		#/ </summary>
		('dog_dotNetRT_num',c_uint),

		#/ </summary>
		('dog_dotNetRT_used',c_uint),

		#/ </summary>
		('dog_date_flag',c_uint32),

		#/ </summary>
		('dog_date_uid',c_uint),

		#/ </summary>
		('dog_date_year',c_uint),

		#/ </summary>
		('dog_date_month',c_uint),

		#/ </summary>
		('dog_date_day',c_uint),

		#/ </summary>
		('res1',c_uint),

		#/ </summary>
		('res3',c_double),

		#/ </summary>
		('lic_status',c_uint32),

		#/ </summary>
		('dog_err',c_uint32),

		#/ </summary>
		('node_ena', c_uint32 * 4),

		#/ </summary>
		('cnc_enable', c_uint32 * 4),

		#/ </summary>
		('runtime_ver',c_uint),

		#/ </summary>
		('plann_ver',c_uint),

		#/ </summary>
		('sim_mode',c_uint32),

		#/ </summary>
		('ecat_snap_node',c_uint32),

		#/ </summary>
		('ecat_snap_span',c_uint),

		#/ </summary>
		('res4',c_uint),

		#/ </summary>
		('res5', c_uint * 34),

		#/ </summary>
		('res2', c_double * 32),
	]

# <summary>
# 数字输入输出配置
# </summary>
class YKS_DigitalIO (Structure):
	_fields_ = [
		#/ </summary>
		('byte_offset',c_uint),

		#/ </summary>
		('bit_offset',c_uint),

		#/ </summary>
		('inv',c_uint32),

		#/ </summary>
		('res',c_uint),
	]

# <summary>
# 数字输入配置
# </summary>
class YKS_DigitalInput (Structure):
	_fields_ = [
		#/ </summary>
		('enable',c_uint32),

		#/ </summary>
		('byte_index',c_uint),

		#/ </summary>
		('bit_offset',c_uint),

		#/ </summary>
		('inv',c_uint32),

		#/ </summary>
		('filter_tim',c_double),

		#/ </summary>
		('value',c_uint32),

		#/ </summary>
		('res1', c_uint * 7),
	]

# <summary>
# 数字输出配置
# </summary>
class YKS_DigitalOutput (Structure):
	_fields_ = [
		#/ </summary>
		('enable',c_uint32),

		#/ </summary>
		('byte_index',c_uint),

		#/ </summary>
		('bit_offset',c_uint),

		#/ </summary>
		('valid',c_uint32),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 同步数字输出配置
# </summary>
class YKS_DigitalOutputCycle (Structure):
	_fields_ = [
		#/ </summary>
		('byte_index',c_uint),

		#/ </summary>
		('bit_offset',c_uint),

		#/ </summary>
		('valid',c_uint32),

		#/ </summary>
		('res', c_uint * 4),
	]

# <summary>
# windows蓝屏后的行为
# </summary>
class YKS_BlueScreenConfig (Structure):
	_fields_ = [
		#/ </summary>
		('enable',c_uint32),

		#/ </summary>
		('stop_axis',c_uint32),

		#/ </summary>
		('close_output',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res1', c_uint * 8),
	]

# <summary>
# 硬件急停配置信息
# </summary>
class YKS_HardEmgProfile (Structure):
	_fields_ = [
		#/ </summary>
		('emg_stop_input', YKS_DigitalInput * 8),

		#/ </summary>
		('emg_stop_output', YKS_DigitalOutput * 4),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 全局状态信息
# </summary>
class YKS_EmgStatus (Structure):
	_fields_ = [
		#/ </summary>
		('emg_stop_soft',c_uint32),

		#/ </summary>
		('emg_stop_input', c_uint32 * 8),

		#/ </summary>
		('emg_stop_input_all',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 4),
	]

# <summary>
# 总线实时信息
# </summary>
class YKS_BusStatus (Structure):
	_fields_ = [
		#/ </summary>
		('config_num',c_uint),

		#/ </summary>
		('useable_num',c_uint),

		#/ </summary>
		('active_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('min_payload',c_double),

		#/ </summary>
		('max_payload',c_double),

		#/ </summary>
		('cur_payload',c_double),

		#/ </summary>
		('min_shift',c_double),

		#/ </summary>
		('max_shift',c_double),

		#/ </summary>
		('cur_shift',c_double),

		#/ </summary>
		('dc_cycle',c_double),

		#/ </summary>
		('lost_frames',c_uint),

		#/ </summary>
		('lost_wkc',c_uint),

		#/ </summary>
		('master_active',c_uint32),

		#/ </summary>
		('offline_num',c_uint),

		#/ </summary>
		('cpu_ticks',c_ulonglong),

		#/ </summary>
		('max_ykg_payload',c_double),

		#/ </summary>
		('cur_ykg_payload',c_double),

		#/ </summary>
		('max_nt_payload',c_double),

		#/ </summary>
		('cur_nt_payload',c_double),

		#/ </summary>
		('max_cnc_payload',c_double),

		#/ </summary>
		('cur_cnc_payload',c_double),

		#/ </summary>
		('heart_tick',c_ulonglong),

		#/ </summary>
		('sys_error_type',c_uint32),

		#/ </summary>
		('sys_error_code1',c_uint),

		#/ </summary>
		('sys_error_code2',c_uint),

		#/ </summary>
		('link_error_type',c_uint32),

		#/ </summary>
		('link_error_code1',c_uint),

		#/ </summary>
		('link_error_code2',c_uint),

		#/ </summary>
		('bus_status',c_uint32),

		#/ </summary>
		('sys_sdo_idel',c_uint),

		#/ </summary>
		('user_sdo_idel',c_uint),

		#/ </summary>
		('frame_length', c_uint * 16),

		#/ </summary>
		('pds_phase',c_uint32),

		#/ </summary>
		('debug1',c_uint),

		#/ </summary>
		('debug2',c_uint),

		#/ </summary>
		('debug3',c_uint),

		#/ </summary>
		('res1', c_uint * 9),

		#/ </summary>
		('res2', c_double * 32),
	]

# <summary>
# 总线数据包的辅助信息
# </summary>
class YKS_BusPacketHeader (Structure):
	_fields_ = [
		#/ </summary>
		('time',c_double),

		#/ </summary>
		('rev_flag',c_uint32),

		#/ </summary>
		('source_mac', c_ubyte * 6),

		#/ </summary>
		('destion_mac', c_ubyte * 6),

		#/ </summary>
		('ethernet_type',c_uint),

		#/ </summary>
		('length',c_uint),

		#/ </summary>
		('res1', c_uint * 4),

		#/ </summary>
		('res2', c_double * 4),
	]

# <summary>
# SDO命令状态
# </summary>
class YKS_SdoStatus (Structure):
	_fields_ = [
		#/ </summary>
		('valid',c_uint32),

		#/ </summary>
		('data',c_uint),

		#/ </summary>
		('tim',c_double),

		#/ </summary>
		('res1', c_uint * 8),
	]

# <summary>
# 总线从站状态
# </summary>
class YKS_SlaveStatus (Structure):
	_fields_ = [
		#/ </summary>
		('esc_status',c_ushort),

		#/ </summary>
		('station_id',c_ushort),

		#/ </summary>
		('clock_offset',c_int),

		#/ </summary>
		('slave_error_type',c_uint32),

		#/ </summary>
		('slave_error_code',c_uint),

		#/ </summary>
		('coe_type',c_uint),

		#/ </summary>
		('coe_code',c_uint),

		#/ </summary>
		('al_res',c_uint),

		#/ </summary>
		('al_code',c_uint),

		#/ </summary>
		('offline',c_uint),

		#/ </summary>
		('pdo_start',c_uint),

		#/ </summary>
		('pdo_length',c_uint),

		#/ </summary>
		('user_vid',c_uint),

		#/ </summary>
		('user_pid',c_uint),

		#/ </summary>
		('user_revsion',c_uint),

		#/ </summary>
		('eep_vid',c_uint),

		#/ </summary>
		('eep_pid',c_uint),

		#/ </summary>
		('eep_revsion',c_uint),

		#/ </summary>
		('port_link', c_uint32 * 4),

		#/ </summary>
		('res1', c_uint * 9),

		#/ </summary>
		('res2', c_double * 24),
	]

# <summary>
# 从站PDO配置
# </summary>
class YKS_SlavePdoConfig (Structure):
	_fields_ = [
		#/ </summary>
		('main_index',c_uint),

		#/ </summary>
		('sub_index',c_uint),

		#/ </summary>
		('bit_num',c_uint),

		#/ </summary>
		('bit_offset',c_uint),

		#/ </summary>
		('g_index',c_uint),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 模轴参数
# </summary>
class YKS_AxisProfileModulo (Structure):
	_fields_ = [
		#/ </summary>
		('enable',c_uint32),

		#/ </summary>
		('drv_modulo_status',c_uint32),

		#/ </summary>
		('single_encoder_count',c_uint),

		#/ </summary>
		('half_turn',c_uint32),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 单轴运动曲线参数
# </summary>
class YKS_AxisProfileMotion (Structure):
	_fields_ = [
		#/ </summary>
		('curve_type',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('start_velocity',c_double),

		#/ </summary>
		('stop_velocity',c_double),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk_acc',c_double),

		#/ </summary>
		('jerk_dec',c_double),

		#/ </summary>
		('constant_velocity_time',c_double),

		#/ </summary>
		('constant_acc_time',c_double),

		#/ </summary>
		('constant_dec_time',c_double),

		#/ </summary>
		('smooth_time',c_double),

		#/ </summary>
		('res', c_double * 32),
	]

# <summary>
# 单轴基本运动参数配置
# </summary>
class YKS_AxisProfileBase (Structure):
	_fields_ = [
		#/ </summary>
		('max_velocity',c_double),

		#/ </summary>
		('max_acceleration',c_double),

		#/ </summary>
		('max_jerk',c_double),

		#/ </summary>
		('stop_dec_emg',c_double),

		#/ </summary>
		('stop_dec_smooth',c_double),

		#/ </summary>
		('stop_dec_limitsoft',c_double),

		#/ </summary>
		('stop_dec_jerk',c_double),

		#/ </summary>
		('enable_cnc',c_uint32),

		#/ </summary>
		('emg_behavior',c_uint32),

		#/ </summary>
		('emg_mask',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('debug1',c_double),

		#/ </summary>
		('res1', c_uint * 16),

		#/ </summary>
		('res2', c_uint * 16),
	]

# <summary>
# 单轴基本运动参数,到位相关
# </summary>
class YKS_AxisProfileInp (Structure):
	_fields_ = [
		#/ </summary>
		('inp',c_double),

		#/ </summary>
		('inp_tim',c_double),

		#/ </summary>
		('inp_timout',c_double),

		#/ </summary>
		('inp1_fb',c_double),

		#/ </summary>
		('inp2_fb',c_double),

		#/ </summary>
		('inp3_fb',c_double),

		#/ </summary>
		('inp4_fb',c_double),

		#/ </summary>
		('inp5_fb',c_double),

		#/ </summary>
		('inp6_fb',c_double),

		#/ </summary>
		('tq_inp',c_double),

		#/ </summary>
		('tq_tim',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 单轴基本运动参数, 跟随误差相关
# </summary>
class YKS_AxisProfilePositionLag (Structure):
	_fields_ = [
		#/ </summary>
		('position_lag_tim',c_double),

		#/ </summary>
		('position_lag_limit',c_double),

		#/ </summary>
		('position_lag_filter_time',c_double),

		#/ </summary>
		('master_position_lag_limit',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 清驱动器报警机制设置
# </summary>
class YKS_AxisProfileClearDrv (Structure):
	_fields_ = [
		#/ </summary>
		('wait_tim',c_double),

		#/ </summary>
		('retry',c_uint),

		#/ </summary>
		('force',c_uint32),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 轴使能机制设置
# </summary>
class YKS_AxisProfilePowerOn (Structure):
	_fields_ = [
		#/ </summary>
		('wait_tim',c_double),

		#/ </summary>
		('lock_tim',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 轴前馈配置
# </summary>
class YKS_AxisProfileFeedforward (Structure):
	_fields_ = [
		#/ </summary>
		('enable',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('velocity_weighting',c_double),

		#/ </summary>
		('velocity_delay',c_double),

		#/ </summary>
		('acceleration_weighting',c_double),

		#/ </summary>
		('acceleration_delay',c_double),

		#/ </summary>
		('jerk_weighting',c_double),

		#/ </summary>
		('jerk_delay',c_double),

		#/ </summary>
		('global_weighting',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 轴基本配置
# </summary>
class YKS_AxisConfigBase (Structure):
	_fields_ = [
		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('phy_type',c_uint32),

		#/ </summary>
		('phy_main',c_uint),

		#/ </summary>
		('phy_sub',c_uint),

		#/ </summary>
		('res1', c_uint * 16),

		#/ </summary>
		('res2', c_double * 16),
	]

# <summary>
# 规划信息
# </summary>
class YKS_AxisStatusPlanner (Structure):
	_fields_ = [
		#/ </summary>
		('plann_flag',c_uint),

		#/ </summary>
		('command_done',c_uint32),

		#/ </summary>
		('command_done_time',c_double),

		#/ </summary>
		('command_run_time',c_double),

		#/ </summary>
		('actual_run_time',c_double),

		#/ </summary>
		('command_total_time',c_double),

		#/ </summary>
		('command_remain_time',c_double),

		#/ </summary>
		('change_time',c_double),

		#/ </summary>
		('payload',c_double),

		#/ </summary>
		('res1', c_uint * 16),

		#/ </summary>
		('res2', c_double * 16),
	]

# <summary>
# 轴位置相关状态
# </summary>
class YKS_AxisStatusPosition (Structure):
	_fields_ = [
		#/ </summary>
		('encoder_raw_position',c_int),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('position_offset',c_longlong),

		#/ </summary>
		('position_lag',c_double),

		#/ </summary>
		('position_lag_filter',c_double),

		#/ </summary>
		('fb_inp1',c_uint32),

		#/ </summary>
		('fb_inp2',c_uint32),

		#/ </summary>
		('fb_inp3',c_uint32),

		#/ </summary>
		('fb_inp4',c_uint32),

		#/ </summary>
		('fb_inp5',c_uint32),

		#/ </summary>
		('fb_inp6',c_uint32),

		#/ </summary>
		('res1', c_uint * 16),

		#/ </summary>
		('res2', c_double * 16),
	]

# <summary>
# 轴补偿状态
# </summary>
class YKS_AxisStatusCompensation (Structure):
	_fields_ = [
		#/ </summary>
		('pitch1d_active',c_uint32),

		#/ </summary>
		('pitch2d_active',c_uint32),

		#/ </summary>
		('backlash_active',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('pitch_value',c_double),

		#/ </summary>
		('backlash_value',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 轴跟随状态
# </summary>
class YKS_AxisStatusFollow (Structure):
	_fields_ = [
		#/ </summary>
		('follow_master',c_uint32),

		#/ </summary>
		('gantry_enable',c_uint32),

		#/ </summary>
		('gantry_master_index',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('gantry_actual_err',c_double),

		#/ </summary>
		('follow_actual_err',c_double),

		#/ </summary>
		('converyor_sync_status',c_uint32),

		#/ </summary>
		('res1', c_uint * 7),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 轴基本状态
# </summary>
class YKS_AxisStatusBase (Structure):
	_fields_ = [
		#/ </summary>
		('motion_type',c_uint32),

		#/ </summary>
		('stop_type',c_uint32),

		#/ </summary>
		('direction',c_uint32),

		#/ </summary>
		('power_on',c_uint32),

		#/ </summary>
		('is_homed',c_uint32),

		#/ </summary>
		('active',c_uint),

		#/ </summary>
		('done',c_uint32),

		#/ </summary>
		('lock_busy',c_uint),

		#/ </summary>
		('warnning',c_uint),

		#/ </summary>
		('axis_warn_id',c_uint32),

		#/ </summary>
		('drv_error_id',c_uint),

		#/ </summary>
		('offline',c_uint32),

		#/ </summary>
		('home_switch',c_uint32),

		#/ </summary>
		('limit_switch_pos',c_uint32),

		#/ </summary>
		('limit_switch_neg',c_uint32),

		#/ </summary>
		('limit_soft_pos',c_uint32),

		#/ </summary>
		('limit_soft_neg',c_uint32),

		#/ </summary>
		('soft_emg',c_uint),

		#/ </summary>
		('hard_emg',c_uint),

		#/ </summary>
		('circle_zone',c_uint),

		#/ </summary>
		('res1', c_uint * 16),

		#/ </summary>
		('res2', c_double * 16),
	]

# <summary>
# 多轴运动状态
# </summary>
class YKS_MultiAxisStatus (Structure):
	_fields_ = [
		#/ </summary>
		('active',c_uint32),

		#/ </summary>
		('done',c_uint32),

		#/ </summary>
		('error',c_uint32),

		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('total_tim',c_double),

		#/ </summary>
		('completed_dist',c_double),

		#/ </summary>
		('remain_dist',c_double),

		#/ </summary>
		('completed_tim',c_double),

		#/ </summary>
		('remain_tim',c_double),

		#/ </summary>
		('debug1',c_uint),

		#/ </summary>
		('res1', c_uint * 9),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 轴软件探针配置
# </summary>
class YKS_AxisProbeConfigSoft (Structure):
	_fields_ = [
		#/ </summary>
		('input',YKS_DigitalIO),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('trig_once',c_uint32),

		#/ </summary>
		('item',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 软件探针状态
# </summary>
class YKS_AxisProbeStatusSoft (Structure):
	_fields_ = [
		#/ </summary>
		('active',c_uint32),

		#/ </summary>
		('count',c_uint),

		#/ </summary>
		('value',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 回原点参数
# </summary>
class YKS_AxisHomeConfig (Structure):
	_fields_ = [
		#/ </summary>
		('curve_type',c_uint32),

		#/ </summary>
		('mode',c_uint32),

		#/ </summary>
		('out_of_probe',c_uint32),

		#/ </summary>
		('pre_probe',c_uint32),

		#/ </summary>
		('index_probe',c_uint),

		#/ </summary>
		('keep_position',c_uint32),

		#/ </summary>
		('clear_encoder',c_uint32),

		#/ </summary>
		('res1', c_uint * 7),

		#/ </summary>
		('logic_position',c_double),

		#/ </summary>
		('vel_high',c_double),

		#/ </summary>
		('vel_low',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('switch_move',c_double),

		#/ </summary>
		('probe_move',c_double),

		#/ </summary>
		('offset',c_double),

		#/ </summary>
		('torque_limit',c_double),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 运动仿真规划信息
# </summary>
class YKS_MovePositionSimResult (Structure):
	_fields_ = [
		#/ </summary>
		('acc_tim',c_double),

		#/ </summary>
		('constant_tim',c_double),

		#/ </summary>
		('dec_tim',c_double),

		#/ </summary>
		('total_tim',c_double),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('position_of_time',c_double),

		#/ </summary>
		('velocity_of_time',c_double),

		#/ </summary>
		('acceleration_of_time',c_double),

		#/ </summary>
		('jerk_of_time',c_double),

		#/ </summary>
		('time_of_position',c_double),

		#/ </summary>
		('velocity_of_position',c_double),

		#/ </summary>
		('acceleration_of_position',c_double),

		#/ </summary>
		('jerk_of_position',c_double),

		#/ </summary>
		('res1', c_uint * 16),

		#/ </summary>
		('res2', c_double * 16),
	]

# <summary>
# 绝对运动配置
# </summary>
class YKS_MoveAbsoluteConfig (Structure):
	_fields_ = [
		#/ </summary>
		('position',c_double),

		#/ </summary>
		('motion',YKS_AxisProfileMotion),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 仿真运动配置
# </summary>
class YKS_MovePositionSimConfig (Structure):
	_fields_ = [
		#/ </summary>
		('motion',YKS_AxisProfileMotion),

		#/ </summary>
		('position',c_double),

		#/ </summary>
		('time_type',c_uint32),

		#/ </summary>
		('set_start_pos',c_uint32),

		#/ </summary>
		('start_pos',c_double),

		#/ </summary>
		('at_position',c_double),

		#/ </summary>
		('at_time',c_double),

		#/ </summary>
		('at_calc',c_uint32),

		#/ </summary>
		('res1', c_uint * 7),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 传送带运动配置
# </summary>
class YKS_MoveConveyorConfig (Structure):
	_fields_ = [
		#/ </summary>
		('direction',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('distance',c_double),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 相对运动配置
# </summary>
class YKS_MoveRelativeConfig (Structure):
	_fields_ = [
		#/ </summary>
		('distance',c_double),

		#/ </summary>
		('motion',YKS_AxisProfileMotion),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 速度运动配置
# </summary>
class YKS_MoveVelocityConfig (Structure):
	_fields_ = [
		#/ </summary>
		('direction',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('motion',YKS_AxisProfileMotion),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 转矩运动配置
# </summary>
class YKS_MoveTorqueConfig (Structure):
	_fields_ = [
		#/ </summary>
		('velocity_max',c_double),

		#/ </summary>
		('torque',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 间隙补偿配置
# </summary>
class YKS_BacklashConfig (Structure):
	_fields_ = [
		#/ </summary>
		('dir',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('backlash_high',c_double),

		#/ </summary>
		('backlash_low',c_double),

		#/ </summary>
		('distance_high',c_double),

		#/ </summary>
		('distance_low',c_double),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 一维螺距补偿配置
# </summary>
class YKS_PitchError1DConfig (Structure):
	_fields_ = [
		#/ </summary>
		('count',c_uint),

		#/ </summary>
		('origin_index',c_uint),

		#/ </summary>
		('origin_position',c_double),

		#/ </summary>
		('pitch_interval',c_double),

		#/ </summary>
		('catchup_velocity',c_double),

		#/ </summary>
		('catchup_acceleration',c_double),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 二维螺距补偿配置
# </summary>
class YKS_PitchError2DConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_index0',c_uint),

		#/ </summary>
		('axis_index1',c_uint),

		#/ </summary>
		('origin_index0',c_uint),

		#/ </summary>
		('origin_index1',c_uint),

		#/ </summary>
		('count0',c_uint),

		#/ </summary>
		('count1',c_uint),

		#/ </summary>
		('origin_position0',c_double),

		#/ </summary>
		('origin_position1',c_double),

		#/ </summary>
		('pitch_interval0',c_double),

		#/ </summary>
		('pitch_interval1',c_double),

		#/ </summary>
		('catchup_velocity',c_double),

		#/ </summary>
		('catchup_acceleration',c_double),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 单轴跟随配置
# </summary>
class YKS_FollowAxis1Config (Structure):
	_fields_ = [
		#/ </summary>
		('mode',c_uint32),

		#/ </summary>
		('source',c_uint32),

		#/ </summary>
		('axis_master',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('numerator',c_double),

		#/ </summary>
		('denominator',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 双轴跟随配置
# </summary>
class YKS_FollowAxis2Config (Structure):
	_fields_ = [
		#/ </summary>
		('combine_mode',c_uint32),

		#/ </summary>
		('follow_mode',c_uint32),

		#/ </summary>
		('source1',c_uint32),

		#/ </summary>
		('source2',c_uint32),

		#/ </summary>
		('axis_master1',c_uint),

		#/ </summary>
		('axis_master2',c_uint),

		#/ </summary>
		('numerator1',c_double),

		#/ </summary>
		('denominator1',c_double),

		#/ </summary>
		('numerator2',c_double),

		#/ </summary>
		('denominator2',c_double),

		#/ </summary>
		('numerator3',c_double),

		#/ </summary>
		('denominator3',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# UG跟随配置
# </summary>
class YKS_FollowUgConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mode',c_uint32),

		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('u_index',c_uint),

		#/ </summary>
		('g_index',c_uint),

		#/ </summary>
		('bit32',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('filter_tim',c_double),

		#/ </summary>
		('numerator',c_double),

		#/ </summary>
		('denominator',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系跟随配置
# </summary>
class YKS_FollowGroupConfig (Structure):
	_fields_ = [
		#/ </summary>
		('group_index',c_uint),

		#/ </summary>
		('mode',c_uint32),

		#/ </summary>
		('source',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('numerator',c_double),

		#/ </summary>
		('denominator',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 本地编码器跟随配置
# </summary>
class YKS_FollowEncoderConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mode',c_uint32),

		#/ </summary>
		('card_index',c_uint),

		#/ </summary>
		('encoder_index',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('filter_tim',c_double),

		#/ </summary>
		('numerator',c_double),

		#/ </summary>
		('denominator',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 凸轮配置
# </summary>
class YKS_CamInConfig (Structure):
	_fields_ = [
		#/ </summary>
		('count',c_uint),

		#/ </summary>
		('curve',c_uint32),

		#/ </summary>
		('axis_master',c_uint),

		#/ </summary>
		('periodic',c_uint32),

		#/ </summary>
		('master_absolute',c_uint32),

		#/ </summary>
		('slave_absolute',c_uint32),

		#/ </summary>
		('master_scale',c_double),

		#/ </summary>
		('slave_scale',c_double),

		#/ </summary>
		('master_offset',c_double),

		#/ </summary>
		('slave_offset',c_double),

		#/ </summary>
		('start_distance',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 凸轮数据
# </summary>
class YKS_CamTable (Structure):
	_fields_ = [
		#/ </summary>
		('master_position',c_double),

		#/ </summary>
		('slave_position',c_double),

		#/ </summary>
		('vel_rate',c_double),

		#/ </summary>
		('acc_rate',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系设置,最大32轴
# </summary>
class YKS_GroupConfig (Structure):
	_fields_ = [
		#/ </summary>
		('buffer_depth',c_uint),

		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('cnc_enable',c_uint32),

		#/ </summary>
		('cnc_mode',c_uint32),

		#/ </summary>
		('close_loop', c_uint32 * 32),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系配置
# </summary>
class YKS_GroupProfile (Structure):
	_fields_ = [
		#/ </summary>
		('max_velocity',c_double),

		#/ </summary>
		('stop_dec_emg',c_double),

		#/ </summary>
		('stop_dec_smooth',c_double),

		#/ </summary>
		('stop_dec_jerk',c_double),

		#/ </summary>
		('output_in_warm',c_uint32),

		#/ </summary>
		('emg_mask',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内CNC配置
# </summary>
class YKS_CncProfile (Structure):
	_fields_ = [
		#/ </summary>
		('feed_rate',c_double),

		#/ </summary>
		('res1', c_uint * 16),

		#/ </summary>
		('res2', c_double * 16),
	]

# <summary>
# MARK坐标系转换
# </summary>
class YKS_GroupTransMarkConfig (Structure):
	_fields_ = [
		#/ </summary>
		('rotate_x',c_double),

		#/ </summary>
		('rotate_y',c_double),

		#/ </summary>
		('offset_x',c_double),

		#/ </summary>
		('offset_y',c_double),

		#/ </summary>
		('scale_x',c_double),

		#/ </summary>
		('scale_y',c_double),

		#/ </summary>
		('angle',c_double),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 坐标系附加的XY输出
# </summary>
class YKS_GroupAddiXYConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_x',c_uint),

		#/ </summary>
		('axis_y',c_uint),

		#/ </summary>
		('trans_config',YKS_GroupTransMarkConfig),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 坐标系基本状态
# </summary>
class YKS_GroupStatusBase (Structure):
	_fields_ = [
		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('inited',c_uint32),

		#/ </summary>
		('active',c_uint32),

		#/ </summary>
		('done',c_uint32),

		#/ </summary>
		('warnning',c_uint32),

		#/ </summary>
		('pause',c_uint32),

		#/ </summary>
		('warn_id',c_uint32),

		#/ </summary>
		('plan_warn',c_uint),

		#/ </summary>
		('soft_emg',c_uint),

		#/ </summary>
		('hard_emg',c_uint),

		#/ </summary>
		('buffer_idel',c_uint),

		#/ </summary>
		('running_line',c_uint),

		#/ </summary>
		('running_mark',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('distance_2d',c_double),

		#/ </summary>
		('distance_3d',c_double),

		#/ </summary>
		('velocity_2d',c_double),

		#/ </summary>
		('velocity_3d',c_double),

		#/ </summary>
		('velocity_feed',c_double),

		#/ </summary>
		('acceleration_feed',c_double),

		#/ </summary>
		('command_time',c_double),

		#/ </summary>
		('actual_time',c_double),

		#/ </summary>
		('plann_type',c_uint),

		#/ </summary>
		('debug_phase',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 24),
	]

# <summary>
# 坐标系CNC模块状态, 须开启CNC选项
# </summary>
class YKS_GroupStatusCnc (Structure):
	_fields_ = [
		#/ </summary>
		('workpiece_pos', c_double * 6),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 24),
	]

# <summary>
# 坐标系直线插补,绝对模式
# </summary>
class YKS_MoveLinearAbsoluteConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('position', c_double * 32),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('buffer_mode',c_uint32),

		#/ </summary>
		('trans_mode',c_uint32),

		#/ </summary>
		('trans_para',YKS_POINT3),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res1',c_uint),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 坐标系直线插补,相对模式
# </summary>
class YKS_MoveLinearRelativeConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('distance', c_double * 32),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('buffer_mode',c_uint32),

		#/ </summary>
		('trans_mode',c_uint32),

		#/ </summary>
		('trans_para',YKS_POINT3),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res1',c_uint),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 坐标系螺旋插补,相对模式
# </summary>
class YKS_MoveHelixRelativeConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('path_choice',c_uint32),

		#/ </summary>
		('aux_mode',c_uint32),

		#/ </summary>
		('distance',YKS_POINT3),

		#/ </summary>
		('aux_point',YKS_POINT3),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('buffer_mode',c_uint32),

		#/ </summary>
		('trans_mode',c_uint32),

		#/ </summary>
		('trans_para',YKS_POINT3),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('circle',c_uint),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 坐标系螺旋插补,绝对模式
# </summary>
class YKS_MoveHelixAbsoluteConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('path_choice',c_uint32),

		#/ </summary>
		('aux_mode',c_uint32),

		#/ </summary>
		('end_point',YKS_POINT3),

		#/ </summary>
		('aux_point',YKS_POINT3),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('buffer_mode',c_uint32),

		#/ </summary>
		('trans_mode',c_uint32),

		#/ </summary>
		('trans_para',YKS_POINT3),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('circle',c_uint),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 坐标系圆弧插补,绝对模式
# </summary>
class YKS_MoveCircularAbsoluteConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('position', c_double * 32),

		#/ </summary>
		('path_choice',c_uint32),

		#/ </summary>
		('aux_mode',c_uint32),

		#/ </summary>
		('aux_point',YKS_POINT3),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('buffer_mode',c_uint32),

		#/ </summary>
		('trans_mode',c_uint32),

		#/ </summary>
		('trans_para',YKS_POINT3),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 坐标系圆弧插补,相对模式
# </summary>
class YKS_MoveCircularRelativeConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('distance', c_double * 32),

		#/ </summary>
		('path_choice',c_uint32),

		#/ </summary>
		('aux_mode',c_uint32),

		#/ </summary>
		('aux_point',YKS_POINT3),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('buffer_mode',c_uint32),

		#/ </summary>
		('trans_mode',c_uint32),

		#/ </summary>
		('trans_para',YKS_POINT3),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 坐标系Cardinal样条插补,相对模式
# </summary>
class YKS_MoveCardinalRelativeConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('distance', c_double * 32),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('buffer_mode',c_uint32),

		#/ </summary>
		('trans_mode',c_uint32),

		#/ </summary>
		('trans_para',YKS_POINT3),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res1',c_uint),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 坐标系Cardinal样条插补,绝对模式
# </summary>
class YKS_MoveCardinalAbsoluteConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('position', c_double * 32),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('acceleration',c_double),

		#/ </summary>
		('deceleration',c_double),

		#/ </summary>
		('jerk',c_double),

		#/ </summary>
		('buffer_mode',c_uint32),

		#/ </summary>
		('trans_mode',c_uint32),

		#/ </summary>
		('trans_para',YKS_POINT3),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res1',c_uint),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 轴信号等待条件
# </summary>
class YKS_WaitAxis (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('timeout',c_double),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 数字输入信号等待条件
# </summary>
class YKS_WaitDigitalInput (Structure):
	_fields_ = [
		#/ </summary>
		('di_num',c_uint),

		#/ </summary>
		('byte_offset', c_uint * 32),

		#/ </summary>
		('bit_offset', c_uint * 32),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('timeout',c_double),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 事件信号等待条件
# </summary>
class YKS_WaitEvent (Structure):
	_fields_ = [
		#/ </summary>
		('event_num',c_uint),

		#/ </summary>
		('event_index', c_uint * 32),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('timeout',c_double),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 等待状态
# </summary>
class YKS_WaitStatus (Structure):
	_fields_ = [
		#/ </summary>
		('active',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('time',c_double),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 圆形区域保护
# </summary>
class YKS_CircleZoneConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('axis_list', c_uint * 3),

		#/ </summary>
		('use_feedback',c_uint32),

		#/ </summary>
		('outside',c_uint32),

		#/ </summary>
		('stop_dec',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('center', c_double * 3),

		#/ </summary>
		('radius',c_double),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 圆形区域保护
# </summary>
class YKS_CircleZoneStatus (Structure):
	_fields_ = [
		#/ </summary>
		('enable',c_uint32),

		#/ </summary>
		('invalid',c_uint32),
	]

# <summary>
# 本地PCI卡配置信息
# </summary>
class YKS_CardConfigPCI (Structure):
	_fields_ = [
		#/ </summary>
		('type',c_uint),

		#/ </summary>
		('hardware_ver',c_uint),

		#/ </summary>
		('firmware_ver',c_uint),

		#/ </summary>
		('dinput_num',c_uint),

		#/ </summary>
		('doutput_num',c_uint),

		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('encode_num',c_uint),

		#/ </summary>
		('compare_num',c_uint),

		#/ </summary>
		('capture_num',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 本地PCI卡脉冲轴IO信息
# </summary>
class YKS_AxisStausPCI (Structure):
	_fields_ = [
		#/ </summary>
		('pls_pin',c_uint),

		#/ </summary>
		('dir_pin',c_uint),

		#/ </summary>
		('mode',c_uint32),

		#/ </summary>
		('duty',c_uint),

		#/ </summary>
		('switch_limit_negative',c_uint32),

		#/ </summary>
		('switch_limit_positive',c_uint32),

		#/ </summary>
		('switch_home',c_uint32),

		#/ </summary>
		('drv_ready',c_uint32),

		#/ </summary>
		('drv_warn',c_uint32),

		#/ </summary>
		('drv_inp',c_uint32),

		#/ </summary>
		('drv_enable',c_uint32),

		#/ </summary>
		('drv_reset',c_uint32),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 本地PCI控制卡编码器配置
# </summary>
class YKS_EncoderConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mode',c_uint32),

		#/ </summary>
		('polarity_a',c_uint32),

		#/ </summary>
		('polarity_b',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 本地PCI控制卡位置比较器配置
# </summary>
class YKS_CompareConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mode',c_uint32),

		#/ </summary>
		('enable_2d',c_uint32),

		#/ </summary>
		('keep_time',c_double),

		#/ </summary>
		('number',c_uint),

		#/ </summary>
		('spacing1',c_int),

		#/ </summary>
		('spacing2',c_int),

		#/ </summary>
		('ena_bit0',c_uint32),

		#/ </summary>
		('ena_bit1',c_uint32),

		#/ </summary>
		('ena_bit2',c_uint32),

		#/ </summary>
		('ena_bit3',c_uint32),

		#/ </summary>
		('res1', c_uint * 7),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 监控对象：轴
# </summary>
class YKS_OscItemAxis (Structure):
	_fields_ = [
		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：坐标系
# </summary>
class YKS_OscItemGroup (Structure):
	_fields_ = [
		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：对象字典
# </summary>
class YKS_OscItemSlaveObject (Structure):
	_fields_ = [
		#/ </summary>
		('node',c_uint32),

		#/ </summary>
		('slave_index',c_uint),

		#/ </summary>
		('main_index',c_uint),

		#/ </summary>
		('sub_index',c_uint),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：对象字典
# </summary>
class YKS_OscItemSlaveUG (Structure):
	_fields_ = [
		#/ </summary>
		('node',c_uint32),

		#/ </summary>
		('slave_index',c_uint),

		#/ </summary>
		('g_index',c_uint),

		#/ </summary>
		('g_dword',c_uint32),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：数字输入
# </summary>
class YKS_OscItemDI (Structure):
	_fields_ = [
		#/ </summary>
		('byte_index',c_uint),

		#/ </summary>
		('bit_offset',c_uint),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：数字输出
# </summary>
class YKS_OscItemDO (Structure):
	_fields_ = [
		#/ </summary>
		('byte_index',c_uint),

		#/ </summary>
		('bit_offset',c_uint),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：数据寄存器
# </summary>
class YKS_OscItemReg (Structure):
	_fields_ = [
		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('data_type',c_uint32),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：系统信息
# </summary>
class YKS_OscItemSystem (Structure):
	_fields_ = [
		#/ </summary>
		('node',c_uint32),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：编码器
# </summary>
class YKS_OscItemEncoder (Structure):
	_fields_ = [
		#/ </summary>
		('card_index',c_uint),

		#/ </summary>
		('encoder_index',c_uint),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：事件
# </summary>
class YKS_OscItemEvent (Structure):
	_fields_ = [
		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：多轴联动
# </summary>
class YKS_OscItemMultiAxis (Structure):
	_fields_ = [
		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象：等待事件
# </summary>
class YKS_OscItemWait (Structure):
	_fields_ = [
		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('res', c_uint * 2),
	]

# <summary>
# 监控对象
# </summary>
class YKS_OscItem (Structure):
	_fields_ = [
		#/ </summary>
		('enable',c_uint32),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('axis',YKS_OscItemAxis),

		#/ </summary>
		('group',YKS_OscItemGroup),

		#/ </summary>
		('coe_obj',YKS_OscItemSlaveObject),

		#/ </summary>
		('ug',YKS_OscItemSlaveUG),

		#/ </summary>
		('digital_input',YKS_OscItemDI),

		#/ </summary>
		('digital_output',YKS_OscItemDO),

		#/ </summary>
		('sys_reg',YKS_OscItemReg),

		#/ </summary>
		('sys_info',YKS_OscItemSystem),

		#/ </summary>
		('encoder',YKS_OscItemEncoder),

		#/ </summary>
		('sys_event',YKS_OscItemEvent),

		#/ </summary>
		('multi_axis',YKS_OscItemMultiAxis),

		#/ </summary>
		('wait',YKS_OscItemWait),

		#/ </summary>
		('res1', c_uint * 24),

		#/ </summary>
		('res2', c_double * 24),
	]

# <summary>
# 打印日志其他配置
# </summary>
class YKS_LoggerItemConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_enable',c_uint32),

		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('group_enable',c_uint32),

		#/ </summary>
		('group_index',c_uint),

		#/ </summary>
		('card_enable',c_uint32),

		#/ </summary>
		('card_index',c_uint),

		#/ </summary>
		('bus_enable',c_uint32),

		#/ </summary>
		('slave_index',c_uint),

		#/ </summary>
		('event_enable',c_uint32),

		#/ </summary>
		('event_index',c_uint),

		#/ </summary>
		('multi_axis_enable',c_uint32),

		#/ </summary>
		('multi_axis_index',c_uint),

		#/ </summary>
		('wait_enable',c_uint32),

		#/ </summary>
		('wait_index',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_uint * 8),
	]

# <summary>
# 日志配置
# </summary>
class YKS_LoggerConfig (Structure):
	_fields_ = [
		#/ </summary>
		('file_path', c_char * 512),

		#/ </summary>
		('file_name', c_char * 64),

		#/ </summary>
		('interval',c_double),

		#/ </summary>
		('do_output',c_uint32),

		#/ </summary>
		('user_data',c_uint32),

		#/ </summary>
		('ret_ng',c_uint32),

		#/ </summary>
		('ret_ok',c_uint32),

		#/ </summary>
		('zero_value',c_uint32),

		#/ </summary>
		('res', c_uint * 10),

		#/ </summary>
		('filter_type',c_uint32),

		#/ </summary>
		('item_config', YKS_LoggerItemConfig * 32),
	]

# <summary>
# 保留
# </summary>
class YKS_ExcTrackItem (Structure):
	_fields_ = [
		#/ </summary>
		('type',c_uint),

		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('file',c_uint),

		#/ </summary>
		('line',c_uint),

		#/ </summary>
		('value',c_int),

		#/ </summary>
		('tick',c_uint),
	]

# <summary>
# 保留
# </summary>
class YKS_ExcTrackConfig (Structure):
	_fields_ = [
		#/ </summary>
		('item_number',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('item_config', YKS_LoggerItemConfig * 16),
	]

# <summary>
# 软模式位置比较器配置
# </summary>
class YKS_CompareConfigSoft (Structure):
	_fields_ = [
		#/ </summary>
		('mode',c_uint32),

		#/ </summary>
		('enable_2d',c_uint32),

		#/ </summary>
		('source',YKS_OscItem),

		#/ </summary>
		('number',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('out0_enable',c_uint32),

		#/ </summary>
		('out0_byte',c_uint),

		#/ </summary>
		('out0_offset',c_uint),

		#/ </summary>
		('out1_enable',c_uint32),

		#/ </summary>
		('out1_byte',c_uint),

		#/ </summary>
		('out1_offset',c_uint),

		#/ </summary>
		('out2_enable',c_uint32),

		#/ </summary>
		('out2_byte',c_uint),

		#/ </summary>
		('out2_offset',c_uint),

		#/ </summary>
		('out3_enable',c_uint32),

		#/ </summary>
		('out3_byte',c_uint),

		#/ </summary>
		('out3_offset',c_uint),

		#/ </summary>
		('spacing1',c_double),

		#/ </summary>
		('spacing2',c_double),

		#/ </summary>
		('threshold',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 本地PCI控制卡位置比较器比较数据
# </summary>
class YKS_CompareItemData (Structure):
	_fields_ = [
		#/ </summary>
		('value1',c_int),

		#/ </summary>
		('value2',c_int),

		#/ </summary>
		('threshold',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('out_bit0',c_uint32),

		#/ </summary>
		('out_bit1',c_uint32),

		#/ </summary>
		('out_bit2',c_uint32),

		#/ </summary>
		('out_bit3',c_uint32),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 软件模式位置比较器比较数据
# </summary>
class YKS_CompareItemDataSoft (Structure):
	_fields_ = [
		#/ </summary>
		('cmp_value1',c_double),

		#/ </summary>
		('cmp_value2',c_double),

		#/ </summary>
		('out0_value',c_uint32),

		#/ </summary>
		('out1_value',c_uint32),

		#/ </summary>
		('out2_value',c_uint32),

		#/ </summary>
		('out3_value',c_uint32),

		#/ </summary>
		('out0_time',c_double),

		#/ </summary>
		('out1_time',c_double),

		#/ </summary>
		('out2_time',c_double),

		#/ </summary>
		('out3_time',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 本地PCI控制卡位置比较器状态
# </summary>
class YKS_CompareStatus (Structure):
	_fields_ = [
		#/ </summary>
		('que_head',c_uint),

		#/ </summary>
		('que_tail',c_uint),

		#/ </summary>
		('hd_idel',c_uint),

		#/ </summary>
		('hd_active',c_uint),

		#/ </summary>
		('hd_finish',c_uint),

		#/ </summary>
		('soft_idel',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 软件模式位置比较器状态
# </summary>
class YKS_CompareStatusSoft (Structure):
	_fields_ = [
		#/ </summary>
		('que_head',c_uint),

		#/ </summary>
		('que_tail',c_uint),

		#/ </summary>
		('finish',c_uint32),

		#/ </summary>
		('success',c_uint),

		#/ </summary>
		('error_count',c_uint),

		#/ </summary>
		('active',c_uint32),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 本地PCI控制卡位置锁存配置
# </summary>
class YKS_CaptureConfig (Structure):
	_fields_ = [
		#/ </summary>
		('source_type',c_uint32),

		#/ </summary>
		('edge',c_uint32),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 本地PCI控制卡PWM输出配置
# </summary>
class YKS_PwmConfig (Structure):
	_fields_ = [
		#/ </summary>
		('freq',c_double),

		#/ </summary>
		('duty',c_double),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内数字输出配置
# </summary>
class YKS_GroupDoConfig (Structure):
	_fields_ = [
		#/ </summary>
		('cmp_mode',c_uint32),

		#/ </summary>
		('out_mode',c_uint32),

		#/ </summary>
		('byte_index',c_uint),

		#/ </summary>
		('bit_offset',c_uint),

		#/ </summary>
		('value',c_uint32),

		#/ </summary>
		('span',c_uint),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('cmp_src',c_uint32),

		#/ </summary>
		('time_dist_rate',c_double),

		#/ </summary>
		('single_unit',c_uint32),

		#/ </summary>
		('res2',c_uint),

		#/ </summary>
		('single_time_dist',c_double),

		#/ </summary>
		('number',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('time_dist_on',c_double),

		#/ </summary>
		('time_dist_off',c_double),

		#/ </summary>
		('alter_unit',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res3', c_double * 8),
	]

# <summary>
# 坐标系内PWM输出配置
# </summary>
class YKS_GroupPwmConfig (Structure):
	_fields_ = [
		#/ </summary>
		('cmp_mode',c_uint32),

		#/ </summary>
		('cmp_src',c_uint32),

		#/ </summary>
		('time_dist_rate',c_double),

		#/ </summary>
		('span',c_uint),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('pwm_mode',c_uint32),

		#/ </summary>
		('card_index',c_uint),

		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('value',c_uint32),

		#/ </summary>
		('filter_tim',c_double),

		#/ </summary>
		('freq_value',c_double),

		#/ </summary>
		('duty_value',c_double),

		#/ </summary>
		('freq_scale',c_double),

		#/ </summary>
		('duty_scale',c_double),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内PDO写入配置
# </summary>
class YKS_GroupWritePdoConfig (Structure):
	_fields_ = [
		#/ </summary>
		('cmp_mode',c_uint32),

		#/ </summary>
		('cmp_src',c_uint32),

		#/ </summary>
		('time_dist_rate',c_double),

		#/ </summary>
		('span',c_uint),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('slave_index',c_uint),

		#/ </summary>
		('main_index',c_uint),

		#/ </summary>
		('sub_index',c_uint),

		#/ </summary>
		('data_type',c_uint32),

		#/ </summary>
		('value',c_uint),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内寄存器写入配置
# </summary>
class YKS_GroupWriteRegisterConfig (Structure):
	_fields_ = [
		#/ </summary>
		('cmp_mode',c_uint32),

		#/ </summary>
		('cmp_src',c_uint32),

		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('time_dist_rate',c_double),

		#/ </summary>
		('span',c_uint),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('data_type',c_uint32),

		#/ </summary>
		('value',c_uint),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内启动事件配置
# </summary>
class YKS_GroupWriteEventConfig (Structure):
	_fields_ = [
		#/ </summary>
		('cmp_mode',c_uint32),

		#/ </summary>
		('cmp_src',c_uint32),

		#/ </summary>
		('time_dist_rate',c_double),

		#/ </summary>
		('span',c_uint),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内延时配置
# </summary>
class YKS_GroupDelayConfig (Structure):
	_fields_ = [
		#/ </summary>
		('delay_ms',c_double),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内等待数字输入配置
# </summary>
class YKS_GroupDigitalInputConfig (Structure):
	_fields_ = [
		#/ </summary>
		('byte_index',c_uint),

		#/ </summary>
		('bit_offset',c_uint),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内等待外轴运动完成
# </summary>
class YKS_GroupWaitAxisConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('item_type',c_uint32),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('trig_value',c_double),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内等待PDO值
# </summary>
class YKS_GroupWaitPdoConfig (Structure):
	_fields_ = [
		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('slave_index',c_uint),

		#/ </summary>
		('main_index',c_uint),

		#/ </summary>
		('sub_index',c_uint),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('data_type',c_uint32),

		#/ </summary>
		('value',c_uint),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内等待寄存器值
# </summary>
class YKS_GroupWaitRegisterConfig (Structure):
	_fields_ = [
		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('data_type',c_uint32),

		#/ </summary>
		('value',c_uint),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 坐标系内等待事件
# </summary>
class YKS_GroupWaitEventConfig (Structure):
	_fields_ = [
		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# Cardinal样条配置
# </summary>
class YKS_GroupCardinalConfig (Structure):
	_fields_ = [
		#/ </summary>
		('tensive',c_double),

		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 示波器监控数据配置
# </summary>
class YKS_OscConfig (Structure):
	_fields_ = [
		#/ </summary>
		('depth',c_uint),

		#/ </summary>
		('interval',c_uint),

		#/ </summary>
		('unit',c_uint32),

		#/ </summary>
		('trig_ch',c_uint),

		#/ </summary>
		('trig_val',c_double),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('trig_pos',c_uint),

		#/ </summary>
		('trig_once',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 示波器采集状态
# </summary>
class YKS_OscStatus (Structure):
	_fields_ = [
		#/ </summary>
		('trig_flag',c_uint32),

		#/ </summary>
		('trig_index',c_uint),

		#/ </summary>
		('remain',c_uint),

		#/ </summary>
		('finish',c_uint32),

		#/ </summary>
		('buff_size',c_uint),

		#/ </summary>
		('buff_valid',c_uint),

		#/ </summary>
		('over_flow',c_uint32),

		#/ </summary>
		('axis_warn',c_uint32),

		#/ </summary>
		('master_period',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 数字IO关联的硬件信息
# </summary>
class YKS_DigitalIOHardInfo (Structure):
	_fields_ = [
		#/ </summary>
		('valid',c_uint32),

		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('index1',c_uint),

		#/ </summary>
		('index2',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 软限位设置
# </summary>
class YKS_AxisSoftLimitConfig (Structure):
	_fields_ = [
		#/ </summary>
		('positive',c_double),

		#/ </summary>
		('negative',c_double),

		#/ </summary>
		('enable',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 硬限位启用
# </summary>
class YKS_AxisHardLimitConfig (Structure):
	_fields_ = [
		#/ </summary>
		('enable_positive',c_uint32),

		#/ </summary>
		('enable_negative',c_uint32),

		#/ </summary>
		('res1', c_uint * 8),
	]

# <summary>
# 多轴直线插补运动,相对模式
# </summary>
class YKS_LinearInterpolationRelativeConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('distance', c_double * 32),

		#/ </summary>
		('motion',YKS_AxisProfileMotion),

		#/ </summary>
		('change_tim',c_double),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 多轴直线插补运动,绝对模式
# </summary>
class YKS_LinearInterpolationAbsoluteConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('position', c_double * 32),

		#/ </summary>
		('motion',YKS_AxisProfileMotion),

		#/ </summary>
		('change_tim',c_double),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 多轴直线同步运动,相对模式
# </summary>
class YKS_LinearSyncRelativeConfig (Structure):
	_fields_ = [
		#/ </summary>
		('sync_mode',c_uint32),

		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('distance', c_double * 32),

		#/ </summary>
		('change_tim',c_double),

		#/ </summary>
		('run_time',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 多轴直线同步运动,绝对模式
# </summary>
class YKS_LinearSyncAbsoluteConfig (Structure):
	_fields_ = [
		#/ </summary>
		('sync_mode',c_uint32),

		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('position', c_double * 32),

		#/ </summary>
		('change_tim',c_double),

		#/ </summary>
		('run_time',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 多轴同时启动
# </summary>
class YKS_SyncStartConfig (Structure):
	_fields_ = [
		#/ </summary>
		('sync_mode',c_uint32),

		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('position', c_double * 32),

		#/ </summary>
		('change_tim',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 圆弧插补,相对模式
# </summary>
class YKS_CircularInterpolationRelativeConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('distance',YKS_POINT3),

		#/ </summary>
		('aux_point',YKS_POINT3),

		#/ </summary>
		('path_choice',c_uint32),

		#/ </summary>
		('aux_mode',c_uint32),

		#/ </summary>
		('motion',YKS_AxisProfileMotion),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# 圆弧插补,绝对模式
# </summary>
class YKS_CircularInterpolationAbsoluteConfig (Structure):
	_fields_ = [
		#/ </summary>
		('axis_num',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('axis_list', c_uint * 32),

		#/ </summary>
		('end_point',YKS_POINT3),

		#/ </summary>
		('aux_point',YKS_POINT3),

		#/ </summary>
		('path_choice',c_uint32),

		#/ </summary>
		('aux_mode',c_uint32),

		#/ </summary>
		('motion',YKS_AxisProfileMotion),

		#/ </summary>
		('res', c_double * 4),
	]

# <summary>
# 探针配置
# </summary>
class YKS_ProbeConfigSoft (Structure):
	_fields_ = [
		#/ </summary>
		('input',YKS_DigitalIO),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('item',YKS_OscItem),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 探针状态
# </summary>
class YKS_ProbeStatusSoft (Structure):
	_fields_ = [
		#/ </summary>
		('active',c_uint32),

		#/ </summary>
		('valid',c_uint32),

		#/ </summary>
		('value',c_double),

		#/ </summary>
		('res1', c_uint * 4),

		#/ </summary>
		('res2', c_double * 4),
	]

# <summary>
# 触发配置
# </summary>
class YKS_AxisTrigger (Structure):
	_fields_ = [
		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('value',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 轴触发状态
# </summary>
class YKS_AxisTriggerStatus (Structure):
	_fields_ = [
		#/ </summary>
		('active',c_uint32),

		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('value',c_double),

		#/ </summary>
		('res1', c_uint * 8),

		#/ </summary>
		('res2', c_uint * 8),
	]

# <summary>
# 单信号触发参数
# </summary>
class YKS_TriggerArgOneSignal (Structure):
	_fields_ = [
		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('inout',YKS_DigitalIO),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 双信号触发参数
# </summary>
class YKS_TriggerArgTwoSignal (Structure):
	_fields_ = [
		#/ </summary>
		('type1',c_uint32),

		#/ </summary>
		('type2',c_uint32),

		#/ </summary>
		('inout1',YKS_DigitalIO),

		#/ </summary>
		('inout2',YKS_DigitalIO),

		#/ </summary>
		('index1',c_uint),

		#/ </summary>
		('index2',c_uint),

		#/ </summary>
		('op_logic',c_uint32),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 轴位置条件触发
# </summary>
class YKS_TriggerArgAxisPosition (Structure):
	_fields_ = [
		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('disable_positive_direction',c_uint32),

		#/ </summary>
		('disable_negative_direction',c_uint32),

		#/ </summary>
		('use_feedback',c_uint32),

		#/ </summary>
		('inv',c_uint32),

		#/ </summary>
		('position',c_double),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 轴时间条件触发
# </summary>
class YKS_TriggerArgAxisTime (Structure):
	_fields_ = [
		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('use_remain',c_uint32),

		#/ </summary>
		('inv',c_uint32),

		#/ </summary>
		('time',c_double),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 轴速度条件触发
# </summary>
class YKS_TriggerArgAxisVelocity (Structure):
	_fields_ = [
		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('use_feedback',c_uint32),

		#/ </summary>
		('inv',c_uint32),

		#/ </summary>
		('velocity',c_double),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 轴转矩条件触发
# </summary>
class YKS_TriggerArgAxisTorque (Structure):
	_fields_ = [
		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('use_feedback',c_uint32),

		#/ </summary>
		('inv',c_uint32),

		#/ </summary>
		('torque',c_double),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 从站PDO触发条件
# </summary>
class YKS_TriggerArgSlavePDO (Structure):
	_fields_ = [
		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('slave_index',c_uint),

		#/ </summary>
		('main_index',c_uint),

		#/ </summary>
		('sub_index',c_uint),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('data_type',c_uint32),

		#/ </summary>
		('inv',c_uint32),

		#/ </summary>
		('value',c_int),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 编码器触发条件
# </summary>
class YKS_TriggerArgEncoder (Structure):
	_fields_ = [
		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('trig_mode',c_uint32),

		#/ </summary>
		('inv',c_uint32),

		#/ </summary>
		('value',c_int),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 触发输出:位参数写入
# </summary>
class YKS_TriggerOutputOneBit (Structure):
	_fields_ = [
		#/ </summary>
		('type',c_uint32),

		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('inout',YKS_DigitalIO),

		#/ </summary>
		('single_shot',c_uint32),

		#/ </summary>
		('set_off_state',c_uint32),

		#/ </summary>
		('enable_reverse',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('delay_ms',c_double),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 触发输出:轴停止
# </summary>
class YKS_TriggerOutputStopAxis (Structure):
	_fields_ = [
		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('single_shot',c_uint32),

		#/ </summary>
		('stop_dec',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res1', c_uint * 8),
	]

# <summary>
# 触发输出:启动坐标系
# </summary>
class YKS_TriggerOutputStartGroup (Structure):
	_fields_ = [
		#/ </summary>
		('group_index',c_uint),

		#/ </summary>
		('single_shot',c_uint32),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 触发输出:启动多轴联动
# </summary>
class YKS_TriggerOutputStartMultiAxis (Structure):
	_fields_ = [
		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('single_shot',c_uint32),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 触发输出:启动轴
# </summary>
class YKS_TriggerOutputStartAxis (Structure):
	_fields_ = [
		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('single_shot',c_uint32),

		#/ </summary>
		('position',c_double),

		#/ </summary>
		('motion',YKS_AxisProfileMotion),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 触发输出:触发软急停信号
# </summary>
class YKS_TriggerOutputSoftEmgStop (Structure):
	_fields_ = [
		#/ </summary>
		('channel',c_uint),

		#/ </summary>
		('single_shot',c_uint32),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 触发输出:从站PDO写入
# </summary>
class YKS_TriggerOutputSlavePDO (Structure):
	_fields_ = [
		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('slave_index',c_uint),

		#/ </summary>
		('main_index',c_uint),

		#/ </summary>
		('sub_index',c_uint),

		#/ </summary>
		('single_shot',c_uint32),

		#/ </summary>
		('set_off_state',c_uint32),

		#/ </summary>
		('data_type',c_uint32),

		#/ </summary>
		('value',c_uint),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 触发输出:写入轴目标转矩
# </summary>
class YKS_TriggerOutputTargetTorque (Structure):
	_fields_ = [
		#/ </summary>
		('axis_index',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('value',c_double),

		#/ </summary>
		('single_shot',c_uint32),

		#/ </summary>
		('set_off_state',c_uint32),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 触发输出:延时
# </summary>
class YKS_TriggerOutputDelayMs (Structure):
	_fields_ = [
		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('value',c_double),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 触发输出:写数据寄存器
# </summary>
class YKS_TriggerOutputDataReg (Structure):
	_fields_ = [
		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('single_shot',c_uint32),

		#/ </summary>
		('set_off_state',c_uint32),

		#/ </summary>
		('index',c_uint),

		#/ </summary>
		('value',c_uint),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# 事件状态
# </summary>
class YKS_EventStatus (Structure):
	_fields_ = [
		#/ </summary>
		('master',c_uint32),

		#/ </summary>
		('status',c_uint32),

		#/ </summary>
		('error',c_uint32),

		#/ </summary>
		('triged',c_uint),

		#/ </summary>
		('res', c_uint * 8),
	]

# <summary>
# PT数据
# </summary>
class YKS_PTData (Structure):
	_fields_ = [
		#/ </summary>
		('position',c_double),

		#/ </summary>
		('tim',c_double),

		#/ </summary>
		('acc_add_percent',c_double),
	]

# <summary>
# PVT数据
# </summary>
class YKS_PVTData (Structure):
	_fields_ = [
		#/ </summary>
		('position',c_double),

		#/ </summary>
		('tim',c_double),

		#/ </summary>
		('velocity',c_double),
	]

# <summary>
# PVTS数据
# </summary>
class YKS_PVTSData (Structure):
	_fields_ = [
		#/ </summary>
		('position',c_double),

		#/ </summary>
		('tim',c_double),

		#/ </summary>
		('res',c_double),
	]

# <summary>
# PVT运动状态
# </summary>
class YKS_PVTStatus (Structure):
	_fields_ = [
		#/ </summary>
		('idel',c_uint),

		#/ </summary>
		('res1', c_uint * 7),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# 看门狗状态
# </summary>
class YKS_WDTStatus (Structure):
	_fields_ = [
		#/ </summary>
		('enable',c_uint32),

		#/ </summary>
		('trigged',c_uint32),

		#/ </summary>
		('timeout',c_double),

		#/ </summary>
		('remain_tim',c_double),

		#/ </summary>
		('res2', c_double * 8),
	]

# <summary>
# CNC轴参数写入
# </summary>
class YKS_CncGCode (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('gcode', c_char * 160),
	]

# <summary>
# 基于控制点的AKIMA样条配置
# </summary>
class YKS_CncASplineConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('start_trans_type',c_uint32),

		#/ </summary>
		('end_trans_type',c_uint32),

		#/ </summary>
		('start_Vector', c_double * 3),

		#/ </summary>
		('end_Vector', c_double * 3),

		#/ </summary>
		('res1', c_double * 4),
	]

# <summary>
# CNC轮廓角偏差平滑配置
# </summary>
class YKS_CncContourDevConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('action_time',c_uint32),

		#/ </summary>
		('check_jerk',c_uint32),

		#/ </summary>
		('vel_const',c_uint32),

		#/ </summary>
		('path_dev_max',c_double),

		#/ </summary>
		('track_dev_max',c_double),

		#/ </summary>
		('relevant_path_min',c_double),

		#/ </summary>
		('relevant_track_min',c_double),

		#/ </summary>
		('remain_part',c_double),

		#/ </summary>
		('angle_max',c_double),
	]

# <summary>
# CNC轮廓角距离平滑配置
# </summary>
class YKS_CncContourDistConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('action_time',c_uint32),

		#/ </summary>
		('check_jerk',c_uint32),

		#/ </summary>
		('vel_const',c_uint32),

		#/ </summary>
		('track_dev_max',c_double),

		#/ </summary>
		('pre_dist',c_double),

		#/ </summary>
		('post_dist',c_double),

		#/ </summary>
		('relevant_path_min',c_double),

		#/ </summary>
		('relevant_track_min',c_double),

		#/ </summary>
		('remain_part',c_double),

		#/ </summary>
		('angle_max',c_double),
	]

# <summary>
# CNC动态轮廓优化平滑配置
# </summary>
class YKS_CncContourDistSoftConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('path_dist',c_double),

		#/ </summary>
		('track_dist',c_double),

		#/ </summary>
		('acc_max',c_double),

		#/ </summary>
		('acc_min',c_double),

		#/ </summary>
		('ramp_time',c_double),

		#/ </summary>
		('dist_weight',c_double),
	]

# <summary>
# CNC进给主轴动态轮廓优化平滑配置
# </summary>
class YKS_CncContourDistMasterConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('path_dist',c_double),

		#/ </summary>
		('acc_max',c_double),

		#/ </summary>
		('acc_min',c_double),

		#/ </summary>
		('ramp_time',c_double),

		#/ </summary>
		('dist_weight',c_double),
	]

# <summary>
# CNC插入点平滑配置
# </summary>
class YKS_CncContourPosConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('action_time',c_uint32),

		#/ </summary>
		('check_jerk',c_uint32),

		#/ </summary>
		('vel_const',c_uint32),

		#/ </summary>
		('pre_dist',c_double),

		#/ </summary>
		('post_dist',c_double),

		#/ </summary>
		('pos_position', c_double * 3),
	]

# <summary>
# CNC完整轮廓动态优化平滑配置
# </summary>
class YKS_CncContourPtpConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('merge',c_uint32),

		#/ </summary>
		('action_time',c_uint32),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('path_dev_max',c_double),

		#/ </summary>
		('path_dist',c_double),
	]

# <summary>
# HSC_B样条平滑配置
# </summary>
class YKS_CncHscBConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('merge',c_uint32),

		#/ </summary>
		('auto_off_path',c_uint32),

		#/ </summary>
		('auto_off_track',c_uint32),

		#/ </summary>
		('auto_off_rapid',c_uint32),

		#/ </summary>
		('auto_off_exactStop',c_uint32),

		#/ </summary>
		('path_dev_max',c_double),

		#/ </summary>
		('track_dev_max',c_double),

		#/ </summary>
		('path_len_max',c_double),

		#/ </summary>
		('angle_max',c_double),

		#/ </summary>
		('res1', c_double * 4),
	]

# <summary>
# HSC_Surface平滑配置
# </summary>
class YKS_CncHscSConfig (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('cir_mode',c_uint32),

		#/ </summary>
		('check_jerk',c_uint32),

		#/ </summary>
		('auto_off_rapid',c_uint32),

		#/ </summary>
		('merge',c_uint32),

		#/ </summary>
		('res0',c_uint),

		#/ </summary>
		('cir_min_angle',c_double),

		#/ </summary>
		('track_dev_rapid',c_double),

		#/ </summary>
		('path_dev_max',c_double),

		#/ </summary>
		('path_dev_rapid',c_double),

		#/ </summary>
		('angle_max',c_double),

		#/ </summary>
		('cir_min_radius',c_double),

		#/ </summary>
		('cir_long_length',c_double),

		#/ </summary>
		('track_dev_max',c_double),

		#/ </summary>
		('res', c_double * 8),
	]

# <summary>
# HSC_PCS1平滑参数
# </summary>
class YKS_CncHscPcs1Config (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('contour_error_Max',c_double),
	]

# <summary>
# HSC_PCS2平滑参数
# </summary>
class YKS_CncHscPcs2Config (Structure):
	_fields_ = [
		#/ </summary>
		('mark',c_uint),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('contour_error_Max',c_double),
	]

# <summary>
# HSC_PCS2平滑参数
# </summary>
class YKS_CncParaStatus (Structure):
	_fields_ = [
		#/ </summary>
		('done',c_uint32),

		#/ </summary>
		('status',c_uint),

		#/ </summary>
		('value', c_char * 128),

		#/ </summary>
		('res',c_uint),

		#/ </summary>
		('res1', c_uint * 8),
	]

# <summary>
# 连接NT控制器
# </summary>
# <param name="ip_addr">ip地址</param>
# <param name="ip_port">端口号，默认50001</param>
# <param name="handle">返回的句柄</param>
# <returns></returns>
def YKM_SysConnect(dllPtr, ip_addr, ip_port, handle):

	return dllPtr.YKM_SysConnect(ip_addr, ip_port, byref(handle));

# <summary>
# 断开NT控制器
# </summary>
# <param name="handle">通讯句柄</param>
# <returns></returns>
def YKM_SysClose(dllPtr, handle):

	return dllPtr.YKM_SysClose(handle);

# <summary>
# 获取库文件(YKCAT2.dll)版本
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="version">当前版本号</param>
# <returns></returns>
def YKM_GetSysVersion(dllPtr, handle, version):

	return dllPtr.YKM_GetSysVersion(handle, byref(version));

# <summary>
# 获取Runtime版本
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="version">当前版本号</param>
# <returns></returns>
def YKM_GetRuntimeVersion(dllPtr, handle, version):

	return dllPtr.YKM_GetRuntimeVersion(handle, byref(version));

# <summary>
# 打开和Runtime(ProR)之间的通讯通道
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_SysLoadLib(dllPtr, handle):

	return dllPtr.YKM_SysLoadLib(handle)

# <summary>
# 释放系统资源，程序退出时调用
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_SysUnloadLib(dllPtr, handle):

	return dllPtr.YKM_SysUnloadLib(handle);

# <summary>
# 设置应用程序看门狗超时时间
# 可用于上位机异常关闭时自动停止轴运动及输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="enable">FALSE:不启用 TRUE:启用</param>
# <param name="tim">超时时间(ms)</param>
# <returns></returns>
def YKM_SetAppWDT(dllPtr, handle, enable, tim):

	return dllPtr.YKM_SetAppWDT(handle, enable, tim);

# <summary>
# 重置应用程序看门狗
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_ClearAppWDT(dllPtr, handle):

	return dllPtr.YKM_ClearAppWDT(handle);

# <summary>
# 获取应用程序看门狗状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadAppWDT(dllPtr, handle, status):

	return dllPtr.YKM_ReadAppWDT(handle, byref(status));

# <summary>
# 开始日志记录
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="process_id">进程ID</param>
# <returns></returns>
def YKM_StartLogger(dllPtr, handle, process_id):

	return dllPtr.YKM_StartLogger(handle, process_id);

# <summary>
# 停止日志记录
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_StopLogger(dllPtr, handle):

	return dllPtr.YKM_StopLogger(handle);

# <summary>
# 获取开启日志的进程ID
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="process_id">进程ID</param>
# <returns></returns>
def YKM_GetLoggerProcessID(dllPtr, handle, process_id):

	return dllPtr.YKM_GetLoggerProcessID(handle, byref(process_id));

# <summary>
# 写日志配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetLoggerConfig(dllPtr, handle, config):

	return dllPtr.YKM_SetLoggerConfig(handle, config);

# <summary>
# 读日志配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetLoggerConfig(dllPtr, handle, config):

	return dllPtr.YKM_GetLoggerConfig(handle, byref(config));

# <summary>
# 保留
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="config">配饰</param>
# <returns></returns>
def YKM_InitExcData(dllPtr, handle, config):

	return dllPtr.YKM_InitExcData(handle, config);

# <summary>
# 保留
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="item_data">保留</param>
# <param name="ret_size">保留</param>
# <returns></returns>
def YKM_GetExcData(dllPtr, handle, item_data, ret_size):

	return dllPtr.YKM_GetExcData(handle, byref(item_data), byref(ret_size));

# <summary>
# 获取进程名称
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="process_id">进程ID</param>
# <param name="name">进程名称</param>
# <param name="size">缓冲区大小</param>
# <returns></returns>
def YKM_GetProcessName(dllPtr, handle, process_id, name, size):

	return dllPtr.YKM_GetProcessName(handle, process_id, byref(name), size);

# <summary>
# 获取调用运动库的进程列表
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="process_num">进程数量</param>
# <param name="process_id">进程ID,至少16个元素空间</param>
# <returns></returns>
def YKM_GetProcessNumber(dllPtr, handle, process_num, process_id):

	return dllPtr.YKM_GetProcessNumber(handle, byref(process_num), byref(process_id));

# <summary>
# 获取当前进程ID
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="process_id">进程ID</param>
# <returns></returns>
def YKM_GetProcessID(dllPtr, handle, process_id):

	return dllPtr.YKM_GetProcessID(handle, byref(process_id));

# <summary>
# 获取本进程函数调用记录，每次最多返回1行
# </summary>
# <param name="handle">固定为0</param>
# <param name="buff">缓冲区地址</param>
# <param name="size">缓冲区大小</param>
# <param name="count">返回的字符数量</param>
# <returns></returns>
def YKM_ReadFunLog(dllPtr, handle, buff, size, count):

	return dllPtr.YKM_ReadFunLog(handle, byref(buff), size, byref(count));

# <summary>
# 获取系统配置信息
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="config"></param>
# <returns></returns>
def YKM_GetSysProfile(dllPtr, handle, config):

	return dllPtr.YKM_GetSysProfile(handle, byref(config));

# <summary>
# 获取当前报警信息
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="buff">缓冲区，不小于2048字节</param>
# <param name="size">缓冲区尺寸</param>
# <param name="num">报警数量</param>
# <returns></returns>
def YKM_ReadSysWarn(dllPtr, handle, buff, size, num):

	return dllPtr.YKM_ReadSysWarn(handle, byref(buff), size, byref(num));

# <summary>
# 获取系统日志
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="buff">缓冲区，不小于2048字节</param>
# <param name="size">缓冲区尺寸</param>
# <param name="ret_size">实际返回数据大小</param>
# <returns></returns>
def YKM_ReadSysLog(dllPtr, handle, buff, size, ret_size):

	return dllPtr.YKM_ReadSysLog(handle, byref(buff), size, byref(ret_size));

# <summary>
# 清除缓存中的日志
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_ClearSysLog(dllPtr, handle):

	return dllPtr.YKM_ClearSysLog(handle);

# <summary>
# 向管理任务发送命令
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="run_stop">YKE_FALSE=停止(轴会停止，输出会关闭) YKE_TRUE=运行</param>
# <returns></returns>
def YKM_SendMgmtCmd(dllPtr, handle, master, run_stop):

	return dllPtr.YKM_SendMgmtCmd(handle, master, run_stop);

# <summary>
# 获取runtime运行状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="status">0=停止 1=运行 2=过渡状态</param>
# <returns></returns>
def YKM_ReadMgmtStatus(dllPtr, handle, master, status):

	return dllPtr.YKM_ReadMgmtStatus(handle, master, byref(status));

# <summary>
# 冷复位，此动作会重启实时系统和Runtime
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="delay">服务停止后延时指定时间后再开启服务(ms)</param>
# <returns></returns>
def YKM_SysColdReset(dllPtr, handle, delay):

	return dllPtr.YKM_SysColdReset(handle, delay);

# <summary>
# 热复位。复位runtime，轴运动停止，关输出。复位A节点时,默认复位其他节点
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <returns></returns>
def YKM_SysWarmReset(dllPtr, handle, master):

	return dllPtr.YKM_SysWarmReset(handle, master);

# <summary>
# 启动Runtime服务
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_SysStartService(dllPtr, handle):

	return dllPtr.YKM_SysStartService(handle);

# <summary>
# 停止Runtime服务
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_SysStopService(dllPtr, handle):

	return dllPtr.YKM_SysStopService(handle);

# <summary>
# 检测Runtime服务是否处于运行状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="status">TRUE:已运行 FALSE:未运行</param>
# <returns></returns>
def YKM_SysCheckService(dllPtr, handle, status):

	return dllPtr.YKM_SysCheckService(handle, byref(status));

# <summary>
# 注册runtime服务
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="path">runtime根目录</param>
# <returns></returns>
def YKM_SysRegisterService(dllPtr, handle, path):

	return dllPtr.YKM_SysRegisterService(handle, path);

# <summary>
# 注销runtime服务
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_SysUnRegisterService(dllPtr, handle):

	return dllPtr.YKM_SysUnRegisterService(handle);

# <summary>
# 获取服务注册状态和服务文件路径
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="registered">TRUE:已注册 FALSE:未注册</param>
# <param name="path">路径缓冲区</param>
# <param name="size">路径缓冲区大小</param>
# <returns></returns>
def YKM_SysGetService(dllPtr, handle, registered, path, size):

	return dllPtr.YKM_SysGetService(handle, byref(registered), byref(path), size);

# <summary>
# 设置硬急停配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号 [0,YKE_EMG_STOP_NUM)</param>
# <param name="config">配置参数</param>
# <returns></returns>
def YKM_SetHardEmgProfile(dllPtr, handle, channel, config):

	return dllPtr.YKM_SetHardEmgProfile(handle, channel, config);

# <summary>
# 获取硬急停配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号 [0,YKE_EMG_STOP_NUM)</param>
# <param name="config"></param>
# <returns></returns>
def YKM_GetHardEmgProfile(dllPtr, handle, channel, config):

	return dllPtr.YKM_GetHardEmgProfile(handle, channel, byref(config));

# <summary>
# 设置软急停信号有效
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号 [0,YKE_EMG_STOP_NUM)</param>
# <returns></returns>
def YKM_SetEmgStopSoft(dllPtr, handle, channel):

	return dllPtr.YKM_SetEmgStopSoft(handle, channel);

# <summary>
# 清除软急停信号有效
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号 [0,YKE_EMG_STOP_NUM)</param>
# <returns></returns>
def YKM_ClearEmgStopSoft(dllPtr, handle, channel):

	return dllPtr.YKM_ClearEmgStopSoft(handle, channel);

# <summary>
# 获取急停状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号 [0,YKE_EMG_STOP_NUM)</param>
# <param name="status">返回状态</param>
# <returns></returns>
def YKM_ReadEmgStatus(dllPtr, handle, channel, status):

	return dllPtr.YKM_ReadEmgStatus(handle, channel, byref(status));

# <summary>
# 设置Windows蓝屏后的行为
# 未实现
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetBlueScreenConfig(dllPtr, handle, config):

	return dllPtr.YKM_SetBlueScreenConfig(handle, config);

# <summary>
# 获取ProEN工程ID
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="prj_id">工程ID缓冲区</param>
# <param name="size">缓冲区大小</param>
# <returns></returns>
def YKM_GetProjectID(dllPtr, handle, prj_id, size):

	return dllPtr.YKM_GetProjectID(handle, byref(prj_id), size);

# <summary>
# 加载由ProEn导出的工程配置数据(bprj扩展名)
# 注意下载前会主动停止正在运动中的轴
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="filename">路径及文件名称</param>
# <param name="mask">数据掩码按位定义(YKE_PROJECT_MASK),置位时下载对应的数据</param>
# <returns></returns>
def YKM_LoadProjectData(dllPtr, handle, filename, mask):

	return dllPtr.YKM_LoadProjectData(handle, filename, mask);

# <summary>
# 获取给PLC模块的控制命令
# 内部使用
# </summary>
# <param name="command">命令</param>
# <returns></returns>
def YKM_GetPLCCommand(dllPtr, command):

	return dllPtr.YKM_GetPLCCommand(byref(command));

# <summary>
# 向PLC发送控制命令
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="command">控制命令</param>
# <returns></returns>
def YKM_SendPLCCommand(dllPtr, handle, command):

	return dllPtr.YKM_SendPLCCommand(handle, command);

# <summary>
# 清除系统报警
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <returns></returns>
def YKM_ClearSysWarn(dllPtr, handle, master):

	return dllPtr.YKM_ClearSysWarn(handle, master);

# <summary>
# 设置总线事件间隔时间
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="tim">时间[0,](ms)</param>
# <returns></returns>
def YKM_SetBusEventTime(dllPtr, handle, master, tim):

	return dllPtr.YKM_SetBusEventTime(handle, master, tim);

# <summary>
# 获取总线事件间隔时间
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="tim">时间[0,](ms)</param>
# <returns></returns>
def YKM_GetBusEventTime(dllPtr, handle, master, tim):

	return dllPtr.YKM_GetBusEventTime(handle, master, byref(tim));

# <summary>
# 等待总线任务事件，指定时间触发一次
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <returns></returns>
def YKM_WaitBusEvent(dllPtr, handle, master):

	return dllPtr.YKM_WaitBusEvent(handle, master);

# <summary>
# 读总线通讯数据帧
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="header">帧头信息</param>
# <param name="buff">缓冲区地址</param>
# <param name="size">缓冲区大小,大于1500</param>
# <returns></returns>
def YKM_ReadBusPacket(dllPtr, handle, header, buff, size):

	return dllPtr.YKM_ReadBusPacket(handle, header, buff, size);

# <summary>
# 写数据寄存器,UIN32模式
# 1024*1024个UINT32空间
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="offset">地址偏移</param>
# <param name="data">数据指针</param>
# <param name="size">数据数量 UINT32单位</param>
# <returns></returns>
def YKM_WriteDataRegU32(dllPtr, handle, offset, data, size):

	return dllPtr.YKM_WriteDataRegU32(handle, offset, data, size);

# <summary>
# 读数据寄存器,UIN32模式
# 1024*1024个UINT32空间
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="offset">地址偏移</param>
# <param name="data">数据指针</param>
# <param name="size">数据数量 UINT32单位</param>
# <returns></returns>
def YKM_ReadDataRegU32(dllPtr, handle, offset, data, size):

	return dllPtr.YKM_ReadDataRegU32(handle, offset, byref(data), size);

# <summary>
# 写数据寄存器,double模式
# 512*1024个double空间
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="offset">地址偏移</param>
# <param name="data">数据指针</param>
# <param name="size">数据数量 double单位</param>
# <returns></returns>
def YKM_WriteDataRegDouble(dllPtr, handle, offset, data, size):

	return dllPtr.YKM_WriteDataRegDouble(handle, offset, data, size);

# <summary>
# 读数据寄存器,double模式
# 512*1024个double空间
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="offset">地址偏移</param>
# <param name="data">数据指针</param>
# <param name="size">数据数量 double单位</param>
# <returns></returns>
def YKM_ReadDataRegDouble(dllPtr, handle, offset, data, size):

	return dllPtr.YKM_ReadDataRegDouble(handle, offset, byref(data), size);

# <summary>
# 获取数据寄存器在内存中的首地址
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="hi_addr">内存地址(高32位)</param>
# <param name="lo_addr">内存地址(低32位)</param>
# <returns></returns>
def YKM_ReadDataRegAddress(dllPtr, handle, hi_addr, lo_addr):

	return dllPtr.YKM_ReadDataRegAddress(handle, byref(hi_addr), byref(lo_addr));

# <summary>
# 保留
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="name">工程名称</param>
# <returns></returns>
def YKM_ProEnAddPrj(dllPtr, handle, name):

	return dllPtr.YKM_ProEnAddPrj(handle, name);

# <summary>
# 保留
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="name">工程名称</param>
# <returns></returns>
def YKM_ProEnDelPrj(dllPtr, handle, name):

	return dllPtr.YKM_ProEnDelPrj(handle, name);

# <summary>
# 保留
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="name">工程名称</param>
# <returns></returns>
def YKM_ProEnCheckPrj(dllPtr, handle, name):

	return dllPtr.YKM_ProEnCheckPrj(handle, name);

# <summary>
# ProEn写配置数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="type">数量类型</param>
# <param name="data">数据</param>
# <param name="size">数据大小</param>
# <returns></returns>
def YKM_ProEnWriteData(dllPtr, handle, type, data, size):

	return dllPtr.YKM_ProEnWriteData(handle, type, data, size);

# <summary>
# 读硬件锁用户区数据
# 阻塞模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="type">硬件锁类型</param>
# <param name="offset">地址偏移</param>
# <param name="data">缓冲区</param>
# <param name="size">期望读出的数据大小(byte)，最大4096字节</param>
# <param name="result">实际读出的数据大小(byte)</param>
# <returns></returns>
def YKM_ReadDoggleData(dllPtr, handle, type, offset, data, size, result):

	return dllPtr.YKM_ReadDoggleData(handle, type, offset, byref(data), size, byref(result));

# <summary>
# 写硬件锁用户区数据
# 阻塞模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="type">硬件锁类型</param>
# <param name="offset">地址偏移</param>
# <param name="data">缓冲区</param>
# <param name="size">期望写入的数据大小(byte)，最大4096字节</param>
# <param name="result">实际写入的数据大小(byte)</param>
# <returns></returns>
def YKM_WriteDoggleData(dllPtr, handle, type, offset, data, size, result):

	return dllPtr.YKM_WriteDoggleData(handle, type, offset, data, size, byref(result));

# <summary>
# 断开总线连接，断开后再次调用复位命令可恢复总线运行
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <returns></returns>
def YKM_DisconnectBus(dllPtr, handle, master):

	return dllPtr.YKM_DisconnectBus(handle, master);

# <summary>
# 热复位并扫描从站
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="info">扫描内容</param>
# <returns></returns>
def YKM_ScanBus(dllPtr, handle, master, info):

	return dllPtr.YKM_ScanBus(handle, master, info);

# <summary>
# 获得总线信息
# </summary>
# <param name="master">主站选择</param>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="info"></param>
# <returns></returns>
def YKM_ReadBusStatus(dllPtr, handle, master, info):

	return dllPtr.YKM_ReadBusStatus(handle, master, byref(info));

# <summary>
# 清除总线负载率/同步偏移/帧丢失数量
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <returns></returns>
def YKM_ClearBusValue(dllPtr, handle, master):

	return dllPtr.YKM_ClearBusValue(handle, master);

# <summary>
# 清除总线报警
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <returns></returns>
def YKM_ClearBusWarn(dllPtr, handle, master):

	return dllPtr.YKM_ClearBusWarn(handle, master);

# <summary>
# 配置总线节点信息
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="slaveIndex">站点序号，从0开始</param>
# <param name="item">配置内容，热复位后生效</param>
# <param name="value">配置值</param>
# <returns></returns>
def YKM_SetBusConfig(dllPtr, handle, master, slaveIndex, item, value):

	return dllPtr.YKM_SetBusConfig(handle, master, slaveIndex, item, value);

# <summary>
# 获取总线节点信息
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="slaveIndex">站点序号，从0开始</param>
# <param name="item">配置内容</param>
# <param name="value">返回的配置值</param>
# <returns></returns>
def YKM_GetBusConfig(dllPtr, handle, master, slaveIndex, item, value):

	return dllPtr.YKM_GetBusConfig(handle, master, slaveIndex, item, byref(value));

# <summary>
# 获得从站名称，名称在ProEn中设置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="slaveIndex">站点序号，从0开始</param>
# <param name="name">返回名称，至少分配64字节</param>
# <param name="size">name缓冲区尺寸</param>
# <returns></returns>
def YKM_GetSlaveAlias(dllPtr, handle, master, slaveIndex, name, size):

	return dllPtr.YKM_GetSlaveAlias(handle, master, slaveIndex, byref(name), size);

# <summary>
# 获得总线各站点状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="slaveIndex">站点序号，从0开始</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadSlaveStatus(dllPtr, handle, master, slaveIndex, status):

	return dllPtr.YKM_ReadSlaveStatus(handle, master, slaveIndex, byref(status));

# <summary>
# 读从站输出PDO数量
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标</param>
# <param name="master">主站</param>
# <param name="slaveIndex">从站序号</param>
# <param name="number">返回数量</param>
# <returns></returns>
def YKM_GetSlaveTxPdoNumber(dllPtr, handle, master, slaveIndex, number):

	return dllPtr.YKM_GetSlaveTxPdoNumber(handle, master, slaveIndex, byref(number));

# <summary>
# 读从站输出PDO配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标</param>
# <param name="master">主站</param>
# <param name="slaveIndex">从站序号</param>
# <param name="pdoIndex">PDO序号，从0开始</param>
# <param name="config">返回数量</param>
# <returns></returns>
def YKM_GetSlaveTxPdoConfig(dllPtr, handle, master, slaveIndex, pdoIndex, config):

	return dllPtr.YKM_GetSlaveTxPdoConfig(handle, master, slaveIndex, pdoIndex, byref(config));

# <summary>
# 读从站输入PDO数量
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标</param>
# <param name="master">主站</param>
# <param name="slaveIndex">从站序号</param>
# <param name="number">返回数量</param>
# <returns></returns>
def YKM_GetSlaveRxPdoNumber(dllPtr, handle, master, slaveIndex, number):

	return dllPtr.YKM_GetSlaveRxPdoNumber(handle, master, slaveIndex, byref(number));

# <summary>
# 读从站输入PDO配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标</param>
# <param name="master">主站</param>
# <param name="slaveIndex">从站序号</param>
# <param name="pdoIndex">PDO序号，从0开始</param>
# <param name="config">返回配置</param>
# <returns></returns>
def YKM_GetSlaveRxPdoConfig(dllPtr, handle, master, slaveIndex, pdoIndex, config):

	return dllPtr.YKM_GetSlaveRxPdoConfig(handle, master, slaveIndex, pdoIndex, byref(config));

# <summary>
# 设置系统保留PDO保护标志
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="uIndex">站点序号</param>
# <param name="check">TRUE=开启写入保护 FALSE=关闭写入保护</param>
# <returns></returns>
def YKM_SetPDOProtect(dllPtr, handle, master, uIndex, check):

	return dllPtr.YKM_SetPDOProtect(handle, master, uIndex, check);

# <summary>
# 获取系统保留PDO保护标志
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="uIndex">站点序号</param>
# <param name="check">TRUE=开启写入保护 FALSE=关闭写入保护</param>
# <returns></returns>
def YKM_GetPDOProtect(dllPtr, handle, master, uIndex, check):

	return dllPtr.YKM_GetPDOProtect(handle, master, uIndex, check);

# <summary>
# 基于UG索引写PDO数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="slaveIndex">站点序号</param>
# <param name="gIndex">G索引号，在从站配置的过程数据页面查看</param>
# <param name="ptr">写入数据</param>
# <param name="size">数据长度，16bit单位</param>
# <returns></returns>
def YKM_WritePDOIndex(dllPtr, handle, master, slaveIndex, gIndex, ptr, size):

	return dllPtr.YKM_WritePDOIndex(handle, master, slaveIndex, gIndex, ptr, size);

# <summary>
# 基于UG索引读PDO数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="slaveIndex">站点序号</param>
# <param name="gIndex">G索引号，在从站配置的过程数据页面查看</param>
# <param name="ptr">返回数据</param>
# <param name="size">数据长度，16bit单位</param>
# <returns></returns>
def YKM_ReadPDOIndex(dllPtr, handle, master, slaveIndex, gIndex, ptr, size):

	return dllPtr.YKM_ReadPDOIndex(handle, master, slaveIndex, gIndex, byref(ptr), size);

# <summary>
# 基于对象字典索引读PDO数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站</param>
# <param name="slaveIndex">站点序号</param>
# <param name="mainIndex">对象字典主索引</param>
# <param name="subIndex">对象字典子索引</param>
# <param name="ptr">返回数据</param>
# <param name="size">数据长度，16bit单位</param>
# <returns></returns>
def YKM_ReadPDOObject(dllPtr, handle, master, slaveIndex, mainIndex, subIndex, ptr, size):

	return dllPtr.YKM_ReadPDOObject(handle, master, slaveIndex, mainIndex, subIndex, byref(ptr), size);

# <summary>
# 基于对象字典索引写PDO数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站</param>
# <param name="slaveIndex">站点序号</param>
# <param name="mainIndex">对象字典主索引</param>
# <param name="subIndex">对象字典子索引</param>
# <param name="ptr">写入数据</param>
# <param name="size">数据长度，16bit单位</param>
# <returns></returns>
def YKM_WritePDOObject(dllPtr, handle, master, slaveIndex, mainIndex, subIndex, ptr, size):

	return dllPtr.YKM_WritePDOObject(handle, master, slaveIndex, mainIndex, subIndex, ptr, size);

# <summary>
# 启动SDO写命令
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="slaveIndex">站点序号</param>
# <param name="mainIndex">对象主索引</param>
# <param name="subIndex">对象子索引</param>
# <param name="byteNum">数量(字节单位)</param>
# <param name="val">写入值</param>
# <param name="sdoIndex">返回的SDO队列索引</param>
# <returns></returns>
def YKM_WriteSDOCmd(dllPtr, handle, master, slaveIndex, mainIndex, subIndex, byteNum, val, sdoIndex):

	return dllPtr.YKM_WriteSDOCmd(handle, master, slaveIndex, mainIndex, subIndex, byteNum, val, byref(sdoIndex));

# <summary>
# 启动SDO读命令
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="uIndex">站点序号</param>
# <param name="mainIndex">对象主索引</param>
# <param name="subIndex">对象子索引</param>
# <param name="byteNum">数量(字节单位)</param>
# <param name="sdoIndex">返回的SDO队列索引</param>
# <returns></returns>
def YKM_ReadSDOCmd(dllPtr, handle, master, uIndex, mainIndex, subIndex, byteNum, sdoIndex):

	return dllPtr.YKM_ReadSDOCmd(handle, master, uIndex, mainIndex, subIndex, byteNum, byref(sdoIndex));

# <summary>
# 读SDO队列状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="sdoIndex">SDO队列索引</param>
# <param name="status">返回状态</param>
def YKM_ReadSDOStatus(dllPtr, handle, master, sdoIndex, status):

	return dllPtr.YKM_ReadSDOStatus(handle, master, sdoIndex, byref(status));

# <summary>
# 获得SDO队列空闲数量
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="num">返回的空闲数量</param>
# <returns></returns>
def YKM_GetSDOIdel(dllPtr, handle, master, num):

	return dllPtr.YKM_GetSDOIdel(handle, master, byref(num));

# <summary>
# 按位读数字输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="value">返回值: FALSE=OFF  TRUE=ON</param>
# <returns></returns>
def YKM_ReadDigitalOutputBit(dllPtr, handle, byteIndex, bitOffset, value):

	return dllPtr.YKM_ReadDigitalOutputBit(handle, byteIndex, bitOffset, byref(value));

# <summary>
# 按位批量读数字输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="value">返回值: FALSE=OFF  TRUE=ON</param>
# <param name="size">读取数量</param>
# <returns></returns>
def YKM_ReadDigitalOutputBits(dllPtr, handle, byteIndex, bitOffset, value, size):

	return dllPtr.YKM_ReadDigitalOutputBits(handle, byteIndex, bitOffset, byref(value), size);

# <summary>
# 按位写数字输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="value">写入值: FALSE=OFF  TRUE=ON</param>
# <returns></returns>
def YKM_WriteDigitalOutputBit(dllPtr, handle, byteIndex, bitOffset, value):

	return dllPtr.YKM_WriteDigitalOutputBit(handle, byteIndex, bitOffset, value);

# <summary>
# 按位批量写数字输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7</param>
# <param name="value">写入值: FALSE=OFF  TRUE=ON</param>
# <param name="size">写入数量</param>
# <returns></returns>
def YKM_WriteDigitalOutputBits(dllPtr, handle, byteIndex, bitOffset, value, size):

	return dllPtr.YKM_WriteDigitalOutputBits(handle, byteIndex, bitOffset, value, size);

# <summary>
# 按字节读数字输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)，每组8位</param>
# <param name="value">输出值</param>
# <returns></returns>
def YKM_ReadDigitalOutputByte(dllPtr, handle, byteIndex, value):

	return dllPtr.YKM_ReadDigitalOutputByte(handle, byteIndex, byref(value));

# <summary>
# 按字节写数字输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)，每组8位</param>
# <param name="value">输出值</param>
# <returns></returns>
def YKM_WriteDigitalOutputByte(dllPtr, handle, byteIndex, value):

	return dllPtr.YKM_WriteDigitalOutputByte(handle, byteIndex, value);

# <summary>
# 按字节写数字输出(带掩码)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)</param>
# <param name="mask">按位定义，对应位为0时无效，为1时输出按value值输出</param>
# <param name="value">按位定义，输出值</param>
# <returns></returns>
def YKM_WriteDigitalOutputMask(dllPtr, handle, byteIndex, mask, value):

	return dllPtr.YKM_WriteDigitalOutputMask(handle, byteIndex, mask, value);

# <summary>
# 按位设置数字输出在热复位时的保持行为
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="hold">写入值: 0=不保持  1=保持</param>
# <returns></returns>
def YKM_SetDigitalOutputHold(dllPtr, handle, byteIndex, bitOffset, hold):

	return dllPtr.YKM_SetDigitalOutputHold(handle, byteIndex, bitOffset, hold);

# <summary>
# 读取数字输出在热复位时的保持行为
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="hold">FALSE=不保持  TRUE=保持</param>
# <returns></returns>
def YKM_GetDigitalOutputHold(dllPtr, handle, byteIndex, bitOffset, hold):

	return dllPtr.YKM_GetDigitalOutputHold(handle, byteIndex, bitOffset, byref(hold));

# <summary>
# 写数字输入滤波时间(ms)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_INPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="filter">滤波时间[0,1000](ms)</param>
# <returns></returns>
def YKM_WriteDigitalInputFilter(dllPtr, handle, byteIndex, bitOffset, filter):

	return dllPtr.YKM_WriteDigitalInputFilter(handle, byteIndex, bitOffset, filter);

# <summary>
# 读数字输入滤波时间(ms)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_INPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="filter">滤波时间[0,1000](ms)</param>
# <returns></returns>
def YKM_ReadDigitalInputFilter(dllPtr, handle, byteIndex, bitOffset, filter):

	return dllPtr.YKM_ReadDigitalInputFilter(handle, byteIndex, bitOffset, byref(filter));

# <summary>
# 按位读数字输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_INPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="value">返回值: FALSE=OFF  TRUE=ON</param>
# <returns></returns>
def YKM_ReadDigitalInputBit(dllPtr, handle, byteIndex, bitOffset, value):

	return dllPtr.YKM_ReadDigitalInputBit(handle, byteIndex, bitOffset, byref(value));

# <summary>
# 按位批量读数字输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="value">返回值: FALSE=OFF  TRUE=ON</param>
# <param name="size">读取数量</param>
# <returns></returns>
def YKM_ReadDigitalInputBits(dllPtr, handle, byteIndex, bitOffset, value, size):

	return dllPtr.YKM_ReadDigitalInputBits(handle, byteIndex, bitOffset, byref(value), size);

# <summary>
# 按位写数字输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_INPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="value"> FALSE=OFF  TRUE=ON</param>
# <returns></returns>
def YKM_WriteDigitalInputBit(dllPtr, handle, byteIndex, bitOffset, value):

	return dllPtr.YKM_WriteDigitalInputBit(handle, byteIndex, bitOffset, value);

# <summary>
# 按字节读数字输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">组序号[0,YKE_DIGITAL_INPUT_NUM/8)，每组8位</param>
# <param name="value">输入值</param>
# <returns></returns>
def YKM_ReadDigitalInputByte(dllPtr, handle, byteIndex, value):

	return dllPtr.YKM_ReadDigitalInputByte(handle, byteIndex, byref(value));

# <summary>
# 按字节写数字输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">组序号[0,YKE_DIGITAL_INPUT_NUM/8)，每组8位</param>
# <param name="value">输入值</param>
# <returns></returns>
def YKM_WriteDigitalInputByte(dllPtr, handle, byteIndex, value):

	return dllPtr.YKM_WriteDigitalInputByte(handle, byteIndex, value);

# <summary>
# 读数字输入(软件滤波前)的上升沿计数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_INPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="value">返回值</param>
# <returns></returns>
def YKM_ReadInputEdgeCount1(dllPtr, handle, byteIndex, bitOffset, value):

	return dllPtr.YKM_ReadInputEdgeCount1(handle, byteIndex, bitOffset, byref(value));

# <summary>
# 写数字输入(软件滤波前)的上升沿计数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_INPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="value">写入值</param>
# <returns></returns>
def YKM_WriteInputEdgeCount1(dllPtr, handle, byteIndex, bitOffset, value):

	return dllPtr.YKM_WriteInputEdgeCount1(handle, byteIndex, bitOffset, value);

# <summary>
# 读数字输入(软件滤波后)的上升沿计数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_INPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="value">返回值</param>
# <returns></returns>
def YKM_ReadInputEdgeCount2(dllPtr, handle, byteIndex, bitOffset, value):

	return dllPtr.YKM_ReadInputEdgeCount2(handle, byteIndex, bitOffset, byref(value));

# <summary>
# 写数字输入(软件滤波后)的上升沿计数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_INPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="value">写入值</param>
# <returns></returns>
def YKM_WriteInputEdgeCount2(dllPtr, handle, byteIndex, bitOffset, value):

	return dllPtr.YKM_WriteInputEdgeCount2(handle, byteIndex, bitOffset, value);

# <summary>
# 读数字输入的硬件信息
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_INPUT_NUM/8)</param>
# <param name="phy">物理位置</param>
# <returns></returns>
def YKM_ReadInputLocation(dllPtr, handle, byteIndex, phy):

	return dllPtr.YKM_ReadInputLocation(handle, byteIndex, byref(phy));

# <summary>
# 读数字输出的硬件信息
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)</param>
# <param name="phy">物理位置</param>
# <returns></returns>
def YKM_ReadOutputLocation(dllPtr, handle, byteIndex, phy):

	return dllPtr.YKM_ReadOutputLocation(handle, byteIndex, byref(phy));

# <summary>
# 延时翻转输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="byteIndex">字节序号[0,YKE_DIGITAL_OUTPUT_NUM/8)</param>
# <param name="bitOffset">位偏移[0,7]</param>
# <param name="time">延时时间(ms)</param>
# <returns></returns>
def YKM_ReverseDigitalOutputBit(dllPtr, handle, byteIndex, bitOffset, time):

	return dllPtr.YKM_ReverseDigitalOutputBit(handle, byteIndex, bitOffset, time);

# <summary>
# 同步数字输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="output">输出列表</param>
# <param name="size">输出数量(0, YKE_DIGITAL_OUTPUT_CYCLE_NUM]</param>
# <returns></returns>
def YKM_WriteDigitalOutputCycle(dllPtr, handle, output, size):

	return dllPtr.YKM_WriteDigitalOutputCycle(handle, output, size);

# <summary>
# 软件模式比较器参数配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_COMPARE_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetCompareConfigSoft(dllPtr, handle, channel, config):

	return dllPtr.YKM_SetCompareConfigSoft(handle, channel, config);

# <summary>
# 获取软件模式比较器参数配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_COMPARE_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetCompareConfigSoft(dllPtr, handle, channel, config):

	return dllPtr.YKM_GetCompareConfigSoft(handle, channel, byref(config));

# <summary>
# 设置比较值
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_COMPARE_NUM)</param>
# <param name="itemdata">比较配置，内部含有512个缓冲区</param>
# <returns></returns>
def YKM_SetCompareValueSoft(dllPtr, handle, channel, itemdata):

	return dllPtr.YKM_SetCompareValueSoft(handle, channel, itemdata);

# <summary>
# 获取软件模式比较器状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_COMPARE_NUM)</param>
# <param name="status">返回值</param>
# <returns></returns>
def YKM_ReadCompareStatusSoft(dllPtr, handle, channel, status):

	return dllPtr.YKM_ReadCompareStatusSoft(handle, channel, byref(status));

# <summary>
# 软件模式比较器开始
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_COMPARE_NUM)</param>
# <returns></returns>
def YKM_StartCompareSoft(dllPtr, handle, channel):

	return dllPtr.YKM_StartCompareSoft(handle, channel);

# <summary>
# 停止软件模式比较器
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_COMPARE_NUM)</param>
# <returns></returns>
def YKM_StopCompareSoft(dllPtr, handle, channel):

	return dllPtr.YKM_StopCompareSoft(handle, channel);

# <summary>
# 写入软件探针配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_PROBE_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetProbeConfigSoft(dllPtr, handle, channel, config):

	return dllPtr.YKM_SetProbeConfigSoft(handle, channel, config);

# <summary>
# 读取软件探针配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_PROBE_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetProbeConfigSoft(dllPtr, handle, channel, config):

	return dllPtr.YKM_GetProbeConfigSoft(handle, channel, byref(config));

# <summary>
# 启动软件探针
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_PROBE_NUM)</param>
# <returns></returns>
def YKM_StartProbeSoft(dllPtr, handle, channel):

	return dllPtr.YKM_StartProbeSoft(handle, channel);

# <summary>
# 停止软件探针
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_PROBE_NUM)</param>
# <returns></returns>
def YKM_StopProbeSoft(dllPtr, handle, channel):

	return dllPtr.YKM_StopProbeSoft(handle, channel);

# <summary>
# 获取软件探针状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_SOFT_PROBE_NUM)</param>
# <param name="status">返回状态</param>
# <returns></returns>
def YKM_ReadProbeStatusSoft(dllPtr, handle, channel, status):

	return dllPtr.YKM_ReadProbeStatusSoft(handle, channel, byref(status));

# <summary>
# 设置规划方向的当量，初始化完成后先设置当量，再使用和当量有关的函数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="dist">位移当量，浮点格式</param>
# <param name="pulse">脉冲当量，浮点格式</param>
# <returns></returns>
def YKM_SetCommandEquiv(dllPtr, handle, axisIndex, dist, pulse):

	return dllPtr.YKM_SetCommandEquiv(handle, axisIndex, dist, pulse);

# <summary>
# 获取规划方向的当量，初始化完成后先设置当量，再使用和当量有关的函数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="dist">位移当量，浮点格式</param>
# <param name="pulse">脉冲当量，浮点格式</param>
# <returns></returns>
def YKM_GetCommandEquiv(dllPtr, handle, axisIndex, dist, pulse):

	return dllPtr.YKM_GetCommandEquiv(handle, axisIndex, byref(dist), byref(pulse));

# <summary>
# 获取反馈方向当量比例，以规划方向当量为参考
# 总线轴有效
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="scale">比例</param>
# <returns></returns>
def YKM_GetFeedbackEquivScale(dllPtr, handle, axisIndex, scale):

	return dllPtr.YKM_GetFeedbackEquivScale(handle, axisIndex, byref(scale));

# <summary>
# 获取反馈方向当量比例，以规划方向当量为参考
# 总线轴有效
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="scale">比例</param>
# <returns></returns>
def YKM_SetFeedbackEquivScale(dllPtr, handle, axisIndex, scale):

	return dllPtr.YKM_SetFeedbackEquivScale(handle, axisIndex, scale);

# <summary>
# 设置转动方向
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="rotate_dir">FALSE:和驱动器一致  TRUE:和驱动器相反</param>
# <returns></returns>
def YKM_SetRotateDir(dllPtr, handle, axisIndex, rotate_dir):

	return dllPtr.YKM_SetRotateDir(handle, axisIndex, rotate_dir);

# <summary>
# 获取转动方向
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="rotate_dir">FALSE:和驱动器一致  TRUE:和驱动器相反</param>
# <returns></returns>
def YKM_GetRotateDir(dllPtr, handle, axisIndex, rotate_dir):

	return dllPtr.YKM_GetRotateDir(handle, axisIndex, byref(rotate_dir));

# <summary>
# 设置模轴配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetAxisProfileModulo(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetAxisProfileModulo(handle, axisIndex, config);

# <summary>
# 获取模轴配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetAxisProfileModulo(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetAxisProfileModulo(handle, axisIndex, byref(config));

# <summary>
# 获得单圈数量
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="counter">单圈数量</param>
# <returns></returns>
def YKM_ReadAxisModuloCounter(dllPtr, handle, axisIndex, counter):

	return dllPtr.YKM_ReadAxisModuloCounter(handle, axisIndex, byref(counter));

# <summary>
# 设置软限位
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">限位配置</param>
# <returns></returns>
def YKM_SetAxisSoftLimit(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetAxisSoftLimit(handle, axisIndex, config);

# <summary>
# 获取软限位配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetAxisSoftLimit(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetAxisSoftLimit(handle, axisIndex, byref(config));

# <summary>
# 写入硬限位启用配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetAxisHardLimitEnable(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetAxisHardLimitEnable(handle, axisIndex, config);

# <summary>
# 获取硬限位启用配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetAxisHardLimitEnable(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetAxisHardLimitEnable(handle, axisIndex, byref(config));

# <summary>
# 设置最大转矩值
# 对象字典(0x6072:00)必须加到PDO中
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="value">转矩值</param>
# <returns></returns>
def YKM_SetAxisMaxTorqueLimit(dllPtr, handle, axisIndex, value):

	return dllPtr.YKM_SetAxisMaxTorqueLimit(handle, axisIndex, value);

# <summary>
# 获取最大转矩值
# 对象字典(0x6072:00)必须加到PDO中
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="value">转矩值</param>
# <returns></returns>
def YKM_GetAxisMaxTorqueLimit(dllPtr, handle, axisIndex, value):

	return dllPtr.YKM_GetAxisMaxTorqueLimit(handle, axisIndex, byref(value));

# <summary>
# 设置正方向转矩限制值
# 对象字典(0x60E0:00)必须加到PDO中
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="value">转矩值</param>
# <returns></returns>
def YKM_SetAxisPositiveTorqueLimit(dllPtr, handle, axisIndex, value):

	return dllPtr.YKM_SetAxisPositiveTorqueLimit(handle, axisIndex, value);

# <summary>
# 获取正方向转矩限制值
# 对象字典(0x60E0:00)必须加到PDO中
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="value">转矩值</param>
# <returns></returns>
def YKM_GetAxisPositiveTorqueLimit(dllPtr, handle, axisIndex, value):

	return dllPtr.YKM_GetAxisPositiveTorqueLimit(handle, axisIndex, byref(value));

# <summary>
# 设置负方向转矩限制值
# 对象字典(0x60E1:00)必须加到PDO中
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="value">转矩值</param>
# <returns></returns>
def YKM_SetAxisNegativeTorqueLimit(dllPtr, handle, axisIndex, value):

	return dllPtr.YKM_SetAxisNegativeTorqueLimit(handle, axisIndex, value);

# <summary>
# 获取负方向转矩限制值
# 对象字典(0x60E1:00)必须加到PDO中
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="value">转矩值</param>
# <returns></returns>
def YKM_GetAxisNegativeTorqueLimit(dllPtr, handle, axisIndex, value):

	return dllPtr.YKM_GetAxisNegativeTorqueLimit(handle, axisIndex, byref(value));

# <summary>
# 设置最大电流限制值
# 对象字典(0x6073:00)必须加到PDO中
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="value">电流限制值</param>
# <returns></returns>
def YKM_SetAxisMaxCurrentLimit(dllPtr, handle, axisIndex, value):

	return dllPtr.YKM_SetAxisMaxCurrentLimit(handle, axisIndex, value);

# <summary>
# 获取最大电流限制值
# 对象字典(0x6073:00)必须加到PDO中
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="value">电流限制值</param>
# <returns></returns>
def YKM_GetAxisMaxCurrentLimit(dllPtr, handle, axisIndex, value):

	return dllPtr.YKM_GetAxisMaxCurrentLimit(handle, axisIndex, byref(value));

# <summary>
# 获得规划位置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="position">位置</param>
# <returns></returns>
def YKM_ReadAxisCommandPosition(dllPtr, handle, axisIndex, position):

	return dllPtr.YKM_ReadAxisCommandPosition(handle, axisIndex, byref(position));

# <summary>
# 获得实际位置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="position">位置</param>
# <returns></returns>
def YKM_ReadAxisActualPosition(dllPtr, handle, axisIndex, position):

	return dllPtr.YKM_ReadAxisActualPosition(handle, axisIndex, byref(position));

# <summary>
# 获得目标位置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="position">位置</param>
# <returns></returns>
def YKM_ReadAxisTargetPosition(dllPtr, handle, axisIndex, position):

	return dllPtr.YKM_ReadAxisTargetPosition(handle, axisIndex, byref(position));

# <summary>
# 获取轴的原始位置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="position">位置</param>
# <returns></returns>
def YKM_ReadAxisRawPosition(dllPtr, handle, axisIndex, position):

	return dllPtr.YKM_ReadAxisRawPosition(handle, axisIndex, byref(position));

# <summary>
# 获得规划速度
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="velocity">速度</param>
# <returns></returns>
def YKM_ReadAxisCommandVelocity(dllPtr, handle, axisIndex, velocity):

	return dllPtr.YKM_ReadAxisCommandVelocity(handle, axisIndex, byref(velocity));

# <summary>
# 获得实际速度
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="velocity">速度</param>
# <returns></returns>
def YKM_ReadAxisActualVelocity(dllPtr, handle, axisIndex, velocity):

	return dllPtr.YKM_ReadAxisActualVelocity(handle, axisIndex, byref(velocity));

# <summary>
# 获得规划加速度
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="acceleration">加速度</param>
# <returns></returns>
def YKM_ReadAxisCommandAcceleration(dllPtr, handle, axisIndex, acceleration):

	return dllPtr.YKM_ReadAxisCommandAcceleration(handle, axisIndex, byref(acceleration));

# <summary>
# 获得变加速度
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="jerk">变加速度</param>
# <returns></returns>
def YKM_ReadAxisCommandJerk(dllPtr, handle, axisIndex, jerk):

	return dllPtr.YKM_ReadAxisCommandJerk(handle, axisIndex, byref(jerk));

# <summary>
# 获得给定转矩，需要在PDO中配置转矩对象字典
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="torque">转矩值</param>
# <returns></returns>
def YKM_ReadAxisCommandTorque(dllPtr, handle, axisIndex, torque):

	return dllPtr.YKM_ReadAxisCommandTorque(handle, axisIndex, byref(torque));

# <summary>
# 获得实际转矩，需要在PDO中配置转矩对象字典
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="torque">转矩值</param>
# <returns></returns>
def YKM_ReadAxisActualTorque(dllPtr, handle, axisIndex, torque):

	return dllPtr.YKM_ReadAxisActualTorque(handle, axisIndex, byref(torque));

# <summary>
# 设置用户自定义数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="mask">掩码</param>
# <param name="value">写入值</param>
# <returns></returns>
def YKM_SetAxisUserData(dllPtr, handle, axisIndex, mask, value):

	return dllPtr.YKM_SetAxisUserData(handle, axisIndex, mask, value);

# <summary>
# 获取用户自定义数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="value">返回的值</param>
# <returns></returns>
def YKM_GetAxisUserData(dllPtr, handle, axisIndex, value):

	return dllPtr.YKM_GetAxisUserData(handle, axisIndex, byref(value));

# <summary>
# 读轴的基本配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_ReadAxisConfigBase(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_ReadAxisConfigBase(handle, axisIndex, byref(config));

# <summary>
# 读轴规划状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadAxisStatusPlanner(dllPtr, handle, axisIndex, status):

	return dllPtr.YKM_ReadAxisStatusPlanner(handle, axisIndex, byref(status));

# <summary>
# 读轴位置相关状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadAxisStatusPosition(dllPtr, handle, axisIndex, status):

	return dllPtr.YKM_ReadAxisStatusPosition(handle, axisIndex, byref(status));

# <summary>
# 读轴机械补偿状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadAxisStatusCompensation(dllPtr, handle, axisIndex, status):

	return dllPtr.YKM_ReadAxisStatusCompensation(handle, axisIndex, byref(status));

# <summary>
# 读轴跟随状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadAxisStatusFollow(dllPtr, handle, axisIndex, status):

	return dllPtr.YKM_ReadAxisStatusFollow(handle, axisIndex, byref(status));

# <summary>
# 读轴基本状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadAxisStatusBase(dllPtr, handle, axisIndex, status):

	return dllPtr.YKM_ReadAxisStatusBase(handle, axisIndex, byref(status));

# <summary>
# 读轴触发状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadAxisTriggerStatus(dllPtr, handle, axisIndex, status):

	return dllPtr.YKM_ReadAxisTriggerStatus(handle, axisIndex, byref(status));

# <summary>
# 轴公共参数设置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">轴配置</param>
# <returns></returns>
def YKM_SetAxisProfileBase(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetAxisProfileBase(handle, axisIndex, config);

# <summary>
# 获得轴公共参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">轴配置</param>
# <returns></returns>
def YKM_GetAxisProfileBase(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetAxisProfileBase(handle, axisIndex, byref(config));

# <summary>
# 运动参数设置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetAxisProfileMotion(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetAxisProfileMotion(handle, axisIndex, config);

# <summary>
# 获得运动参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetAxisProfileMotion(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetAxisProfileMotion(handle, axisIndex, byref(config));

# <summary>
# 设置轴到位配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">到位配置</param>
# <returns></returns>
def YKM_SetAxisProfileInp(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetAxisProfileInp(handle, axisIndex, config);

# <summary>
# 获取轴到位配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">到位配置</param>
# <returns></returns>
def YKM_GetAxisProfileInp(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetAxisProfileInp(handle, axisIndex, byref(config));

# <summary>
# 设置轴跟随误差配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">跟随误差配置</param>
# <returns></returns>
def YKM_SetAxisProfilePositionLag(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetAxisProfilePositionLag(handle, axisIndex, config);

# <summary>
# 获取轴跟随配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">跟随误差配置</param>
# <returns></returns>
def YKM_GetAxisProfilePositionLag(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetAxisProfilePositionLag(handle, axisIndex, byref(config));

# <summary>
# 获得轴使用列表
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisNum">返回值，轴数量</param>
# <param name="axisList">轴序号列表</param>
# <param name="size">axisList缓冲区大小</param>
# <returns></returns>
def YKM_GetAxisList(dllPtr, handle, axisNum, axisList, size):

	return dllPtr.YKM_GetAxisList(handle, byref(axisNum), byref(axisList), size);

# <summary>
# 设置驱动器控制模式，总线轴专用
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="mode">模式</param>
# <returns></returns>
def YKM_SetAxisDrvOpMode(dllPtr, handle, axisIndex, mode):

	return dllPtr.YKM_SetAxisDrvOpMode(handle, axisIndex, mode);

# <summary>
# 获取驱动器控制模式，总线轴专用
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="mode">模式</param>
# <returns></returns>
def YKM_GetAxisDrvOpMode(dllPtr, handle, axisIndex, mode):

	return dllPtr.YKM_GetAxisDrvOpMode(handle, axisIndex, byref(mode));

# <summary>
# 设置轴报警屏蔽配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="mask">屏蔽配置，按位定义 BIT0=硬限位 BIT1=保留 BIT2=软限位</param>
# <returns></returns>
def YKM_SetAxisWarnMask(dllPtr, handle, axisIndex, mask):

	return dllPtr.YKM_SetAxisWarnMask(handle, axisIndex, mask);

# <summary>
# 获取轴报警屏蔽配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="mask">屏蔽配置，按位定义 BIT0=硬限位  BIT1=保留 BIT2=软限位</param>
# <returns></returns>
def YKM_GetAxisWarnMask(dllPtr, handle, axisIndex, mask):

	return dllPtr.YKM_GetAxisWarnMask(handle, axisIndex, byref(mask));

# <summary>
# 获取轴名称，名称在ProEn中设置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="name">返回名称，至少分配64字节</param>
# <param name="size">name缓冲区尺寸</param>
# <returns></returns>
def YKM_GetAxisAlias(dllPtr, handle, axisIndex, name, size):

	return dllPtr.YKM_GetAxisAlias(handle, axisIndex, byref(name), size);

# <summary>
# 清除轴的回原完成状态(YKS_AxisStatusBase.is_homed)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_ClearAxisHomed(dllPtr, handle, axisIndex):

	return dllPtr.YKM_ClearAxisHomed(handle, axisIndex);

# <summary>
# 设置轴的回原完成状态(YKS_AxisStatusBase.is_homed)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_SetAxisHomed(dllPtr, handle, axisIndex):

	return dllPtr.YKM_SetAxisHomed(handle, axisIndex);

# <summary>
# 将指编码器指定位置设为原点
# 绝对值编码器工况下使用
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="encoder_value">设定值</param>
# <returns></returns>
def YKM_SetAxisHomeAbsEncoder(dllPtr, handle, axisIndex, encoder_value):

	return dllPtr.YKM_SetAxisHomeAbsEncoder(handle, axisIndex, encoder_value);

# <summary>
# 获取原点对应的编码器值(由YKM_SetAxisHomeAbsEncoder写入)
# 绝对值编码器工况下使用
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="encoder_value">返回值</param>
# <returns></returns>
def YKM_GetAxisHomeAbsEncoder(dllPtr, handle, axisIndex, encoder_value):

	return dllPtr.YKM_GetAxisHomeAbsEncoder(handle, axisIndex, byref(encoder_value));

# <summary>
# 写入正限位开关配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetSwitchLimitPositive(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetSwitchLimitPositive(handle, axisIndex, config);

# <summary>
# 读取正限位开关配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetSwitchLimitPositive(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetSwitchLimitPositive(handle, axisIndex, byref(config));

# <summary>
# 写入负限位开关配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetSwitchLimitNegative(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetSwitchLimitNegative(handle, axisIndex, config);

# <summary>
# 读取负限位开关配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetSwitchLimitNegative(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetSwitchLimitNegative(handle, axisIndex, byref(config));

# <summary>
# 写入原点开关配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetSwitchHome(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetSwitchHome(handle, axisIndex, config);

# <summary>
# 读取原点开关配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetSwitchHome(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetSwitchHome(handle, axisIndex, byref(config));

# <summary>
# 写入探针开关配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">通道号 (0~1)  0/1为硬件探针函数使用</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetSwitchProbe(dllPtr, handle, axisIndex, channel, config):

	return dllPtr.YKM_SetSwitchProbe(handle, axisIndex, channel, config);

# <summary>
# 读取探针开关配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">通道号 (0~1)  0/1为硬件探针函数使用</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetSwitchProbe(dllPtr, handle, axisIndex, channel, config):

	return dllPtr.YKM_GetSwitchProbe(handle, axisIndex, channel, byref(config));

# <summary>
# 写入回原探针开关配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetHomeProbe(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetHomeProbe(handle, axisIndex, config);

# <summary>
# 读取回原探针开关配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetHomeProbe(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetHomeProbe(handle, axisIndex, byref(config));

# <summary>
# 设置当前位置，将当前位置设置为指定值
# 会清除IsHomed信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="position">指定位置</param>
# <returns></returns>
def YKM_SetAxisPosition(dllPtr, handle, axisIndex, position):

	return dllPtr.YKM_SetAxisPosition(handle, axisIndex, position);

# <summary>
# 设置清除驱动器报警重试参数，总线轴有效
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="profile"></param>
# <returns></returns>
def YKM_SetAxisProfileClearDrv(dllPtr, handle, axisIndex, profile):

	return dllPtr.YKM_SetAxisProfileClearDrv(handle, axisIndex, profile);

# <summary>
# 获取清除驱动器报警重试参数，总线轴有效
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="profile">返回配置</param>
# <returns></returns>
def YKM_GetAxisProfileClearDrv(dllPtr, handle, axisIndex, profile):

	return dllPtr.YKM_GetAxisProfileClearDrv(handle, axisIndex, byref(profile));

# <summary>
# 清除驱动器报警
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_ClearDrvWarn(dllPtr, handle, axisIndex):

	return dllPtr.YKM_ClearDrvWarn(handle, axisIndex);

# <summary>
# 复位轴状态，清除报警
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_ClearAxisWarn(dllPtr, handle, axisIndex):

	return dllPtr.YKM_ClearAxisWarn(handle, axisIndex);

# <summary>
# 获取轴使能参数，总线轴有效
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="profile">配置</param>
# <returns></returns>
def YKM_GetAxisProfilePowerOn(dllPtr, handle, axisIndex, profile):

	return dllPtr.YKM_GetAxisProfilePowerOn(handle, axisIndex, byref(profile));

# <summary>
# 设置轴使能参数，总线轴有效
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="profile">配置</param>
# <returns></returns>
def YKM_SetAxisProfilePowerOn(dllPtr, handle, axisIndex, profile):

	return dllPtr.YKM_SetAxisProfilePowerOn(handle, axisIndex, profile);

# <summary>
# 获取轴前馈参数，总线轴有效
# 未实现
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="profile">配置</param>
# <returns></returns>
def YKM_GetAxisProfileFeedforward(dllPtr, handle, axisIndex, profile):

	return dllPtr.YKM_GetAxisProfileFeedforward(handle, axisIndex, byref(profile));

# <summary>
# 设置轴前馈参数，总线轴有效
# 未实现
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="profile">配置</param>
# <returns></returns>
def YKM_SetAxisProfileFeedforward(dllPtr, handle, axisIndex, profile):

	return dllPtr.YKM_SetAxisProfileFeedforward(handle, axisIndex, profile);

# <summary>
# 轴使能
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_PowerOn(dllPtr, handle, axisIndex):

	return dllPtr.YKM_PowerOn(handle, axisIndex);

# <summary>
# 轴去使能
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_PowerOff(dllPtr, handle, axisIndex):

	return dllPtr.YKM_PowerOff(handle, axisIndex);

# <summary>
# 单轴停止
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="dec_sel">减速度选择</param>
# <returns></returns>
def YKM_StopAxis(dllPtr, handle, axisIndex, dec_sel):

	return dllPtr.YKM_StopAxis(handle, axisIndex, dec_sel);

# <summary>
# 触发轴停止
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="dec_sel">减速度选择</param>
# <param name="trigger">触发条件</param>
# <returns></returns>
def YKM_StopAxisTrigger(dllPtr, handle, axisIndex, dec_sel, trigger):

	return dllPtr.YKM_StopAxisTrigger(handle, axisIndex, dec_sel, trigger);

# <summary>
# 启动回原点
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_StartHome(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_StartHome(handle, axisIndex, config);

# <summary>
# 获取回原点配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetHomeConfig(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetHomeConfig(handle, axisIndex, byref(config));

# <summary>
# 绝对运动
# 支持API缓冲区
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="position">目标位置</param>
# <returns></returns>
def YKM_MoveAbsolute(dllPtr, handle, axisIndex, position):

	return dllPtr.YKM_MoveAbsolute(handle, axisIndex, position);

# <summary>
# 绝对运动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_MoveAbsoluteEx(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_MoveAbsoluteEx(handle, axisIndex, config);

# <summary>
# 绝对运动(条件触发)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">运动配置</param>
# <param name="trigger">触发条件</param>
# <returns></returns>
def YKM_MoveAbsoluteTrigger(dllPtr, handle, axisIndex, config, trigger):

	return dllPtr.YKM_MoveAbsoluteTrigger(handle, axisIndex, config, trigger);

# <summary>
# 绝对运动(事件触发)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">运动配置</param>
# <returns></returns>
def YKM_MoveAbsoluteEvent(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_MoveAbsoluteEvent(handle, axisIndex, config);

# <summary>
# 相对运动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="distance">移动距离</param>
# <returns></returns>
def YKM_MoveRelative(dllPtr, handle, axisIndex, distance):

	return dllPtr.YKM_MoveRelative(handle, axisIndex, distance);

# <summary>
# 相对运动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_MoveRelativeEx(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_MoveRelativeEx(handle, axisIndex, config);

# <summary>
# 相对运动(条件触发)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">运动配置</param>
# <param name="trigger">触发条件</param>
# <returns></returns>
def YKM_MoveRelativeTrigger(dllPtr, handle, axisIndex, config, trigger):

	return dllPtr.YKM_MoveRelativeTrigger(handle, axisIndex, config, trigger);

# <summary>
# 相对运动(事件触发)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">运动配置</param>
# <returns></returns>
def YKM_MoveRelativeEvent(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_MoveRelativeEvent(handle, axisIndex, config);

# <summary>
# 运动仿真
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">运动配置</param>
# <param name="result">规划结果</param>
# <returns></returns>
def YKM_MovePositionSim(dllPtr, handle, axisIndex, config, result):

	return dllPtr.YKM_MovePositionSim(handle, axisIndex, config, byref(result));

# <summary>
# 速度运动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="velocity">新速度</param>
# <param name="direction">运动方向</param>
# <returns></returns>
def YKM_MoveVelocity(dllPtr, handle, axisIndex, velocity, direction):

	return dllPtr.YKM_MoveVelocity(handle, axisIndex, velocity, direction);

# <summary>
# 速度运动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_MoveVelocityEx(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_MoveVelocityEx(handle, axisIndex, config);

# <summary>
# 传送带运动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_MoveConveyor(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_MoveConveyor(handle, axisIndex, config);

# <summary>
# 写入事件触发条件
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">保留，固定为0</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_WriteAxisEventOneSignal(dllPtr, handle, axisIndex, channel, config):

	return dllPtr.YKM_WriteAxisEventOneSignal(handle, axisIndex, channel, config);

# <summary>
# 写入事件触发条件
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">保留，固定为0</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_WriteAxisEventTwoSignal(dllPtr, handle, axisIndex, channel, config):

	return dllPtr.YKM_WriteAxisEventTwoSignal(handle, axisIndex, channel, config);

# <summary>
# 速度运动(条件触发)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">运动配置</param>
# <param name="trigger">触发条件</param>
# <returns></returns>
def YKM_MoveVelocityTrigger(dllPtr, handle, axisIndex, config, trigger):

	return dllPtr.YKM_MoveVelocityTrigger(handle, axisIndex, config, trigger);

# <summary>
# 速度运动(事件触发)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">运动配置</param>
# <returns></returns>
def YKM_MoveVelocityEvent(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_MoveVelocityEvent(handle, axisIndex, config);

# <summary>
# 转矩
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_MoveTorque(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_MoveTorque(handle, axisIndex, config);

# <summary>
# 修改目标位置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="position">新的位置</param>
# <returns></returns>
def YKM_OverridePosition(dllPtr, handle, axisIndex, position):

	return dllPtr.YKM_OverridePosition(handle, axisIndex, position);

# <summary>
# 修改目标速度
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="velocity">新的速度</param>
# <returns></returns>
def YKM_OverrideVelocity(dllPtr, handle, axisIndex, velocity):

	return dllPtr.YKM_OverrideVelocity(handle, axisIndex, velocity);

# <summary>
# 修改加速度
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="acc">新的加速度</param>
# <returns></returns>
def YKM_OverrideAcceleration(dllPtr, handle, axisIndex, acc):

	return dllPtr.YKM_OverrideAcceleration(handle, axisIndex, acc);

# <summary>
# 修改减速度
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="dec">新的减速度</param>
# <returns></returns>
def YKM_OverrideDeceleration(dllPtr, handle, axisIndex, dec):

	return dllPtr.YKM_OverrideDeceleration(handle, axisIndex, dec);

# <summary>
# 修改加速度过程的变加速度
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="jerk_acc">新的变加速度</param>
# <returns></returns>
def YKM_OverrideJerkAcc(dllPtr, handle, axisIndex, jerk_acc):

	return dllPtr.YKM_OverrideJerkAcc(handle, axisIndex, jerk_acc);

# <summary>
# 修改减速过程的变加速度
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="jerk_dec">新的变加速度</param>
# <returns></returns>
def YKM_OverrideJerkDec(dllPtr, handle, axisIndex, jerk_dec):

	return dllPtr.YKM_OverrideJerkDec(handle, axisIndex, jerk_dec);

# <summary>
# 在指定位置生效新参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="motion">新的运动参数</param>
# <param name="position">指定位置</param>
# <returns></returns>
def YKM_OverrideAtPosition(dllPtr, handle, axisIndex, motion, position):

	return dllPtr.YKM_OverrideAtPosition(handle, axisIndex, motion, position);

# <summary>
# 写入PT数据，支持动态添加
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="data">配置</param>
# <param name="size">数量</param>
# <returns></returns>
def YKM_WritePTData(dllPtr, handle, axisIndex, data, size):

	return dllPtr.YKM_WritePTData(handle, axisIndex, data, size);

# <summary>
# 写入PVT数据，支持动态添加
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="data">配置</param>
# <param name="size">数量</param>
# <returns></returns>
def YKM_WritePVTData(dllPtr, handle, axisIndex, data, size):

	return dllPtr.YKM_WritePVTData(handle, axisIndex, data, size);

# <summary>
# 写入PVTS数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="start_velocity">启动速度</param>
# <param name="end_velocity">停止速度</param>
# <param name="data">配置</param>
# <param name="size">数量</param>
# <returns></returns>
def YKM_WritePVTSData(dllPtr, handle, axisIndex, start_velocity, end_velocity, data, size):

	return dllPtr.YKM_WritePVTSData(handle, axisIndex, start_velocity, end_velocity, data, size);

# <summary>
# 启动PT运动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_MovePVTStart(dllPtr, handle, axisIndex):

	return dllPtr.YKM_MovePVTStart(handle, axisIndex);

# <summary>
# 同时启动多轴的PT运动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisNum">轴数量, 最大32轴</param>
# <param name="axisList">轴序号列表</param>
# <returns></returns>
def YKM_MoveMultiPVTStart(dllPtr, handle, axisNum, axisList):

	return dllPtr.YKM_MoveMultiPVTStart(handle, axisNum, byref(axisList));

# <summary>
# 获取PVT缓冲区状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="status">返回状态</param>
# <returns></returns>
def YKM_ReadPVTStatus(dllPtr, handle, axisIndex, status):

	return dllPtr.YKM_ReadPVTStatus(handle, axisIndex, byref(status));

# <summary>
# 清除PVT数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_ClearPVTData(dllPtr, handle, axisIndex):

	return dllPtr.YKM_ClearPVTData(handle, axisIndex);

# <summary>
# 轴跟随其他单轴
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_FollowAxis1(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_FollowAxis1(handle, axisIndex, config);

# <summary>
# 轴跟随其他多轴
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_FollowAxis2(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_FollowAxis2(handle, axisIndex, config);

# <summary>
# 轴跟随UG数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_FollowUG(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_FollowUG(handle, axisIndex, config);

# <summary>
# 轴跟随本地编码器
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_FollowEncoderPCI(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_FollowEncoderPCI(handle, axisIndex, config);

# <summary>
#	轴跟随坐标系数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_FollowGroup(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_FollowGroup(handle, axisIndex, config);

# <summary>
# 写入凸轮配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">写入配置</param>
# <returns></returns>
def YKM_SetCamInConfig(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetCamInConfig(handle, axisIndex, config);

# <summary>
# 读取凸轮配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">返回配置</param>
# <returns></returns>
def YKM_GetCamInConfig(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetCamInConfig(handle, axisIndex, byref(config));

# <summary>
# 设置凸轮表数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="rowIndex">表行数</param>
# <param name="data">数据</param>
# <returns></returns>
def YKM_SetCamTable(dllPtr, handle, axisIndex, rowIndex, data):

	return dllPtr.YKM_SetCamTable(handle, axisIndex, rowIndex, data);

# <summary>
# 获取凸轮表的一行数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="rowIndex">表行号，从0开始</param>
# <param name="data">行数据</param>
# <returns></returns>
def YKM_GetCamTable(dllPtr, handle, axisIndex, rowIndex, data):

	return dllPtr.YKM_GetCamTable(handle, axisIndex, rowIndex, byref(data));

# <summary>
# 启动凸轮
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_StartCamIn(dllPtr, handle, axisIndex):

	return dllPtr.YKM_StartCamIn(handle, axisIndex);

# <summary>
# 凸轮表求解，厂家使用
# </summary>
# <param name="table">输入数据</param>
# <param name="size">数据数量</param>
# <param name="result">解析结果</param>
# <param name="type">曲线类型</param>
# <returns></returns>
def YKM_CalcCam(dllPtr, table, size, result, type):

	return dllPtr.YKM_CalcCam(byref(table), size, byref(result), type);

# <summary>
# 获取凸轮表插值，厂家使用
# </summary>
# <param name="result">解析结果</param>
# <param name="size">数据数量</param>
# <param name="key">输入值</param>
# <param name="value">输出值</param>
# <param name="type">曲线类型</param>
# <returns></returns>
def YKM_GetCam(dllPtr, result, size, key, value, type):

	return dllPtr.YKM_GetCam(byref(result), size, key, byref(value), type);

# <summary>
# 直线插补，相对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道序号 0~127</param>
# <param name="config">参数</param>
# <returns></returns>
def YKM_LinearInterpolationRelative(dllPtr, handle, channel, config):

	return dllPtr.YKM_LinearInterpolationRelative(handle, channel, config);

# <summary>
# 直线插补，绝对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道序号 0~127</param>
# <param name="config">参数</param>
# <returns></returns>
def YKM_LinearInterpolationAbsolute(dllPtr, handle, channel, config):

	return dllPtr.YKM_LinearInterpolationAbsolute(handle, channel, config);

# <summary>
# 多轴直线同步运动，绝对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道序号 0~127</param>
# <param name="config">参数</param>
# <returns></returns>
def YKM_LinearSyncAbsolute(dllPtr, handle, channel, config):

	return dllPtr.YKM_LinearSyncAbsolute(handle, channel, config);

# <summary>
# 多轴直线同步运动，相对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道序号 0~127</param>
# <param name="config">参数</param>
# <returns></returns>
def YKM_LinearSyncRelative(dllPtr, handle, channel, config):

	return dllPtr.YKM_LinearSyncRelative(handle, channel, config);

# <summary>
# 圆弧运动，相对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道序号 0~127</param>
# <param name="config">参数</param>
# <returns></returns>
def YKM_CircularInterpolationRelative(dllPtr, handle, channel, config):

	return dllPtr.YKM_CircularInterpolationRelative(handle, channel, config);

# <summary>
# 圆弧运动，绝对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道序号 0~127</param>
# <param name="config">参数</param>
# <returns></returns>
def YKM_CircularInterpolationAbsolute(dllPtr, handle, channel, config):

	return dllPtr.YKM_CircularInterpolationAbsolute(handle, channel, config);

# <summary>
# 停止多轴联动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道序号 0~127</param>
# <param name="dec_sel">保留</param>
# <returns></returns>
def YKM_StopMultiAxis(dllPtr, handle, channel, dec_sel):

	return dllPtr.YKM_StopMultiAxis(handle, channel, dec_sel);

# <summary>
# 获取多轴联动状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道序号 0~127</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadMultiAxisStatus(dllPtr, handle, channel, status):

	return dllPtr.YKM_ReadMultiAxisStatus(handle, channel, byref(status));

# <summary>
# 多轴同时启动，绝对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_MoveSyncAbsolute(dllPtr, handle, config):

	return dllPtr.YKM_MoveSyncAbsolute(handle, config);

# <summary>
# 设置坐标系参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetGroupProfile(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_SetGroupProfile(handle, groupIndex, config);

# <summary>
# 获取坐标系参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetGroupProfile(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GetGroupProfile(handle, groupIndex, byref(config));

# <summary>
# 坐标系轴绑定,2到32轴
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_InitGroup(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_InitGroup(handle, groupIndex, config);

# <summary>
# 获取坐标系绑定配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetGroupConfig(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GetGroupConfig(handle, groupIndex, byref(config));

# <summary>
# 将轴从坐标系移出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <returns></returns>
def YKM_DeInitGroup(dllPtr, handle, groupIndex):

	return dllPtr.YKM_DeInitGroup(handle, groupIndex);

# <summary>
# 写CNC通道配置，在坐标系初始化前调用生效
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">CNC通道配置</param>
# <returns></returns>
def YKM_SetCncProfile(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_SetCncProfile(handle, groupIndex, config);

# <summary>
# 读CNC通道配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">CNC通道配置</param>
# <returns></returns>
def YKM_GetCncProfile(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GetCncProfile(handle, groupIndex, byref(config));

# <summary>
# 获取坐标系基础状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="status">状态值</param>
# <returns></returns>
def YKM_ReadGroupStatusBase(dllPtr, handle, groupIndex, status):

	return dllPtr.YKM_ReadGroupStatusBase(handle, groupIndex, byref(status));

# <summary>
# 获取坐标系CNC状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="status">状态值</param>
# <returns></returns>
def YKM_ReadGroupStatusCnc(dllPtr, handle, groupIndex, status):

	return dllPtr.YKM_ReadGroupStatusCnc(handle, groupIndex, byref(status));

# <summary>
# 清除坐标系报警
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <returns></returns>
def YKM_ClearGroupWarn(dllPtr, handle, groupIndex):

	return dllPtr.YKM_ClearGroupWarn(handle, groupIndex);

# <summary>
# 停止坐标系运动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="dec_sel">停止减速度选择</param>
# <returns></returns>
def YKM_StopGroup(dllPtr, handle, groupIndex, dec_sel):

	return dllPtr.YKM_StopGroup(handle, groupIndex, dec_sel);

# <summary>
# 启动坐标系运动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <returns></returns>
def YKM_StartGroup(dllPtr, handle, groupIndex):

	return dllPtr.YKM_StartGroup(handle, groupIndex);

# <summary>
# 暂停坐标系运行,未实现
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <returns></returns>
def YKM_PauseGroup(dllPtr, handle, groupIndex):

	return dllPtr.YKM_PauseGroup(handle, groupIndex);

# <summary>
# 坐标系内直线插补，绝对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置参数</param>
# <returns></returns>
def YKM_MoveLinearAbsolute(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_MoveLinearAbsolute(handle, groupIndex, config);

# <summary>
# 坐标系内直线插补，相对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置参数</param>
# <returns></returns>
def YKM_MoveLinearRelative(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_MoveLinearRelative(handle, groupIndex, config);

# <summary>
# 坐标系内螺旋插补，绝对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置参数</param>
# <returns></returns>
def YKM_MoveHelixAbsolute(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_MoveHelixAbsolute(handle, groupIndex, config);

# <summary>
# 坐标系内螺旋插补，相对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置参数</param>
# <returns></returns>
def YKM_MoveHelixRelative(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_MoveHelixRelative(handle, groupIndex, config);

# <summary>
# 坐标系内圆弧插补，绝对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置参数</param>
# <returns></returns>
def YKM_MoveCircularAbsolute(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_MoveCircularAbsolute(handle, groupIndex, config);

# <summary>
# 坐标系内圆弧插补，相对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置参数</param>
# <returns></returns>
def YKM_MoveCircularRelative(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_MoveCircularRelative(handle, groupIndex, config);

# <summary>
# Cardinal样条插补，相对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置参数</param>
# <returns></returns>
def YKM_MoveCardinalRelative(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_MoveCardinalRelative(handle, groupIndex, config);

# <summary>
# Cardinal样条插补，绝对模式
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置参数</param>
# <returns></returns>
def YKM_MoveCardinalAbsolute(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_MoveCardinalAbsolute(handle, groupIndex, config);

# <summary>
# 坐标系内数字输出，参考下一段运动行
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">输出配置</param>
# <returns></returns>
def YKM_GroupDigitalOutput(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupDigitalOutput(handle, groupIndex, config);

# <summary>
# 坐标系内PWM输出，参考下一段运动行
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">PWM输出配置</param>
# <returns></returns>
def YKM_GroupPwmOutput(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupPwmOutput(handle, groupIndex, config);

# <summary>
# 坐标系内写入PDO，参考下一段运动行
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">PDO配置</param>
# <returns></returns>
def YKM_GroupWritePDO(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupWritePDO(handle, groupIndex, config);

# <summary>
# 坐标系内写入数据寄存器，参考下一段运动行
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">VD配置</param>
# <returns></returns>
def YKM_GroupWriteRegister(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupWriteRegister(handle, groupIndex, config);

# <summary>
# 坐标系内启动事件，参考下一段运动行
# </summary>
# <param name="handle"></param>
# <param name="groupIndex"></param>
# <param name="config"></param>
# <returns></returns>
def YKM_GroupWriteEvent(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupWriteEvent(handle, groupIndex, config);

# <summary>
# Cardinal样条插补参数设置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupWriteTensive(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupWriteTensive(handle, groupIndex, config);

# <summary>
# 坐标系内延时
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">延时配置</param>
# <returns></returns>
def YKM_GroupDelay(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupDelay(handle, groupIndex, config);

# <summary>
# 坐标系内等待数字输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">数字输入配置</param>
# <returns></returns>
def YKM_GroupWaitDigitalInput(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupWaitDigitalInput(handle, groupIndex, config);

# <summary>
# 坐标系内等待外轴完成
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">外轴配置</param>
# <returns></returns>
def YKM_GroupWaitAxis(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupWaitAxis(handle, groupIndex, config);

# <summary>
# 坐标系内等待PDO数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">PDO配置</param>
# <returns></returns>
def YKM_GroupWaitPdo(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupWaitPdo(handle, groupIndex, config);

# <summary>
# 坐标系内等待数据寄存器
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">寄存器配置</param>
# <returns></returns>
def YKM_GroupWaitRegister(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupWaitRegister(handle, groupIndex, config);

# <summary>
# 坐标系内等待事件信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">事件配置</param>
# <returns></returns>
def YKM_GroupWaitEvent(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupWaitEvent(handle, groupIndex, config);

# <summary>
# 保留
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">Mark配置</param>
# <returns></returns>
def YKM_GroupTransMarkOn(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupTransMarkOn(handle, groupIndex, config);

# <summary>
# 保留
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <returns></returns>
def YKM_GroupTransMarkOff(dllPtr, handle, groupIndex):

	return dllPtr.YKM_GroupTransMarkOff(handle, groupIndex);

# <summary>
# 保留
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系编号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupAddiXYOn(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupAddiXYOn(handle, groupIndex, config);

# <summary>
# 保留
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系编号</param>
# <returns></returns>
def YKM_GroupAddiXYOff(dllPtr, handle, groupIndex):

	return dllPtr.YKM_GroupAddiXYOff(handle, groupIndex);

# <summary>
# 视觉Mark转换
# </summary>
# <param name="ptRef">图纸坐标</param>
# <param name="ptReal">实际坐标</param>
# <param name="config">转换结果</param>
# <returns></returns>
def YKM_CalcMark(dllPtr, ptRef, ptReal, config):

	return dllPtr.YKM_CalcMark(ptRef, ptReal, byref(config));

# <summary>
# 写G代码命令
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">G代码</param>
# <returns></returns>
def YKM_GroupWriteGCode(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupWriteGCode(handle, groupIndex, config);

# <summary>
# 加载NC文件进行加工
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="filename">文件全路径</param>
# <returns></returns>
def YKM_GroupLoadFile(dllPtr, handle, groupIndex, filename):

	return dllPtr.YKM_GroupLoadFile(handle, groupIndex, filename);

# <summary>
# 基于控制点的AKIMA样条配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupCncASpline(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncASpline(handle, groupIndex, config);

# <summary>
# 关闭样条平滑
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="mark">用户标记</param>
# <returns></returns>
def YKM_GroupCncSplineClose(dllPtr, handle, groupIndex, mark):

	return dllPtr.YKM_GroupCncSplineClose(handle, groupIndex, mark);

# <summary>
# CNC轮廓角偏差平滑配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupCncContourDev(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncContourDev(handle, groupIndex, config);

# <summary>
# CNC轮廓角距离平滑配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupCncContourDist(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncContourDist(handle, groupIndex, config);

# <summary>
# CNC动态轮廓优化平滑配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupCncContourDistSoft(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncContourDistSoft(handle, groupIndex, config);

# <summary>
# CNC进给主轴动态轮廓优化平滑配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config"></param>
# <returns></returns>
def YKM_GroupCncContourDistMaster(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncContourDistMaster(handle, groupIndex, config);

# <summary>
# CNC插入点平滑配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupCncContourPos(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncContourPos(handle, groupIndex, config);

# <summary>
# CNC完整轮廓动态优化平滑配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupCncContourPtp(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncContourPtp(handle, groupIndex, config);

# <summary>
# 关闭轮廓平滑
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="mark">用户标记</param>
# <returns></returns>
def YKM_GroupCncContourClose(dllPtr, handle, groupIndex, mark):

	return dllPtr.YKM_GroupCncContourClose(handle, groupIndex, mark);

# <summary>
# HSC_B样条平滑配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupCncHscB(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncHscB(handle, groupIndex, config);

# <summary>
# HSC_Surface平滑配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupCncHscS(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncHscS(handle, groupIndex, config);

# <summary>
# HSC_PCS1平滑参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupCncHscPcs1(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncHscPcs1(handle, groupIndex, config);

# <summary>
# HSC_PCS2平滑参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GroupCncHscPcs2(dllPtr, handle, groupIndex, config):

	return dllPtr.YKM_GroupCncHscPcs2(handle, groupIndex, config);

# <summary>
# 关闭HSC平滑
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="groupIndex">坐标系序号</param>
# <param name="mark">用户标记</param>
# <returns></returns>
def YKM_GroupCncHscClose(dllPtr, handle, groupIndex, mark):

	return dllPtr.YKM_GroupCncHscClose(handle, groupIndex, mark);

# <summary>
# 读CNC的轴参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="para_name">参数名称</param>
# <param name="size_name">参数数据缓冲区大小</param>
# <returns></returns>
def YKM_ReadCncParaCmd(dllPtr, handle, axisIndex, para_name, size_name):

	return dllPtr.YKM_ReadCncParaCmd(handle, axisIndex, para_name, size_name);

# <summary>
# 写CNC的轴参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="para_name">参数名称</param>
# <param name="size_name">参数数据缓冲区大小</param>
# <param name="para_value">参数值</param>
# <param name="size_value">值缓冲区大小</param>
# <returns></returns>
def YKM_WriteCncParaCmd(dllPtr, handle, axisIndex, para_name, size_name, para_value, size_value):

	return dllPtr.YKM_WriteCncParaCmd(handle, axisIndex, para_name, size_name, para_value, size_value);

# <summary>
# 读CNC参数操作状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="status">返回状态</param>
# <returns></returns>
def YKM_ReadCncParaStatus(dllPtr, handle, axisIndex, status):

	return dllPtr.YKM_ReadCncParaStatus(handle, axisIndex, byref(status));

# <summary>
# 启动硬件探针
# 总线轴探针参数在总线节点中设置
# 脉冲轴探针参数在脉冲节点中设置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">通道号 (0~1)</param>
# <returns></returns>
def YKM_StartProbeHard(dllPtr, handle, axisIndex, channel):

	return dllPtr.YKM_StartProbeHard(handle, axisIndex, channel);

# <summary>
# 停止硬件探针
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">通道号 (0~1)</param>
# <returns></returns>
def YKM_StopProbeHard(dllPtr, handle, axisIndex, channel):

	return dllPtr.YKM_StopProbeHard(handle, axisIndex, channel);

# <summary>
# 获取硬件探针状态及值
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">通道号 (0~1)</param>
# <param name="status">返回状态 0=未完成 1=完成</param>
# <param name="position">返回的探针位置</param>
# <returns></returns>
def YKM_ReadProbeStatusHard(dllPtr, handle, axisIndex, channel, status, position):

	return dllPtr.YKM_ReadProbeStatusHard(handle, axisIndex, channel, byref(status), byref(position));

# <summary>
# 获取轴软件探针配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">通道号(0~3)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetAxisProbeConfigSoft(dllPtr, handle, axisIndex, channel, config):

	return dllPtr.YKM_GetAxisProbeConfigSoft(handle, axisIndex, channel, byref(config));

# <summary>
# 设置轴软件探针配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">通道号(0~3)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetAxisProbeConfigSoft(dllPtr, handle, axisIndex, channel, config):

	return dllPtr.YKM_SetAxisProbeConfigSoft(handle, axisIndex, channel, config);

# <summary>
# 轴软件探针状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">通道号(0~3)</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadAxisProbeStatusSoft(dllPtr, handle, axisIndex, channel, status):

	return dllPtr.YKM_ReadAxisProbeStatusSoft(handle, axisIndex, channel, byref(status));

# <summary>
# 轴软件探针启动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">通道号(0~3)</param>
# <returns></returns>
def YKM_StartAxisProbeSoft(dllPtr, handle, axisIndex, channel):

	return dllPtr.YKM_StartAxisProbeSoft(handle, axisIndex, channel);

# <summary>
# 轴软件探针停止
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="channel">通道号(0~3)</param>
# <returns></returns>
def YKM_StopAxisProbeSoft(dllPtr, handle, axisIndex, channel):

	return dllPtr.YKM_StopAxisProbeSoft(handle, axisIndex, channel);

# <summary>
# 单IO触发输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_EVENT_NUM)</param>
# <param name="input">信号源</param>
# <returns></returns>
def YKM_WriteEventInputOneSignal(dllPtr, handle, channel, input):

	return dllPtr.YKM_WriteEventInputOneSignal(handle, channel, input);

# <summary>
# 双IO触发输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_EVENT_NUM)</param>
# <param name="input">信号源</param>
# <returns></returns>
def YKM_WriteEventInputTwoSignal(dllPtr, handle, channel, input):

	return dllPtr.YKM_WriteEventInputTwoSignal(handle, channel, input);

# <summary>
# 轴位置触发输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_EVENT_NUM)</param>
# <param name="input">配置</param>
# <returns></returns>
def YKM_WriteEventInputAxisPosition(dllPtr, handle, channel, input):

	return dllPtr.YKM_WriteEventInputAxisPosition(handle, channel, input);

# <summary>
# 轴时间触发输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_EVENT_NUM)</param>
# <param name="input">配置</param>
# <returns></returns>
def YKM_WriteEventInputAxisTime(dllPtr, handle, channel, input):

	return dllPtr.YKM_WriteEventInputAxisTime(handle, channel, input);

# <summary>
# 轴速度触发输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_EVENT_NUM)</param>
# <param name="input">信号源</param>
# <returns></returns>
def YKM_WriteEventInputAxisVelocity(dllPtr, handle, channel, input):

	return dllPtr.YKM_WriteEventInputAxisVelocity(handle, channel, input);

# <summary>
# 轴转矩触发输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_EVENT_NUM)</param>
# <param name="input">信号源</param>
# <returns></returns>
def YKM_WriteEventInputAxisTorque(dllPtr, handle, channel, input):

	return dllPtr.YKM_WriteEventInputAxisTorque(handle, channel, input);

# <summary>
# 从站PDO触发输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_EVENT_NUM)</param>
# <param name="input">信号源</param>
# <returns></returns>
def YKM_WriteEventInputSlavePDO(dllPtr, handle, channel, input):

	return dllPtr.YKM_WriteEventInputSlavePDO(handle, channel, input);

# <summary>
# 编码器触发输入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_EVENT_NUM)</param>
# <param name="input">信号源</param>
# <returns></returns>
def YKM_WriteEventInputEncoder(dllPtr, handle, channel, input):

	return dllPtr.YKM_WriteEventInputEncoder(handle, channel, input);

# <summary>
# 触发输出:位参数写入
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_EVENT_NUM)</param>
# <param name="output">输出配置</param>
# <returns></returns>
def YKM_WriteEventOutputOneSignal(dllPtr, handle, channel, output):

	return dllPtr.YKM_WriteEventOutputOneSignal(handle, channel, output);

# <summary>
# 触发输出:停止轴
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_EVENT_NUM)</param>
# <param name="output">输出配置</param>
# <returns></returns>
def YKM_WriteEventOutputStopAxis(dllPtr, handle, channel, output):

	return dllPtr.YKM_WriteEventOutputStopAxis(handle, channel, output);

# <summary>
# 触发输出:启动坐标系
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_EVENT_NUM)</param>
# <param name="output">输出配置</param>
# <returns></returns>
def YKM_WriteEventOutputStartGroup(dllPtr, handle, channel, output):

	return dllPtr.YKM_WriteEventOutputStartGroup(handle, channel, output);

# <summary>
# 触发输出:启动单轴
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_EVENT_NUM)</param>
# <param name="output">输出配置</param>
# <returns></returns>
def YKM_WriteEventOutputStartAxis(dllPtr, handle, channel, output):

	return dllPtr.YKM_WriteEventOutputStartAxis(handle, channel, output);

# <summary>
# 触发输出:软急停
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_EVENT_NUM)</param>
# <param name="output">输出配置</param>
# <returns></returns>
def YKM_WriteEventOutputSoftEmgStop(dllPtr, handle, channel, output):

	return dllPtr.YKM_WriteEventOutputSoftEmgStop(handle, channel, output);

# <summary>
# 触发输出:写PDO
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_EVENT_NUM)</param>
# <param name="output">通道号</param>
# <returns></returns>
def YKM_WriteEventOutputSlavePDO(dllPtr, handle, channel, output):

	return dllPtr.YKM_WriteEventOutputSlavePDO(handle, channel, output);

# <summary>
# 触发输出:启动多轴联动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_EVENT_NUM)</param>
# <param name="output">输出配置</param>
# <param name="motion">运动配置</param>
# <returns></returns>
def YKM_WriteEventOutputMultiAxis(dllPtr, handle, channel, output, motion):

	return dllPtr.YKM_WriteEventOutputMultiAxis(handle, channel, output, motion);

# <summary>
# 触发输出:写目标转矩
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_EVENT_NUM)</param>
# <param name="output">输出配置</param>
# <returns></returns>
def YKM_WriteEventOutputTargetTorque(dllPtr, handle, channel, output):

	return dllPtr.YKM_WriteEventOutputTargetTorque(handle, channel, output);

# <summary>
# 触发输出:延时
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_EVENT_NUM)</param>
# <param name="output">输出配置</param>
# <returns></returns>
def YKM_WriteEventOutputDelayMs(dllPtr, handle, channel, output):

	return dllPtr.YKM_WriteEventOutputDelayMs(handle, channel, output);

# <summary>
# 触发输出:写数据寄存器
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_EVENT_NUM)</param>
# <param name="output">输出配置</param>
# <returns></returns>
def YKM_WriteEventOutputDataReg(dllPtr, handle, channel, output):

	return dllPtr.YKM_WriteEventOutputDataReg(handle, channel, output);

# <summary>
# 启动事件
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,1023)</param>
# <returns></returns>
def YKM_EnableEvent(dllPtr, handle, channel):

	return dllPtr.YKM_EnableEvent(handle, channel);

# <summary>
# 禁用事件
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,1023)</param>
# <returns></returns>
def YKM_DisableEvent(dllPtr, handle, channel):

	return dllPtr.YKM_DisableEvent(handle, channel);

# <summary>
# 获取事件状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="status">返回的状态</param>
# <param name="channel">通道[0,1023)</param>
# <returns></returns>
def YKM_ReadEventStatus(dllPtr, handle, channel, status):

	return dllPtr.YKM_ReadEventStatus(handle, channel, byref(status));

# <summary>
# 获取PCI控制数量
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="num">返回数量</param>
# <returns></returns>
def YKM_GetCardNumPCI(dllPtr, handle, num):

	return dllPtr.YKM_GetCardNumPCI(handle, byref(num));

# <summary>
# 获取PCI控制卡信息
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetCardConfigPCI(dllPtr, handle, card_index, config):

	return dllPtr.YKM_GetCardConfigPCI(handle, card_index, byref(config));

# <summary>
# 获取数字输入的沿次数  Tseies:上升沿计数  XMen:边沿计数  NT:不支持
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">DI序号，本地序号0~63</param>
# <param name="value">计数值</param>
# <returns></returns>
def YKM_ReadUpEdgeNumPCI(dllPtr, handle, card_index, channel, value):

	return dllPtr.YKM_ReadUpEdgeNumPCI(handle, card_index, channel, byref(value));

# <summary>
# 设置数字输入的沿次数 Tseies:上升沿计数  XMen:边沿计数 NT:不支持
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">DI序号，本地序号0~63</param>
# <param name="value">计数值</param>
# <returns></returns>
def YKM_WriteUpEdgeNumPCI(dllPtr, handle, card_index, channel, value):

	return dllPtr.YKM_WriteUpEdgeNumPCI(handle, card_index, channel, value);

# <summary>
# 获取脉冲轴的IO状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="status">IO状态</param>
# <returns></returns>
def YKM_ReadAxisStatusPCI(dllPtr, handle, card_index, channel, status):

	return dllPtr.YKM_ReadAxisStatusPCI(handle, card_index, channel, byref(status));

# <summary>
# 设置脉冲轴的驱动Ready信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetSwitchDrvReadyPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_SetSwitchDrvReadyPCI(handle, card_index, channel, config);

# <summary>
# 获取脉冲轴的驱动Ready信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetSwitchDrvReadyPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_GetSwitchDrvReadyPCI(handle, card_index, channel, byref(config));

# <summary>
# 设置脉冲轴的驱动报警信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetSwitchDrvWarnPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_SetSwitchDrvWarnPCI(handle, card_index, channel, config);

# <summary>
# 获取脉冲轴的驱动报警信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetSwitchDrvWarnPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_GetSwitchDrvWarnPCI(handle, card_index, channel, byref(config));

# <summary>
# 设置脉冲轴的驱动到位信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetSwitchDrvInpPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_SetSwitchDrvInpPCI(handle, card_index, channel, config);

# <summary>
# 获取脉冲轴的驱动到位信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetSwitchDrvInpPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_GetSwitchDrvInpPCI(handle, card_index, channel, byref(config));

# <summary>
# 设置脉冲轴的驱动使能信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetSwitchDrvEnablePCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_SetSwitchDrvEnablePCI(handle, card_index, channel, config);

# <summary>
# 获取脉冲轴的驱动使能信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetSwitchDrvEnablePCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_GetSwitchDrvEnablePCI(handle, card_index, channel, byref(config));

# <summary>
# 设置脉冲轴的驱动复位信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetSwitchDrvResetPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_SetSwitchDrvResetPCI(handle, card_index, channel, config);

# <summary>
# 获取脉冲轴的驱动复位信号
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetSwitchDrvResetPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_GetSwitchDrvResetPCI(handle, card_index, channel, byref(config));

# <summary>
# 参数配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">编码器序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetEncoderConfigPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_SetEncoderConfigPCI(handle, card_index, channel, config);

# <summary>
# 获取配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">编码器序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetEncoderConfigPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_GetEncoderConfigPCI(handle, card_index, channel, byref(config));

# <summary>
# 设置编码器的当前值
# Xmen:只能设0
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">编码器序号</param>
# <param name="value">当前值</param>
# <returns></returns>
def YKM_WriteEncoderValuePCI(dllPtr, handle, card_index, channel, value):

	return dllPtr.YKM_WriteEncoderValuePCI(handle, card_index, channel, value);

# <summary>
# 获取编码器的当前值
# Xmen:只能设0
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">编码器序号</param>
# <param name="value">当前值</param>
# <returns></returns>
def YKM_ReadEncoderValuePCI(dllPtr, handle, card_index, channel, value):

	return dllPtr.YKM_ReadEncoderValuePCI(handle, card_index, channel, byref(value));

# <summary>
# 编码器开始计数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">编码器序号</param>
# <returns></returns>
def YKM_StartEncoderPCI(dllPtr, handle, card_index, channel):

	return dllPtr.YKM_StartEncoderPCI(handle, card_index, channel);

# <summary>
# 编码器停止计数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">编码器序号</param>
# <returns></returns>
def YKM_StopEncoderPCI(dllPtr, handle, card_index, channel):

	return dllPtr.YKM_StopEncoderPCI(handle, card_index, channel);

# <summary>
# 比较器参数配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">比较器序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetCompareConfigPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_SetCompareConfigPCI(handle, card_index, channel, config);

# <summary>
# 获取比较器参数配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">比较器序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetCompareConfigPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_GetCompareConfigPCI(handle, card_index, channel, byref(config));

# <summary>
# 设置比较值
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">比较器序号</param>
# <param name="itemdata">比较配置，内部含有512个缓冲区</param>
# <returns></returns>
def YKM_SetCompareValuePCI(dllPtr, handle, card_index, channel, itemdata):

	return dllPtr.YKM_SetCompareValuePCI(handle, card_index, channel, itemdata);

# <summary>
# 获取比较器状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">比较器序号</param>
# <param name="status">返回值</param>
# <returns></returns>
def YKM_ReadCompareStatusPCI(dllPtr, handle, card_index, channel, status):

	return dllPtr.YKM_ReadCompareStatusPCI(handle, card_index, channel, byref(status));

# <summary>
# 比较器开始
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">比较器序号</param>
# <returns></returns>
def YKM_StartComparePCI(dllPtr, handle, card_index, channel):

	return dllPtr.YKM_StartComparePCI(handle, card_index, channel);

# <summary>
# 停止比较器
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">比较器序号</param>
# <returns></returns>
def YKM_StopComparePCI(dllPtr, handle, card_index, channel):

	return dllPtr.YKM_StopComparePCI(handle, card_index, channel);

# <summary>
# 锁存器参数配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">锁存器序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetCaptureConfigPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_SetCaptureConfigPCI(handle, card_index, channel, config);

# <summary>
# 获取锁存器参数配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">锁存器序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetCaptureConfigPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_GetCaptureConfigPCI(handle, card_index, channel, byref(config));

# <summary>
# 获取锁存器的状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">锁存器序号</param>
# <param name="status">0:无数据 1:有数据</param>
# <returns></returns>
def YKM_ReadCaptureStatusPCI(dllPtr, handle, card_index, channel, status):

	return dllPtr.YKM_ReadCaptureStatusPCI(handle, card_index, channel, byref(status));

# <summary>
# 获取锁存器的当前值
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">锁存器序号</param>
# <param name="value">锁存值</param>
# <returns></returns>
def YKM_ReadCaptureValuePCI(dllPtr, handle, card_index, channel, value):

	return dllPtr.YKM_ReadCaptureValuePCI(handle, card_index, channel, byref(value));

# <summary>
# 锁存器开始
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">锁存器序号</param>
# <returns></returns>
def YKM_StartCapturePCI(dllPtr, handle, card_index, channel):

	return dllPtr.YKM_StartCapturePCI(handle, card_index, channel);

# <summary>
# 停止锁存器
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">锁存器序号</param>
# <returns></returns>
def YKM_StopCapturePCI(dllPtr, handle, card_index, channel):

	return dllPtr.YKM_StopCapturePCI(handle, card_index, channel);

# <summary>
# 启动PWM输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">通道号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_StartPwmPCI(dllPtr, handle, card_index, channel, config):

	return dllPtr.YKM_StartPwmPCI(handle, card_index, channel, config);

# <summary>
# 停止PWM输出
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="card_index">卡序号</param>
# <param name="channel">通道号</param>
# <returns></returns>
def YKM_StopPwmPCI(dllPtr, handle, card_index, channel):

	return dllPtr.YKM_StopPwmPCI(handle, card_index, channel);

# <summary>
# 设置间隙补偿参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetBacklashConfig(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetBacklashConfig(handle, axisIndex, config);

# <summary>
# 获取间隙补偿参数
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetBacklashConfig(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetBacklashConfig(handle, axisIndex, byref(config));

# <summary>
# 启用间隙补偿
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_EnableBacklash(dllPtr, handle, axisIndex):

	return dllPtr.YKM_EnableBacklash(handle, axisIndex);

# <summary>
# 禁用间隙补偿
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_DisableBacklash(dllPtr, handle, axisIndex):

	return dllPtr.YKM_DisableBacklash(handle, axisIndex);

# <summary>
# 设置螺距补偿配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetPitchError1DConfig(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetPitchError1DConfig(handle, axisIndex, config);

# <summary>
# 获取螺距补偿配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetPitchError1DConfig(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetPitchError1DConfig(handle, axisIndex, byref(config));

# <summary>
# 设置螺距补偿数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="pos_data">正向补偿数据</param>
# <param name="neg_data">负向补偿数据</param>
# <param name="size">单方向数据数量</param>
# <returns></returns>
def YKM_SetPitchError1DData(dllPtr, handle, axisIndex, pos_data, neg_data, size):

	return dllPtr.YKM_SetPitchError1DData(handle, axisIndex, pos_data, neg_data, size);

# <summary>
# 获取螺距补偿数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="pos_data">正向补偿数据</param>
# <param name="neg_data">负向补偿数据</param>
# <param name="size">单方向数据数量</param>
# <returns></returns>
def YKM_GetPitchError1DData(dllPtr, handle, axisIndex, pos_data, neg_data, size):

	return dllPtr.YKM_GetPitchError1DData(handle, axisIndex, byref(pos_data), byref(neg_data), size);

# <summary>
# 启用螺距补偿
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_EnablePitchError1D(dllPtr, handle, axisIndex):

	return dllPtr.YKM_EnablePitchError1D(handle, axisIndex);

# <summary>
# 禁用螺距补偿
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_DisablePitchError1D(dllPtr, handle, axisIndex):

	return dllPtr.YKM_DisablePitchError1D(handle, axisIndex);

# <summary>
# 设置二维补偿配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetPitchError2DConfig(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_SetPitchError2DConfig(handle, axisIndex, config);

# <summary>
# 获取二维补偿配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetPitchError2DConfig(dllPtr, handle, axisIndex, config):

	return dllPtr.YKM_GetPitchError2DConfig(handle, axisIndex, byref(config));

# <summary>
# 设置二维补偿数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="data">数据,先X后Y的排列方式</param>
# <param name="size">缓冲区大小</param>
# <returns></returns>
def YKM_SetPitchError2DData(dllPtr, handle, axisIndex, data, size):

	return dllPtr.YKM_SetPitchError2DData(handle, axisIndex, data, size);

# <summary>
# 获取二维补偿数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <param name="data">数据</param>
# <param name="size">缓冲区大小</param>
# <returns></returns>
def YKM_GetPitchError2DData(dllPtr, handle, axisIndex, data, size):

	return dllPtr.YKM_GetPitchError2DData(handle, axisIndex, byref(data), size);

# <summary>
# 启用二维补偿
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_EnablePitchError2D(dllPtr, handle, axisIndex):

	return dllPtr.YKM_EnablePitchError2D(handle, axisIndex);

# <summary>
# 禁用二维补偿
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="axisIndex">轴序号</param>
# <returns></returns>
def YKM_DisablePitchError2D(dllPtr, handle, axisIndex):

	return dllPtr.YKM_DisablePitchError2D(handle, axisIndex);

# <summary>
# 设置圆形区域配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_CIRCLE_ZONE_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetCircleZoneConfig(dllPtr, handle, channel, config):

	return dllPtr.YKM_SetCircleZoneConfig(handle, channel, config);

# <summary>
# 获取圆形区域配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_CIRCLE_ZONE_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetCircleZoneConfig(dllPtr, handle, channel, config):

	return dllPtr.YKM_GetCircleZoneConfig(handle, channel, byref(config));

# <summary>
# 启用圆形区域保护
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_CIRCLE_ZONE_NUM)</param>
# <returns></returns>
def YKM_EnableCircleZone(dllPtr, handle, channel):

	return dllPtr.YKM_EnableCircleZone(handle, channel);

# <summary>
# 禁用用圆形区域保护
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_CIRCLE_ZONE_NUM)</param>
# <returns></returns>
def YKM_DisableCircleZone(dllPtr, handle, channel):

	return dllPtr.YKM_DisableCircleZone(handle, channel);

# <summary>
# 读取圆形区域状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_CIRCLE_ZONE_NUM)</param>
# <param name="status">状态</param>
# <returns></returns>
def YKM_ReadCircleZoneStatus(dllPtr, handle, channel, status):

	return dllPtr.YKM_ReadCircleZoneStatus(handle, channel, byref(status));

# <summary>
# 设置示波器配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="oscIndex">示波器序号[0,YKE_OSC_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_SetOscConfig(dllPtr, handle, oscIndex, config):

	return dllPtr.YKM_SetOscConfig(handle, oscIndex, config);

# <summary>
# 获取示波器配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="oscIndex">示波器序号[0,YKE_OSC_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_GetOscConfig(dllPtr, handle, oscIndex, config):

	return dllPtr.YKM_GetOscConfig(handle, oscIndex, byref(config));

# <summary>
# 设置示波器采集内容
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="oscIndex">示波器序号[0,YKE_OSC_NUM)</param>
# <param name="itemIndex">采集对象序号[0,YKE_OSC_ITEM_NUM)</param>
# <param name="item">采集配置</param>
# <returns></returns>
def YKM_SetOscItem(dllPtr, handle, oscIndex, itemIndex, item):

	return dllPtr.YKM_SetOscItem(handle, oscIndex, itemIndex, item);

# <summary>
# 获取示波器采集内容
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="oscIndex">示波器序号[0,YKE_OSC_NUM</param>
# <param name="itemIndex">采集对象序号[0,YKE_OSC_ITEM_NUM)</param>
# <param name="item">采集配置</param>
# <returns></returns>
def YKM_GetOscItem(dllPtr, handle, oscIndex, itemIndex, item):

	return dllPtr.YKM_GetOscItem(handle, oscIndex, itemIndex, byref(item));

# <summary>
# 清除示波器所有通道配置
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="oscIndex">示波器序号[0,YKE_OSC_NUM)</param>
# <returns></returns>
def YKM_ClearOscItem(dllPtr, handle, oscIndex):

	return dllPtr.YKM_ClearOscItem(handle, oscIndex);

# <summary>
# 读示波器状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="oscIndex">示波器序号[0,YKE_OSC_NUM))</param>
# <param name="status">返回的状态</param>
# <returns></returns>
def YKM_ReadOscStatus(dllPtr, handle, oscIndex, status):

	return dllPtr.YKM_ReadOscStatus(handle, oscIndex, byref(status));

# <summary>
# 读示波器采集数据
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="oscIndex">示波器序号[0,YKE_OSC_NUM)</param>
# <param name="buffer">缓冲区地址</param>
# <param name="size">缓冲区尺寸</param>
# <param name="ret_size">返回的数据个数</param>
# <returns></returns>
def YKM_ReadOscData(dllPtr, handle, oscIndex, buffer, size, ret_size):

	return dllPtr.YKM_ReadOscData(handle, oscIndex, byref(buffer), size, byref(ret_size));

# <summary>
# 启动示波器采集
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="oscIndex">示波器序号[0,YKE_OSC_NUM)</param>
# <returns></returns>
def YKM_StartOsc(dllPtr, handle, oscIndex):

	return dllPtr.YKM_StartOsc(handle, oscIndex);

# <summary>
# 停止示波器采集
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="oscIndex">示波器序号[0,YKE_OSC_NUM)</param>
# <returns></returns>
def YKM_StopOsc(dllPtr, handle, oscIndex):

	return dllPtr.YKM_StopOsc(handle, oscIndex);

# <summary>
# 示波器手动触发
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="oscIndex">示波器序号[0,YKE_OSC_NUM)</param>
# <returns></returns>
def YKM_TrigOsc(dllPtr, handle, oscIndex):

	return dllPtr.YKM_TrigOsc(handle, oscIndex);

# <summary>
# 写轴规划位置，厂家调试用
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="magic"></param>
# <param name="axisIndex">轴序号</param>
# <param name="position">位置</param>
# <returns></returns>
def YKM_WriteCommandPosition(dllPtr, handle, magic, axisIndex, position):

	return dllPtr.YKM_WriteCommandPosition(handle, magic, axisIndex, position);

# <summary>
# 加载控制台类型的.NET应用程序到实时系统中运行
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="exe_name">文件名及路径</param>
# <returns></returns>
def YKM_LoadNTFDotNet(dllPtr, handle, master, exe_name):

	return dllPtr.YKM_LoadNTFDotNet(handle, master, exe_name);

# <summary>
# 检查NTF(C#)程序状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="exe_name">文件名，不包含路径</param>
# <param name="status">返回状态 FALSE=未启动 TRUE=已启动</param>
# <returns></returns>
def YKM_CheckNTFDotNet(dllPtr, handle, master, exe_name, status):

	return dllPtr.YKM_CheckNTFDotNet(handle, master, exe_name, status);

# <summary>
# 加载控制台类型的.rta应用程序到实时系统中运行
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="file_name">路径及文件名</param>
# <param name="para">程序参数</param>
# <returns></returns>
def YKM_LoadRtaApp(dllPtr, handle, master, file_name, para):

	return dllPtr.YKM_LoadRtaApp(handle, master, file_name, para);

# <summary>
# 检查RTA程序状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="rta_name">程序名称</param>
# <param name="status">返回状态 FALSE=未启动 TRUE=已启动</param>
# <returns></returns>
def YKM_CheckRtaApp(dllPtr, handle, master, rta_name, status):

	return dllPtr.YKM_CheckRtaApp(handle, master, rta_name, byref(status));

# <summary>
# 强制关闭RTA程序
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="master">主站选择</param>
# <param name="rta_name">程序名称</param>
# <param name="status">返回状态 FALSE=未关闭 TRUE=已关闭</param>
# <returns></returns>
def YKM_KillRtaApp(dllPtr, handle, master, rta_name, status):

	return dllPtr.YKM_KillRtaApp(handle, master, rta_name, byref(status));

# <summary>
# 设置API缓冲区回调函数(未实现)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="callback">回调函数句柄</param>
# <param name="size"></param>
# <returns></returns>
def YKM_SetApiBufferCallBack(dllPtr, handle, callback, size):

	return dllPtr.YKM_SetApiBufferCallBack(handle, callback, size);

# <summary>
# API缓冲区开始记录(未实现)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号[0,YKE_API_BUFFER_NUM)</param>
# <returns></returns>
def YKM_StartApiBufferRecord(dllPtr, handle, channel):

	return dllPtr.YKM_StartApiBufferRecord(handle, channel);

# <summary>
# API缓冲区停止记录(未实现)
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号通道号[0,YKE_API_BUFFER_NUM)</param>
# <returns></returns>
def YKM_EndApiBufferRecord(dllPtr, handle, channel):

	return dllPtr.YKM_EndApiBufferRecord(handle, channel);

# <summary>
# 设置API缓冲区Mark标记
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道号通道号[0,YKE_API_BUFFER_NUM)</param>
# <param name="mark">用户标记</param>
# <returns></returns>
def YKM_SetApiBufferMark(dllPtr, handle, channel, mark):

	return dllPtr.YKM_SetApiBufferMark(handle, channel, mark);

# <summary>
# 连接Coppelia服务器
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="ipAddress">IP地址</param>
# <param name="port">端口</param>
# <returns></returns>
def YKM_SimConnect(dllPtr, handle, ipAddress, port):

	return dllPtr.YKM_SimConnect(handle, ipAddress, port);

# <summary>
# 设置关节
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="jointIndex">关节序号</param>
# <param name="jointName">关节名称</param>
# <param name="axisIndex">轴序号</param>
# <param name="axisType">轴类型</param>
# <returns></returns>
def YKM_SimJointConfig(dllPtr, handle, jointIndex, jointName, axisIndex, axisType):

	return dllPtr.YKM_SimJointConfig(handle, jointIndex, jointName, axisIndex, axisType);

# <summary>
# 仿真启动
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_SimStart(dllPtr, handle):

	return dllPtr.YKM_SimStart(handle);

# <summary>
# 仿真停止
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_SimStop(dllPtr, handle):

	return dllPtr.YKM_SimStop(handle);

# <summary>
# 断开连接
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <returns></returns>
def YKM_SimDisconnect(dllPtr, handle):

	return dllPtr.YKM_SimDisconnect(handle);

# <summary>
# 等待轴信号(阻塞式)
# 支持API缓冲区
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_WAIT_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_WaitAxis(dllPtr, handle, channel, config):

	return dllPtr.YKM_WaitAxis(handle, channel, config);

# <summary>
# 等待数字输入(阻塞式)
# 支持API缓冲区
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_WAIT_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_WaitDigitalInput(dllPtr, handle, channel, config):

	return dllPtr.YKM_WaitDigitalInput(handle, channel, config);

# <summary>
# 等待事件信号(阻塞式)
# 支持API缓冲区
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_WAIT_NUM)</param>
# <param name="config">配置</param>
# <returns></returns>
def YKM_WaitEvent(dllPtr, handle, channel, config):

	return dllPtr.YKM_WaitEvent(handle, channel, config);

# <summary>
# 延时等待(阻塞式)
# 支持API缓冲区
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_WAIT_NUM)</param>
# <param name="time">延时时间(ms)</param>
# <returns></returns>
def YKM_WaitSleepMs(dllPtr, handle, channel, time):

	return dllPtr.YKM_WaitSleepMs(handle, channel, time);

# <summary>
# 复位等待事件
# 支持API缓冲区
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_WAIT_NUM)</param>
# <returns></returns>
def YKM_WaitReset(dllPtr, handle, channel):

	return dllPtr.YKM_WaitReset(handle, channel);

# <summary>
# 获取等待状态
# </summary>
# <param name="handle">0:共享内存 其他:通讯链接标识</param>
# <param name="channel">通道[0,YKE_WAIT_NUM)</param>
# <param name="status">返回状态</param>
# <returns></returns>
def YKM_ReadWaitStatus(dllPtr, handle, channel, status):

	return dllPtr.YKM_ReadWaitStatus(handle, channel, byref(status));


