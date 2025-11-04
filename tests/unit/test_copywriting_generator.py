from __future__ import annotations

from core.config.models import GenerationTemplate, SensitiveDictionary
from core.text.generator import CopywritingGenerator
from core.text.ollama_client import OllamaClient
from core.text.template_repository import TemplateDefinition, TemplateRepository


class DummyRepo(TemplateRepository):
    def __init__(self) -> None:
        self.definition = TemplateDefinition(
            title="示例标题 {style_code}",
            body="示例正文 {desc}",
        )

    def get(self, category: str) -> TemplateDefinition:
        return self.definition


class DummyOllama(OllamaClient):
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses

    def generate(self, model: str, prompt: str, retries: int = 2) -> str:
        if self._responses:
            return self._responses.pop(0)
        return "兜底响应"


def test_copywriting_generator_basic():
    repo = DummyRepo()
    ollama = DummyOllama(["AMIRI 违禁 内容", "AMIRI 违禁 内容"])
    dictionary = SensitiveDictionary(
        sensitive_words=("违禁",), brand_alias_mapping={"AMIRI": "克罗"}
    )
    generator = CopywritingGenerator(repo, ollama, dictionary)
    template = GenerationTemplate(category="tee", variations=2)
    context = {"style_code": "STYLE_X", "desc": "AMIRI 违禁 描述"}
    result = generator.generate(template, "model", context)
    assert len(result.bodies) == 2
    assert all("克罗" in body for body in result.bodies)
    assert all("✂️" in body for body in result.bodies)


def test_copywriting_generator_fallback():
    repo = DummyRepo()
    ollama = DummyOllama([])
    dictionary = SensitiveDictionary()
    generator = CopywritingGenerator(repo, ollama, dictionary)
    template = GenerationTemplate(category="tee", variations=1)
    context = {"style_code": "STYLE_F", "desc": "普通描述"}
    result = generator.generate(template, "model", context)
    assert "STYLE_F" in result.bodies[0]
