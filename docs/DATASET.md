# 数据集说明

## 一、说明范围

本文件只说明数据集的名称、类别、数量、结构特点和本项目如何使用这些数据。

本仓库不会公开提交原始数据集文件，也不会提交生成后的训练集文件。

不会提交的内容包括：

- `raw_data/`
- `output/dataset/`

## 二、原始数据集名称

本项目使用的原始压缩包名称如下：

| 原始压缩包 | 名义主类 | 图像数量 |
| --- | --- | ---: |
| `ConvexPoint.zip` | `ConvexPoint` | 1344 |
| `ExposeWhite.zip` | `ExposeWhite` | 1050 |
| `FiberNep.zip` | `FiberNep` | 409 |
| `FabricExposed.zip` | `FabricExposed` | 149 |

原始总图像数：`2952`

## 三、检测类别

本项目共使用 4 个检测类别：

| 类别 ID | 类别名称 |
| --- | --- |
| 0 | `ConvexPoint` |
| 1 | `ExposeWhite` |
| 2 | `FiberNep` |
| 3 | `FabricExposed` |

## 四、数据集特点

数据集有几个非常关键的特点：

1. 所有提供的图像都是缺陷图。
2. 原始数据中没有正常样本，也没有无缺陷样本。
3. 数据并不是严格的一图一类。
4. 部分图片同时包含多个类别的缺陷框。

这意味着：

- 这个任务更适合做目标检测
- 不适合直接当成单标签分类任务来理解

## 五、混合类别情况

根据数据结构分析报告，原始数据中混合类别图片的情况如下：

| 原始压缩包 | 混合类别图片数 | 混合比例 |
| --- | ---: | ---: |
| `ConvexPoint.zip` | 0 | 0.00% |
| `ExposeWhite.zip` | 239 | 22.76% |
| `FiberNep.zip` | 286 | 69.93% |
| `FabricExposed.zip` | 76 | 51.01% |
| 全部数据 | 601 | 20.36% |

其中最需要注意的是：

- `FiberNep.zip` 的混合比例非常高
- `FabricExposed.zip` 也有较高比例的混合类别图片

这也是本项目后续设计弱类增强策略的重要原因。

## 六、标注格式

原始标签采用 YOLO 格式，每一行表示一个目标框：

```text
class_id x_center y_center width height
```

每张图中可以有：

- 一个或多个目标框
- 一个或多个缺陷类别

## 七、本项目如何组织生成后的训练数据

本项目在本地训练时，会把数据整理成标准 YOLO 目录结构：

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

其中：

- `manifest.csv` 记录每张图来自哪个原始数据集、属于哪个 split、以及多种图像级标签解释
- `summary.json` 记录切分后的总体统计
- `reports/` 记录评估输出

## 八、切分后的样本数量

在当前这次训练中，原始样本切分结果为：

| 数据划分 | 数量 |
| --- | ---: |
| train | 2065 |
| val | 588 |
| test | 299 |

这是原始样本切分结果，不包含后续离线增强生成的训练样本。

## 九、弱类增强后的训练规模

为了增强弱类识别能力，本项目对训练集中的弱类做了离线增强。

当前这次训练的增强结果为：

- 原始 train 图像数：`2065`
- 新增增强图像数：`3040`
- 增强后 train 目录图像总数：`5105`

按类别统计的增强数量为：

- `FiberNep`：`1882`
- `FabricExposed`：`1158`

## 十、公开发布时应该怎么描述数据集

如果这个仓库要公开发布到 GitHub，推荐做法是：

- 可以公开说明原始压缩包名称
- 可以公开说明类别名称和数量统计
- 可以公开说明数据结构特点和训练方法
- 不要公开提交原始图片和标签文件
- 不要公开提交 `raw_data/*.zip`
- 不要公开提交 `output/dataset/**`

## 十一、相关文档

- [训练环境与训练流程](./TRAINING.md)
- [推理与结果查看说明](./INFERENCE.md)
- [数据集结构分析报告](../code/yolo_defect_framework/reports/dataset_architecture_report.md)

