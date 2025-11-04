from __future__ import annotations

from app.desktop.services.device_scanner import (
    DeviceScanner,
    DeviceScannerError,
    RunnerResult,
)


def _make_runner(output: str, code: int = 0) -> callable:
    def runner(command):
        assert command[:3] == ["adb", "devices", "-l"]
        return RunnerResult(returncode=code, stdout=output, stderr="" if code == 0 else "boom")

    return runner


def test_device_scanner_parses_devices():
    stdout = """List of devices attached
0123456789ABCDEF\tdevice product:sagit model:MI_6 device:sagit transport_id:1
ZXCVBNM123\tunauthorized

"""
    scanner = DeviceScanner(adb_path="adb", runner=_make_runner(stdout))
    devices = scanner.scan()
    assert len(devices) == 2
    first = devices[0]
    assert first.serial == "0123456789ABCDEF"
    assert first.status == "device"
    assert first.product == "sagit"
    assert first.model == "MI_6"
    second = devices[1]
    assert second.serial == "ZXCVBNM123"
    assert second.status == "unauthorized"


def test_device_scanner_handles_empty_output():
    scanner = DeviceScanner(adb_path="adb", runner=_make_runner("List of devices attached\n\n"))
    assert scanner.scan() == []


def test_device_scanner_raises_on_failure():
    scanner = DeviceScanner(adb_path="adb", runner=_make_runner("", code=1))
    try:
        scanner.scan()
    except DeviceScannerError as exc:
        assert "adb devices" in exc.args[0] or exc.args[0]
    else:  # pragma: no cover - ensure exception is raised
        raise AssertionError("expected DeviceScannerError")

