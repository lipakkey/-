"""单款处理器：文案 + 水印 + 元数据。"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from core.config.models import (
    CentralKitchenConfig,
    ManifestEntry,
    PriceConfig,
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

        for image_path in raw.images:
            output_image = image_dir / image_path.name
            self.watermarker.apply_to(image_path, output_image)

        manifest_path = style_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "style_code": raw.style_code,
                    "context": context,
                    "sensitive_hits": copy_result.sensitive_hits,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        price = self._resolve_price(raw, context)
        macro_delay = raw.meta.macro_delay_override if raw.meta else self.config.delays.macro_delay_min
        return ManifestEntry(
            style_code=raw.style_code,
            device_id="",
            output_dir=style_dir,
            title_file=title_file,
            description_files=tuple(description_files),
            image_files=tuple(sorted(image_dir.glob("*"))),
            price=price,
            macro_delay_min=macro_delay,
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


__all__ = ["StyleProcessor"]
