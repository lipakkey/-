"""素材扫描器。"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from core.config.models import StyleMeta

META_FILENAMES = {"meta.yaml", "meta.yml", "meta.json"}


@dataclass(slots=True)
class RawStyle:
    style_code: str
    base_dir: Path
    desc_file: Path
    images: tuple[Path, ...]
    meta: StyleMeta | None


class InputScanner:
    """遍历输入目录，识别有效的款号。"""

    def __init__(self, input_root: Path) -> None:
        self.input_root = input_root

    def scan(self) -> Iterator[RawStyle]:
        for candidate in sorted(self.input_root.iterdir()):
            if not candidate.is_dir():
                continue
            style_code = candidate.name
            desc = candidate / "desc.txt"
            if not desc.exists():
                continue
            images = tuple(sorted(p for p in candidate.glob("*.jpg")))
            meta = self._load_meta(candidate, style_code)
            yield RawStyle(
                style_code=style_code,
                base_dir=candidate,
                desc_file=desc,
                images=images,
                meta=meta,
            )

    def _load_meta(self, directory: Path, style_code: str) -> StyleMeta | None:
        for filename in META_FILENAMES:
            meta_path = directory / filename
            if meta_path.exists():
                return self._parse_meta(meta_path, style_code)
        return None

    def _parse_meta(self, meta_path: Path, style_code: str) -> StyleMeta:
        if meta_path.suffix.lower() == ".json":
            data = json.loads(meta_path.read_text(encoding="utf-8"))
        else:
            import yaml  # type: ignore

            data = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}

        return StyleMeta(
            style_code=data.get("style_code", style_code),
            price_override=data.get("price"),
            colors=tuple(data.get("colors", [])),
            sizes=tuple(data.get("sizes", [])),
            stock_per_variant=data.get("stock"),
            macro_delay_override=tuple(data.get("macro_delay"))
            if data.get("macro_delay")
            else None,
        )


__all__ = ["InputScanner", "RawStyle"]
