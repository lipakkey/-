#!/usr/bin/env python3
"""本地一键检查脚本：lint / typecheck / tests / 工具校验。"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS: list[list[str]] = [
    [sys.executable, "-m", "ruff", "check", "--fix"],
    [sys.executable, "-m", "ruff", "format"],
    [sys.executable, "-m", "mypy", "core", "app", "scripts"],
    [sys.executable, "-m", "pytest", "tests"],
    [sys.executable, "scripts/validate_manifest.py", "--output", "data/demo_output"],
    [
        sys.executable,
        "scripts/report_summary.py",
        "--report",
        "data/demo_output/reports/delivery_report.json",
    ],
    [
        sys.executable,
        "scripts/copy_batch.py",
        "--source",
        "data/demo_output",
        "--target",
        ".tmp/run_checks_copy",
        "--dry-run",
    ],
]


def run(commands: Sequence[Sequence[str]]) -> int:
    for cmd in commands:
        print(f"\n[run_checks] 执行：{' '.join(cmd)}")
        try:
            subprocess.run(cmd, cwd=ROOT, check=True)
        except subprocess.CalledProcessError as exc:  # pragma: no cover
            print(f"[run_checks] 命令失败，退出码 {exc.returncode}")
            return exc.returncode
    print("\n[run_checks] 所有检查通过 ✅")
    return 0


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description="运行项目完整检查流程")
    parser.add_argument(
        "--extra",
        nargs=argparse.REMAINDER,
        help="附加命令（会在默认命令之后执行），例如 --extra python scripts/report_summary.py --top 3",
    )
    cli_args = parser.parse_args()

    commands = COMMANDS.copy()
    if cli_args.extra:
        commands.append([sys.executable] + cli_args.extra)

    raise SystemExit(run(commands))
