# 数据库数据交互说明

面向需要扩展 API、仿真脚本或 UI 数据流的开发者，本文概述 `app/db` 模块的结构以及常见的读写模式。系统默认使用 SQLAlchemy ORM 连接 MySQL，当无法连通远程实例时会自动回退到本地 SQLite，确保仿真环境可用。

---

## 1. 数据库连接与回退策略

| 优先级 | 连接串 | 说明 |
| --- | --- | --- |
| 1 | `mysql+pymysql://mz:123456@192.168.2.32/MzPoliShineDB` | 生产/共享测试库，3s 超时，失败会尝试自动建库 |
| 2 | `mysql+pymysql://root:nercar@127.0.0.1/MzPoliShineDB` | 本机 MySQL，沿用相同 schema |
| 3 | `sqlite:///database/test.db` | 自动创建，保证离线/CI 可运行 |

入口 `app/db/base.py`：

```python
ENGINE, DATABASE_URL = _initialise_engine()
SessionLocal = sessionmaker(bind=ENGINE, future=True, autocommit=False, autoflush=False)
```

运行 `python -m app.server.run_api` 时，日志会打印 `Connected to <label> database: <url>`，用于确认当前使用的实例。

---

## 2. ORM 模型目录

```
app/db/models/
├── tool.py                # 手写的工装/夹具模型（示例/测试）
├── MzPoliShineDB.py       # 主库表（SQLACodeGen 导出，含 dataclass mixin）
└── MzPoliShineDB2.py      # 同步版本，供二次开发对比
```

### 2.1 dataclass + SQLAlchemy

自动生成的模型继承 `MappedAsDataclass`，注意：

- 字段顺序会影响 `__init__` 参数。新增字段时需把带默认值的属性放在“非默认参数”之后，并显式设置 `default=` 或 `init=False`。
- FastAPI 场景通常只传入业务必需字段，其余交由数据库默认值。例如创建工件：

```python
WorkpieceTable(
    w_workpiece_id="WP-DEMO-0001",
    w_workpiece_type="DEMO",
    w_material="Copper",
    w_dimensions="100x100x10",
    w_surface_requirement="Ra <= 0.2",
    w_status=0,
)
```

---

## 3. 会话管理

### 3.1 FastAPI 依赖

`app/server/api/api_data.py` 等模块通过依赖注入管理连接：

```python
from app.db import SessionLocal

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- 每个请求独立 Session，确保线程安全。
- 写操作需 `session.add(...)` → `session.commit()` → `session.refresh(instance)`，否则 UI 获取不到自增主键。
- 异常路径应显式 `rollback()` 或让 FastAPI 自动在未提交时回滚。

### 3.2 后台任务 / 脚本

离线批处理推荐使用 `with SessionLocal() as session:` 上下文或 `try/finally` 关闭，防止连接池耗尽。

---

## 4. 常用交互流程

| 文件 | 作用 | 关键点 |
| --- | --- | --- |
| `app/server/api/api_data.py` | 工件 / 任务 / 记录 CRUD | `_ensure_default_workpiece` 自动插入演示工件；`_serialize_*` 统一响应 |
| `app/server/api/api_image.py` | UI 图像数据 | `/image/test?type=<color|gray|depth|normal>` 读取 `TestData/images`；`/image.png` 透传实时帧 |
| `app/common/tasks.py` | 任务状态枚举 | 与 `TaskTable`、`RecordTable` 字段对应，避免魔法数 |

### 4.1 Demo 工件自检

`_ensure_default_workpiece(session)` 会：

1. 查询最新工件，若存在直接返回。
2. 若不存在，则创建演示工件（仅填必需字段），并 `commit/refresh`。
3. 返回供 UI 显示的 `WorkpieceTable`。

如需更换默认数据，可修改该函数或在启动脚本中预先写入。

### 4.2 图像接口与 UI 绑定

- UI (`CoreState.qml`) 通过 `Api.Urls.api("image/test") + "?type=" + token` 拉取测试图像，`token` 由前端映射自中文标签。
- 后端 `/image/test` 支持中英文类型别名，并按扩展名设置 `Content-Type`。
- 生产环境可移除别名映射，直接使用实时 `/image.png`。

---

## 5. 数据种子与测试

| 场景 | 步骤 |
| --- | --- |
| 初始化所有表 | `python -m app.db.init_db`（或在 API 启动时自动调用）|
| 注入模拟数据 | `python scripts/smoke_api.py` 会触发常用 API 并检查数据库连接 |
| 单元测试 | `python -m pytest`；必要时通过 `monkeypatch(app.db.base.PRIMARY_DB_URL, "sqlite:///..." )` 指向隔离文件 |

建议复用 `TestData/` 下的图像/遥测样例到数据库相关用例，以保持 UI 与算法一致。

---

## 6. 开发注意事项

1. **勿修改 `configs/` 模板中的 DSN**；本地实验请在 `.env` 或 shell 变量中覆盖 `COPPER_APP_HOST` 等参数。
2. **提交前清理 `runs/` 目录**，该目录可能包含 SQLite 或导出文件。
3. 新增模型字段时同步更新：
   - `app/db/models/MzPoliShineDB.py`（如由代码生成，可重新导出）
   - 相关 `tests/` 与 `docs/ui_data_contracts.md`
4. 长事务场景务必使用 `session.begin()` 并妥善处理异常，避免在 FastAPI handler 中持有 session 超过请求生命周期。

如需补充特定表的字段说明或 ER 图，建议将 UML/ER 产物放入 `docs/export/` 并在此文档附链接。
