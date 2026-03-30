from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from common import (
    CLASS_NAMES,
    IMAGE_EXTENSIONS,
    aggregate_prediction,
    dump_json,
    write_csv,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run YOLO on one image or a directory of images and save annotated outputs."
    )
    parser.add_argument("--weights", type=Path, required=True, help="Path to the trained YOLO weights.")
    parser.add_argument("--source", type=Path, required=True, help="Path to one image or a directory of images.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for annotated images and reports.")
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--device", type=str, default="0")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument(
        "--pred-mode",
        type=str,
        default="max_conf",
        choices=["max_conf", "sum_conf", "area_conf"],
        help="How to aggregate detections into one image-level class.",
    )
    return parser


def collect_image_paths(source: Path) -> list[Path]:
    if not source.exists():
        raise FileNotFoundError(f"Source path does not exist: {source}")
    if source.is_file():
        if source.suffix.lower() not in IMAGE_EXTENSIONS:
            raise ValueError(f"Unsupported image file: {source}")
        return [source]

    image_paths = sorted(
        path
        for path in source.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not image_paths:
        raise FileNotFoundError(f"No supported images found under: {source}")
    return image_paths


def build_detections(result) -> list[dict]:
    detections: list[dict] = []
    if result.boxes is None:
        return detections

    xyxy = result.boxes.xyxy.cpu().tolist()
    cls = result.boxes.cls.cpu().tolist()
    confs = result.boxes.conf.cpu().tolist()
    for box, class_id, confidence in zip(xyxy, cls, confs):
        width = max(float(box[2]) - float(box[0]), 0.0)
        height = max(float(box[3]) - float(box[1]), 0.0)
        detections.append(
            {
                "class_id": int(class_id),
                "class_name": CLASS_NAMES[int(class_id)],
                "confidence": float(confidence),
                "box_xyxy": [float(v) for v in box],
                "box_area": width * height,
            }
        )
    return detections


def build_relative_path(source: Path, image_path: Path) -> Path:
    if source.is_file():
        return Path(image_path.name)
    return image_path.relative_to(source)


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    image_paths = collect_image_paths(args.source)
    output_dir = args.output_dir
    annotated_dir = output_dir / "annotated"
    details_dir = output_dir / "details"
    annotated_dir.mkdir(parents=True, exist_ok=True)
    details_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(args.weights.as_posix())
    summary_rows: list[dict] = []
    summary_payload = {
        "weights": args.weights.as_posix(),
        "source": args.source.as_posix(),
        "output_dir": output_dir.as_posix(),
        "imgsz": args.imgsz,
        "device": args.device,
        "conf": args.conf,
        "iou": args.iou,
        "pred_mode": args.pred_mode,
        "images": [],
    }

    for image_path in image_paths:
        result = model.predict(
            source=image_path.as_posix(),
            imgsz=args.imgsz,
            device=args.device,
            conf=args.conf,
            iou=args.iou,
            verbose=False,
        )[0]

        detections = build_detections(result)
        pred_class_id, scores = aggregate_prediction(detections, mode=args.pred_mode)
        pred_class_name = CLASS_NAMES[pred_class_id] if pred_class_id is not None else "NO_PREDICTION"
        score_text = ";".join(f"{CLASS_NAMES[k]}={v:.6f}" for k, v in sorted(scores.items()))

        relative_path = build_relative_path(args.source, image_path)
        annotated_path = annotated_dir / relative_path
        detail_path = details_dir / relative_path.with_suffix(".json")
        annotated_path.parent.mkdir(parents=True, exist_ok=True)
        detail_path.parent.mkdir(parents=True, exist_ok=True)

        annotated = result.plot()
        Image.fromarray(annotated[..., ::-1]).save(annotated_path)

        payload = {
            "image": image_path.as_posix(),
            "image_rel": relative_path.as_posix(),
            "predicted_class_id": pred_class_id,
            "predicted_class_name": pred_class_name,
            "prediction_scores": {CLASS_NAMES[k]: v for k, v in sorted(scores.items())},
            "num_detections": len(detections),
            "annotated_image": annotated_path.as_posix(),
            "detections": detections,
        }
        dump_json(detail_path, payload)
        summary_payload["images"].append(payload)
        summary_rows.append(
            {
                "image_rel": relative_path.as_posix(),
                "predicted_class_id": pred_class_id,
                "predicted_class_name": pred_class_name,
                "num_detections": len(detections),
                "prediction_scores": score_text,
                "annotated_image": annotated_path.as_posix(),
                "detail_json": detail_path.as_posix(),
            }
        )

    write_csv(
        output_dir / "summary.csv",
        summary_rows,
        [
            "image_rel",
            "predicted_class_id",
            "predicted_class_name",
            "num_detections",
            "prediction_scores",
            "annotated_image",
            "detail_json",
        ],
    )
    dump_json(output_dir / "summary.json", summary_payload)

    print(f"Processed images: {len(image_paths)}")
    print(f"Annotated images: {annotated_dir}")
    print(f"Summary JSON: {output_dir / 'summary.json'}")
    print(f"Summary CSV: {output_dir / 'summary.csv'}")


if __name__ == "__main__":
    main()

