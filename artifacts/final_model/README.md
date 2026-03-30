# 最终模型说明

这个目录用于对外提供“最终训练好的模型”和它对应的说明信息。

如果别人只想拿这个模型去检测自己的样本，重点看本文件和 [推理与结果查看说明](../../docs/INFERENCE.md) 即可。

## 一、目录结构

```text
artifacts/final_model/
  README.md
  metadata/
    model_summary.json
  weights/
    defect_yolov8m_1536_detect_all_best.pt
```

## 二、模型文件

- 最终模型文件：
  - `weights/defect_yolov8m_1536_detect_all_best.pt`
- 对应训练运行名：
  - `defect_yolov8m_1536_detect_all`
- 基础模型：
  - `yolov8m.pt`
- 文件大小：
  - 约 `50 MB`
- SHA256：
  - `54eaa874368e222e689dfeab88a0b3e6b3b6aee8ccba9418a7bdc6033d8ba173`

## 三、模型对应的缺陷类别

本模型一共检测 4 类缺陷：

- `ConvexPoint`
- `ExposeWhite`
- `FiberNep`
- `FabricExposed`

## 四、最快速的使用方式

### 1. 检测单张图片

```bash
cd /home/rui/defect_project
python code/yolo_defect_framework/scripts/infer_image.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --image /path/to/test.bmp \
  --save-annotated ./inference_output/test_result.bmp
```

### 2. 批量检测一个目录

```bash
cd /home/rui/defect_project
python code/yolo_defect_framework/scripts/infer_directory.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --source /path/to/test_images \
  --output-dir ./inference_output
```

## 五、跑完推理后去哪里看结果

如果你执行的是目录批量检测，默认结果目录里会有：

- `annotated/`
  - 带检测框的结果图
- `details/`
  - 每张图的详细 JSON
- `summary.csv`
  - 批量结果汇总表
- `summary.json`
  - 批量结果汇总 JSON

如果你执行的是单张图检测，那么：

- 终端会打印一份 JSON
- `--save-annotated` 指定的位置会保存标注图

## 六、只想使用模型时需要看哪些文档

如果你不训练，只推理，建议阅读顺序：

1. 本文件
2. [推理与结果查看说明](../../docs/INFERENCE.md)

## 七、如果你想复现训练

如果你想知道这个模型是怎么训练出来的，请看：

- [训练环境与训练流程](../../docs/TRAINING.md)
- [数据集说明](../../docs/DATASET.md)
- [模型摘要 JSON](./metadata/model_summary.json)

