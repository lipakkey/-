#!/usr/bin/env python3
"""
Generate demo Input_Raw data and optionally run the central kitchen pipeline.

Usage examples:
    python scripts/run_demo.py
    python scripts/run_demo.py --input data/demo_input/Input_Raw --output data/demo_output --no-run
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Sequence

import yaml
from PIL import Image, ImageDraw, ImageFont

DEFAULT_STYLES: list[dict[str, Any]] = [
    {
        "style_code": "STYLE_A",
        "description": (
            "克罗❤️ 2025 秋冬重磅短袖，雪花图案点缀，男女同款宽松版。"
            "尺码齐全，面料舒适透气，适合日常穿搭。"
        ),
        "price": 299.0,
        "colors": ["黑色", "白色"],
        "sizes": ["S", "M", "L", "XL"],
        "image_count": 2,
    },
    {
        "style_code": "STYLE_B",
        "description": (
            "Chrome Hearts 经典系列，烫钻工艺，背后字母印花。"
            "320 克重磅面料，做工精细，质感出众。"
        ),
        "price": 329.0,
        "colors": ["黑色", "水洗灰", "咖啡色"],
        "sizes": ["M", "L", "XL", "XXL"],
        "image_count": 3,
    },
    {
        "style_code": "STYLE_C",
        "description": (
            "秋冬潮流推荐款，牛仔面料拼接设计，宽松休闲版型。"
            "男女皆宜，搭配百搭，支持尺码咨询。"
        ),
        "price": 309.0,
        "colors": ["靛蓝", "浅蓝"],
        "sizes": ["S", "M", "L"],
        "image_count": 2,
    },
]


def load_styles(spec_path: Path | None) -> list[dict[str, Any]]:
    if spec_path is None:
        return DEFAULT_STYLES
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("spec 文件必须是列表")
    return data  # type: ignore[return-value]


def generate_image(path: Path, lines: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img_size = (800, 800)
    background = Image.new("RGB", img_size, color=(242, 242, 242))
    draw = ImageDraw.Draw(background)
    font = ImageFont.load_default()
    y = 40
    for line in lines:
        draw.text((40, y), line, fill=(40, 40, 40), font=font)
        y += 60
    draw.rectangle([60, 160, 740, 740], outline=(120, 120, 120), width=4)
    background.save(path, format="JPEG", quality=92)


def write_meta(style: dict[str, Any], style_path: Path) -> None:
    meta = {
        "style_code": style["style_code"],
        "price": style.get("price", 0),
        "colors": style.get("colors", []),
        "sizes": style.get("sizes", []),
        "stock": style.get("stock", 50),
        "macro_delay": style.get("macro_delay", [10, 45]),
    }
    (style_path / "meta.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True), encoding="utf-8")


def create_style(style: dict[str, Any], root: Path) -> None:
    style_code = style.get("style_code")
    if not style_code:
        raise ValueError("style_code 不能为空")

    style_path = root / style_code
    style_path.mkdir(parents=True, exist_ok=True)
    desc_text = style.get("description", "示例文案")
    (style_path / "desc.txt").write_text(desc_text, encoding="utf-8")

    image_count = int(style.get("image_count", 2))
    for idx in range(1, image_count + 1):
        generate_image(style_path / f"main_{idx}.jpg", [style_code, f"主图 {idx}"])

    for color in style.get("colors", []):
        safe_color = str(color).strip().replace(" ", "_")
        generate_image(style_path / f"color_{safe_color}_1.jpg", [style_code, f"颜色 {color}"])

    write_meta(style, style_path)


def create_input_dataset(styles: Iterable[dict[str, Any]], input_root: Path) -> None:
    for style in styles:
        create_style(style, input_root)


def run_pipeline(
    input_root: Path,
    output_root: Path,
    devices: Sequence[str],
    price: float | None,
    category: str,
    watermark: str,
) -> None:
    device_arg = ",".join(devices)
    cmd = [
        sys.executable,
        "-m",
        "scripts.central_kitchen",
        "--input",
        str(input_root),
        "--output",
        str(output_root),
        "--devices",
        device_arg,
        "--category",
        category,
        "--watermark",
        watermark,
    ]
    if price is not None:
        cmd.extend(["--price", str(price)])

    print(">> 运行中央厨房:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成示例 Input_Raw 数据，并可选运行中央厨房")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/demo_input/Input_Raw"),
        help="示例素材输出目录",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/demo_output"),
        help="中央厨房示例输出目录",
    )
    parser.add_argument("--spec", type=Path, help="自定义样式 JSON 文件")
    parser.add_argument(
        "--devices",
        default="device1,device2,device3",
        help="设备 ID 列表，逗号分隔",
    )
    parser.add_argument("--category", default="tee", help="文案模板分类")
    parser.add_argument("--price", type=float, help="基础价格（默认按照 meta.yaml 中的 price）")
    parser.add_argument("--watermark", default="电子衣柜", help="水印文字")
    parser.add_argument("--no-run", action="store_true", help="仅生成示例素材，不运行中央厨房")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    styles = load_styles(args.spec)

    input_root = args.input.resolve()
    output_root = args.output.resolve()
    input_root.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)

    print(f">> 生成示例素材到 {input_root}")
    create_input_dataset(styles, input_root)

    if not args.no_run:
        devices = [device.strip() for device in args.devices.split(",") if device.strip()]
        if len(devices) != 3:
            raise ValueError("必须提供 3 个设备 ID，例如 device1,device2,device3")
        price_override = args.price if args.price is not None else None
        run_pipeline(input_root, output_root, devices, price_override, args.category, args.watermark)
        print(f">> 中央厨房示例输出位于 {output_root}")
    else:
        print(">> 已生成素材，未执行中央厨房（--no-run）")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
