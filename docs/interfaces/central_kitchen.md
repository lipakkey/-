# 中央厨房接口说明

## 1. 总览
中央厨房负责扫描 `Input_Raw/` 素材、生成文案与水印图片、构建任务包，并生成报告供桌面/安卓端使用。

```
素材目录 → Copywriting + Watermark → 任务拆分 → Output_Batch_Phone_* → 报告汇总
```

## 2. 输入前置条件
- 目录结构：`Input_Raw/<style_code>/`
  - `desc.txt`：UTF-8 原文案（必有）
  - `meta.yaml`：可选，定义 `price/colors/sizes` 等
  - 图片：`*.jpg`，命名建议 `main_*` 主图、`color_<颜色>_*` 规格图
- CLI 参数（`scripts/central_kitchen.py`）：
  - `--input` 输入根目录
  - `--output` 输出根目录
  - `--devices` 三个设备 ID，逗号分隔
  - `--price` 基础价格
  - `--category` 文案模板分类（默认 `tee`）
  - `--watermark` 水印文字（默认“电子衣柜”）
  - `--report-dir` 报告子目录（默认 `reports`）
  - `--fixed-price` 取消随机尾数

### 调用示例
```
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \\
python -m scripts.central_kitchen \\
  --input data/demo_input/Input_Raw \\
  --output data/demo_output \\
  --devices device1,device2,device3 \\
  --price 299 --category tee --watermark 电子衣柜
```

## 3. 输出目录结构
```
Output_Batch_Phone_1/
  batch_manifest.json
  STYLE001/
    text/title.txt
    text/description_1.txt
    images/main_1.jpg
    manifest.json
Output_Batch_Phone_2/
...
reports/delivery_report.json
```

### 批次 Manifest（`Output_Batch_Phone_n/batch_manifest.json`）
```json
{
  "device_id": "device1",
  "count": 15,
  "entries": [
    {
      "style_code": "STYLE001",
      "title_file": "STYLE001/text/title.txt",
      "description_files": ["STYLE001/text/description_1.txt"],
      "images": ["STYLE001/images/main_1.jpg"],
      "price": 299.11,
      "macro_delay": [10, 45]
    }
  ]
}
```

### 单款 manifest（`STYLE/text/manifest.json`）
```json
{
  "style_code": "STYLE001",
  "context": {
    "colors": "黑色, 白色",
    "sizes": "S M L XL XXL",
    "fabric": "320g 重磅面料",
    "fit": "男女同款宽松版"
  },
  "sensitive_hits": ["AMIRI"]
}
```

## 4. 报告结构（`reports/delivery_report.json`）
```json
{
  "summary": {
    "total": 45,
    "success": 45,
    "failures": [],
    "per_device": {"device1": 15, "device2": 15, "device3": 15},
    "sensitive_hits": { "违禁": ["STYLE005"] }
  },
  "entries": [
    {
      "style_code": "STYLE001",
      "device_id": "device1",
      "price": 299.11,
      "macro_delay": [10, 45],
      "title_file": "Output_Batch_Phone_1/STYLE001/text/title.txt",
      "description_files": [
        "Output_Batch_Phone_1/STYLE001/text/description_1.txt"
      ],
      "image_files": [
        "Output_Batch_Phone_1/STYLE001/images/main_1.jpg"
      ]
    }
  ]
}
```

## 5. 文案与敏感词策略
- 模板位于 `core/text/templates_store/`，可按类别扩充。
- `SensitiveDictionary` 支持：
  - `sensitive_words`：命中后替换为 `✂️`
  - `brand_alias_mapping`：如 `AMIRI -> 克罗`
- 文案生成失败会使用 `_fallback_body` 兜底，保证输出稳定。

## 6. 常见 FAQ
1. **输出为空或失败列表有内容**：检查输入目录是否存在图片/desc；查看 `reports/testlogs/` 日志。
2. **设备数不足**：CLI `--devices` 需提供 3 个 ID，否则报错。
3. **价格随机尾数**：默认开启，每次运行 or 每款可不同；如需固定，用 `--fixed-price`。
4. **敏感词命中**：`delivery_report` 会列出命中词及款号，人工检查即可。
5. **多次生成覆盖旧输出**：`TaskPartitioner.export` 会清理同名目录，请先备份旧批次。

## 7. 日志回传建议
- 安卓执行完成后，将 `/sdcard/XianyuTasks/Done/<task>/result.json`、`session.log` 复制到桌面端 `sync/device_<id>/YYYYMMDD/`。
- 桌面端可再聚合至 `reports/logs/<date>/`，便于追踪与归档。

## 8. 扩展计划
- 价格策略：未来提供 per-style `price_override`、批次权重等。
- 模板切换：根据 `meta.yaml` 中的品类/性别选择不同模板。
- JSON Schema：考虑为 manifest/report 定义 schema，供桌面或安卓执行器验证。

---
> 接口如有更新，请同步 README 与 docs 索引。
