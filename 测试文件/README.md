# 测试文件

本目录用于存放项目测试用的示例数据与说明，便于快速验证脚本与流程。

结构
- `测试文件/<流水号>/...`：每个测试组使用一个子文件夹，名称为“流水号”。
- `sample_logs/`：包含简化版的 MFC Demo 日志，用于测试路径导出脚本。

用法
- 准备演示图片（可选）：`python scripts/setup_test_images.py`（会在 `测试文件/demo-0001/` 放入示例图）
- 导出路径点（JSON/CSV）：
  - `bin/export_paths.bat --input "测试文件/sample_logs/log_small.txt" --name sample_from_small`
- 通过 API 加载并在 UI 显示（集成运行 `bin/run_app.bat` 后）：
  - 创建测试组：`POST /test/group/create {"serial":"demo-0002"}`
  - 向组内添加示例图：`POST /test/group/demo-0002/add_image?name=1_IMG_Texture_8Bit.png`
  - 加载显示：`POST /test/load_image?name=demo-0002/1_IMG_Texture_8Bit.png`
