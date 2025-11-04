#!/usr/bin/env python3
"""Print a brief summary of delivery_report.json."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from json import JSONDecodeError
from pathlib import Path

LOG = logging.getLogger("report_summary")


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s",
        stream=sys.stdout,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Report summary helper")
    parser.add_argument(
        "--report", type=Path, default=Path("data/demo_output/reports/delivery_report.json")
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="输出调试日志",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="额外展示前 N 条 entries 明细（默认不展示）",
    )
    args = parser.parse_args()
    configure_logging(args.verbose)

    if not args.report.exists():
        LOG.error("报告 %s 不存在", args.report)
        return 2

    try:
        data = json.loads(args.report.read_text(encoding="utf-8"))
    except JSONDecodeError as exc:
        LOG.error("解析报告 %s 失败：%s", args.report, exc)
        return 1

    summary = data.get("summary", {})
    total = summary.get("total")
    success = summary.get("success")
    failures = summary.get("failures")

    LOG.info("任务汇总：total=%s success=%s failures=%s", total, success, failures)
    per_device = summary.get("per_device", {})
    for device, count in sorted(per_device.items()):
        LOG.info("  设备 %s: %s", device, count)

    if args.top > 0:
        entries = data.get("entries", [])
        for idx, entry in enumerate(entries[: args.top], start=1):
            style = entry.get("style_code")
            device = entry.get("device_id") or "-"
            status = "FAIL" if entry.get("flags", {}).get("needs_manual_review") else "OK"
            LOG.info("  #%s %s (%s) -> %s", idx, style, device, status)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
