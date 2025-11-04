# 桌面端 UI Style Guide（v0.1）

## 色彩体系
- 主色（Primary）：#1E88E5 ─ 应用于按钮、重点图标。
- 辅色（Accent）：#FFB300 ─ 用于警告/高亮。
- 成功（Success）：#43A047；失败（Error）：#E53935；信息（Info）：#546E7A。
- 背景：浅灰 #F5F5F5；卡片/面板：#FFFFFF；分隔线：#E0E0E0。

## 字体
- 标题：Source Han Sans SC SemiBold，字号 16–20。
- 正文：Source Han Sans SC Regular，字号 12–14。
- 等宽：JetBrains Mono 或 Consolas，用于日志/命令输出。

## 组件规范
- 按钮：高度 32px，圆角 6px；主按钮使用主色背景，禁用态改为 #B0BEC5。
- 表格：表头背景 #ECEFF1，行 hover 使用 #E3F2FD，支持多选。
- Tag：用于显示状态（在线、离线、警告）；颜色匹配状态色。
- Toast/通知：右上角弹出，默认 3s 自动关闭。

## 图标
- 使用 Fluent UI System Icons，保持线性风格。
- 常用图标：刷新（ArrowClockwise24Regular）、上传（CloudArrowUp24Regular）、下载（CloudArrowDown24Regular）、日志（ClipboardTextLtr24Regular）。

## 间距
- 页面统一使用 8px spacing 系统：组件间距 8/16/24；Panel 内部边距 24。
- 列表左对齐，按钮组右对齐。

## 暗色模式（预留）
- 背景切换为 #1E1E1E，文本 #FFFFFF，主色调保持相同但亮度降低 20%。

## 资源管理
- 统一在 pp/desktop/ui/assets/ 存放图标（SVG），在 QSS 中引用。
- 颜色、字体变量在 style.py 维护，提供 StylePalette 数据类供各组件调用。

