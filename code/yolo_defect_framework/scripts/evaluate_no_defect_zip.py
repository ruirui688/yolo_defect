from __future__ import annotations

import argparse
import json
import statistics
import zipfile
from collections import Counter
from io import BytesIO
from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from common import CLASS_NAMES, dump_json, write_csv


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate the defect model on a no-defect zip dataset and report false positives."
    )
    parser.add_argument("--weights", type=Path, required=True, help="Path to the trained YOLO weights.")
    parser.add_argument("--zip-path", type=Path, required=True, help="Path to a zip dataset with images and LabelMe JSON.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write evaluation reports.")
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--device", type=str, default="0")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--limit", type=int, default=0, help="Only evaluate the first N images. 0 means all.")
    parser.add_argument(
        "--save-fp-images",
        action="store_true",
        help="Save annotated images only for false-positive samples.",
    )
    return parser


def parse_labelme_shape_count(raw_json: str) -> int:
    payload = json.loads(raw_json)
    shapes = payload.get("shapes", [])
    if not isinstance(shapes, list):
        raise ValueError("Invalid LabelMe JSON: 'shapes' must be a list.")
    return len(shapes)


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


def summarize_scores(detections: list[dict]) -> str:
    if not detections:
        return ""
    by_class: dict[str, list[float]] = {}
    for det in detections:
        by_class.setdefault(det["class_name"], []).append(float(det["confidence"]))
    parts: list[str] = []
    for class_name in sorted(by_class):
        values = by_class[class_name]
        parts.append(f"{class_name}:count={len(values)},max_conf={max(values):.6f}")
    return ";".join(parts)


def numeric_summary(values: list[float]) -> dict | None:
    if not values:
        return None
    ordered = sorted(values)
    return {
        "min": min(ordered),
        "mean": statistics.mean(ordered),
        "median": statistics.median(ordered),
        "max": max(ordered),
    }


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    fp_dir = output_dir / "false_positive_images"
    fp_detail_dir = output_dir / "false_positive_details"
    if args.save_fp_images:
        fp_dir.mkdir(parents=True, exist_ok=True)
    fp_detail_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(args.weights.as_posix())
    image_rows: list[dict] = []
    fp_details: list[dict] = []
    box_counter = Counter()
    image_counter = Counter()
    fp_box_confidences: list[float] = []
    fp_image_max_confidences: list[float] = []

    total_images_in_zip = 0
    total_json_in_zip = 0
    evaluated_images = 0
    true_negative_images = 0
    false_positive_images = 0
    skipped_missing_json = 0
    skipped_non_empty_json = 0

    with zipfile.ZipFile(args.zip_path) as archive:
        image_members: dict[str, str] = {}
        json_members: dict[str, str] = {}
        for member in archive.infolist():
            if member.is_dir():
                continue
            suffix = Path(member.filename).suffix.lower()
            stem = Path(member.filename).stem
            if suffix == ".json":
                json_members[stem] = member.filename
                total_json_in_zip += 1
            elif suffix in {".bmp", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
                image_members[stem] = member.filename
                total_images_in_zip += 1

        paired_stems = sorted(image_members)
        if args.limit > 0:
            paired_stems = paired_stems[: args.limit]

        for stem in paired_stems:
            image_member = image_members[stem]
            json_member = json_members.get(stem)
            if json_member is None:
                skipped_missing_json += 1
                image_rows.append(
                    {
                        "image_name": Path(image_member).name,
                        "status": "SKIPPED_MISSING_JSON",
                        "num_detections": "",
                        "max_confidence": "",
                        "predicted_classes": "",
                        "box_summary": "",
                    }
                )
                continue

            shape_count = parse_labelme_shape_count(archive.read(json_member).decode("utf-8"))
            if shape_count != 0:
                skipped_non_empty_json += 1
                image_rows.append(
                    {
                        "image_name": Path(image_member).name,
                        "status": "SKIPPED_NON_EMPTY_JSON",
                        "num_detections": "",
                        "max_confidence": "",
                        "predicted_classes": "",
                        "box_summary": f"shape_count={shape_count}",
                    }
                )
                continue

            evaluated_images += 1
            with Image.open(BytesIO(archive.read(image_member))) as image:
                rgb_image = image.convert("RGB")
                result = model.predict(
                    source=rgb_image,
                    imgsz=args.imgsz,
                    device=args.device,
                    conf=args.conf,
                    iou=args.iou,
                    verbose=False,
                )[0]

            detections = build_detections(result)
            max_confidence = max((float(det["confidence"]) for det in detections), default=0.0)
            predicted_classes = sorted({str(det["class_name"]) for det in detections})
            has_prediction = bool(detections)

            if has_prediction:
                false_positive_images += 1
                fp_image_max_confidences.append(max_confidence)
                for det in detections:
                    class_name = str(det["class_name"])
                    box_counter[class_name] += 1
                    fp_box_confidences.append(float(det["confidence"]))
                for class_name in predicted_classes:
                    image_counter[class_name] += 1

                annotated_rel_path = ""
                if args.save_fp_images:
                    annotated_rel_path = f"{Path(image_member).stem}.jpg"
                    annotated = result.plot()
                    Image.fromarray(annotated[..., ::-1]).save(fp_dir / annotated_rel_path)

                detail_payload = {
                    "image_name": Path(image_member).name,
                    "image_member": image_member,
                    "json_member": json_member,
                    "status": "FALSE_POSITIVE",
                    "num_detections": len(detections),
                    "max_confidence": max_confidence,
                    "predicted_classes": predicted_classes,
                    "detections": detections,
                    "annotated_image": annotated_rel_path,
                }
                dump_json(fp_detail_dir / f"{Path(image_member).stem}.json", detail_payload)
                fp_details.append(detail_payload)
                status = "FALSE_POSITIVE"
            else:
                true_negative_images += 1
                status = "TRUE_NEGATIVE"

            image_rows.append(
                {
                    "image_name": Path(image_member).name,
                    "status": status,
                    "num_detections": len(detections),
                    "max_confidence": f"{max_confidence:.6f}" if detections else "",
                    "predicted_classes": ";".join(predicted_classes),
                    "box_summary": summarize_scores(detections),
                }
            )

    image_level_false_positive_rate = false_positive_images / evaluated_images if evaluated_images else 0.0
    image_level_true_negative_rate = true_negative_images / evaluated_images if evaluated_images else 0.0

    top_false_positive_images = sorted(
        (
            {
                "image_name": item["image_name"],
                "num_detections": item["num_detections"],
                "max_confidence": item["max_confidence"],
                "predicted_classes": item["predicted_classes"],
                "annotated_image": item["annotated_image"],
            }
            for item in fp_details
        ),
        key=lambda item: (float(item["max_confidence"]), int(item["num_detections"])),
        reverse=True,
    )[:30]

    summary = {
        "zip_path": args.zip_path.as_posix(),
        "weights": args.weights.as_posix(),
        "output_dir": output_dir.as_posix(),
        "config": {
            "imgsz": args.imgsz,
            "device": args.device,
            "conf": args.conf,
            "iou": args.iou,
            "limit": args.limit,
            "save_fp_images": args.save_fp_images,
        },
        "dataset": {
            "total_images_in_zip": total_images_in_zip,
            "total_json_in_zip": total_json_in_zip,
            "evaluated_images": evaluated_images,
            "skipped_missing_json": skipped_missing_json,
            "skipped_non_empty_json": skipped_non_empty_json,
        },
        "metrics": {
            "true_negative_images": true_negative_images,
            "false_positive_images": false_positive_images,
            "image_level_true_negative_rate": image_level_true_negative_rate,
            "image_level_false_positive_rate": image_level_false_positive_rate,
            "total_false_positive_boxes": sum(box_counter.values()),
            "false_positive_boxes_per_class": dict(sorted(box_counter.items())),
            "false_positive_images_per_class": dict(sorted(image_counter.items())),
            "false_positive_box_confidence_stats": numeric_summary(fp_box_confidences),
            "false_positive_image_max_confidence_stats": numeric_summary(fp_image_max_confidences),
        },
        "top_false_positive_images": top_false_positive_images,
    }

    write_csv(
        output_dir / "per_image_results.csv",
        image_rows,
        ["image_name", "status", "num_detections", "max_confidence", "predicted_classes", "box_summary"],
    )
    dump_json(output_dir / "summary.json", summary)

    print(f"Evaluated images: {evaluated_images}")
    print(f"True negative images: {true_negative_images}")
    print(f"False positive images: {false_positive_images}")
    print(f"Image-level false positive rate: {image_level_false_positive_rate:.4%}")
    print(f"Summary JSON: {output_dir / 'summary.json'}")
    print(f"Per-image CSV: {output_dir / 'per_image_results.csv'}")
    if args.save_fp_images:
        print(f"False positive images: {fp_dir}")
    print(f"False positive details: {fp_detail_dir}")


if __name__ == "__main__":
    main()

