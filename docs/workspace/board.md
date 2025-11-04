# 多工作区任务看板

## 工作区 1（中央厨房核心 / Stage 1-C）
- [x] 修复报告模块并生成测试报告
- [x] 完成 `scripts/central_kitchen.py` 自检
- [x] 运行 `pytest` 并保存日志
- [x] 更新 `docs/architecture.md`、`docs/workflow.md`
- [ ] 打包 Stage 1-C 提交（commit + push + bundle），在 `workspace1.md` 记录

## 工作区 2（桌面端 UI/同步 / Stage 2 预研）
- [ ] 梳理桌面端界面草图，写入 `docs/ui/desktop_wireframe.md`
- [ ] 列出同步模块需求，记录在 `workspace2.md`
- [ ] 评估 PySide6 依赖，与工作区1确认后添加
- [ ] 规划 `app/desktop/` 目录与模块职责
- [ ] 记录桌面端测试计划（`tests/desktop/README.md`）

## 工作区 3（安卓执行器 / Stage 4 预研）
- [ ] 整理三台设备信息，写入 `workspace3.md`
- [ ] 调研无障碍 Selector JSON，产出 `docs/android/selectors_plan.md`
- [ ] 列出必须权限、服务声明，更新 `app/android/README.md`
- [ ] 设计执行状态机草案，存放 `docs/android/state_machine.md`
- [ ] 约定 result.json & 日志字段

> 完成任务后请在看板勾选，并在 `workspaceX.md` 记录日期、操作及协同事项。
