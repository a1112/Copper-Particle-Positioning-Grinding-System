# ProCon DLL 封装 / ProCon DLL Wrapper

该目录提供一个基于 `ctypes` 的 ProCon (YKCat2) DLL 封装，覆盖 GantryMilling 中使用的轴控、群组插补、数字 IO、复位/报警清除以及气缸控制等常用能力，便于在 Python 侧进行调试或搭建 Demo。

## 目录结构
- `controller.py`：核心封装，提供 `ProConController` 类。
- `__init__.py`：导出 `ProConController`、`DigitalPoint`、`ProConDllError`。
- `dll/`：示例依赖的运行时 DLL（需与现场版本保持一致）。
- `YKCat2.py`：官方生成的 Python 头文件（包含所有结构体 / 枚举）。
- `MoveAbsolute.py`：原始 DLL 调用示例。
- `example_usage.py`：快速体验封装的基础示例。
- `example/axis_demo.py`：演示位置 / 速度 / 扭矩 / 状态读取与绝对定位。
- `example/device_demo.py`：命令行工具，覆盖轴运动、速度模式、气缸控制、温度（PDO）读取等场景。

## 快速开始
1. 确认 `dll/` 目录中的 `YKCat2.dll`、`NoSys.dll` 等文件与控制器版本一致，必要时从正式安装目录复制。
2. 在 64 位 Windows + Python 环境执行：
   ```powershell
   cd F:\Copper-Particle-Positioning-Grinding-System\demo\procon_python
   python -m demo.procon_python.example_usage --axis 0 --distance 100
   ```
   - `--ip` / `--port` 可选，默认使用共享内存模式（与 GantryMilling 一致）。
   - 运行前请确认控制器、急停、总线状态均已准备就绪。

## 示例命令
- 轴状态采集：`python -m demo.procon_python.example.device_demo status --axis 0`
- 温度读取（需提供现场 PDO 索引）：`python -m demo.procon_python.example.device_demo status --axis 0 --temperature 0x2324:1 --temperature-size 2`
- 绝对定位：`python -m demo.procon_python.example.device_demo move --axis 0 --position 120 --velocity 80`
- 恒速运行：`python -m demo.procon_python.example.device_demo velocity --axis 0 --velocity 50`
- 气缸动作：`python -m demo.procon_python.example.device_demo cylinder-set --output 0:3 --state 1 --feedback 0:4`
- 气缸状态：`python -m demo.procon_python.example.device_demo cylinder-get --output 0:3 --feedback 0:4`

## 核心能力
`ProConController` 封装了常见的底层接口：
- **系统管理**：`load()/unload()`、`wait_bus_ready()`、`warm_reset()`、`clear_bus_warn()`、`clear_system_warn()` 等。
- **轴控操作**：`power_on()`、`power_off()`、`move_absolute()`、`move_relative()`、`move_velocity()` / `move_velocity_ex()`、`start_home()`、`stop_axis()`、`set_axis_soft_limit()`、`set_command_equiv()`、`read_axis_position()`、`read_axis_velocity()`、`read_axis_torque()`、`clear_axis_error()` 等。
- **群组 / 插补**：`init_group()`、`set_group_profile()`、`move_linear_absolute()`、`start_group()`、`stop_group()`、`deinit_group()`、`read_group_status()`、`follow_ug()`。
- **IO 与气缸**：`write_digital_output()`、`read_digital_input()`、`wait_digital_input()`、`operate_cylinder()`、`write_pdo_object()`、`read_pdo_object()`。

所有方法调用 DLL 后都会检查返回码，失败时抛出 `ProConDllError`，错误信息包含原始 `YKE_RESULT_CODE`。

## 集成建议
- GantryMilling 的轴配置（速度、加速度、齿轮比等）可直接传入封装方法，内部默认使用 S7 曲线构造 `YKS_AxisProfileMotion`。
- 气缸与其它 IO 可通过 `DigitalPoint(slave_id, index)` 表示，方便将现有设备映射表迁移到 Python 脚本中。
- 如需拓展更多底层接口，可参考 `controller.py` 内 `_check_rc`、`_create_motion_profile`、`read_pdo_object()` 的实现按需新增。

## 注意事项
- 运行脚本前务必确认现场安全，运动命令不会自动做限位 / 防撞检测。
- TCP 模式需要提供实际控制器 IP，并确保授权、INtime / 服务进程已启动。
- 若 `ProConDllError` 抛出错误码，可结合 `other/ProCon/comment/ErrorCodeChs.xml` 查询含义。
- 温度读取需根据驱动实际 PDO 对象配置索引，示例命令仅为占位参考。

更多底层接口说明请参阅 `other/ProCon/doc/180API`。
