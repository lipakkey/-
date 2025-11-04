"""文案生成流水线。"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from core.config.models import GenerationTemplate, SensitiveDictionary
from core.text.ollama_client import OllamaClient
from core.text.sensitive import SensitiveFilter
from core.text.template_repository import TemplateRepository


@dataclass(slots=True)
class CopywritingResult:
    title: str
    bodies: tuple[str, ...]
    sensitive_hits: tuple[str, ...]


class CopywritingGenerator:
    """包装模板、模型调用与敏感词过滤。"""

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
        prompt = self._build_prompt(title_prompt, body_prompt, context)
        for index in range(max(template_config.variations, 1)):
            response = self._call_ollama(model, prompt, context, index)
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

    def _call_ollama(
        self,
        model: str,
        prompt: str,
        context: Mapping[str, Any],
        index: int,
    ) -> str:
        fake_template = os.environ.get("OLLAMA_FAKE_RESPONSE")
        if fake_template:
            return fake_template.format(**{**context, "variation": index})
        try:
            response = self.ollama.generate(model=model, prompt=prompt)
        except RuntimeError:
            return self._fallback_body(context)
        sanitized = response.strip()
        if not sanitized or sanitized in {"兜底响应", "FALLBACK"}:
            return self._fallback_body(context)
        return response

    def _build_prompt(
        self,
        title_prompt: str,
        body_prompt: str,
        context: Mapping[str, Any],
    ) -> str:
        return (
            "你是闲鱼服饰文案助手，请根据提供的素材生成 150-300 字的商品描述，"
            "要求自然、真实、有代入感，避免使用平台敏感词。\\n"
            f"推荐标题：{title_prompt}\\n"
            f"描述模板：{body_prompt}\\n"
            f"原始素材：{context}\\n"
        )

    def _fallback_body(self, context: Mapping[str, Any]) -> str:
        return (
            f"{context.get('style_code', '本款')} 上新，"
            f"采用 {context.get('fabric', '高品质面料')}，"
            f"版型 {context.get('fit', '宽松舒适')}。"
            f"尺码覆盖：{context.get('sizes', 'S-XL')}；"
            f"颜色选择：{context.get('colors', '基础百搭配色')}。"
            "细节做工扎实，日常通勤或休闲都适合，欢迎私信咨询尺码与细节。"
        )


__all__ = ["CopywritingGenerator", "CopywritingResult"]
