# 示例输出解读

## 1. 示例任务概览
运行 `python scripts/run_demo.py --price 299` 后，`data/demo_output/` 会生成三个批次和报告：

- `Output_Batch_Phone_1/`
- `Output_Batch_Phone_2/`
- `Output_Batch_Phone_3/`
- `reports/delivery_report.json`

示例报告（截取）：
```json
{
  "summary": {
    "total": 4,
    "success": 4,
    "failures": [],
    "per_device": {},
    "sensitive_hits": {}
  },
  "entries": [ { ... } ]
}
```
说明：
- `total`/`success`：生成的总任务数与成功数。
- `per_device`：示例未指定设备 ID，实际运行时会按设备统计。
- `sensitive_hits`：示例未触发敏感词，实际若命中会列出词条与款号。

## 2. entries 字段说明
以单条记录为例：
- `style_code`：款号，如 `STYLE_A`。
- `device_id`：分配的设备 ID（示例为空）。
- `price`：最终价格，若启用随机尾数会体现在此。
- `macro_delay`：任务间宏观休眠区间（分钟）。
- `title_file`：标题文本路径，设备需读取。
- `description_files`：描述文本列表，用于填入发布页。
- `image_files`：水印后的图片路径，确保设备可访问。

## 3. 敏感词校验
示例中未触发敏感词。如果需验证，可在 `SensitiveDictionary` 中加入词条并修改 `desc.txt`，运行后在 `delivery_report.json` 的 `summary.sensitive_hits` 中会出现记录。

## 4. 清理
使用示例后，可删除 `data/demo_input/` 与 `data/demo_output/`，或重新运行脚本覆盖。
