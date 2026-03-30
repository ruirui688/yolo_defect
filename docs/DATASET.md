# Dataset Description

## Status

The dataset is intentionally not included in this repository.

The following content should remain local only:

- raw zip archives under `raw_data/`
- generated training dataset under `output/dataset/`

## Raw Archive Names

The original raw archives used by this project are:

| Archive Name | Nominal Class | Image Count |
| --- | --- | ---: |
| `ConvexPoint.zip` | `ConvexPoint` | 1344 |
| `ExposeWhite.zip` | `ExposeWhite` | 1050 |
| `FiberNep.zip` | `FiberNep` | 409 |
| `FabricExposed.zip` | `FabricExposed` | 149 |

Total raw images: `2952`

## Detection Classes

This project uses 4 detection classes:

| Class ID | Class Name |
| --- | --- |
| 0 | `ConvexPoint` |
| 1 | `ExposeWhite` |
| 2 | `FiberNep` |
| 3 | `FabricExposed` |

## Data Characteristics

- all provided images are defect images
- no clean or normal images were found in the provided archives
- the dataset is not strictly single-class per image
- mixed-class images are common in `FiberNep.zip` and `FabricExposed.zip`

Mixed-image statistics observed in the original analysis:

| Archive Name | Mixed Images | Mixed Ratio |
| --- | ---: | ---: |
| `ConvexPoint.zip` | 0 | 0.00% |
| `ExposeWhite.zip` | 239 | 22.76% |
| `FiberNep.zip` | 286 | 69.93% |
| `FabricExposed.zip` | 76 | 51.01% |
| All archives | 601 | 20.36% |

This is the main reason the project is designed as an object detection project instead of a pure image classification project.

## Label Format

The raw labels are YOLO-format text labels:

```text
class_id x_center y_center width height
```

Each image can contain one or more bounding boxes and one or more classes.

## Generated Dataset Layout

The local generated dataset layout is:

```text
output/dataset/
  images/
    train/
    val/
    test/
  labels/
    train/
    val/
    test/
  metadata/
    manifest.csv
    summary.json
  reports/
    image_eval_test.csv
    image_eval_test.json
```

This generated dataset is also excluded from version control.

## Privacy And Publishing

If this repository is published publicly:

- do not commit `raw_data/*.zip`
- do not commit `output/dataset/**`
- keep only dataset names, counts, and task description in the public docs

