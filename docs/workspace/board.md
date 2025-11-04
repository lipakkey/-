# 多工作区任务看板

## 工作区1（中央厨房核心 / Stage 1-C）

- [ ] 修复报表模块并确认可导入
- [ ] 自检 `scripts/central_kitchen.py`
- [ ] 运行 `pytest` 并保存日志
- [ ] 更新 `docs/architecture.md`、`docs/workflow.md`
- [ ] Stage 1-C 收尾：commit + push + bundle，并在 `workspace1.md` 记录

## 工作区2（桌面端 UI/同步 / Stage 2 预研）

- [ ] 梳理桌面端界面草图，写入 `docs/ui/desktop_wireframe.md`
- [ ] 梳理同步模块需求，记录在 `workspace2.md`
- [ ] 确认 PySide6 依赖后合入（待工作区1确认）
- [ ] 规划 `app/desktop/` 目录结构和模块职责
- [ ] 在 `tests/desktop/README.md` 记录桌面端测试计划

## 工作区3（安卓执行器 / Stage 4 预研）

- [ ] 整理三台设备信息，写入 `workspace3.md`
- [ ] 调研无障碍控件与 selector，产出 `docs/android/selectors_plan.md`
- [ ] 列出权限/服务声明，更新 `app/android/README.md`
- [ ] 设计执行状态机草案（文本或 Mermaid），放在 `docs/android/state_machine.md`
- [ ] 初步定义 result.json 与日志字段，写入 `workspace3.md`

> 完成任务后请在对应 `workspaceX.md` 写明日期、操作与待协同事项。
