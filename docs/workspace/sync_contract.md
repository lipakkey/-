# 桌面端 ↔ 安卓执行器 同步协议（更新版）

## 设备配置
- 3 台小米 8（Android 10，6+64 GB，Bootloader 解锁 + Root）。
- `config/device_map.yaml` 维护 `device_id、adb_serial、remote_root` 映射；示例：
  ```yaml
  devices:
    - device_id: phone1
      adb_serial: XYZ123
      remote_root: /sdcard/XianyuTasks
  ```
- 桌面端 SyncService 根据该文件推送/拉取，并在 `sync/status.json` 记录最近一次操作。

## 推送任务（Desktop → Phone）
1. 选择 `Output_Batch_Phone_n/` 目录。
2. `adb shell mkdir -p /sdcard/XianyuTasks/Todo/`。
3. `adb push Output_Batch_Phone_n /sdcard/XianyuTasks/Todo/`。
4. 写入 `sync/status.json`：
   ```json
   {
     "devices": {
       "phone1": {
         "last_push": "2025-11-04T17:00:00",
         "last_batch": "Output_Batch_Phone_1",
         "last_manifest": { ...batch_manifest.json 内容... }
       }
     }
   }
   ```
5. 同步完成后在 UI 展示批次、任务数、生成时间。

### batch_manifest.json 要点
- 每条 entry 包含 `paths/media/pricing/flags`，详见 `docs/interfaces/examples.md`。
- 桌面端推送前可调用 `scripts/validate_manifest.py` 检查必填字段。

## 安卓执行 & 回传
- 执行器读取 `/sdcard/XianyuTasks/Todo/Output_Batch_Phone_n`，并在 `/Done/<style_code>/` 中写入：
  - `result.json`：含 `style_code、batch_id、device_id、status、error_code、retry_count、duration_ms、screenshots、source_paths、pricing、media`；结构与 Stage1 manifest 对齐。
  - `session.log`：时间戳 + 状态流转日志。
  - 截图：`success.png` / `fail_<retry>.png`。
- 发布成功后把整个款目录移动至 `/Done/`，以便桌面端统一拉取。

## 拉取任务（Phone → Desktop）
1. `adb pull /sdcard/XianyuTasks/Done/ <workspace>/sync/device_<id>/YYYYMMDD_HHMMSS/`。
2. 遍历 `result.json`：
   - 汇总 `status=failed` 的 `error_code`、`sensitive_hits`；
   - 更新 `reports/delivery_report.json` 或附加 `reports/logs/...`。
3. 记录状态：
   ```json
   {
     "devices": {
       "phone1": {
         "last_pull": "2025-11-04T17:30:00",
         "last_pull_path": "sync/device_phone1/20251104_173000",
         "last_error": null
       }
     }
   }
   ```
4. 若需要增量获取，可在 `sync/status.json` 保存 `pulled_batches`；安卓端也可在完成后删除 `/Done/` 下的款目录，避免重复。

## 错误与告警
- ADB 命令失败：写入 `last_error`，并在桌面端 UI 弹出提示。
- Manifest 缺字段：`scripts/validate_manifest.py` 提前拦截；若到达手机，则安卓 ResultWriter 在 `error_code` 中体现 `MANIFEST_INVALID`。
- Root/权限缺失：安卓在 `EnvDiagnostics` 中返回 `isHealthy=false`，并写入 `session.log`。

## 日志与截图归档
- 所有拉取的内容保存在 `sync/device_<id>/YYYYMMDD_HHMMSS/`，禁止覆盖。
- 若目录大，可按月移至 `archives/`。
- `LogSink` 输出 `session.log`（INFO/WARN/ERROR），桌面端可聚合分析。

## 未决事项
- 是否需要回传闲鱼发布后的 URL？（预留 `result.json -> flags.published_url`）。
- 桌面端是否自动合并 `result.json` → `delivery_report.json`，或仅提示人工导入？
- 清理策略：推送/拉取成功后是否自动删除 `/Todo/`、`/Done/` 对应款目录。
