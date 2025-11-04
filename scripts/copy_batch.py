#!/usr/bin/env python3
"""Copy Output_Batch_Phone_* directories to an external location."""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

LOG = logging.getLogger("copy_batch")


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s",
        stream=sys.stdout,
    )


def discover_batches(source: Path) -> dict[str, Path]:
    batches: dict[str, Path] = {}
    for path in sorted(source.glob("Output_Batch_Phone_*")):
        if path.is_dir():
            batches[path.name] = path
    return batches


def normalise_selector(selector: str) -> str:
    if selector.isdigit():
        return f"Output_Batch_Phone_{int(selector)}"
    return selector


def copy_batches(
    source: Path,
    target: Path,
    selectors: list[str] | None,
    overwrite: bool,
    dry_run: bool,
) -> int:
    batches = discover_batches(source)
    if not batches:
        LOG.error("在 %s 下未找到任何 Output_Batch_Phone_* 目录", source)
        return 2

    if selectors:
        wanted = [normalise_selector(sel) for sel in selectors]
    else:
        wanted = list(batches.keys())

    missing = [sel for sel in wanted if sel not in batches]
    if missing:
        for item in missing:
            LOG.error("指定的批次 %s 不存在", item)
        return 2

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    exit_code = 0
    for key in wanted:
        src = batches[key]
        dest = target / key
        if dry_run:
            LOG.info("[dry-run] 拷贝 %s -> %s", src, dest)
            continue

        if dest.exists():
            if overwrite:
                LOG.debug("目标 %s 已存在，执行覆盖", dest)
                shutil.rmtree(dest)
            else:
                LOG.error("目标 %s 已存在（使用 --overwrite 覆盖或 --dry-run 演练）", dest)
                exit_code = 1
                continue

        LOG.info("拷贝 %s -> %s", src, dest)
        shutil.copytree(src, dest)
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="复制手机批次目录到指定位置")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("data/demo_output"),
        help="输入目录（默认：data/demo_output）",
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="目标目录，复制后的 Output_Batch_Phone_* 将放置于此",
    )
    parser.add_argument(
        "--batch",
        dest="batches",
        action="append",
        help="仅复制指定批次（可多次传入，支持编号如 1 或完整目录名）",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="目标存在时删除后再复制",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅输出计划，不实际复制",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="输出调试日志",
    )
    args = parser.parse_args()

    configure_logging(args.verbose)

    if not args.source.exists():
        LOG.error("源目录 %s 不存在", args.source)
        return 2
    if not args.source.is_dir():
        LOG.error("源路径 %s 不是目录", args.source)
        return 2

    batches = args.batches if args.batches is not None else None
    return copy_batches(args.source, args.target, batches, args.overwrite, args.dry_run)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
