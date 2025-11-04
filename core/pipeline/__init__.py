"""中央厨房流水线入口。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from core.config.models import CentralKitchenConfig, ManifestEntry
from core.pipeline.partitioner import TaskPartitioner
from core.pipeline.scanner import InputScanner
from core.pipeline.style_processor import StyleProcessor
from core.text.generator import CopywritingGenerator
from core.text.ollama_client import OllamaClient
from core.text.template_repository import TemplateRepository
from core.watermark.processor import WatermarkProcessor


@dataclass(slots=True)
class PipelineResult:
    entries: Sequence[ManifestEntry]
    failures: Sequence[str]


class CentralPipeline:
    """串联中央厨房的各个处理步骤。"""

    def __init__(self, config: CentralKitchenConfig) -> None:
        self.config = config
        template_repo = TemplateRepository()
        ollama = OllamaClient()
        generator = CopywritingGenerator(template_repo, ollama, config.sensitive_dictionary)
        watermarker = WatermarkProcessor(config.watermark)
        self.scanner = InputScanner(config.input_root)
        self.processor = StyleProcessor(config, generator, watermarker)
        self.partitioner = TaskPartitioner(config)

    def run(self) -> PipelineResult:
        entries: list[ManifestEntry] = []
        failures: list[str] = []
        for raw in self.scanner.scan():
            try:
                entries.append(self.processor.process(raw))
            except Exception as exc:  # pragma: no cover - 记录错误并继续
                failures.append(f"{raw.style_code}: {exc}")
        batches = self.partitioner.partition(entries)
        self.partitioner.export(batches)
        return PipelineResult(entries=tuple(entries), failures=tuple(failures))


__all__ = ["CentralPipeline", "PipelineResult"]
