from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from ultralytics import YOLO

from common import CLASS_NAMES, aggregate_prediction, dump_json, read_manifest, write_csv


GT_MODE_TO_FIELD = {
    "source_package": ("primary_by_source_id", "primary_by_source_name"),
    "most_boxes": ("primary_by_count_id", "primary_by_count_name"),
    "largest_area": ("primary_by_area_id", "primary_by_area_name"),
}


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate image-level defect classification accuracy.")
    parser.add_argument("--weights", type=Path, required=True, help="Path to best.pt or another YOLO weights file.")
    parser.add_argument("--dataset-root", type=Path, required=True, help="Prepared dataset root containing images/ and metadata/.")
    parser.add_argument("--split", type=str, default="test", choices=["train", "val", "test"])
    parser.add_argument(
        "--gt-mode",
        type=str,
        default="source_package",
        choices=sorted(GT_MODE_TO_FIELD),
        help="Ground-truth image label mode.",
    )
    parser.add_argument(
        "--pred-mode",
        type=str,
        default="max_conf",
        choices=["max_conf", "sum_conf", "area_conf"],
        help="How to turn detection outputs into one image-level prediction.",
    )
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--device", type=str, default="0")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.5)
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    manifest_path = args.dataset_root / "metadata" / "manifest.csv"
    manifest = [row for row in read_manifest(manifest_path) if row["split"] == args.split]
    model = YOLO(args.weights.as_posix())

    gt_id_field, gt_name_field = GT_MODE_TO_FIELD[args.gt_mode]
    prediction_rows: list[dict] = []
    confusion: dict[str, Counter] = defaultdict(Counter)
    gt_counter = Counter()
    pred_counter = Counter()
    correct = 0

    for row in manifest:
        image_path = args.dataset_root / row["image_rel"]
        result = model.predict(
            source=image_path.as_posix(),
            imgsz=args.imgsz,
            device=args.device,
            conf=args.conf,
            iou=args.iou,
            verbose=False,
        )[0]
        detections = []
        if result.boxes is not None:
            xyxy = result.boxes.xyxy.cpu().tolist()
            cls = result.boxes.cls.cpu().tolist()
            confs = result.boxes.conf.cpu().tolist()
            for box, class_id, confidence in zip(xyxy, cls, confs):
                width = max(float(box[2]) - float(box[0]), 0.0)
                height = max(float(box[3]) - float(box[1]), 0.0)
                detections.append(
                    {
                        "class_id": int(class_id),
                        "confidence": float(confidence),
                        "box_area": width * height,
                    }
                )

        pred_class_id, scores = aggregate_prediction(detections, mode=args.pred_mode)
        pred_class_name = CLASS_NAMES[pred_class_id] if pred_class_id is not None else "NO_PREDICTION"
        gt_class_id = int(row[gt_id_field])
        gt_class_name = row[gt_name_field]
        is_correct = pred_class_id == gt_class_id

        gt_counter[gt_class_name] += 1
        pred_counter[pred_class_name] += 1
        confusion[gt_class_name][pred_class_name] += 1
        if is_correct:
            correct += 1

        prediction_rows.append(
            {
                "file_name": row["file_name"],
                "gt_class_name": gt_class_name,
                "pred_class_name": pred_class_name,
                "is_correct": int(is_correct),
                "scores": ";".join(f"{CLASS_NAMES[k]}={v:.6f}" for k, v in sorted(scores.items())),
            }
        )

    total = len(manifest)
    accuracy = correct / total if total else 0.0
    metrics = {
        "split": args.split,
        "gt_mode": args.gt_mode,
        "pred_mode": args.pred_mode,
        "total_images": total,
        "correct_images": correct,
        "image_accuracy": accuracy,
        "gt_distribution": dict(sorted(gt_counter.items())),
        "pred_distribution": dict(sorted(pred_counter.items())),
        "confusion_matrix": {key: dict(sorted(value.items())) for key, value in sorted(confusion.items())},
    }

    reports_dir = args.dataset_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        reports_dir / f"image_eval_{args.split}.csv",
        prediction_rows,
        ["file_name", "gt_class_name", "pred_class_name", "is_correct", "scores"],
    )
    dump_json(reports_dir / f"image_eval_{args.split}.json", metrics)

    print(f"Image-level accuracy: {accuracy:.4%} ({correct}/{total})")
    print(f"Detailed report: {reports_dir / f'image_eval_{args.split}.json'}")


if __name__ == "__main__":
    main()
