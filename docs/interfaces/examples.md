# ʾ���ļ����ʺ�

## 1. ʾ�����ɵĿ¼
ִ�� `python scripts/run_demo.py --price 299` �� `data/demo_output/` �ڽ���ҵ�����ݺͱ���

- `Output_Batch_Phone_1/`
- `Output_Batch_Phone_2/`
- `Output_Batch_Phone_3/`
- `reports/delivery_report.json`

## 2. batch_manifest.json ���ṹ
ÿ���豸�������� `batch_manifest.json` ��ÿ�� entry �ṹ����:

```json
{
  "style_code": "STYLE_A",
  "paths": {
    "root": "STYLE_A",
    "title": "STYLE_A/text/title.txt",
    "descriptions": [
      "STYLE_A/text/description_1.txt",
      "STYLE_A/text/description_2.txt",
      "STYLE_A/text/description_3.txt"
    ],
    "meta": "STYLE_A/manifest.json"
  },
  "media": {
    "primary": [
      "STYLE_A/images/main_1.jpg",
      "STYLE_A/images/main_2.jpg"
    ],
    "variants": [
      {
        "name": "白色",
        "images": ["STYLE_A/images/color_白色_1.jpg"]
      },
      {
        "name": "黑色",
        "images": ["STYLE_A/images/color_黑色_1.jpg"]
      }
    ]
  },
  "pricing": {
    "price": 299.0,
    "stock_per_variant": 50,
    "macro_delay": { "min": 10, "max": 45 }
  },
  "flags": {
    "sensitive_hits": [],
    "needs_manual_review": false
  }
}
```

> · `paths.*` ��·����ԭ������ͼͼƬ��ɨ���·���� 
> · `media.primary` Ϊ��ͼ���ϣ�`variants` ���ڸ����ɫ/�ֻ�����ͼƬ�б�� 
> · `pricing.macro_delay` �� min/max ʱ�䣬��Χ���� Stage3 �宏观休眠��

## 3. manifest.json (staging/STYLE_X/manifest.json)
���Ҫ�� Stage3 ��ȡԭʼ context ��敏感词，staging ���ڸ��� style ���� manifest.json �ֶ�����

```json
{
  "style_code": "STYLE_A",
  "context": {
    "colors": "黑色, 白色",
    "sizes": "S, M, L, XL"
  },
  "sensitive_hits": [],
  "price": 299.0,
  "stock_per_variant": 50,
  "macro_delay": { "min": 10, "max": 45 },
  "media": {
    "primary": ["main_1.jpg", "main_2.jpg"],
    "variants": [
      {"name": "白色", "images": ["color_白色_1.jpg"]}
    ]
  }
}
```

## 4. delivery_report.json ���Ա߿���
`delivery_report.json` �� `summary` + `entries` ����֧������ȡ�豸ͳ����敏感词命�У�

```json
{
  "summary": {
    "total": 4,
    "success": 4,
    "failures": [],
    "per_device": {"phone1": 2, "phone2": 2},
    "sensitive_hits": {}
  },
  "entries": [
    {
      "style_code": "STYLE_A",
      "device_id": "phone1",
      "pricing": {
        "price": 299.0,
        "stock_per_variant": 50,
        "macro_delay": {"min": 10, "max": 45}
      },
      "paths": {
        "title": ".../STYLE_A/text/title.txt",
        "descriptions": [".../description_1.txt", "..."],
        "manifest": ".../STYLE_A/manifest.json"
      },
      "media": {
        "primary": [".../images/main_1.jpg"],
        "variants": {"白色": ["...color_白色_1.jpg"]}
      },
      "sensitive_hits": []
    }
  ]
}
```

## 5. result.json (安卓回传)
安卓执行器每完成一款会在 `Done/<style>/result.json` 写入：

```json
{
  "style_code": "STYLE_A",
  "batch_id": "phone1-01-20251104165030",
  "device_id": "phone1",
  "status": "success",
  "error_code": null,
  "retry_count": 0,
  "published_at": "2025-11-04T17:12:03+08:00",
  "duration_ms": 153245,
  "screenshots": ["/sdcard/XianyuTasks/Done/STYLE_A/success.png"],
  "source_paths": {...与 batch_manifest 相同...},
  "pricing": {...},
  "media": {...}
}
```

桌面端拉取 `result.json` �� `session.log` �����ڻ�ص��� Stage1 delivery_report.json �вɼ�ԭ�򡣵���ɹ����ֶ�+截图λ�ã���ʧ���ֶξ���������

## 6. scripts
- `scripts/validate_manifest.py`：У�� batch_manifest.json / delivery_report.json ��������ֶΡ�
- `scripts/report_summary.py`：快读 summary，展示 per_device。
- `scripts/copy_batch.py`：拷贝指定批次到目标目录（例如 ADB 挂载点）。

��ǰ示例���� `data/demo_output/` ��ת���ͻָ�����ʹ `python scripts/run_demo.py --no-run` ����ڱ༭��չ���ļ��ṹ��
