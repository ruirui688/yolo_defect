from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from pathlib import Path

import yaml
from PIL import Image, ImageEnhance

from common import CLASS_NAME_TO_ID, CLASS_NAMES, read_manifest


@dataclass
class YoloBox:
    class_id: int
    x_center: float
    y_center: float
    width: float
    height: float


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Augment the train split with target-centered crops for weak classes."
    )
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def load_boxes(label_path: Path) -> list[YoloBox]:
    boxes: list[YoloBox] = []
    text = label_path.read_text(encoding="utf-8").strip()
    for line in text.splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        class_id = int(float(parts[0]))
        xc, yc, w, h = map(float, parts[1:])
        boxes.append(YoloBox(class_id, xc, yc, w, h))
    return boxes


def yolo_to_xyxy(box: YoloBox, img_w: int, img_h: int) -> tuple[float, float, float, float]:
    x_center = box.x_center * img_w
    y_center = box.y_center * img_h
    width = box.width * img_w
    height = box.height * img_h
    x1 = x_center - width / 2
    y1 = y_center - height / 2
    x2 = x_center + width / 2
    y2 = y_center + height / 2
    return x1, y1, x2, y2


def clip_crop_window(cx: float, cy: float, crop_size: int, img_w: int, img_h: int) -> tuple[int, int, int, int]:
    half = crop_size / 2
    left = int(round(cx - half))
    top = int(round(cy - half))
    left = max(0, min(left, max(img_w - crop_size, 0)))
    top = max(0, min(top, max(img_h - crop_size, 0)))
    right = min(left + crop_size, img_w)
    bottom = min(top + crop_size, img_h)
    return left, top, right, bottom


def clip_box_to_crop(
    xyxy: tuple[float, float, float, float],
    crop: tuple[int, int, int, int],
    min_visible_fraction: float,
    min_box_size_px: float,
) -> tuple[float, float, float, float] | None:
    x1, y1, x2, y2 = xyxy
    crop_left, crop_top, crop_right, crop_bottom = crop
    inter_x1 = max(x1, crop_left)
    inter_y1 = max(y1, crop_top)
    inter_x2 = min(x2, crop_right)
    inter_y2 = min(y2, crop_bottom)
    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return None

    orig_area = max((x2 - x1) * (y2 - y1), 1e-6)
    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
    if inter_area / orig_area < min_visible_fraction:
        return None
    if (inter_x2 - inter_x1) < min_box_size_px or (inter_y2 - inter_y1) < min_box_size_px:
        return None

    return (
        inter_x1 - crop_left,
        inter_y1 - crop_top,
        inter_x2 - crop_left,
        inter_y2 - crop_top,
    )


def xyxy_to_yolo(xyxy: tuple[float, float, float, float], crop_w: int, crop_h: int) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = xyxy
    width = x2 - x1
    height = y2 - y1
    x_center = x1 + width / 2
    y_center = y1 + height / 2
    return (
        x_center / crop_w,
        y_center / crop_h,
        width / crop_w,
        height / crop_h,
    )


def pick_crop_size(box_xyxy: tuple[float, float, float, float], base_crop_size: int, context_scale: float, img_w: int, img_h: int) -> int:
    x1, y1, x2, y2 = box_xyxy
    target_size = max(x2 - x1, y2 - y1) * context_scale
    crop_size = int(min(max(base_crop_size, math.ceil(target_size)), min(img_w, img_h)))
    return crop_size


def apply_photometric_variant(image: Image.Image, brightness_factor: float, contrast_factor: float) -> Image.Image:
    output = ImageEnhance.Brightness(image).enhance(brightness_factor)
    output = ImageEnhance.Contrast(output).enhance(contrast_factor)
    return output


def choose_variant_factors(config: dict, index: int) -> tuple[float, float]:
    brightness = config["brightness_factors"][index % len(config["brightness_factors"])]
    contrast = config["contrast_factors"][index % len(config["contrast_factors"])]
    return brightness, contrast


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()
    rng = random.Random(args.seed)

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    target_class_ids = {CLASS_NAME_TO_ID[name] for name in config["target_classes"]}
    base_crop_size = int(config["crop_size"])
    context_scale = float(config["context_scale"])
    min_visible_fraction = float(config["min_visible_fraction"])
    min_box_size_px = float(config["min_box_size_px"])
    copies_per_object = int(config["copies_per_object"])
    jitter_ratio = float(config["jitter_ratio"])

    dataset_root = args.dataset_root
    manifest = [row for row in read_manifest(dataset_root / "metadata" / "manifest.csv") if row["split"] == "train"]
    image_dir = dataset_root / "images" / "train"
    label_dir = dataset_root / "labels" / "train"
    generated_image_dir = dataset_root / "images" / "train"
    generated_label_dir = dataset_root / "labels" / "train"

    generated_count = 0
    generated_per_class = {name: 0 for name in config["target_classes"]}

    for row in manifest:
        image_path = dataset_root / row["image_rel"]
        label_path = dataset_root / row["label_rel"]
        boxes = load_boxes(label_path)
        if not any(box.class_id in target_class_ids for box in boxes):
            continue

        with Image.open(image_path) as image:
            image = image.convert("RGB")
            img_w, img_h = image.size

            for target_index, target_box in enumerate(boxes):
                if target_box.class_id not in target_class_ids:
                    continue

                target_xyxy = yolo_to_xyxy(target_box, img_w, img_h)
                crop_size = pick_crop_size(target_xyxy, base_crop_size, context_scale, img_w, img_h)
                x1, y1, x2, y2 = target_xyxy
                target_cx = (x1 + x2) / 2
                target_cy = (y1 + y2) / 2

                for copy_idx in range(copies_per_object):
                    jitter = crop_size * jitter_ratio
                    jitter_x = rng.uniform(-jitter, jitter)
                    jitter_y = rng.uniform(-jitter, jitter)
                    crop = clip_crop_window(target_cx + jitter_x, target_cy + jitter_y, crop_size, img_w, img_h)
                    crop_image = image.crop(crop)

                    adjusted_labels: list[str] = []
                    for box in boxes:
                        clipped = clip_box_to_crop(
                            yolo_to_xyxy(box, img_w, img_h),
                            crop,
                            min_visible_fraction=min_visible_fraction,
                            min_box_size_px=min_box_size_px,
                        )
                        if clipped is None:
                            continue
                        yolo_box = xyxy_to_yolo(clipped, crop[2] - crop[0], crop[3] - crop[1])
                        adjusted_labels.append(
                            f"{box.class_id} {yolo_box[0]:.6f} {yolo_box[1]:.6f} {yolo_box[2]:.6f} {yolo_box[3]:.6f}"
                        )

                    if not adjusted_labels:
                        continue

                    brightness, contrast = choose_variant_factors(config, copy_idx)
                    variant_image = apply_photometric_variant(crop_image, brightness, contrast)

                    stem = Path(row["file_name"]).stem
                    class_name = CLASS_NAMES[target_box.class_id]
                    out_stem = f"{stem}__aug_{class_name}_{target_index:02d}_{copy_idx:02d}"
                    out_image_path = generated_image_dir / f"{out_stem}.jpg"
                    out_label_path = generated_label_dir / f"{out_stem}.txt"

                    variant_image.save(out_image_path, quality=95)
                    out_label_path.write_text("\n".join(adjusted_labels) + "\n", encoding="utf-8")

                    generated_count += 1
                    generated_per_class[class_name] += 1

    print(f"Generated train augmentations: {generated_count}")
    for class_name, count in generated_per_class.items():
        print(f"  {class_name}: {count}")


if __name__ == "__main__":
    main()
