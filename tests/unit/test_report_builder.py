from __future__ import annotations

import json
from pathlib import Path

from core.config.models import ManifestEntry
from core.pipeline import PipelineResult
from core.reporting.report_builder import ReportBuilder


def _entry(tmp_path: Path, style: str, device: str, hits: list[str]) -> ManifestEntry:
    style_dir = tmp_path / style
    (style_dir / "text").mkdir(parents=True, exist_ok=True)
    manifest_path = style_dir / "manifest.json"
    json.dump(
        {"style_code": style, "sensitive_hits": hits},
        manifest_path.open("w", encoding="utf-8"),
        ensure_ascii=False,
    )
    return ManifestEntry(
        style_code=style,
        device_id=device,
        output_dir=style_dir,
        title_file=style_dir / "text" / "title.txt",
        description_files=(),
        primary_images=(),
        variant_images={},
        price=299.0,
        stock_per_variant=None,
        macro_delay_range=(10, 45),
    )


def test_report_builder_aggregate(tmp_path):
    entry1 = _entry(tmp_path, "STYLE_A", "device1", ["违禁"])
    entry2 = _entry(tmp_path, "STYLE_B", "device2", ["AMIRI"])
    result = PipelineResult(entries=(entry1, entry2), failures=())
    builder = ReportBuilder()
    report = builder.build(result)
    assert report["summary"]["per_device"]["device1"] == 1
    assert set(report["summary"]["sensitive_hits"].keys()) == {"违禁", "AMIRI"}


def test_report_builder_write(tmp_path):
    entry = _entry(tmp_path, "STYLE_C", "device1", [])
    result = PipelineResult(entries=(entry,), failures=["STYLE_D: error"])
    builder = ReportBuilder()
    report_path = builder.write(result, tmp_path / "reports")
    assert report_path.exists()
