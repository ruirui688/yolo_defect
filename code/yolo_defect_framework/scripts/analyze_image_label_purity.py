from __future__ import annotations

import argparse
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from common import CLASS_NAMES, IMAGE_EXTENSIONS, SOURCE_ARCHIVES, parse_yolo_label_text


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze whether each image contains one class or multiple classes."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        required=True,
        help="Directory containing the four raw zip archives.",
    )
    parser.add_argument(
        "--show-examples",
        type=int,
        default=10,
        help="How many mixed-label examples to print per archive.",
    )
    return parser


def collect_pairs(archive: zipfile.ZipFile) -> tuple[dict[str, str], dict[str, str]]:
    image_members: dict[str, str] = {}
    label_members: dict[str, str] = {}
    for member in archive.infolist():
        if member.is_dir():
            continue
        suffix = Path(member.filename).suffix.lower()
        stem = Path(member.filename).stem
        normalized_name = member.filename.replace("\\", "/").lower()
        if suffix in IMAGE_EXTENSIONS:
            image_members[stem] = member.filename
        elif suffix == ".txt" and "/labels/" in normalized_name:
            label_members[stem] = member.filename
    return image_members, label_members


def analyze_archive(archive_path: Path, example_limit: int) -> dict:
    with zipfile.ZipFile(archive_path) as archive:
        image_members, label_members = collect_pairs(archive)
        paired_stems = sorted(image_members.keys() & label_members.keys())

        class_combo_counter: Counter[str] = Counter()
        num_classes_counter: Counter[int] = Counter()
        box_counter_by_combo: Counter[str] = Counter()
        mixed_examples: list[dict] = []

        for stem in paired_stems:
            label_text = archive.read(label_members[stem]).decode("utf-8").strip()
            label_records = parse_yolo_label_text(label_text)
            class_ids = sorted({int(item["class_id"]) for item in label_records})
            class_names = [CLASS_NAMES[idx] for idx in class_ids]
            combo_name = " + ".join(class_names)

            class_combo_counter[combo_name] += 1
            num_classes_counter[len(class_ids)] += 1
            box_counter_by_combo[combo_name] += len(label_records)

            if len(class_ids) > 1 and len(mixed_examples) < example_limit:
                mixed_examples.append(
                    {
                        "image_name": Path(image_members[stem]).name,
                        "label_name": Path(label_members[stem]).name,
                        "class_names": class_names,
                        "num_boxes": len(label_records),
                    }
                )

    total_images = len(paired_stems)
    single_class_images = num_classes_counter.get(1, 0)
    mixed_class_images = total_images - single_class_images
    return {
        "archive_name": archive_path.name,
        "total_images": total_images,
        "single_class_images": single_class_images,
        "mixed_class_images": mixed_class_images,
        "mixed_ratio": (mixed_class_images / total_images) if total_images else 0.0,
        "num_classes_counter": dict(sorted(num_classes_counter.items())),
        "class_combo_counter": dict(class_combo_counter.most_common()),
        "box_counter_by_combo": dict(box_counter_by_combo.most_common()),
        "mixed_examples": mixed_examples,
    }


def print_report(report: dict) -> None:
    print("=" * 80)
    print(report["archive_name"])
    print(f"total_images={report['total_images']}")
    print(f"single_class_images={report['single_class_images']}")
    print(f"mixed_class_images={report['mixed_class_images']}")
    print(f"mixed_ratio={report['mixed_ratio']:.2%}")
    print(f"num_classes_per_image={report['num_classes_counter']}")
    print("top_class_combinations:")
    for combo_name, count in list(report["class_combo_counter"].items())[:10]:
        print(f"  {combo_name}: {count}")
    if report["mixed_examples"]:
        print("mixed_examples:")
        for item in report["mixed_examples"]:
            print(
                f"  {item['image_name']} | labels={item['class_names']} | num_boxes={item['num_boxes']}"
            )


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    reports = []
    overall_combo_counter: Counter[str] = Counter()
    overall_num_classes_counter: Counter[int] = Counter()
    overall_total = 0
    overall_mixed = 0

    for archive_name in SOURCE_ARCHIVES:
        archive_path = args.raw_dir / archive_name
        if not archive_path.exists():
            raise FileNotFoundError(f"Missing archive: {archive_path}")
        report = analyze_archive(archive_path, args.show_examples)
        reports.append(report)
        print_report(report)
        overall_total += report["total_images"]
        overall_mixed += report["mixed_class_images"]
        overall_combo_counter.update(report["class_combo_counter"])
        overall_num_classes_counter.update(report["num_classes_counter"])

    print("=" * 80)
    print("OVERALL")
    print(f"total_images={overall_total}")
    print(f"mixed_class_images={overall_mixed}")
    print(f"mixed_ratio={(overall_mixed / overall_total) if overall_total else 0.0:.2%}")
    print(f"num_classes_per_image={dict(sorted(overall_num_classes_counter.items()))}")
    print("top_class_combinations:")
    for combo_name, count in overall_combo_counter.most_common(12):
        print(f"  {combo_name}: {count}")


if __name__ == "__main__":
    main()
