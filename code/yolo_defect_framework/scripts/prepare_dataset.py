from __future__ import annotations

import argparse
import random
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from common import (
    CLASS_NAME_TO_ID,
    CLASS_NAMES,
    IMAGE_EXTENSIONS,
    SOURCE_ARCHIVES,
    choose_primary_label,
    dump_json,
    parse_yolo_label_text,
    summarize_label_records,
    write_csv,
    write_data_yaml,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare YOLO dataset from raw defect zip archives.")
    parser.add_argument("--raw-dir", type=Path, required=True, help="Directory containing the four raw zip archives.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for the prepared YOLO dataset.")
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def compute_split_counts(total: int, train_ratio: float, val_ratio: float, test_ratio: float) -> dict[str, int]:
    if total <= 0:
        return {"train": 0, "val": 0, "test": 0}
    if abs((train_ratio + val_ratio + test_ratio) - 1.0) > 1e-6:
        raise ValueError("train/val/test ratios must sum to 1.0")

    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)
    test_count = total - train_count - val_count

    if total >= 3:
        if train_count == 0:
            train_count = 1
            test_count -= 1
        if val_count == 0:
            val_count = 1
            if test_count > 1:
                test_count -= 1
            else:
                train_count -= 1
        if test_count == 0:
            test_count = 1
            train_count -= 1
    return {"train": train_count, "val": val_count, "test": test_count}


def collect_records_from_zip(raw_dir: Path) -> list[dict]:
    records: list[dict] = []
    for archive_name, nominal_class_name in SOURCE_ARCHIVES.items():
        archive_path = raw_dir / archive_name
        if not archive_path.exists():
            raise FileNotFoundError(f"Missing archive: {archive_path}")

        nominal_class_id = CLASS_NAME_TO_ID[nominal_class_name]
        with zipfile.ZipFile(archive_path) as archive:
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

            paired_stems = sorted(image_members.keys() & label_members.keys())
            if not paired_stems:
                raise RuntimeError(f"No image/label pairs found in {archive_path}")

            for stem in paired_stems:
                label_text = archive.read(label_members[stem]).decode("utf-8").strip()
                label_records = parse_yolo_label_text(label_text)
                summary = summarize_label_records(label_records)

                records.append(
                    {
                        "archive_path": archive_path,
                        "archive_name": archive_name,
                        "source_dataset": nominal_class_name,
                        "source_class_id": nominal_class_id,
                        "stem": stem,
                        "file_name": Path(image_members[stem]).name,
                        "image_member": image_members[stem],
                        "label_member": label_members[stem],
                        "actual_class_ids": summary["actual_class_ids"],
                        "actual_class_names": summary["actual_class_names"],
                        "num_boxes": summary["num_boxes"],
                        "counts": summary["counts"],
                        "area_by_class": summary["area_by_class"],
                        "primary_by_source": choose_primary_label(
                            nominal_class_id, summary["counts"], summary["area_by_class"], "source_package"
                        ),
                        "primary_by_count": choose_primary_label(
                            nominal_class_id, summary["counts"], summary["area_by_class"], "most_boxes"
                        ),
                        "primary_by_area": choose_primary_label(
                            nominal_class_id, summary["counts"], summary["area_by_class"], "largest_area"
                        ),
                    }
                )
    return records


def split_records(records: list[dict], seed: int, train_ratio: float, val_ratio: float, test_ratio: float) -> list[dict]:
    rng = random.Random(seed)
    by_source: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        by_source[record["source_dataset"]].append(record)

    output: list[dict] = []
    for source_dataset, items in by_source.items():
        rng.shuffle(items)
        counts = compute_split_counts(len(items), train_ratio, val_ratio, test_ratio)
        train_end = counts["train"]
        val_end = counts["train"] + counts["val"]
        for idx, record in enumerate(items):
            if idx < train_end:
                split = "train"
            elif idx < val_end:
                split = "val"
            else:
                split = "test"
            updated = dict(record)
            updated["split"] = split
            output.append(updated)
        print(f"{source_dataset}: train={counts['train']} val={counts['val']} test={counts['test']}")
    return sorted(output, key=lambda item: (item["split"], item["source_dataset"], item["stem"]))


def ensure_output_structure(output_dir: Path) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(
            f"Output directory is not empty: {output_dir}. "
            "Use a new directory or clean it manually before rerunning."
        )
    for split in ("train", "val", "test"):
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)
    (output_dir / "metadata").mkdir(parents=True, exist_ok=True)


def materialize_dataset(records: list[dict], output_dir: Path) -> list[dict]:
    manifest_rows: list[dict] = []
    grouped_by_archive: dict[Path, list[dict]] = defaultdict(list)
    for record in records:
        grouped_by_archive[record["archive_path"]].append(record)

    for archive_path, group_records in grouped_by_archive.items():
        with zipfile.ZipFile(archive_path) as archive:
            for record in group_records:
                split = record["split"]
                image_out = output_dir / "images" / split / record["file_name"]
                label_out = output_dir / "labels" / split / f"{record['stem']}.txt"
                image_out.write_bytes(archive.read(record["image_member"]))
                label_out.write_bytes(archive.read(record["label_member"]))
                manifest_rows.append(
                    {
                        "split": split,
                        "file_name": record["file_name"],
                        "image_rel": image_out.relative_to(output_dir).as_posix(),
                        "label_rel": label_out.relative_to(output_dir).as_posix(),
                        "source_dataset": record["source_dataset"],
                        "source_class_id": record["source_class_id"],
                        "source_class_name": CLASS_NAMES[record["source_class_id"]],
                        "primary_by_source_id": record["primary_by_source"],
                        "primary_by_source_name": CLASS_NAMES[record["primary_by_source"]],
                        "primary_by_count_id": record["primary_by_count"],
                        "primary_by_count_name": CLASS_NAMES[record["primary_by_count"]],
                        "primary_by_area_id": record["primary_by_area"],
                        "primary_by_area_name": CLASS_NAMES[record["primary_by_area"]],
                        "actual_class_ids": ";".join(str(item) for item in record["actual_class_ids"]),
                        "actual_class_names": ";".join(record["actual_class_names"]),
                        "num_boxes": record["num_boxes"],
                    }
                )
    return manifest_rows


def build_summary(manifest_rows: list[dict]) -> dict:
    summary: dict[str, dict] = {
        "images_per_split": Counter(),
        "images_per_source_dataset": Counter(),
        "primary_by_source_counts": Counter(),
        "primary_by_count_counts": Counter(),
        "primary_by_area_counts": Counter(),
    }
    for row in manifest_rows:
        summary["images_per_split"][row["split"]] += 1
        summary["images_per_source_dataset"][row["source_dataset"]] += 1
        summary["primary_by_source_counts"][row["primary_by_source_name"]] += 1
        summary["primary_by_count_counts"][row["primary_by_count_name"]] += 1
        summary["primary_by_area_counts"][row["primary_by_area_name"]] += 1

    normalized = {key: dict(sorted(value.items())) for key, value in summary.items()}
    normalized["class_names"] = CLASS_NAMES
    normalized["notes"] = [
        "All provided raw images are defect samples; no clean images were found in the archives.",
        "primary_by_source uses the archive name as the image-level label.",
        "primary_by_count uses the class with the most boxes in that image.",
        "primary_by_area uses the class with the largest summed YOLO box area in that image.",
    ]
    return normalized


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    ensure_output_structure(args.output_dir)
    raw_records = collect_records_from_zip(args.raw_dir)
    prepared_records = split_records(
        raw_records,
        seed=args.seed,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
    )
    manifest_rows = materialize_dataset(prepared_records, args.output_dir)

    write_data_yaml(args.output_dir / "data.yaml", args.output_dir)
    write_csv(
        args.output_dir / "metadata" / "manifest.csv",
        manifest_rows,
        [
            "split",
            "file_name",
            "image_rel",
            "label_rel",
            "source_dataset",
            "source_class_id",
            "source_class_name",
            "primary_by_source_id",
            "primary_by_source_name",
            "primary_by_count_id",
            "primary_by_count_name",
            "primary_by_area_id",
            "primary_by_area_name",
            "actual_class_ids",
            "actual_class_names",
            "num_boxes",
        ],
    )
    dump_json(args.output_dir / "metadata" / "summary.json", build_summary(manifest_rows))

    print(f"Prepared dataset written to: {args.output_dir}")
    print(f"Data config written to: {args.output_dir / 'data.yaml'}")
    print(f"Manifest written to: {args.output_dir / 'metadata' / 'manifest.csv'}")


if __name__ == "__main__":
    main()
