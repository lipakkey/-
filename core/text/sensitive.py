"""敏感词处理。"""

from __future__ import annotations

from dataclasses import dataclass

from core.config.models import SensitiveDictionary


@dataclass(slots=True)
class SensitiveFilterResult:
    text: str
    hits: tuple[str, ...]


class SensitiveFilter:
    def __init__(self, dictionary: SensitiveDictionary) -> None:
        self.dictionary = dictionary

    def apply(self, text: str) -> SensitiveFilterResult:
        hits: list[str] = []
        normalized = text
        for word in self.dictionary.sensitive_words:
            if word in normalized:
                hits.append(word)
                normalized = normalized.replace(word, "✂️")
        for alias, replacement in self.dictionary.brand_alias_mapping.items():
            if alias in normalized:
                hits.append(alias)
                normalized = normalized.replace(alias, replacement)
        return SensitiveFilterResult(text=normalized, hits=tuple(hits))


__all__ = ["SensitiveFilter", "SensitiveFilterResult"]
