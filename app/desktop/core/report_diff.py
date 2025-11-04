from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, MutableMapping, Optional, Set


@dataclass(frozen=True)
class ReportDiff:
    new_styles: Set[str]
    missing_styles: Set[str]
    failed_styles: Set[str]


def _build_index(report: Mapping[str, object]) -> MutableMapping[str, Mapping[str, object]]:
    index: MutableMapping[str, Mapping[str, object]] = {}
    entries = report.get("entries", [])
    if isinstance(entries, list):
        for entry in entries:
            if isinstance(entry, Mapping) and "style_code" in entry:
                index[str(entry["style_code"])] = entry  # type: ignore[assignment]
    return index


def diff_reports(current: Mapping[str, object], previous: Optional[Mapping[str, object]] = None) -> ReportDiff:
    current_index = _build_index(current)
    previous_index = _build_index(previous or {})

    new_styles = set(current_index.keys()) - set(previous_index.keys())
    missing_styles = set(previous_index.keys()) - set(current_index.keys())

    failed_styles: Set[str] = set()
    summary = current.get("summary", {})
    if isinstance(summary, Mapping):
        failures = summary.get("failures")
        if isinstance(failures, list):
            for message in failures:
                if isinstance(message, str):
                    failed_styles.add(message.split(":", 1)[0].strip())

    return ReportDiff(new_styles=new_styles, missing_styles=missing_styles, failed_styles=failed_styles)


__all__ = ["ReportDiff", "diff_reports"]
