# 电子衣柜 1.0

面向闲鱼多账号服装上架场景的“中央厨房 + 隔离执行”系统。

- **中央厨房（Windows 桌面端）**：素材管理、AI 文案生成、水印、任务分发、报告汇总。
- **安卓隔离执行器**：三台独立设备读取任务包，通过无障碍 + Root 模拟人工操作。
- **运维保障**：任务拆分、风控策略、日志留存、备份与回溯。

## 阶段规划

| 阶段 | 目标 | 交付 | 状态 |
| --- | --- | --- | --- |
| Stage 0 | 基础设施 | 仓库结构、依赖管理、质量工具 | ? 完成 |
| Stage 1 | 中央厨房 | 素材解析、AI 文案、水印、任务打包 | ? 完成 |
| Stage 2 | 桌面应用 | PySide6 UI、同步控制、日志可视化 | ? 暂缓 |
| Stage 3 | 图片标注 | GUI 标注器、快捷键、校验提醒 | ? |
| Stage 4 | 安卓执行器 | 无障碍执行、Root 文件操作、失败回写 | ? |
| Stage 5 | 联调 | 三设备同步、异常回放、日志归档 | ? |
| Stage 6 | 文档交付 | 操作手册、维护指南、打包脚本 | ? |
| Stage 7 | 验收 | 测试矩阵、风控复核、性能评估 | ? |
| Stage 8 | 运维交接 | 版本规范、备份策略、模型更新流程 | ? |

## 运行环境

- Windows 10/11（管理员权限，建议 RTX 2070 / 32GB 内存）
- Python 3.11（推荐 uv 统一管理，兼容 poetry）
- Ollama 本地模型（文案改写、敏感词过滤）
- Android 设备：小米 8 ×3，Android 10，已 Root，开启无障碍
- Git + PowerShell 7 / Windows Terminal

## 目录概览

`
电子衣柜1.0/
├── app/              # 桌面端、安卓端子工程
├── core/             # 中央厨房核心逻辑
├── docs/             # 架构、流程、接口、SOP 等文档
├── scripts/          # 辅助脚本、自动化工具
├── tests/            # 单元 / 集成 / 端到端测试
├── tools/            # 第三方工具、临时依赖
└── archives/         # bundle 等快照备份
`

## 关键文档

- [中央厨房接口说明](docs/interfaces/central_kitchen.md)
- [整体工作流](docs/workflow.md)
- [任务包 / 报告字段规范](docs/file_conventions.md)
- [阶段规划](docs/stages.md)
- [工作区看板与日志](docs/workspace/)

## 快速体验

1. 准备素材：在 data/demo_input/Input_Raw/ 放置示例款式。
2. 运行中央厨房：
   `ash
   PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
   python -m scripts.central_kitchen \
     --input data/demo_input/Input_Raw \
     --output data/demo_output \
     --devices device1,device2,device3 \
     --price 299 --category tee --watermark 电子衣柜
   `
3. 查看输出：Output_Batch_Phone_* 目录与 eports/delivery_report.json。
4. 执行测试：PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest。

## 维护记录

- 最新 bundle：rchives/stage1c-final.bundle
- 测试日志目录：eports/testlogs/
- 日常工作流与待办：docs/workspace/board.md、workspace1.md

若需重新启动后续阶段，请先阅读接口说明和工作流文档，确保与现有中央厨房输出保持一致。
