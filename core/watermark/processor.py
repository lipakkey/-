"""图片水印处理。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from core.config.models import WatermarkConfig


@dataclass(slots=True)
class WatermarkProcessor:
    config: WatermarkConfig

    def apply_to(self, input_path: Path, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(input_path).convert("RGBA") as base:
            watermark_layer = self._build_overlay(base.size)
            combined = Image.alpha_composite(base, watermark_layer)
            combined.convert("RGB").save(output_path, quality=95)

    def _build_overlay(self, size: tuple[int, int]) -> Image.Image:
        width, height = size
        overlay = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        font = self._font()
        step = self.config.spacing
        for x in range(-step, width + step, step):
            for y in range(-step, height + step, step):
                draw.text(
                    (x, y),
                    self.config.text,
                    font=font,
                    fill=self._rgba_color(),
                    anchor="lt",
                )
        return overlay.rotate(self.config.angle, expand=0)

    def _font(self) -> ImageFont.FreeTypeFont:
        try:
            return ImageFont.truetype("msyh.ttc", self.config.font_size)
        except OSError:  # pragma: no cover
            return ImageFont.load_default()

    def _rgba_color(self) -> tuple[int, int, int, int]:
        r, g, b = self.config.color
        return (r, g, b, int(255 * self.config.opacity))


__all__ = ["WatermarkProcessor"]
