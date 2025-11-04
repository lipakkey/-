# Stage 2 下一步拆解

## 1. 设备扫描功能
- [ ] 编写 services/device_scanner.py：封装 db devices -l，返回序列号、型号、状态。
- [ ] 在 SyncController 里增加“扫描设备”入口，更新 state。
- [ ] 测试：	ests/desktop/test_device_scanner.py 使用伪 ADB 输出验证解析逻辑。

## 2. MainWindow 布局与基础交互
- [ ] 使用 QSplitter 将左侧导航与右侧 Tab 区分开。
- [ ] 在状态栏展示当前设备、上次操作时间、运行状态。
- [ ] 左侧树控件绑定批次列表，选中条目时触发 Pipeline 面板刷新。

## 3. Sync 面板完善
- [ ] 将 SyncService push/pull 操作绑定到 UI 按钮，显示执行进度。
- [ ] 设计日志表格列（时间、设备、操作、结果、详情）。
- [ ] 提供日志过滤（成功/失败）和导出按钮。

## 4. Pipeline 面板
- [ ] 整合 Stage1 central_kitchen.py 调用，执行时锁定按钮并输出日志。
- [ ] 显示当前任务进度条（总款数/已完成数）。
- [ ] 处理异常：捕获 subprocess 错误，弹窗并记录日志。

## 5. 报告视图（Stage2.2）
- [ ] 解析 delivery_report.json 并展示 Summary（表格 + 条形图）。
- [ ] 敏感词分布列表，点击可查看涉及的款号。
- [ ] 导出 CSV/复制到剪贴板等辅助功能。

## 6. 测试与打包
- [ ] 新增 	ests/desktop/test_main_window.py（使用 QtBot）覆盖基础交互。
- [ ] 在 README 中记录 PySide6 环境配置与常见问题。
- [ ] 评估 PyInstaller 打包策略，列出依赖清单。

