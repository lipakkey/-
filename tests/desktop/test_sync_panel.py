import pytest
from types import SimpleNamespace

QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QtCore = pytest.importorskip("PySide6.QtCore")

from app.desktop.ui.sync_panel import SyncPanel


class StubViewModel(QtCore.QObject):
    sync_message = QtCore.Signal(str)
    status_changed = QtCore.Signal(object)
    queue_changed = QtCore.Signal(object)
    scan_completed = QtCore.Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._configured = []
        self.status_payload: dict = {"devices": {}}

    def register_bundles(self, bundles) -> None:
        pass

    def configured_devices(self):
        return self._configured

    def refresh_status(self) -> None:
        self.status_changed.emit(self.status_payload)

    def scan_devices(self) -> None:
        pass

    def push_all_devices(self) -> None:
        pass

    def pull_all_devices(self) -> None:
        pass


@pytest.fixture
def qapp():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


def test_sync_panel_updates_tables(qapp):
    vm = StubViewModel()
    vm._configured = [SimpleNamespace(device_id="dev1", adb_serial="ABC123")]
    vm.status_payload = {"devices": {"dev1": {"last_batch": "STYLE1"}}}
    panel = SyncPanel(viewmodel=vm)

    vm.queue_changed.emit({"dev1": 2})

    assert panel.table.rowCount() == 1
    assert panel.table.item(0, 0).text() == "dev1"
    assert panel.queue_list.count() == 1


def test_sync_panel_logs_messages(qapp):
    vm = StubViewModel()
    vm._configured = [SimpleNamespace(device_id="dev1", adb_serial="ABC123")]
    panel = SyncPanel(viewmodel=vm)

    vm.sync_message.emit("测试消息")
    assert panel.log_table.rowCount() == 1
    assert "测试消息" in panel.log_table.item(0, 1).text()

    vm.scan_completed.emit([SimpleNamespace(serial="ABC123", status="device")])
    assert panel.scan_status.get("ABC123") == "device"
