# 示例数据与操作指南

## 1. 生成示例素材
使用脚本 `scripts/run_demo.py` 可以快速创建示例 `Input_Raw/` 目录：

```bash
python scripts/run_demo.py
```

默认会在 `data/demo_input/Input_Raw/` 下创建三款示例（STYLE_A/B/C），并运行中央厨房，将结果输出到 `data/demo_output/`。

- 每款包含 `desc.txt`、`meta.yaml`、若干主图 (`main_*.jpg`) 与颜色图 (`color_<颜色>_*.jpg`)。
- `meta.yaml` 中预设价格、尺码、颜色和宏观休眠区间。

如需仅生成素材而不运行中央厨房：

```bash
python scripts/run_demo.py --no-run
```

可通过 `--spec my_styles.json` 自定义款式列表（JSON 数组），字段包括：

```json
{
  "style_code": "STYLE_X",
  "description": "示例描述",
  "price": 299,
  "colors": ["黑色", "白色"],
  "sizes": ["S", "M", "L"],
  "image_count": 2
}
```

## 2. 查看示例输出
运行脚本后可在 `data/demo_output/` 查看生成结果：

- `Output_Batch_Phone_1/`：示例批次目录，包含 `batch_manifest.json` 与单款任务。
- `reports/delivery_report.json`：汇总统计，展示成功任务、每设备任务量、敏感词命中。

建议打开 `docs/interfaces/central_kitchen.md` 对照字段说明，熟悉 manifest 结构。

## 3. 常见验证
- 检查 `manifest.json` 中的 `sensitive_hits` 是否符合预期（如命中 “AMIRI” 后替换为 “克罗”）。
- 在 `description_*.txt` 中确认文案段落有 150-300 字、包含模板信息。
- 确认图片文件均已生成并可预览（脚本生成的图片为简易占位图）。

## 4. 清理
如需重新生成或清理示例数据，可直接删除 `data/demo_input/` 与 `data/demo_output/` 目录后再次运行脚本。确保 `.gitignore` 已忽略这些目录，防止示例数据进入版本控制。
