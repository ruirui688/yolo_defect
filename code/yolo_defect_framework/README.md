# YOLO Defect Framework

This project is scaffolded for a 4-class defect-detection task built on YOLO. It assumes:

- all provided raw images are defect samples
- the four classes are `ConvexPoint`, `ExposeWhite`, `FiberNep`, and `FabricExposed`
- the final business output is all defect boxes and classes in each image

The training architecture is now detection-first. It keeps every labeled box, trains on all defects in an image, and adds offline augmentation focused on weak classes such as `FiberNep` and `FabricExposed`.

## Recommended environment

Target machine:

- Ubuntu
- `conda` environment
- NVIDIA GeForce RTX 5060 Ti 16 GB
- NVIDIA driver `580.126.09`

The environment setup here uses:

- `Python 3.10`
- `PyTorch` installed from the official `cu128` wheel index
- `Ultralytics YOLO`

This is a pragmatic fit for your GPU and current Linux setup.

## Project layout

```text
yolo_defect_framework/
  configs/
    train_config.yaml
  scripts/
    augment_train_split.py
    common.py
    prepare_dataset.py
    train.py
    evaluate.py
    infer_image.py
    export_model.py
    verify_env.py
  environment.yml
  requirements.txt
  setup_env.sh
  run_augment.sh
  run_prepare.sh
  run_train.sh
  run_evaluate.sh
```

## Quick start on Ubuntu with conda

1. Copy this folder to the training machine.
2. Put the 4 raw zip files in one directory such as `/data/defect_raw`.
3. Open a terminal in the project root.
4. Create the conda environment and install GPU packages:

```bash
chmod +x setup_env.sh run_prepare.sh run_augment.sh run_train.sh run_evaluate.sh
./setup_env.sh defect-yolo
```

5. Activate the environment:

```bash
conda activate defect-yolo
```

6. Prepare the dataset:

```bash
./run_prepare.sh /data/defect_raw ./dataset
```

7. Generate weak-class augmentations on the train split:

```bash
./run_augment.sh ./dataset ./configs/augment_config.yaml
```

8. Start training:

```bash
./run_train.sh ./dataset ./configs/train_config.yaml
```

9. Evaluate detection and image-level outputs:

```bash
./run_evaluate.sh ./runs/detect/runs/defect_yolov8m_1536_detect_all/weights/best.pt ./dataset
```

## Direct commands

Prepare dataset:

```bash
python ./scripts/prepare_dataset.py --raw-dir /data/defect_raw --output-dir ./dataset
```

Generate weak-class augmentations:

```bash
python ./scripts/augment_train_split.py --dataset-root ./dataset --config ./configs/augment_config.yaml
```

Train:

```bash
python ./scripts/train.py --config ./configs/train_config.yaml --data ./dataset/data.yaml
```

Evaluate image-level accuracy:

```bash
python ./scripts/evaluate.py --weights ./runs/detect/runs/defect_yolov8m_1536_detect_all/weights/best.pt --dataset-root ./dataset --split test --gt-mode largest_area --pred-mode area_conf
```

Infer a single image:

```bash
python ./scripts/infer_image.py --weights ./runs/detect/runs/defect_yolov8m_1536_detect_all/weights/best.pt --image /data/test.bmp --save-annotated ./outputs/infer.bmp
```

Export ONNX:

```bash
python ./scripts/export_model.py --weights ./runs/detect/runs/defect_yolov8m_1536_detect_all/weights/best.pt --format onnx
```

Check GPU environment:

```bash
python ./scripts/verify_env.py
```

## Notes on labels

The dataset preparation script stores three image-level label interpretations in `dataset/metadata/manifest.csv`:

- `primary_by_source`: uses the original archive name as the image label
- `primary_by_count`: uses the class with the most boxes in the image
- `primary_by_area`: uses the class with the largest total labeled area in the image

For pure detection training, all box labels are kept as-is. The image-level fields in `manifest.csv` are only helper metadata for later reporting.

## Recommended first run

- model: `yolov8m.pt`
- image size: `1536`
- epochs: `200`
- batch: `4`
- workers: `4` to start
- generate targeted train augmentations before training
- final business metric: per-class detection recall/precision/mAP, especially `FiberNep` and `FabricExposed`

## Practical notes for your GPU

- With a 16 GB RTX 5060 Ti, this repo now starts at `batch=4` for `imgsz=1536`.
- If you hit CUDA OOM, reduce `imgsz` to `1280` before reducing model size.
- If recall is still weak on small defects after the second run, increase `copies_per_object` in `configs/augment_config.yaml`.
- If you need better deployment speed later, export ONNX first, then move to TensorRT.
