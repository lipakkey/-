# Workspace4 日志（Stage 4 运行期与回传）

## Stage 4 目标
- 打通手机端执行日志回传 + PC 汇总流程（manifest/result.json/session.log）。
- 衔接 Stage 2 同步、Stage 3 selector/state machine，形成完整闭环。

## 当前成果
- [x] 初始化 Workspace4，确认职责分工。
- [x] 补充 TaskRunner / ActionScheduler / TaskStateMachine / TaskController 等占位类。
- [x] ResultWriter、TaskRepository、Logger、EnvDiagnostics 初始实现。
- [x] AutomationAccessibilityService 占位代码与依赖梳理。
- [ ] Root 文件移动与截图抓取流程（mv/cp/chmod 等命令包装）。
- [ ] result.json / session.log 字段定义与文档说明。

## 待办摘要
1. TaskRunner 内加入状态机错误分支与重试策略。
2. 丰富 RandomDelays / ActionScheduler 参数来源，支持配置化。
3. 编写 LogSink + ResultWriter 输出规范，并与 Stage 2 报告对齐。
4. 预研 Root shell 调用封装（异常处理、安全策略）。
5. 与 Workspace3 协同，确认数据接口对接方式。

## 风险提示
- Accessibility 关键节点仍需真机录制印证。
- Root 权限在 MIUI 上的稳定性需长期观察。
- manifest/result.json 字段若调整，需同步更新桌面端解析逻辑。
