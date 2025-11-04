"""文案模板加载工具。"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from typing import Any, Dict, Iterable

import yaml

_TEMPLATE_PKG = "core.text.templates_store"


@dataclass(frozen=True)
class TemplateDefinition:
    title: str
    body: str


class TemplateRepository:
    """从内置 YAML 模板中读取文案骨架。"""

    def __init__(self) -> None:
        self._cache: dict[str, TemplateDefinition] = {}

    def get(self, category: str) -> TemplateDefinition:
        if category not in self._cache:
            self._cache[category] = self._load(category)
        return self._cache[category]

    def _load(self, category: str) -> TemplateDefinition:
        try:
            content = (
                resources.files(_TEMPLATE_PKG)
                .joinpath(f"{category}.yaml")
                .read_text(encoding="utf-8")
            )
        except FileNotFoundError as exc:  # pragma: no cover
            raise KeyError(f"模板 {category} 未定义") from exc

        raw_data = yaml.safe_load(content)
        data: Dict[str, Any] = {}
        if isinstance(raw_data, dict):
            data = {str(key): value for key, value in raw_data.items()}

        title = str(data.get("title", "精选好物"))
        body = str(data.get("body", "默认文案模板，后续补充详细描述。"))
        return TemplateDefinition(title=str(title), body=str(body))


__all__ = ["TemplateRepository", "TemplateDefinition"]
