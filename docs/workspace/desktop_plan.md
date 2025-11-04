# PySide6 桌面端初始化方案

## 目标
- 快速搭建可运行的基础框架，为 Stage 2 迭代提供结构化支持。
- 保持与中央厨房输出的数据结构一致，便于后续联调。

## 模块划分
1. `app/desktop/core/`
   - `config_loader.py`：读取桌面端配置（设备映射、路径、延迟参数）。
   - `report_loader.py`：解析 `reports/delivery_report.json` 与同步记录。
   - `task_sync.py`：USB/ADB 同步占位（后续与工作区1协作实现）。
2. `app/desktop/ui/`
   - `main_window.py`：主窗口（标签页：任务概览、日志同步、配置中心）。
   - `widgets/`：复用组件（设备列表、任务详情、日志查看器）。
   - `resources/`：后续放置 qss/icon。
3. `app/desktop/state/`
   - 轻量状态管理（dataclass + signals），记录当前选中的批次、设备状态。
4. `app/desktop/services/`
   - 与中央厨房/安卓端交互的服务对象（未来可加载 CLI/ADB 命令）。

## 初始化步骤（Stage 2 Sprint 1）
1. 创建 PySide6 应用入口：`python -m app.desktop.main`。
2. 引入 `QtForPython`（PySide6）依赖，更新 `pyproject.toml` optional group `desktop`。
3. 落地主窗口框架：
   - 左侧：批次列表（读取 `Output_Batch_Phone_*`）。
   - 右侧：任务详情（展示 `entries` 字段）。
   - 底部：状态栏（当前设备、同步状态）。
4. 实现报告加载：
   - 使用 `docs/workspace/report_sync.md` 中定义的字段。
   - 缓存最近一次读取时间，方便刷新。
5. 日志与配置占位：
   - 在 `state/` 中预留 `sync_status`、`last_report_path`。
   - `config_loader.py` 读取 `config/desktop.yaml`（待创建）。

## 后续迭代关注点
- 集成 `scripts/central_kitchen.py` 调用，提供“一键生成+同步”按钮。
- 引入任务包差异对比（展示 entries 中文案/图像路径差异）。
- 打包：使用 `PyInstaller`，提供 `scripts/build_desktop.bat`。

## 协同需求
- 需要工作区1提供设备映射样例（`device_map.yaml`）。
- 需要工作区3确认日志回传目录规范（`sync/device_<id>/YYYYMMDD/`）。
