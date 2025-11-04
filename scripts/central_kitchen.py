"""中央厨房命令行入口。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.config.models import (
    CentralKitchenConfig,
    DelayConfig,
    DeviceAssignment,
    GenerationTemplate,
    PriceConfig,
    SensitiveDictionary,
    WatermarkConfig,
)
from core.pipeline import CentralPipeline
from core.reporting.report_builder import ReportBuilder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="中央厨房批量任务生成")
    parser.add_argument("--input", required=True, help="原始素材目录 Input_Raw")
    parser.add_argument("--output", required=True, help="任务包输出目录")
    parser.add_argument(
        "--devices",
        required=True,
        help="设备 ID 列表，逗号分隔，例如 device1,device2,device3",
    )
    parser.add_argument(
        "--price",
        type=float,
        required=True,
        help="基础价格（元），小数部分将自动处理",
    )
    parser.add_argument(
        "--category",
        default="tee",
        help="文案模板品类（默认为 tee）",
    )
    parser.add_argument(
        "--watermark",
        default="电子衣柜",
        help="水印文字（默认为 电子衣柜）",
    )
    parser.add_argument(
        "--report-dir",
        default="reports",
        help="报告输出目录（默认 output/reports/）",
    )
    parser.add_argument(
        "--fixed-price",
        action="store_true",
        help="禁用随机尾数，价格保持两位小数",
    )
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> CentralKitchenConfig:
    input_root = Path(args.input).resolve()
    output_root = Path(args.output).resolve()
    devices = [device.strip() for device in args.devices.split(",") if device.strip()]
    if len(devices) != 3:
        raise ValueError("目前必须提供 3 个设备 ID")

    return CentralKitchenConfig(
        input_root=input_root,
        output_root=output_root,
        price=PriceConfig(base_yuan=args.price, random_tail=not args.fixed_price),
        delays=DelayConfig(),
        device_assignment=DeviceAssignment(device_ids=tuple(devices)),
        template=GenerationTemplate(category=args.category, variations=3),
        sensitive_dictionary=SensitiveDictionary(),
        watermark=WatermarkConfig(text=args.watermark),
    )


def main() -> None:
    args = parse_args()
    config = build_config(args)
    config.ensure_paths()

    pipeline = CentralPipeline(config)
    result = pipeline.run()

    report_dir = (config.output_root / args.report_dir).resolve()
    report_path = ReportBuilder().write(result, report_dir)

    summary = {
        "report": str(report_path),
        "success": len(result.entries),
        "failures": list(result.failures),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
