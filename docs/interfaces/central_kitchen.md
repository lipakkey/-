# 中央厨房接口说明

## 1. 总览
中央厨房负责扫描 `Input_Raw/` 素材、生成文案与水印图片、构建任务包，并生成报告供桌面/安卓端使用。

```
素材目录 → Copywriting + Watermark → 任务拆分 → Output_Batch_Phone_* → 报告汇总
```

## 2. 输入前置条件
- 目录结构：`Input_Raw/<style_code>/`
  - `desc.txt`：UTF-8 原文案（必有）
  - `meta.yaml`：可选，定义 `price/colors/sizes/stock/macro_delay` 等
  - 图片：`*.jpg`，建议 `main_*` 为主图、`color_<颜色>_*` 为规格图
- CLI 参数（`scripts/central_kitchen.py`）：
  - `--input` 输入根目录
  - `--output` 输出根目录
  - `--devices` 三个设备 ID，逗号分隔
  - `--price` 基础价格（未指定时按 meta.yaml）
  - `--category` 文案模板分类（默认 `tee`）
  - `--watermark` 水印文字（默认“电子衣柜”）
  - `--report-dir` 报告子目录（默认 `reports`）
  - `--fixed-price` 取消随机尾数

### 调用示例
```
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python -m scripts.central_kitchen \
  --input data/demo_input/Input_Raw \
  --output data/demo_output \
  --devices device1,device2,device3 \
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
  "device_id": "phone1",
  "batch_id": "phone1-01-20251104165030",
  "generated_at": "2025-11-04T16:50:30Z",
  "count": 15,
  "entries": [
    {
      "style_code": "STYLE001",
      "paths": {
        "root": "STYLE001",
        "title": "STYLE001/text/title.txt",
        "descriptions": ["STYLE001/text/description_1.txt"],
        "meta": "STYLE001/manifest.json"
      },
      "media": {
        "primary": ["STYLE001/images/main_1.jpg"],
        "variants": [
          {"name": "白色", "images": ["STYLE001/images/color_白色_1.jpg"]}
        ]
      },
      "pricing": {
        "price": 299.11,
        "stock_per_variant": 50,
        "macro_delay": {"min": 10, "max": 45}
      },
      "flags": {
        "sensitive_hits": [],
        "needs_manual_review": false
      }
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
  "sensitive_hits": ["AMIRI"],
  "price": 299.11,
  "stock_per_variant": 50,
  "macro_delay": {"min": 10, "max": 45},
  "media": {
    "primary": ["main_1.jpg", "main_2.jpg"],
    "variants": [
      {"name": "白色", "images": ["color_白色_1.jpg"]}
    ]
  }
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
      "pricing": {
        "price": 299.11,
        "stock_per_variant": 50,
        "macro_delay": {"min": 10, "max": 45}
      },
      "paths": {
        "title": "Output_Batch_Phone_1/STYLE001/text/title.txt",
        "descriptions": ["Output_Batch_Phone_1/STYLE001/text/description_1.txt"],
        "manifest": "Output_Batch_Phone_1/STYLE001/manifest.json"
      },
      "media": {
        "primary": ["Output_Batch_Phone_1/STYLE001/images/main_1.jpg"],
        "variants": {"白色": ["Output_Batch_Phone_1/STYLE001/images/color_白色_1.jpg"]}
      },
      "sensitive_hits": []
    }
  ]
}
```

## 5. result.json（安卓回传）
安卓执行器写入的 `result.json` 与 batch manifest 对齐，并附加执行信息：
```json
{
  "style_code": "STYLE001",
  "batch_id": "phone1-01-20251104165030",
  "device_id": "phone1",
  "status": "success",
  "error_code": null,
  "retry_count": 0,
  "published_at": "2025-11-04T17:12:03+08:00",
  "duration_ms": 153245,
  "screenshots": ["/sdcard/XianyuTasks/Done/STYLE001/success.png"],
  "source_paths": { ...与 batch_manifest entry.paths 相同 ... },
  "pricing": { ...同 batch_manifest entry.pricing... },
  "media": { ...同 batch_manifest entry.media... }
}
```

## 6. 文案与敏感词策略
- 模板位于 `core/text/templates_store/`，可按类别扩充。
- `SensitiveDictionary` 支持：
  - `sensitive_words`：命中后替换为 `✂️`
  - `brand_alias_mapping`：如 `AMIRI -> 克罗`
- 文案生成失败会使用 `_fallback_body` 兜底，保证输出稳定。

## 7. 常见 FAQ
1. **输出为空或失败列表有内容**：检查输入目录是否存在图片/desc；查看 `reports/testlogs/` 日志。
2. **设备数不足**：CLI `--devices` 需提供 3 个 ID，否则报错。
3. **价格随机尾数**：默认开启，如需固定用 `--fixed-price`。
4. **敏感词命中**：`delivery_report` 会列出命中词及款号，人工检查即可。
5. **重复生成覆盖**：`TaskPartitioner.export` 会清理同名目录，需提前备份历史批次。

## 8. 日志回传建议
- 安卓执行完成后，将 `/sdcard/XianyuTasks/Done/<style>/result.json`、`session.log`、截图复制到桌面端 `sync/device_<id>/YYYYMMDD_HHMMSS/`。
- 桌面端可合并结果，更新 `delivery_report.json` 或输出独立分析报表。

## 9. 扩展计划
- 价格策略：未来提供 per-style `price_override`、批次权重等。
- 模板切换：根据 `meta.yaml` 中的品类/性别选择不同模板。
- JSON Schema：考虑为 manifest/result 定义 schema，供桌面或安卓执行器验证。

---
> 接口如有更新，请同步 README 与 docs 索引。
