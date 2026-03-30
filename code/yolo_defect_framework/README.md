# yolo_defect_framework 代码目录说明

这个目录是项目的核心代码目录，包含训练、评估、推理、环境安装和数据准备所需的脚本。

如果你是第一次接触这个仓库，建议先看仓库根目录的：

- [项目总览](../../README.md)
- [训练环境与训练流程](../../docs/TRAINING.md)
- [推理与结果查看说明](../../docs/INFERENCE.md)

## 一、目录作用

这个目录主要负责：

- 创建训练环境
- 从原始 zip 数据准备 YOLO 数据集
- 对弱类生成离线增强样本
- 训练 YOLO 检测模型
- 评估模型
- 对单张或一批图片做推理

## 二、主要文件说明

### 配置文件

- `configs/train_config.yaml`
  - 训练配置
- `configs/augment_config.yaml`
  - 弱类增强配置

### 核心脚本

- `scripts/common.py`
  - 公共常量和工具函数
- `scripts/prepare_dataset.py`
  - 从 4 个原始 zip 包生成训练数据集
- `scripts/augment_train_split.py`
  - 对训练集中的弱类做离线增强
- `scripts/train.py`
  - 启动 YOLO 训练
- `scripts/evaluate.py`
  - 生成图像级聚合评估结果
- `scripts/infer_image.py`
  - 对单张图片做推理
- `scripts/infer_directory.py`
  - 对图片目录做批量推理并输出汇总结果
- `scripts/export_model.py`
  - 导出 ONNX / engine 模型
- `scripts/verify_env.py`
  - 检查当前 Python / CUDA / YOLO 环境是否可用

### 包装脚本

- `setup_env.sh`
  - 创建并安装 Ubuntu + conda 环境
- `run_prepare.sh`
  - 数据准备包装脚本
- `run_augment.sh`
  - 数据增强包装脚本
- `run_train.sh`
  - 训练包装脚本
- `run_evaluate.sh`
  - 评估包装脚本
- `run_infer.sh`
  - 批量推理包装脚本

### 其他文件

- `environment.yml`
  - conda 环境定义
- `requirements.txt`
  - Python 依赖
- `reports/dataset_architecture_report.md`
  - 原始数据结构分析报告

## 三、最常用命令

### 1. 创建环境

```bash
cd /home/rui/defect_project/code/yolo_defect_framework
./setup_env.sh defect-yolo
conda activate defect-yolo
```

### 2. 准备数据

```bash
./run_prepare.sh /home/rui/defect_project/raw_data /home/rui/defect_project/output/dataset
```

### 3. 执行弱类增强

```bash
./run_augment.sh /home/rui/defect_project/output/dataset ./configs/augment_config.yaml
```

### 4. 训练模型

```bash
./run_train.sh /home/rui/defect_project/output/dataset ./configs/train_config.yaml
```

### 5. 评估模型

```bash
./run_evaluate.sh \
  /home/rui/defect_project/artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  /home/rui/defect_project/output/dataset
```

### 6. 批量检测自己的样本

```bash
./run_infer.sh /path/to/your_images /home/rui/defect_project/inference_output
```

## 四、当前推荐的阅读顺序

如果你要训练：

1. [训练环境与训练流程](../../docs/TRAINING.md)
2. [数据集说明](../../docs/DATASET.md)
3. 本文件

如果你只想推理：

1. [最终模型说明](../../artifacts/final_model/README.md)
2. [推理与结果查看说明](../../docs/INFERENCE.md)
3. 本文件

