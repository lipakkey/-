"""任务分配与导出逻辑。"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Sequence

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
        return [TaskBatch(device, batch) for device, batch in zip(devices, result)]

    def export(self, batches: Sequence[TaskBatch]) -> None:
        for index, batch in enumerate(batches, start=1):
            output_dir = self.config.output_root / f"Output_Batch_Phone_{index}"
            output_dir.mkdir(parents=True, exist_ok=True)
            for entry in batch.entries:
                target_dir = output_dir / entry.style_code
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(entry.output_dir, target_dir)
            manifest = {
                "device_id": batch.device_id,
                "count": len(batch.entries),
                "entries": [self._entry_info(entry) for entry in batch.entries],
            }
            (output_dir / "batch_manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def _entry_info(self, entry: ManifestEntry) -> dict[str, object]:
        return {
            "style_code": entry.style_code,
            "title_file": str(Path(entry.style_code) / "text" / entry.title_file.name),
            "description_files": [
                str(Path(entry.style_code) / "text" / path.name) for path in entry.description_files
            ],
            "images": [
                str(Path(entry.style_code) / "images" / path.name) for path in entry.image_files
            ],
            "price": entry.price,
            "macro_delay": entry.macro_delay_min,
        }


__all__ = ["TaskPartitioner", "TaskBatch"]
