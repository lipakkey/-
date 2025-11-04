# PySide6 依赖评估（草案）

## 推荐版本
- PySide6 >= 6.7.0（Python 3.11 兼容）。
- 可选依赖：
  - `watchdog`（监控任务目录）
  - `pytest-qt`（UI 测试）

## 安装建议
```
uv add --group desktop PySide6>=6.7
uv add --group dev pytest-qt>=4.4
```

## 构建环境
- Windows 10/11 + Visual C++ Redistributable。
- 打包建议 `PyInstaller>=6.8`。

## 待确认事项
- 是否立即将 PySide6 添加到仓库依赖，或待桌面端代码完成后再合入。
- Watchdog 与 UI 事件循环的并发管理策略。
- 是否需要引入目录监听/ADB 封装第三方库。
