#!/usr/bin/env python3
"""本地一键检查脚本：ruff、mypy、pytest。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "-m", "ruff", "check", "--fix"],
    [sys.executable, "-m", "ruff", "format"],
    [sys.executable, "-m", "mypy", "core", "app", "scripts"],
    [sys.executable, "-m", "pytest", "tests"],
]


def run() -> int:
    for cmd in COMMANDS:
        print(f"\n[run_checks] 执行：{' '.join(cmd)}")
        try:
            subprocess.run(cmd, cwd=ROOT, check=True)
        except subprocess.CalledProcessError as exc:  # pragma: no cover
            print(f"[run_checks] 命令失败，退出码 {exc.returncode}")
            return exc.returncode
    print("\n[run_checks] 所有检查通过。")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
