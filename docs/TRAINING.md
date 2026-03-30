# Training Method And Environment

## Environment

The training environment used by this project is:

- OS: Ubuntu
- environment manager: conda
- Python: `3.10`
- pip: `>=24`
- PyTorch: installed from `https://download.pytorch.org/whl/cu128`
- Ultralytics YOLO: `>=8.3.0`

Dependency files:

- `code/yolo_defect_framework/environment.yml`
- `code/yolo_defect_framework/requirements.txt`
- `code/yolo_defect_framework/setup_env.sh`

Recommended hardware from the original project notes:

- NVIDIA GeForce RTX 5060 Ti 16 GB
- NVIDIA driver `580.126.09`

## Environment Setup

```bash
cd code/yolo_defect_framework
chmod +x setup_env.sh run_prepare.sh run_augment.sh run_train.sh run_evaluate.sh
./setup_env.sh defect-yolo
conda activate defect-yolo
```

## Training Pipeline

### 1. Dataset Preparation

Prepare the dataset from the four raw zip archives:

```bash
python code/yolo_defect_framework/scripts/prepare_dataset.py \
  --raw-dir ./raw_data \
  --output-dir ./output/dataset
```

The preparation script:

- reads the four raw archives
- matches images and YOLO labels
- splits the data into train, val, and test
- writes `data.yaml`
- writes `metadata/manifest.csv`
- writes `metadata/summary.json`

### 2. Weak-Class Offline Augmentation

Generate targeted training augmentations:

```bash
python code/yolo_defect_framework/scripts/augment_train_split.py \
  --dataset-root ./output/dataset \
  --config code/yolo_defect_framework/configs/augment_config.yaml
```

Augmentation strategy:

- target classes:
  - `FiberNep`
  - `FabricExposed`
- crop around target objects
- keep all valid boxes that remain inside the crop
- apply brightness and contrast perturbation
- add jitter to crop center

Configured augmentation values:

| Item | Value |
| --- | --- |
| `crop_size` | `1536` |
| `context_scale` | `6.0` |
| `min_visible_fraction` | `0.35` |
| `min_box_size_px` | `6` |
| `copies_per_object` | `2` |
| `jitter_ratio` | `0.08` |

Observed local result:

- original train images: `2065`
- augmented train images added: `3040`
- final local train directory size: `5105` images
- added weak-class crops:
  - `FiberNep`: `1882`
  - `FabricExposed`: `1158`

### 3. YOLO Training

Training command:

```bash
python code/yolo_defect_framework/scripts/train.py \
  --config code/yolo_defect_framework/configs/train_config.yaml \
  --data output/dataset/data.yaml
```

Training configuration:

| Item | Value |
| --- | --- |
| base model | `yolov8m.pt` |
| image size | `1536` |
| epochs | `200` |
| batch size | `4` |
| workers | `4` |
| device | `0` |
| seed | `42` |
| patience | `60` |
| AMP | `true` |

Important built-in train augmentations:

| Item | Value |
| --- | --- |
| `degrees` | `4.0` |
| `translate` | `0.05` |
| `scale` | `0.15` |
| `fliplr` | `0.5` |
| `mosaic` | `0.10` |
| `close_mosaic` | `15` |
| `hsv_v` | `0.08` |

## Evaluation

### Detection Metrics From The Saved Training Run

The saved training run name is `defect_yolov8m_1536_detect_all`.

Best recorded metrics in the training log:

| Metric | Best Value | Epoch |
| --- | ---: | ---: |
| precision(B) | `0.72900` | `108` |
| recall(B) | `0.58531` | `14` |
| mAP50(B) | `0.63379` | `44` |
| mAP50-95(B) | `0.33113` | `94` |

Final recorded row in the local run log:

| Metric | Value | Epoch |
| --- | ---: | ---: |
| precision(B) | `0.70471` | `154` |
| recall(B) | `0.50190` | `154` |
| mAP50(B) | `0.60218` | `154` |
| mAP50-95(B) | `0.32043` | `154` |

### Image-Level Aggregation Report

The repository also contains an image-level aggregation evaluation on the test split.

Evaluation mode used in the saved report:

- ground truth mode: `source_package`
- prediction mode: `max_conf`

Saved result:

- test images: `299`
- correct images: `268`
- image accuracy: `89.63%`

Important note:

- this image-level accuracy is an auxiliary report
- the core task is still object detection
- the main deployment artifact is the detection model, not a single-label classifier

## Final Model Artifact

- final weight file:
  - `artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt`
- SHA256:
  - `54eaa874368e222e689dfeab88a0b3e6b3b6aee8ccba9418a7bdc6033d8ba173`

See `artifacts/final_model/README.md` for usage details.

