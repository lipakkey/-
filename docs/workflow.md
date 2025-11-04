# 工作流概览

## Stage 1：中央厨房
1. **素材准备**：Input_Raw/<style>/ 放置 desc.txt、图片和可选 meta.yaml。
2. **文案生成**：CopywritingGenerator 根据模板调用本地模型，输出多版本文案并执行敏感词替换。
3. **图片水印**：WatermarkProcessor 为主图、规格图批量添加“电子衣柜”文字水印。
4. **单款打包**：StyleProcessor 生成 	ext/、images/ 与 manifest.json，记录上下文与敏感词命中。
5. **任务分配**：TaskPartitioner 将任务均分到 Output_Batch_Phone_<n>/，写入批次 atch_manifest.json。
6. **报告汇总**：ReportBuilder 输出 eports/delivery_report.json，统计成功数、失败列表、每设备任务量与敏感词命中。

`mermaid
flowchart LR
    A[Input_Raw 目录] --> B[Copywriting 生成]
    B --> C[Watermark 批处理]
    C --> D[StyleProcessor 单款打包]
    D --> E[TaskPartitioner 拆分]
    E --> F[Output_Batch_Phone_*]
    E --> G[ReportBuilder 汇总]
    F --> H[安卓执行器]
    H --> I[日志回传 / sync/]
`

### 失败重试与人工干预
- 单款处理失败会写入 PipelineResult.failures，报告中可见。
- 建议人工检查失败批次或敏感词命中款，必要时调整素材后重跑。
- CLI 运行失败常见原因：设备 ID 数量不足、输入目录缺少 desc.txt。

### 风控与操作建议
- 任务顺序随机化、操作间随机延迟、任务间宏观休息均可降低风控风险。
- 发布前可人工抽查文案与图片，避免敏感词或版权问题。

### 与桌面端对接
- 桌面端需读取 Output_Batch_Phone_<n>/ 的 atch_manifest.json、	ext/、images/。
- 需要展示 delivery_report.json 内的成功统计、敏感词命中信息。

### 与安卓执行器对接
- 安卓端需根据 atch_manifest.json 中的 	itle_file、description_files、images 进行操作。
- manifest.json 内的 sensitive_hits、context 可用于安全检查或 UI 提示。

### 日志归档
- 建议将安卓回传日志放在 sync/device_<id>/YYYYMMDD/，桌面端再汇总到 eports/logs/<date>/。
- 每次运行中央厨房后，备份 eports/delivery_report.json 与批次目录供溯源。

### 使用 bundle 快照恢复
1. 运行 git bundle create archives/<name>.bundle master 备份。
2. 恢复时使用 git clone bundle <dir> 或 git fetch bundle master。

### Stage 1 验收 Checklist
- [ ] 所有输入款生成成功，无失败项。
- [ ] 批次目录分配正确，设备数量匹配。
- [ ] 报告生成并记录敏感词命中。
- [ ] 测试（pytest、ruff、mypy）通过并记录日志。
- [ ] 生成最新 bundle 备份并写入工作日志。

## Stage 2（规划）
- 桌面端负责素材管理、配置编辑、同步控制、日志可视化。
- 需要额外的 UI 层、服务层（ADB/USB、日志聚合）与配置加载模块。

## Stage 4（规划）
- 安卓执行器从批次目录读取任务，按 manifest 自动发布。
- 状态机：环境检查 → 任务循环 → 失败重试/人工提示 → 日志写入 → 回传。
- 回传文件 esult.json、session.log 用于桌面端汇总与 QA。

> 随阶段推进，会持续补充更详细的流程与接口说明。
