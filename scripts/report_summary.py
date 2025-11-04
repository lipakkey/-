#!/usr/bin/env python3
"""Print a brief summary of delivery_report.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Report summary helper")
    parser.add_argument(
        "--report", type=Path, default=Path("data/demo_output/reports/delivery_report.json")
    )
    args = parser.parse_args()

    data = json.loads(args.report.read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    print(
        f"Total: {summary.get('total')}, Success: {summary.get('success')}, Failures: {summary.get('failures')}"
    )
    per_device = summary.get("per_device", {})
    for device, count in per_device.items():
        print(f"  {device}: {count}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
