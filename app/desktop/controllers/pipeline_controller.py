from __future__ import annotations

from typing import Iterable

from app.desktop.core.background import Worker
from app.desktop.core.logger import get_logger
from app.desktop.models.pipeline_config import PipelineConfig
from app.desktop.models.task_bundle import TaskBundle
from app.desktop.services.central_kitchen_runner import CentralKitchenRunner

logger = get_logger("pipeline.controller")


class PipelineController:
    def __init__(self, presenter) -> None:
        self.presenter = presenter
        self.runner = CentralKitchenRunner()
        self._worker: Worker | None = None

    def update_config(self, config: PipelineConfig) -> None:
        self.runner.update_config(config)

    def run_async(self) -> None:
        worker = Worker(
            self.runner.run_pipeline,
            kwargs={"progress": self.presenter.on_progress},
        )
        worker.finished.connect(self._handle_finished)  # type: ignore[arg-type]
        worker.failed.connect(self.presenter.on_failed)  # type: ignore[arg-type]
        self._worker = worker
        worker.start()

    def _handle_finished(self, bundles) -> None:
        self.presenter.on_finished(bundles)
        self._notify_new_bundles(bundles)
        self._worker = None

    def _notify_new_bundles(self, bundles: Iterable[TaskBundle]) -> None:
        for bundle in bundles:
            logger.info("任务包生成: %s -> %s", bundle.device_id, bundle.bundle_path)
