"""文案生成流水线。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from core.config.models import GenerationTemplate, SensitiveDictionary
from core.text.ollama_client import OllamaClient
from core.text.sensitive import SensitiveFilter
from core.text.templates import TemplateRepository


@dataclass(slots=True)
class CopywritingResult:
    title: str
    bodies: tuple[str, ...]
    sensitive_hits: tuple[str, ...]


class CopywritingGenerator:
    def __init__(
        self,
        template_repo: TemplateRepository,
        ollama: OllamaClient,
        dictionary: SensitiveDictionary,
    ) -> None:
        self.template_repo = template_repo
        self.ollama = ollama
        self.filter = SensitiveFilter(dictionary)

    def generate(
        self,
        template_config: GenerationTemplate,
        model: str,
        context: Mapping[str, Any],
    ) -> CopywritingResult:
        template = self.template_repo.get(template_config.category)
        title_prompt = template.title.format(**context)
        body_prompt = template.body.format(**context)

        bodies: list[str] = []
        hits: list[str] = []
        for _ in range(template_config.variations):
            response = self.ollama.generate(
                model=model,
                prompt=self._build_prompt(title_prompt, body_prompt, context),
            )
            filtered = self.filter.apply(response)
            bodies.append(filtered.text)
            hits.extend(filtered.hits)

        title_filtered = self.filter.apply(title_prompt)
        hits.extend(list(title_filtered.hits))
        return CopywritingResult(
            title=title_filtered.text,
            bodies=tuple(bodies),
            sensitive_hits=tuple(sorted(set(hits))),
        )

    def _build_prompt(
        self,
        title_prompt: str,
        body_prompt: str,
        context: Mapping[str, Any],
    ) -> str:
        return (
            "你是闲鱼服饰文案助手，请参考以下上下文，生成 150-300 字的商品描述，"
            "保持真实、自然、人性化，避免触发敏感词：\n"
            f"标题：{title_prompt}\n"
            f"描述模板：{body_prompt}\n"
            f"上下文：{context}\n"
        )


__all__ = ["CopywritingGenerator", "CopywritingResult"]
