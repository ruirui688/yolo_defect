from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from ultralytics import YOLO


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train YOLO on the prepared 4-class defect dataset.")
    parser.add_argument("--config", type=Path, required=True, help="Path to training YAML config.")
    parser.add_argument("--data", type=Path, required=True, help="Path to generated data.yaml.")
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    model = YOLO(config["model"])
    augment = config.get("augment", {})

    train_kwargs = {
        "data": args.data.as_posix(),
        "imgsz": config.get("imgsz", 1280),
        "epochs": config.get("epochs", 150),
        "batch": config.get("batch", 4),
        "workers": config.get("workers", 4),
        "device": config.get("device", "0"),
        "seed": config.get("seed", 42),
        "patience": config.get("patience", 40),
        "project": config.get("project", "runs"),
        "name": config.get("name", "defect_yolo"),
        "conf": config.get("conf_threshold", 0.25),
        "iou": config.get("iou_threshold", 0.5),
        "amp": config.get("amp", True),
        "cache": config.get("cache", False),
        "save_period": config.get("save_period", -1),
        "plots": True,
        **augment,
    }

    results = model.train(**train_kwargs)
    best_weights = Path(results.save_dir) / "weights" / "best.pt"
    print(f"Training finished. Best weights: {best_weights}")

    val_metrics = model.val(data=args.data.as_posix(), split="test")
    print("Validation on test split finished.")
    print(val_metrics.results_dict)


if __name__ == "__main__":
    main()
