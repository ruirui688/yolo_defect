# Final Model Artifact

## Files

```text
artifacts/final_model/
  README.md
  metadata/
    model_summary.json
  weights/
    defect_yolov8m_1536_detect_all_best.pt
```

## Model Summary

- task: 4-class defect detection
- framework: Ultralytics YOLO
- trained model name: `defect_yolov8m_1536_detect_all`
- base model: `yolov8m.pt`
- final weight file:
  - `weights/defect_yolov8m_1536_detect_all_best.pt`
- SHA256:
  - `54eaa874368e222e689dfeab88a0b3e6b3b6aee8ccba9418a7bdc6033d8ba173`

## Detection Classes

- `ConvexPoint`
- `ExposeWhite`
- `FiberNep`
- `FabricExposed`

## Inference Example

```bash
python code/yolo_defect_framework/scripts/infer_image.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --image /path/to/test.bmp \
  --save-annotated ./infer_result.bmp
```

## Supporting Documentation

- repository overview:
  - `README.md`
- dataset documentation:
  - `docs/DATASET.md`
- training method:
  - `docs/TRAINING.md`
- artifact metadata:
  - `metadata/model_summary.json`

