"""单款处理器：文案 + 水印 + 元数据。"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass

from core.config.models import (
    CentralKitchenConfig,
    ManifestEntry,
    StyleMeta,
)
from core.pipeline.scanner import RawStyle
from core.text.generator import CopywritingGenerator
from core.watermark.processor import WatermarkProcessor


@dataclass(slots=True)
class StyleProcessor:
    config: CentralKitchenConfig
    generator: CopywritingGenerator
    watermarker: WatermarkProcessor

    def process(self, raw: RawStyle) -> ManifestEntry:
        style_dir = self.config.output_root / "staging" / raw.style_code
        text_dir = style_dir / "text"
        image_dir = style_dir / "images"
        text_dir.mkdir(parents=True, exist_ok=True)
        image_dir.mkdir(parents=True, exist_ok=True)

        context = self._build_context(raw)
        copy_result = self.generator.generate(
            template_config=self.config.template,
            model=self.config.ollama_model,
            context=context,
        )
        title_file = text_dir / "title.txt"
        title_file.write_text(copy_result.title, encoding="utf-8")
        description_files = []
        for idx, body in enumerate(copy_result.bodies, start=1):
            file_path = text_dir / f"description_{idx}.txt"
            file_path.write_text(body, encoding="utf-8")
            description_files.append(file_path)

        primary_images: list = []
        variant_map: dict[str, list] = {}
        for image_path in raw.images:
            output_image = image_dir / image_path.name
            self.watermarker.apply_to(image_path, output_image)
            stem = image_path.stem
            if stem.startswith("color_"):
                parts = stem.split("_", 2)
                color = parts[1] if len(parts) > 1 else "默认"
                variant_map.setdefault(color, []).append(output_image)
            else:
                primary_images.append(output_image)

        stock = self._resolve_stock(raw)
        macro_delay = (
            raw.meta.macro_delay_override if raw.meta else self.config.delays.macro_delay_min
        )
        manifest_payload = {
            "style_code": raw.style_code,
            "context": context,
            "sensitive_hits": copy_result.sensitive_hits,
            "price": price,
            "stock_per_variant": stock,
            "macro_delay": {"min": macro_delay[0], "max": macro_delay[1]},
            "media": {
                "primary": [img.name for img in primary_images],
                "variants": [
                    {"name": color, "images": [img.name for img in sorted(paths)]}
                    for color, paths in sorted(variant_map.items())
                ],
            },
        }
        manifest_path = style_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return ManifestEntry(
            style_code=raw.style_code,
            device_id="",
            output_dir=style_dir,
            title_file=title_file,
            description_files=tuple(description_files),
            primary_images=tuple(primary_images),
            variant_images={color: tuple(sorted(paths)) for color, paths in variant_map.items()},
            price=price,
            stock_per_variant=stock,
            macro_delay_range=macro_delay,
        )

    def _build_context(self, raw: RawStyle) -> Mapping[str, str]:
        desc = raw.desc_file.read_text(encoding="utf-8").strip()
        meta = raw.meta or StyleMeta(style_code=raw.style_code)
        colors = ", ".join(meta.colors) if meta.colors else "黑色 白色"
        sizes = ", ".join(meta.sizes) if meta.sizes else "S M L XL XXL"
        return {
            "style_code": raw.style_code,
            "style": raw.style_code,
            "desc": desc,
            "colors": colors,
            "sizes": sizes,
            "year": "2025",
            "fabric": "320g 重磅面料",
            "fit": "男女同款宽松版",
            "highlights": "雪花图案、做旧洗水、细节满满",
        }

    def _resolve_price(self, raw: RawStyle, context: Mapping[str, str]) -> float:
        if raw.meta and raw.meta.price_override is not None:
            return raw.meta.price_override
        return self.config.price.derive_price()

    def _resolve_stock(self, raw: RawStyle) -> int | None:
        if raw.meta and raw.meta.stock_per_variant is not None:
            return int(raw.meta.stock_per_variant)
        return None


__all__ = ["StyleProcessor"]
