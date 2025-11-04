# 工作流概览

## Stage 1：中央厨房
1. **素材准备**：`Input_Raw/<style>/` 下存放 `desc.txt`、图片、可选 `meta.yaml`。
2. **文案生成**：`CopywritingGenerator` 使用模板 + 模型生成多版本描述，敏感词/品牌别名替换。
3. **图片水印**：`WatermarkProcessor` 批量为主图、规格图添加“电子衣柜”文字水印。
4. **单款打包**：`StyleProcessor` 生成 `text/`、`images/`、`manifest.json`，记录敏感词命中。
5. **任务分配**：`TaskPartitioner` 将任务均分到 `Output_Batch_Phone_<n>/`。
6. **报告汇总**：`ReportBuilder` 输出 `reports/delivery_report.json`，包含成功数、失败列表、敏感词命中、每设备任务量。

## Stage 2（规划）
- 桌面端应用负责素材管理、配置调整、运行状态展示、日志同步。
- 同步模块读取 `Output_Batch_Phone_<n>/`，对接 USB/ADB 复制，并监控安卓端回传日志。

## Stage 4（规划）
- 安卓执行器读取批次任务，按 manifest 步骤完成发布；`result.json` 回传桌面端。
- 状态机包含：环境检查 → 任务循环 → 失败重试 → 日志写入/回传。

> 随阶段推进，将在此文档追加时序图、异常流程及回传链路。
