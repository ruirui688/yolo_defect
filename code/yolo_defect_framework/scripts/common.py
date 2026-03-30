from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


CLASS_NAMES = [
    "ConvexPoint",
    "ExposeWhite",
    "FiberNep",
    "FabricExposed",
]
CLASS_NAME_TO_ID = {name: idx for idx, name in enumerate(CLASS_NAMES)}
SOURCE_ARCHIVES = {
    "ConvexPoint.zip": "ConvexPoint",
    "ExposeWhite.zip": "ExposeWhite",
    "FiberNep.zip": "FiberNep",
    "FabricExposed.zip": "FabricExposed",
}
IMAGE_EXTENSIONS = {".bmp", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def parse_yolo_label_text(label_text: str) -> list[dict]:
    records: list[dict] = []
    for line in label_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid YOLO label line: {line!r}")
        class_id = int(float(parts[0]))
        x_center, y_center, width, height = map(float, parts[1:])
        records.append(
            {
                "class_id": class_id,
                "x_center": x_center,
                "y_center": y_center,
                "width": width,
                "height": height,
                "area": width * height,
            }
        )
    return records


def summarize_label_records(label_records: Iterable[dict]) -> dict:
    counts = Counter()
    area_by_class: dict[int, float] = defaultdict(float)
    for item in label_records:
        class_id = int(item["class_id"])
        counts[class_id] += 1
        area_by_class[class_id] += float(item["area"])
    actual_class_ids = sorted(counts)
    return {
        "counts": dict(counts),
        "area_by_class": dict(area_by_class),
        "actual_class_ids": actual_class_ids,
        "actual_class_names": [CLASS_NAMES[idx] for idx in actual_class_ids],
        "num_boxes": sum(counts.values()),
    }


def choose_primary_label(
    source_class_id: int,
    counts: dict[int, int],
    area_by_class: dict[int, float],
    mode: str,
) -> int:
    if mode == "source_package":
        return source_class_id
    if mode == "most_boxes":
        if not counts:
            return source_class_id
        return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
    if mode == "largest_area":
        if not area_by_class:
            return source_class_id
        return sorted(area_by_class.items(), key=lambda item: (-item[1], item[0]))[0][0]
    raise ValueError(f"Unsupported primary label mode: {mode}")


def aggregate_prediction(
    detections: Iterable[dict],
    mode: str = "max_conf",
) -> tuple[int | None, dict[int, float]]:
    scores: dict[int, float] = defaultdict(float)
    best_class_id: int | None = None
    best_score = -1.0
    for det in detections:
        class_id = int(det["class_id"])
        confidence = float(det["confidence"])
        box_area = float(det.get("box_area", 0.0))
        if mode == "max_conf":
            score = confidence
            if score > scores[class_id]:
                scores[class_id] = score
        elif mode == "sum_conf":
            scores[class_id] += confidence
            score = scores[class_id]
        elif mode == "area_conf":
            scores[class_id] += confidence * max(box_area, 1.0)
            score = scores[class_id]
        else:
            raise ValueError(f"Unsupported prediction aggregation mode: {mode}")
        if score > best_score:
            best_score = score
            best_class_id = class_id
    return best_class_id, dict(scores)


def write_data_yaml(output_path: Path, dataset_root: Path) -> None:
    lines = [
        f"path: {dataset_root.as_posix()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "",
        "names:",
    ]
    for idx, name in enumerate(CLASS_NAMES):
        lines.append(f"  {idx}: {name}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def dump_json(output_path: Path, payload: dict | list) -> None:
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_csv(output_path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_manifest(manifest_path: Path) -> list[dict]:
    with manifest_path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
