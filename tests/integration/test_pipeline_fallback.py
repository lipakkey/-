from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from core.config.models import (
    CentralKitchenConfig,
    DelayConfig,
    DeviceAssignment,
    GenerationTemplate,
    PriceConfig,
    SensitiveDictionary,
    WatermarkConfig,
)
from core.pipeline import CentralPipeline
from core.reporting.report_builder import ReportBuilder
from core.text import ollama_client


def _create_sample_input(root: Path) -> None:
    style_dir = root / "STYLE001"
    style_dir.mkdir(parents=True, exist_ok=True)
    (style_dir / "desc.txt").write_text("AMIRI 秋冬新款", encoding="utf-8")
    image_path = style_dir / "main_1.jpg"
    Image.new("RGB", (100, 100), color=(200, 200, 200)).save(image_path)


def test_pipeline_with_mock_ollama(monkeypatch, tmp_path):
    input_root = tmp_path / "Input_Raw"
    output_root = tmp_path / "Output"
    _create_sample_input(input_root)

    def fake_generate(self, model: str, prompt: str, retries: int = 2) -> str:
        return "克罗❤️ 秋冬新品，面料舒适，值得入手！"

    monkeypatch.setattr(ollama_client.OllamaClient, "generate", fake_generate)

    config = CentralKitchenConfig(
        input_root=input_root,
        output_root=output_root,
        price=PriceConfig(base_yuan=199.0, random_tail=False),
        delays=DelayConfig(),
        device_assignment=DeviceAssignment(device_ids=("device1", "device2", "device3")),
        template=GenerationTemplate(category="tee", variations=2),
        sensitive_dictionary=SensitiveDictionary(),
        watermark=WatermarkConfig(opacity=0.1),
    )

    pipeline = CentralPipeline(config)
    result = pipeline.run()
    assert len(result.entries) == 1
    assert result.failures == ()

    batch_dir = output_root / "Output_Batch_Phone_1" / "STYLE001"
    assert (batch_dir / "text" / "title.txt").exists()
    assert (batch_dir / "images" / "main_1.jpg").exists()

    report_path = ReportBuilder().write(result, output_root / "reports")
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["summary"]["success"] == 1
    assert data["entries"][0]["style_code"] == "STYLE001"
