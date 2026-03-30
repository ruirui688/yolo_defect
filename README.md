# 织物缺陷检测 YOLO 项目

这是一个基于 Ultralytics YOLO 的 4 类织物缺陷检测项目仓库。仓库中已经整理好了训练脚本、环境说明、训练好的最终模型，以及发布到 GitHub 所需的文档。

这个仓库支持两种典型使用方式：

1. 你已经有训练好的模型，只想拿它去检测自己的样本。
2. 你希望按完整流程复现数据准备、增强、训练和评估。

## 一、项目目标

本项目的任务类型是目标检测，不是单标签图像分类。

缺陷类别共 4 类：

- `ConvexPoint`
- `ExposeWhite`
- `FiberNep`
- `FabricExposed`

业务目标是：

- 输入一张样本图像
- 输出图中的全部缺陷框
- 输出每个缺陷框对应的缺陷类别

由于原始数据中存在大量“一张图里有多个缺陷类别”的情况，所以本项目采用 detection-first 的训练思路，即保留每张图中的全部标注框，而不是强行把每张图压成单个类别标签。

## 二、如果你只想直接使用训练好的模型

如果你只是想拿仓库里的最终模型去检测自己的样本，你不需要准备训练数据集，也不需要执行训练流程。你只需要：

1. 安装 `conda`
2. 创建运行环境
3. 使用最终模型执行推理
4. 查看标注后的结果图和检测结果 JSON / CSV

请直接看这两份文档：

- [推理与结果查看说明](./docs/INFERENCE.md)
- [最终模型说明](./artifacts/final_model/README.md)

## 三、如果你想复现训练流程

如果你希望从原始 zip 数据重新训练模型，请按下面的顺序阅读：

1. [数据集说明](./docs/DATASET.md)
2. [训练环境与训练流程](./docs/TRAINING.md)
3. [代码目录说明](./code/yolo_defect_framework/README.md)

## 四、仓库里包含什么

当前仓库会被纳入 Git 管理并用于 GitHub 发布的内容包括：

- 训练脚本
- 配置文件
- 环境安装脚本
- 最终训练好的模型
- 中文数据说明文档
- 中文训练说明文档
- 中文推理说明文档
- GitHub 发布说明文档

## 五、仓库里不包含什么

下面这些内容不会提交到 GitHub：

- 原始数据压缩包 `raw_data/`
- 生成后的训练数据集 `output/dataset/`
- 本地训练中间结果 `code/yolo_defect_framework/runs/`
- 本地下载的基础预训练权重 `yolov8m.pt`、`yolo26n.pt`

这样做的目的是：

- 避免把原始数据公开
- 避免仓库体积过大
- 保留完整的工程、训练方法和最终模型

## 六、项目目录结构

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
      reports/
      scripts/
      README.md
      environment.yml
      requirements.txt
      setup_env.sh
      run_prepare.sh
      run_augment.sh
      run_train.sh
      run_evaluate.sh
      run_infer.sh
  docs/
    DATASET.md
    INFERENCE.md
    PUBLISHING.md
    TRAINING.md
```

## 七、最终模型说明

本仓库已经包含最终训练好的模型：

- 模型文件：
  - `artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt`
- 文件大小：
  - 约 `50 MB`
- 对应训练运行名：
  - `defect_yolov8m_1536_detect_all`
- 基础模型：
  - `yolov8m.pt`

模型元数据见：

- [最终模型说明](./artifacts/final_model/README.md)
- [模型摘要 JSON](./artifacts/final_model/metadata/model_summary.json)

## 八、当前训练结果概览

当前保存的训练结果中，核心检测指标如下：

- 最佳 `mAP50(B)`：`0.63379`
- 最佳 `mAP50-95(B)`：`0.33113`
- 图像级聚合测试准确率：`89.63%`

需要注意：

- 上面的 `89.63%` 是图像级聚合结果，只能作为辅助参考
- 本项目真正的主任务仍然是目标检测
- 最终交付物应理解为“缺陷检测模型”，不是“单标签分类器”

更完整的训练方法和结果解释见：

- [训练环境与训练流程](./docs/TRAINING.md)

当前已经公开整理的一份无缺陷测试集评估结果见：

- [NoDefectTempSelect 评估报告](./docs/reports/NoDefectTempSelect/evaluation_report.md)
- [NoDefectTempSelect 汇总 JSON](./docs/reports/NoDefectTempSelect/summary.json)
- [NoDefectTempSelect 逐图 CSV](./docs/reports/NoDefectTempSelect/per_image_results.csv)

## 九、数据集名称与基本情况

原始数据集不包含在本仓库中，但文档里保留了数据集名称和基本统计，便于别人理解你的训练来源。

原始压缩包名称如下：

- `ConvexPoint.zip`
- `ExposeWhite.zip`
- `FiberNep.zip`
- `FabricExposed.zip`

已知数据特点：

- 原始总图像数：`2952`
- 提供的数据全部都是缺陷图
- 原始数据中没有正常样本 / 无缺陷样本
- 部分图片同时包含多个缺陷类别

详细说明见：

- [数据集说明](./docs/DATASET.md)
- [数据集结构分析报告](./code/yolo_defect_framework/reports/dataset_architecture_report.md)

## 十、最常用的两个入口

### 1. 直接检测自己的样本

```bash
cd code/yolo_defect_framework
./run_infer.sh /path/to/your_images ./../../inference_output
```

### 2. 重新训练模型

```bash
cd code/yolo_defect_framework
./setup_env.sh defect-yolo
conda activate defect-yolo
./run_prepare.sh /path/to/raw_data ./../../output/dataset
./run_augment.sh ./../../output/dataset ./configs/augment_config.yaml
./run_train.sh ./../../output/dataset ./configs/train_config.yaml
```

## 十一、文档导航

- [数据集说明](./docs/DATASET.md)
- [训练环境与训练流程](./docs/TRAINING.md)
- [推理与结果查看说明](./docs/INFERENCE.md)
- [GitHub 发布说明](./docs/PUBLISHING.md)
- [最终模型说明](./artifacts/final_model/README.md)
- [代码目录说明](./code/yolo_defect_framework/README.md)
- [NoDefectTempSelect 评估报告](./docs/reports/NoDefectTempSelect/evaluation_report.md)

## 十二、GitHub 发布

当前目录已经初始化为本地 Git 仓库，并已切换到 `main` 分支。后续你只需要提交并绑定 GitHub 远端即可。

发布步骤见：

- [GitHub 发布说明](./docs/PUBLISHING.md)
