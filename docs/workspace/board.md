# 工作区任务看板

## 工作区 1（中央厨房流水线）
- [x] 文档：接口说明、流程图、README 更新
- [x] 示例脚本：scripts/run_demo.py + 指南
- [x] 示例数据深化：补充 demo_output 结构、敏感词校验记录
- [x] 测试增强：PriceConfig / DelayConfig / TaskPartitioner 等
- [ ] 脚本工具：manifest 校验、批量复制、报告摘要脚本（已初版 validate_manifest/report_summary，待补充说明）

## 工作区 2（桌面端 UI/同步）
- [ ] 完成桌面线框稿，写入 docs/ui/desktop_wireframe.md
- [x] 梳理同步模块需求，更新 workspace2.md
- [ ] 确认 PySide6 组件栈与 Stage1 数据接口
- [x] 规划 app/desktop/ 目录结构与模块职责
- [x] 实现 SyncService + 单测 tests/desktop/test_sync_service.py
- [ ] 在 tests/desktop/README.md 记录测试规划

## 工作区 3（安卓执行器）
- [ ] 收集三台设备信息，写入 workspace3.md（待补序列号）
- [x] 设计 Selector 策略，编写 docs/android/selectors_plan.md
- [x] 列出权限/依赖，更新 app/android/README.md
- [x] 设计执行状态机，写入 docs/android/state_machine.md
- [x] 对齐 Stage1 manifest/result 结构（TaskRepository / ResultWriter / TaskRunner）
- [ ] 细化 Accessibility 操作封装，完成图片选择 / 规格绑定
- [ ] result.json 字段与日志格式说明补登到 workspace3.md

> 更新看板后需同步各自 workspaceX.md，并通过即时沟通提醒。
