# Defect Detection YOLO Project

This repository contains a 4-class fabric defect detection project built with Ultralytics YOLO.

The repository is organized for GitHub publishing:

- source code and training scripts are kept under `code/yolo_defect_framework`
- the final trained model is collected under `artifacts/final_model`
- raw datasets and generated datasets are excluded from version control

## Project Overview

- Task type: object detection
- Framework: Ultralytics YOLO
- Classes:
  - `ConvexPoint`
  - `ExposeWhite`
  - `FiberNep`
  - `FabricExposed`
- Business goal: detect all defect boxes and defect classes in each image

This project uses a detection-first training strategy. It keeps all labeled boxes in each image instead of forcing the problem into single-label image classification.

## Repository Layout

```text
defect_project/
  artifacts/
    final_model/
      README.md
      metadata/
        model_summary.json
      weights/
        defect_yolov8m_1536_detect_all_best.pt
  code/
    yolo_defect_framework/
      configs/
      scripts/
      README.md
      environment.yml
      requirements.txt
      setup_env.sh
      run_prepare.sh
      run_augment.sh
      run_train.sh
      run_evaluate.sh
  docs/
    DATASET.md
    TRAINING.md
    PUBLISHING.md
```

## Included In This Repository

- training scripts
- config files
- environment setup script
- final trained model
- training and evaluation documentation

## Not Included In This Repository

- raw zip datasets
- generated YOLO dataset under `output/dataset`
- intermediate checkpoints and local training cache

See [docs/DATASET.md](docs/DATASET.md) for dataset names, counts, and structure.

## Final Model

- Final weight file: `artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt`
- Size: about 50 MB
- Training run name: `defect_yolov8m_1536_detect_all`
- Base model: `yolov8m.pt`

Supporting metadata is stored in:

- [artifacts/final_model/README.md](artifacts/final_model/README.md)
- [artifacts/final_model/metadata/model_summary.json](artifacts/final_model/metadata/model_summary.json)

## Training Environment

- OS: Ubuntu
- Environment manager: conda
- Python: 3.10
- PyTorch: installed from the CUDA 12.8 wheel index
- Main dependencies:
  - `ultralytics>=8.3.0`
  - `PyYAML>=6.0`
  - `Pillow>=10.0`
- Target GPU in the original setup:
  - NVIDIA GeForce RTX 5060 Ti 16 GB
  - NVIDIA driver `580.126.09`

See [docs/TRAINING.md](docs/TRAINING.md) for the full training method and current results.

## Quick Start

Create the environment:

```bash
cd code/yolo_defect_framework
chmod +x setup_env.sh run_prepare.sh run_augment.sh run_train.sh run_evaluate.sh
./setup_env.sh defect-yolo
conda activate defect-yolo
```

Run inference with the final model:

```bash
python code/yolo_defect_framework/scripts/infer_image.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --image /path/to/test.bmp \
  --save-annotated ./infer_result.bmp
```

## Training Pipeline

1. Prepare the dataset from four raw zip archives.
2. Generate offline augmentations for weak classes.
3. Train YOLO detection.
4. Evaluate both detection metrics and image-level aggregation metrics.

The detailed pipeline and hyperparameters are documented in [docs/TRAINING.md](docs/TRAINING.md).

## Dataset Summary

The raw dataset is not committed to this repository. The original archive names are:

- `ConvexPoint.zip`
- `ExposeWhite.zip`
- `FiberNep.zip`
- `FabricExposed.zip`

Known characteristics of the data:

- total raw images: `2952`
- all images are defect samples
- there are no clean or normal images in the provided archives
- some archives contain mixed-class images, so this is better treated as a detection task than a pure classification task

## Publishing Notes

This repository is prepared for GitHub publishing and is already initialized as a local git repository.

Suggested next step:

- follow [docs/PUBLISHING.md](docs/PUBLISHING.md) to create the first commit and push to GitHub
