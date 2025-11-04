from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable, Iterable, Sequence

from app.desktop.core.logger import get_logger
from app.desktop.models.pipeline_config import PipelineConfig
from app.desktop.models.task_bundle import TaskBundle

ProgressCallback = Callable[[int, str], None]
logger = get_logger("pipeline.runner")


class CentralKitchenRunner:
    """封装中央厨房 CLI 调用逻辑。"""

    def __init__(self) -> None:
        self._config = PipelineConfig(
            input_root=Path("data/Input_Raw"),
            output_root=Path("data/Output"),
            devices=("phone1", "phone2", "phone3"),
            price=299.0,
        )

    def update_config(self, config: PipelineConfig) -> None:
        self._config = config

    def run_pipeline(self, progress: ProgressCallback | None = None) -> Iterable[TaskBundle]:
        command = [
            sys.executable,
            str(Path("scripts/central_kitchen.py").resolve()),
            "--input",
            str(self._config.input_root),
            "--output",
            str(self._config.output_root),
            "--devices",
            ",".join(self._config.devices),
            "--price",
            f"{self._config.price:.2f}",
            "--category",
            "tee",
            "--report-dir",
            "reports",
        ]

        logger.info("启动中央厨房: %s", " ".join(command))
        if progress:
            progress(5, "中央厨房任务启动")

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=Path("."),
        )

        if process.returncode != 0:
            logger.error("中央厨房失败: %s", process.stderr.strip())
            raise RuntimeError(f"中央厨房失败: {process.stderr.strip()}")

        try:
            summary = json.loads(process.stdout or "{}")
        except json.JSONDecodeError as exc:  # pragma: no cover - 输出异常
            logger.error("解析中央厨房输出失败: %s", exc)
            raise RuntimeError("解析中央厨房输出失败") from exc

        if progress:
            progress(40, "中央厨房生成完成，解析输出中")

        bundles = self._collect_bundles(self._config.devices, self._config.output_root)

        logger.info(
            "中央厨房完成: report=%s success=%s failures=%s",
            summary.get("report"),
            summary.get("success"),
            summary.get("failures"),
        )

        if progress:
            progress(100, "中央厨房任务完成")
        return bundles

    def _collect_bundles(self, devices: Sequence[str], output_root: Path) -> list[TaskBundle]:
        bundles: list[TaskBundle] = []
        for device in devices:
            bundle_dir = output_root / f"Output_Batch_{device}"
            manifest_path = bundle_dir / "batch_manifest.json"
            style_count = self._extract_style_count(manifest_path, bundle_dir)
            bundles.append(
                TaskBundle(
                    bundle_path=bundle_dir,
                    device_id=device,
                    style_count=style_count,
                    manifest_path=manifest_path if manifest_path.exists() else None,
                )
            )
        return bundles

    @staticmethod
    def _extract_style_count(manifest_path: Path, bundle_dir: Path) -> int:
        if manifest_path.exists():
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {}
            style_count = data.get("summary", {}).get("style_count")
            if isinstance(style_count, int):
                return style_count
        if bundle_dir.exists():
            return len([p for p in bundle_dir.iterdir() if p.is_dir()])
        return 0
