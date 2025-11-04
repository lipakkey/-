# 素材与任务包目录约定

## 输入目录 `Input_Raw/`
- 结构：`Input_Raw/<style_code>/`
- 必须文件：
  - `desc.txt`：原始文案，UTF-8。
  - `meta.yaml`（可选）：价格、尺码、颜色、库存等补充信息。
- 图片命名：
  - 主图默认 `main_*.jpg`；
  - 颜色规格图 `color_<颜色>_*.jpg`；
  - 如无命名，中央厨房将按 `meta.yaml` 中的映射提示人工补全。

## 任务包输出 `Output_Batch_Phone_<n>/`
- 每台设备一个批次目录，例如：
  - `Output_Batch_Phone_1/`
  - `Output_Batch_Phone_2/`
  - `Output_Batch_Phone_3/`
- 单个商品目录：`<style_code>/`
  - `manifest.json`：文案、价格、规格、延迟配置。
  - `images/`：水印后的主图与规格图（命名保持与输入一致）。
  - `text/`：`title.txt`、`description.txt`，多文案版本以 `description_alt<n>.txt` 存储。
- 批次根目录包含：
  - `batch_manifest.json`：任务列表、创建时间、分配设备 ID。
  - `README.txt`：操作提示。

## 日志同步 `sync/`
- 安卓执行后将 `result.json`、`session.log` 回传至 `sync/device_<serial>/YYYYMMDD/`。
- 桌面端汇总到 `reports/`，生成 `delivery_report.json`。

> 本文档会在 Stage 3 图片标注与 Stage 5 联调后补充更多约束。
