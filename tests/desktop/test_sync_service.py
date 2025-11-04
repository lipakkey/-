from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from app.desktop.services.sync_service import (
    ConfigurationError,
    DeviceConfig,
    RunnerResult,
    SyncCommandError,
    SyncService,
)


class StubRunner:
    def __init__(self, results: list[RunnerResult]) -> None:
        self.results = results
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str]) -> RunnerResult:
        self.commands.append(command)
        if not self.results:
            return RunnerResult(returncode=0)
        return self.results.pop(0)


def fixed_clock(times: list[str]):
    values = [datetime.fromisoformat(ts) for ts in times]

    def _inner() -> datetime:
        if not values:
            return datetime.fromisoformat(times[-1])
        return values.pop(0)

    return _inner


def create_style_batch(batch_dir: Path) -> None:
    style_dir = batch_dir / "STYLE001"
    style_dir.mkdir(parents=True)
    (style_dir / "1.jpg").write_bytes(b"fake")


def read_status(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_push_batch_updates_status(tmp_path):
    runner = StubRunner(
        [
            RunnerResult(returncode=0),
            RunnerResult(returncode=0),
        ]
    )
    clock = fixed_clock(["2025-11-04T10:00:00"])

    service = SyncService(
        tmp_path,
        devices=[DeviceConfig(device_id="phone1", adb_serial="ABC123")],
        runner=runner,
        clock=clock,
    )

    batch_dir = tmp_path / "Output_Batch_Phone_1"
    create_style_batch(batch_dir)

    service.push_batch("phone1", batch_dir)

    assert runner.commands == [
        ["adb", "-s", "ABC123", "shell", "mkdir", "-p", "/sdcard/XianyuTasks/Todo"],
        ["adb", "-s", "ABC123", "push", str(batch_dir), "/sdcard/XianyuTasks/Todo"],
    ]

    status = read_status(service.status_path)
    assert status["devices"]["phone1"]["last_batch"] == "Output_Batch_Phone_1"
    assert (
        status["devices"]["phone1"].get("last_manifest", {}).get("summary", {}).get("style_count")
        == 1
    )


def test_pull_logs_writes_to_sync_folder(tmp_path):
    runner = StubRunner([RunnerResult(returncode=0)])
    clock = fixed_clock(["2025-11-04T12:00:00"])
    service = SyncService(
        tmp_path,
        devices=[DeviceConfig(device_id="phone1", adb_serial="ABC123")],
        runner=runner,
        clock=clock,
    )

    target_dir = service.pull_logs("phone1")

    assert target_dir.exists()
    assert "device_phone1" in str(target_dir)
    assert runner.commands == [
        ["adb", "-s", "ABC123", "pull", "/sdcard/XianyuTasks/Done", str(target_dir)]
    ]
    status = read_status(service.status_path)
    assert status["devices"]["phone1"]["last_pull_path"] == str(target_dir)


def test_push_failure_records_error(tmp_path):
    runner = StubRunner(
        [
            RunnerResult(returncode=0),
            RunnerResult(returncode=1, stderr="permission denied"),
        ]
    )
    service = SyncService(
        tmp_path,
        devices=[DeviceConfig(device_id="phone1", adb_serial="ABC123")],
        runner=runner,
    )

    batch_dir = tmp_path / "Output_Batch_Phone_1"
    create_style_batch(batch_dir)

    with pytest.raises(SyncCommandError):
        service.push_batch("phone1", batch_dir)

    status = read_status(service.status_path)
    assert status["devices"]["phone1"]["last_error"] == "permission denied"


def test_load_devices_from_yaml(tmp_path):
    config = tmp_path / "device_map.yaml"
    config.write_text(
        """
devices:
  - device_id: phone1
    adb_serial: ABC123
    remote_root: /sdcard/CustomRoot
""",
        encoding="utf-8",
    )

    service = SyncService(tmp_path, config_path=config)
    assert service.list_devices()[0].remote_root == "/sdcard/CustomRoot"


def test_missing_config_raises(tmp_path):
    with pytest.raises(ConfigurationError):
        SyncService(tmp_path, config_path=tmp_path / "missing.yaml")
