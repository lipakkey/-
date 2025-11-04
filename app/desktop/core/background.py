from __future__ import annotations

from typing import Any, Callable, Iterable, Optional

from PySide6.QtCore import QObject, QThread, Signal


ProgressCallback = Callable[[int, str], None]


class Worker(QObject):
    finished = Signal(object)
    failed = Signal(str)
    progress = Signal(int, str)

    def __init__(
        self,
        fn: Callable[..., Any],
        *,
        args: Optional[Iterable[Any]] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._fn = fn
        self._args = list(args or ())
        self._kwargs = dict(kwargs or {})
        self._thread: QThread | None = None

    def start(self) -> None:
        thread = QThread()
        self.moveToThread(thread)
        thread.started.connect(self._run)  # type: ignore[arg-type]
        thread.start()
        self._thread = thread

    def _run(self) -> None:
        try:
            result = self._fn(*self._args, **self._kwargs)
        except Exception as exc:  # pragma: no cover - runtime diagnostics
            self.failed.emit(str(exc))
        else:
            self.finished.emit(result)
        finally:
            if self._thread:
                self._thread.quit()
                self._thread.wait()
                self._thread = None

