# 备份策略（Stage 0 草稿）

## 目标
- 保证任意阶段代码丢失后可在 30 分钟内恢复。
- 对桌面端、安卓端、模型数据分别制定快照策略。

## 建议流程
1. **Git 远程**：主干 `main`，功能分支 `feature/*`；每日结束前推送。
2. **本地快照**：执行 `git bundle create archives/<date>-stage0.bundle main`；保存在 `archives/` 并同步到移动硬盘。
3. **自动压缩**：使用 PowerShell 计划任务，每日 02:00 将仓库压缩到 `archives/daily/<date>.zip`。
4. **日志归档**：桌面端运行结束后，将 `reports/`、`logs/` 复制到 `archives/logs/<date>/`。
5. **安卓设备**：执行器在任务完成后，把 `/sdcard/XianyuTasks/Done/` 同步到 PC 的 `sync/device_<id>/<date>/`。
6. **模型缓存**：Ollama 模型体积大，记录下载版本，若有更新，保存旧版本哈希，避免回退困难。

## 恢复流程
- 若 Git 数据丢失：使用最新 `.bundle` 或远程仓库重新克隆。
- 若日志缺失：从 `archives/logs/` 取回，并重新导入到桌面端。
- 若安卓任务包损坏：重新从中央厨房生成，并对照 `Manifest.json` 校验数量。

## TODO
- 完善自动化脚本（`scripts/backup.ps1`）。
- 定义备份检查清单（每周人工点验一次）。
