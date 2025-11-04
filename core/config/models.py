"""配置数据模型定义。"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class PriceConfig:
    """价格设置，支持随机尾数。"""

    base_yuan: float
    keep_decimal: bool = True
    random_tail: bool = True
    tail_candidates: Sequence[int] = field(
        default_factory=lambda: tuple(range(0, 100))
    )  # 0-99 可选

    def derive_price(self, seed: int | None = None) -> float:
        import random

        rng = random.Random(seed)
        if not self.keep_decimal:
            return round(self.base_yuan)

        if self.random_tail and self.tail_candidates:
            tail = rng.choice(list(self.tail_candidates))
            return float(f"{int(self.base_yuan)}.{tail:02d}")
        return round(self.base_yuan, 2)


@dataclass(frozen=True)
class DelayConfig:
    """执行延迟配置（毫秒/分钟）。"""

    micro_delay_ms: tuple[int, int] = (1500, 4000)
    macro_delay_min: tuple[int, int] = (10, 45)

    def validate(self) -> None:
        low, high = self.micro_delay_ms
        if low < 0 or high < low:
            raise ValueError("micro_delay_ms 范围非法")
        low, high = self.macro_delay_min
        if low < 0 or high < low:
            raise ValueError("macro_delay_min 范围非法")


@dataclass(frozen=True)
class DeviceAssignment:
    """设备分配策略。"""

    device_ids: Sequence[str]
    weights: Mapping[str, int] | None = None

    def normalized_weights(self) -> Mapping[str, float]:
        if not self.weights:
            uniform = 1 / max(len(self.device_ids), 1)
            return {device: uniform for device in self.device_ids}
        total = sum(self.weights.values())
        if total <= 0:
            raise ValueError("设备权重之和必须大于 0")
        return {device: weight / total for device, weight in self.weights.items()}


@dataclass(frozen=True)
class GenerationTemplate:
    """文案生成模板配置。"""

    category: str  # 例如 tee/hoodie/outerwear
    variations: int = 3
    allow_sensitive_replacement: bool = True


@dataclass(frozen=True)
class SensitiveDictionary:
    """敏感词与品牌别名配置。"""

    sensitive_words: tuple[str, ...] = ()
    brand_alias_mapping: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class WatermarkConfig:
    """水印参数配置。"""

    text: str = "电子衣柜"
    font_size: int = 48
    opacity: float = 0.18
    spacing: int = 220
    color: Tuple[int, int, int] = (255, 255, 255)
    angle: int = 30


@dataclass(frozen=True)
class CentralKitchenConfig:
    """中央厨房全局配置。"""

    input_root: Path
    output_root: Path
    price: PriceConfig
    delays: DelayConfig
    device_assignment: DeviceAssignment
    template: GenerationTemplate
    sensitive_dictionary: SensitiveDictionary
    watermark: WatermarkConfig = WatermarkConfig()
    ollama_model: str = "qwen:4b"

    def ensure_paths(self) -> None:
        for path in (self.input_root, self.output_root):
            if not path.exists():
                raise FileNotFoundError(path)


@dataclass(frozen=True)
class StyleMeta:
    """单个款号的元数据。"""

    style_code: str
    price_override: float | None = None
    colors: tuple[str, ...] = ()
    sizes: tuple[str, ...] = ()
    stock_per_variant: int | None = None
    macro_delay_override: tuple[int, int] | None = None


@dataclass(frozen=True)
class ManifestEntry:
    """生成任务包时的记录。"""

    style_code: str
    device_id: str
    output_dir: Path
    title_file: Path
    description_files: Sequence[Path]
    image_files: Sequence[Path]
    price: float
    macro_delay_min: tuple[int, int]


__all__ = [
    "PriceConfig",
    "DelayConfig",
    "DeviceAssignment",
    "GenerationTemplate",
    "SensitiveDictionary",
    "WatermarkConfig",
    "CentralKitchenConfig",
    "StyleMeta",
    "ManifestEntry",
]
