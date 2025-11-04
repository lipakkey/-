#!/usr/bin/env python3
"""Validate Output_Batch and report manifest structures."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Iterable
from json import JSONDecodeError
from pathlib import Path

LOG = logging.getLogger("validate_manifest")

REQUIRED_ENTRY_KEYS = {"style_code", "paths", "media", "pricing"}
REQUIRED_PATH_KEYS = {"root", "title", "descriptions"}
REQUIRED_MEDIA_KEYS = {"primary", "variants"}
REQUIRED_PRICING_KEYS = {"price", "macro_delay"}
REQUIRED_DELAY_KEYS = {"min", "max"}
LEGACY_ENTRY_KEYS = {
    "style_code",
    "title_file",
    "description_files",
    "images",
    "price",
    "macro_delay",
}


def iter_batch_manifests(batch_root: Path) -> Iterable[Path]:
    yield from batch_root.glob("Output_Batch_Phone_*/batch_manifest.json")


def _ensure_keys(node: dict, required: set[str], context: str, errors: list[str]) -> None:
    missing = required - node.keys()
    if missing:
        errors.append(f"{context} missing keys: {sorted(missing)}")


def _load_json(path: Path, errors: list[str]) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path}: file not found")
        return {}
    except JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON ({exc})")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path}: expected object at top level")
        return {}
    return data


def validate_batch_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    data = _load_json(path, errors)
    if not data:
        return errors
    if "entries" not in data:
        return [f"{path}: expected dict with 'entries'"]

    for entry in data["entries"]:
        if not isinstance(entry, dict):
            errors.append(f"{path}: entry must be object")
            continue

        if REQUIRED_ENTRY_KEYS.issubset(entry.keys()):
            paths = entry.get("paths", {})
            if isinstance(paths, dict):
                _ensure_keys(paths, REQUIRED_PATH_KEYS, f"{path} entry.paths", errors)
            else:
                errors.append(f"{path}: entry.paths must be object")

            media = entry.get("media", {})
            if isinstance(media, dict):
                _ensure_keys(media, REQUIRED_MEDIA_KEYS, f"{path} entry.media", errors)
            else:
                errors.append(f"{path}: entry.media must be object")

            pricing = entry.get("pricing", {})
            if isinstance(pricing, dict):
                _ensure_keys(pricing, REQUIRED_PRICING_KEYS, f"{path} entry.pricing", errors)
                macro = pricing.get("macro_delay", {})
                if isinstance(macro, dict):
                    _ensure_keys(
                        macro,
                        REQUIRED_DELAY_KEYS,
                        f"{path} entry.pricing.macro_delay",
                        errors,
                    )
                else:
                    errors.append(f"{path}: entry.pricing.macro_delay must be object")
            else:
                errors.append(f"{path}: entry.pricing must be object")
        elif LEGACY_ENTRY_KEYS.issubset(entry.keys()):
            macro = entry.get("macro_delay")
            if not isinstance(macro, list) or len(macro) != 2:
                errors.append(f"{path}: legacy macro_delay 应为长度为 2 的列表")
        else:
            errors.append(f"{path}: entry 缺少必要字段（支持新旧结构）")
    return errors


def validate_report(report_path: Path) -> list[str]:
    load_errors: list[str] = []
    data = _load_json(report_path, load_errors)
    if load_errors:
        return load_errors
    errors: list[str] = []
    if "summary" not in data or "entries" not in data:
        errors.append(f"{report_path}: must contain summary + entries")
    return errors


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s",
        stream=sys.stdout,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate manifest/report structure")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/demo_output"),
        help="目录，包含 Output_Batch_Phone_* 子文件夹（默认: data/demo_output）",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="指定 delivery_report.json 路径，未提供时默认使用 <output>/reports/delivery_report.json",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="输出详细日志",
    )
    args = parser.parse_args()
    configure_logging(args.verbose)

    if not args.output.exists():
        LOG.error("输出目录 %s 不存在", args.output)
        return 2
    if not args.output.is_dir():
        LOG.error("输出路径 %s 不是目录", args.output)
        return 2

    errors: list[str] = []
    manifests = list(sorted(iter_batch_manifests(args.output)))
    if not manifests:
        LOG.warning("未在 %s 下找到任何批次 manifest", args.output)
    for manifest in manifests:
        LOG.debug("校验 manifest: %s", manifest)
        errors.extend(validate_batch_manifest(manifest))

    report_path = args.report if args.report is not None else args.output / "reports" / "delivery_report.json"
    if report_path.exists():
        LOG.debug("校验报告: %s", report_path)
        errors.extend(validate_report(report_path))
    else:
        LOG.info("未找到报告文件 %s，跳过报告校验", report_path)

    if errors:
        LOG.error("发现 %s 个问题：", len(errors))
        for err in errors:
            LOG.error(" - %s", err)
        return 1
    LOG.info("所有批次 manifest 与报告结构校验通过")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
