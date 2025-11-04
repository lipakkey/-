#!/usr/bin/env python3
"""Validate Output_Batch and report manifest structures."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path

REQUIRED_ENTRY_KEYS = {"style_code", "paths", "media", "pricing"}
REQUIRED_PATH_KEYS = {"root", "title", "descriptions"}
REQUIRED_MEDIA_KEYS = {"primary", "variants"}
REQUIRED_PRICING_KEYS = {"price", "macro_delay"}
REQUIRED_DELAY_KEYS = {"min", "max"}


def iter_batch_manifests(batch_root: Path) -> Iterable[Path]:
    yield from batch_root.glob("Output_Batch_Phone_*/batch_manifest.json")


def _ensure_keys(node: dict, required: set[str], context: str, errors: list[str]) -> None:
    missing = required - node.keys()
    if missing:
        errors.append(f"{context} missing keys: {sorted(missing)}")


def validate_batch_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "entries" not in data:
        return [f"{path}: expected dict with 'entries'"]

    for entry in data["entries"]:
        if not isinstance(entry, dict):
            errors.append(f"{path}: entry must be object")
            continue
        _ensure_keys(entry, REQUIRED_ENTRY_KEYS, f"{path} entry", errors)

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
                _ensure_keys(macro, REQUIRED_DELAY_KEYS, f"{path} entry.pricing.macro_delay", errors)
            else:
                errors.append(f"{path}: entry.pricing.macro_delay must be object")
        else:
            errors.append(f"{path}: entry.pricing must be object")
    return errors


def validate_report(report_path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(report_path.read_text(encoding="utf-8"))
    if "summary" not in data or "entries" not in data:
        errors.append(f"{report_path}: must contain summary + entries")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate manifest/report structure")
    parser.add_argument("--output", type=Path, default=Path("data/demo_output"))
    args = parser.parse_args()

    errors: list[str] = []
    for manifest in iter_batch_manifests(args.output):
        errors.extend(validate_batch_manifest(manifest))

    report = args.output / "reports" / "delivery_report.json"
    if report.exists():
        errors.extend(validate_report(report))

    if errors:
        print("Found issues:")
        for err in errors:
            print(" -", err)
        return 1
    print("All manifests look good.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
