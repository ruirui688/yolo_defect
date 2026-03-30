from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export YOLO weights for deployment.")
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--format", type=str, default="onnx", choices=["onnx", "engine"])
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--device", type=str, default="0")
    parser.add_argument("--half", action="store_true", help="Use FP16 export when supported.")
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    model = YOLO(args.weights.as_posix())
    output = model.export(format=args.format, imgsz=args.imgsz, device=args.device, half=args.half)
    print(f"Exported model: {output}")


if __name__ == "__main__":
    main()
