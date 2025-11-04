from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class ReportLoader:
    """读取中央厨房 delivery_report.json，返回原始数据结构。"""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> Dict[str, Any]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self._validate(data)
        return data

    def _validate(self, data: Dict[str, Any]) -> None:
        if "summary" not in data or "entries" not in data:
            raise ValueError("report 缺少 summary 或 entries 字段")
        if not isinstance(data["entries"], list):
            raise ValueError("entries 字段必须是列表")


__all__ = ["ReportLoader"]
