from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from app.desktop.core.logger import get_logger
from app.desktop.models.report_entry import ReportEntry

logger = get_logger("report.controller")


class ReportController:
    def __init__(self, report_root: Path | str | None = None, sync_root: Path | str | None = None) -> None:
        self.report_root = Path(report_root or "reports")
        self.sync_root = Path(sync_root or "sync")

    def list_reports(self) -> Iterable[ReportEntry]:
        reports = sorted(self.report_root.rglob("delivery_report.json"), reverse=True)
        entries: list[ReportEntry] = []
        for report_file in reports:
            try:
                data = json.loads(report_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logger.warning("跳过无法解析的报告: %s", report_file)
                continue

            created_at = datetime.fromtimestamp(report_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            per_device = data.get("summary", {}).get("per_device", {})
            if not per_device:
                per_device = self._fallback_per_device(data)

            for device_id, total in per_device.items():
                failures = self._collect_failures(device_id, data)
                screenshots = self._collect_screenshots(device_id)
                success = max(total - len(failures), 0)
                entries.append(
                    ReportEntry(
                        title=f"{report_file.parent.name or report_file.stem} - {device_id}",
                        created_at=created_at,
                        report_path=report_file,
                        device_id=device_id,
                        total=int(total),
                        success=success,
                        failures=failures,
                        screenshots=screenshots,
                    )
                )
        return entries

    def _fallback_per_device(self, data: dict) -> dict[str, int]:
        result: dict[str, int] = {}
        for entry in data.get("entries", []):
            device = entry.get("device_id")
            if not device:
                continue
            result[device] = result.get(device, 0) + 1
        return result

    def _collect_failures(self, device_id: str, data: dict) -> List[str]:
        failures: List[str] = []
        for failure in data.get("failures", []):
            if isinstance(failure, str):
                failures.append(failure)
            elif isinstance(failure, dict) and failure.get("device_id") == device_id:
                message = failure.get("reason") or str(failure)
                failures.append(message)
        for entry in data.get("entries", []):
            if entry.get("device_id") != device_id:
                continue
            status = entry.get("status")
            if status and status.lower() != "success":
                failures.append(f"{entry.get('style_code', '-')}: {status}")
        return failures

    def _collect_screenshots(self, device_id: str) -> List[Path]:
        screenshots: List[Path] = []
        device_dir = self.sync_root / f"device_{device_id}"
        if not device_dir.exists():
            return screenshots
        for result_file in device_dir.rglob("result.json"):
            try:
                payload = json.loads(result_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            shot = payload.get("screenshot")
            if isinstance(shot, str) and shot:
                shot_path = (result_file.parent / shot).resolve()
                screenshots.append(shot_path)
        return screenshots
