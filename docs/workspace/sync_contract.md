# 同步接口约定（桌面端 ↔ 安卓端）

## 设备信息
- 设备：小米 8（6+64 GB）×3，Android 10，Bootloader 解锁 + Root。
- ADB：允许自动识别；建议维护 `config/device_map.yaml`（device_id、adb_serial、目标路径）。
- 参考：`docs/workspace/attachments/device_summary.md`。

## 任务推送（桌面 → 手机）
1. 桌面端选择批次目录 `Output_Batch_Phone_n/`。
2. 通过 USB/MTP 或 `adb push` 拷贝至 `/sdcard/XianyuTasks/Todo/`。
3. 推送完成后记录：批次、设备、时间戳、文件数；写入 `sync/status.json`。

## 日志拉取（手机 → 桌面）
- 安卓执行器输出：
  - `/sdcard/XianyuTasks/Done/<style_code>/result.json`
  - `/sdcard/XianyuTasks/Done/<style_code>/session.log`
- 桌面端运行 `Pull Logs`：
  - `adb pull /sdcard/XianyuTasks/Done/ <workspace>/sync/device_<id>/YYYYMMDD/`
  - 读取 `result.json` 字段（建议：`style_code`, `status`, `error_code`, `retry_count`, `screenshot`）。
  - 更新 `sync/status.json` 的 `last_pull`、`last_error`。

## 状态文件 `sync/status.json`
```json
{
  "devices": {
    "device1": {
      "last_push": "2025-11-04T17:00:00",
      "last_pull": "2025-11-04T17:30:00",
      "last_error": null
    }
  }
}
```

## 待确认
- 安卓端 `result.json` 实际字段（W3 已在 README 中记录，仍需样例）。
- 是否需要桌面端执行 “合并 result.json → delivery_report.json” 功能。
- 日志保留策略：`sync/device_id/YYYYMMDD/` 是否按天清理。
