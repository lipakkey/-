"""任务分配与导出逻辑。"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from core.config.models import CentralKitchenConfig, ManifestEntry


@dataclass(slots=True)
class TaskBatch:
    device_id: str
    entries: Sequence[ManifestEntry]


class TaskPartitioner:
    """将生成好的任务分配到各设备批次目录。"""

    def __init__(self, config: CentralKitchenConfig) -> None:
        self.config = config

    def partition(self, entries: Sequence[ManifestEntry]) -> Sequence[TaskBatch]:
        devices = list(self.config.device_assignment.device_ids)
        if not devices:
            raise ValueError("device_ids 不能为空")
        result: list[list[ManifestEntry]] = [[] for _ in devices]
        for idx, entry in enumerate(entries):
            slot = idx % len(devices)
            result[slot].append(replace(entry, device_id=devices[slot]))
        return [TaskBatch(device, batch) for device, batch in zip(devices, result, strict=True)]

    def export(self, batches: Sequence[TaskBatch]) -> None:
        for index, batch in enumerate(batches, start=1):
            output_dir = self.config.output_root / f"Output_Batch_Phone_{index}"
            output_dir.mkdir(parents=True, exist_ok=True)
            for entry in batch.entries:
                target_dir = output_dir / entry.style_code
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(entry.output_dir, target_dir)

            generated_at = datetime.now(timezone.utc)
            manifest = {
                "device_id": batch.device_id,
                "batch_id": self._build_batch_id(batch.device_id, generated_at, index),
                "generated_at": generated_at.isoformat(),
                "count": len(batch.entries),
                "entries": [self._entry_info(entry) for entry in batch.entries],
            }
            (output_dir / "batch_manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def _entry_info(self, entry: ManifestEntry) -> dict[str, object]:
        meta_path = entry.output_dir / "manifest.json"
        meta_data: dict[str, object] = {}
        if meta_path.exists():
            meta_data = json.loads(meta_path.read_text(encoding="utf-8"))

        primary = [
            self._relative_image(entry.style_code, path)
            for path in entry.primary_images
        ]
        variants = [
            {
                "name": color,
                "images": [self._relative_image(entry.style_code, image) for image in images],
            }
            for color, images in sorted(entry.variant_images.items())
        ]

        sensitive_hits = []
        if isinstance(meta_data, dict):
            hits = meta_data.get("sensitive_hits", [])
            if isinstance(hits, list):
                sensitive_hits = hits

        stock_value: int | None = entry.stock_per_variant
        if stock_value is None and isinstance(meta_data, dict):
            maybe_stock = meta_data.get("stock_per_variant")
            if isinstance(maybe_stock, int):
                stock_value = maybe_stock

        macro_min, macro_max = entry.macro_delay_range

        return {
            "style_code": entry.style_code,
            "paths": {
                "root": entry.style_code,
                "title": self._relative_text(entry.style_code, entry.title_file),
                "descriptions": [
                    self._relative_text(entry.style_code, path) for path in entry.description_files
                ],
                "meta": str((Path(entry.style_code) / "manifest.json").as_posix()),
            },
            "media": {
                "primary": primary,
                "variants": variants,
            },
            "pricing": {
                "price": entry.price,
                "stock_per_variant": stock_value,
                "macro_delay": {
                    "min": macro_min,
                    "max": macro_max,
                },
            },
            "flags": {
                "sensitive_hits": sensitive_hits,
                "needs_manual_review": bool(sensitive_hits),
            },
        }

    def _relative_text(self, style_code: str, path: Path) -> str:
        return str((Path(style_code) / "text" / path.name).as_posix())

    def _relative_image(self, style_code: str, path: Path) -> str:
        return str((Path(style_code) / "images" / path.name).as_posix())

    def _build_batch_id(self, device_id: str, generated_at: datetime, index: int) -> str:
        suffix = generated_at.strftime("%Y%m%d%H%M%S")
        return f"{device_id}-{index:02d}-{suffix}"


__all__ = ["TaskPartitioner", "TaskBatch"]
