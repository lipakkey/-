from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AppState:
    current_report: Optional[str] = None
    selected_batch: Optional[str] = None
    sync_status: Optional[str] = None


__all__ = ["AppState"]
