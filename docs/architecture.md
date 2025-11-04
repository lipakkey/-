# 架构总览

## 模块层级
- **中央厨房（桌面端核心）**：素材扫描、文案生成、水印、任务分配、报告。
- **安卓隔离执行器**：读取批次任务包，通过无障碍自动发布。
- **日志与运维层**：任务回传、交付报告、备份归档。

## Stage 1 数据流
1. `InputScanner` 遍历 `Input_Raw/<style>/`，读取 `desc.txt`、图片、`meta.*`。
2. `CopywritingGenerator`：模板 + Ollama → 敏感词过滤 → 多版本文案。
3. `WatermarkProcessor`：统一文字水印；输出到 `staging/<style>/images/`。
4. `StyleProcessor`：写出标题/描述文本、元数据 `manifest.json`。
5. `TaskPartitioner`：按设备均分任务 → `Output_Batch_Phone_<n>/<style>/`。
6. `ReportBuilder`：生成 `reports/delivery_report.json`（成功数、失败列表、敏感词命中、设备任务量）。

## 接口约定
- 单款 manifest：`context`、`sensitive_hits`、`price`、`macro_delay`。
- 批次 manifest：`device_id`、`entries`（相对路径）；
  安卓端仅需读取批次内 `text/` 与 `images/`。
- 报告：`summary.per_device`、`summary.sensitive_hits` 与 `entries` 列表。

## 后续更新点
- Stage 2：补充桌面端 UI/同步服务的组件交互图。
- Stage 4：补充执行器状态机、result.json 字段定义。
- 联调完成后补全日志、回传、备份流程的全链路图。
