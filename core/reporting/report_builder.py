"""中央厨房报告聚合模块。"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from core.config.models import ManifestEntry
from core.pipeline import PipelineResult


@dataclass(slots=True)
class DeliveryStats:
    total: int
    failures: Sequence[str]
    per_device: dict[str, int]
    sensitive_hits: dict[str, Sequence[str]]

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "success": self.total - len(self.failures),
            "failures": list(self.failures),
            "per_device": self.per_device,
            "sensitive_hits": self.sensitive_hits,
        }


class ReportBuilder:
    """汇总中央厨房生成的报告信息。"""

    def build(self, result: PipelineResult) -> dict[str, object]:
        stats = self._aggregate(result.entries, result.failures)
        manifest = {
            "summary": stats.to_dict(),
            "entries": [self._manifest_info(entry) for entry in result.entries],
        }
        return manifest

    def write(self, result: PipelineResult, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "delivery_report.json"
        report = self.build(result)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report_path

    def _aggregate(
        self, entries: Sequence[ManifestEntry], failures: Sequence[str]
    ) -> DeliveryStats:
        per_device: dict[str, int] = {}
        hits: dict[str, set[str]] = {}
        for entry in entries:
            if entry.device_id:
                per_device[entry.device_id] = per_device.get(entry.device_id, 0) + 1

            meta_path = entry.output_dir / "manifest.json"
            if not meta_path.exists():
                continue
            data = json.loads(meta_path.read_text(encoding="utf-8"))
            for word in data.get("sensitive_hits", []):
                hits.setdefault(word, set()).add(entry.style_code)

        return DeliveryStats(
            total=len(entries),
            failures=failures,
            per_device=dict(sorted(per_device.items())),
            sensitive_hits={word: tuple(sorted(styles)) for word, styles in sorted(hits.items())},
        )

    def _manifest_info(self, entry: ManifestEntry) -> dict[str, object]:
        meta_path = entry.output_dir / "manifest.json"
        meta_data: dict[str, object] = {}
        if meta_path.exists():
            meta_data = json.loads(meta_path.read_text(encoding="utf-8"))

        macro_min, macro_max = entry.macro_delay_range

        return {
            "style_code": entry.style_code,
            "device_id": entry.device_id,
            "pricing": {
                "price": entry.price,
                "stock_per_variant": entry.stock_per_variant
                if entry.stock_per_variant is not None
                else meta_data.get("stock_per_variant"),
                "macro_delay": {"min": macro_min, "max": macro_max},
            },
            "paths": {
                "title": str(entry.title_file),
                "descriptions": [str(path) for path in entry.description_files],
                "manifest": str(meta_path),
            },
            "media": {
                "primary": [str(path) for path in entry.primary_images],
                "variants": {
                    color: [str(path) for path in images]
                    for color, images in entry.variant_images.items()
                },
            },
            "sensitive_hits": meta_data.get("sensitive_hits", []),
        }


__all__ = ["ReportBuilder", "DeliveryStats"]
