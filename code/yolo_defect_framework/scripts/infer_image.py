from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from common import CLASS_NAMES, aggregate_prediction


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run YOLO on a single image and output the predicted defect type.")
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--device", type=str, default="0")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--pred-mode", type=str, default="max_conf", choices=["max_conf", "sum_conf", "area_conf"])
    parser.add_argument("--save-annotated", type=Path, default=None)
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    model = YOLO(args.weights.as_posix())
    result = model.predict(
        source=args.image.as_posix(),
        imgsz=args.imgsz,
        device=args.device,
        conf=args.conf,
        iou=args.iou,
        verbose=False,
    )[0]

    detections = []
    if result.boxes is not None:
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

    pred_class_id, scores = aggregate_prediction(detections, mode=args.pred_mode)
    payload = {
        "image": args.image.as_posix(),
        "predicted_class_id": pred_class_id,
        "predicted_class_name": CLASS_NAMES[pred_class_id] if pred_class_id is not None else "NO_PREDICTION",
        "prediction_scores": {CLASS_NAMES[k]: v for k, v in sorted(scores.items())},
        "detections": detections,
    }

    if args.save_annotated is not None:
        args.save_annotated.parent.mkdir(parents=True, exist_ok=True)
        annotated = result.plot()
        Image.fromarray(annotated[..., ::-1]).save(args.save_annotated)
        payload["annotated_image"] = args.save_annotated.as_posix()

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
