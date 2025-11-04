from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from core.config.models import (
    CentralKitchenConfig,
    DelayConfig,
    DeviceAssignment,
    GenerationTemplate,
    ManifestEntry,
    PriceConfig,
    SensitiveDictionary,
    WatermarkConfig,
)
from core.pipeline.partitioner import TaskPartitioner


def _make_config(tmp_path: Path, device_ids: Sequence[str]) -> CentralKitchenConfig:
    return CentralKitchenConfig(
        input_root=tmp_path,
        output_root=tmp_path / "output",
        price=PriceConfig(base_yuan=299),
        delays=DelayConfig(),
        device_assignment=DeviceAssignment(device_ids=device_ids),
        template=GenerationTemplate(category="tee"),
        sensitive_dictionary=SensitiveDictionary(),
        watermark=WatermarkConfig(),
    )


def _entry(tmp_path: Path, style: str) -> ManifestEntry:
    style_dir = tmp_path / style
    (style_dir / "text").mkdir(parents=True, exist_ok=True)
    return ManifestEntry(
        style_code=style,
        device_id="",
        output_dir=style_dir,
        title_file=style_dir / "text" / "title.txt",
        description_files=(),
        primary_images=(),
        variant_images={},
        price=299.0,
        stock_per_variant=None,
        macro_delay_range=(10, 45),
    )


def test_partitioner_even_distribution(tmp_path):
    config = _make_config(tmp_path, ("device1", "device2", "device3"))
    partitioner = TaskPartitioner(config)
    entries = [_entry(tmp_path, f"STYLE_{i}") for i in range(6)]
    batches = partitioner.partition(entries)
    counts = [len(batch.entries) for batch in batches]
    assert counts == [2, 2, 2]
    assert {batch.device_id for batch in batches} == {"device1", "device2", "device3"}


def test_partitioner_requires_devices(tmp_path):
    config = _make_config(tmp_path, ())
    partitioner = TaskPartitioner(config)
    try:
        partitioner.partition([])
    except ValueError:
        pass
    else:  # pragma: no cover - should not happen
        raise AssertionError("expected ValueError when no devices configured")
