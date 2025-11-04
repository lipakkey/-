"""文案模板加载。"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from typing import Mapping

import yaml


_TEMPLATE_PKG = "core.text.templates"


@dataclass(frozen=True)
class TemplateDefinition:
    title: str
    body: str


class TemplateRepository:
    def __init__(self) -> None:
        self._cache: dict[str, TemplateDefinition] = {}

    def get(self, category: str) -> TemplateDefinition:
        if category not in self._cache:
            self._cache[category] = self._load(category)
        return self._cache[category]

    def _load(self, category: str) -> TemplateDefinition:
        try:
            with resources.open_text(_TEMPLATE_PKG, f"{category}.yaml", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        except FileNotFoundError as exc:  # pragma: no cover
            raise KeyError(f"模板 {category} 未定义") from exc

        return TemplateDefinition(
            title=data.get("title", "精选好物"),
            body=data.get("body", "默认文案模板，后续补写具体内容。"),
        )


__all__ = ["TemplateRepository", "TemplateDefinition"]
