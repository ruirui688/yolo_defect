# 推理与结果查看说明

这份文档面向两类人：

1. 你只想使用已经训练好的模型去检测自己的样本。
2. 你想知道模型跑完之后，结果文件在哪里、怎么查看。

## 一、只做推理时你不需要什么

如果你只是要使用训练好的模型做检测，你不需要：

- 原始数据压缩包
- `output/dataset/` 训练集
- 重新执行数据准备和训练

你只需要：

- 本仓库代码
- 最终模型文件
- 你自己的待检测图片

## 二、先准备运行环境

推荐环境是 Ubuntu + conda。

如果你的机器还没有安装 conda，请先参考 [训练环境与训练流程](./TRAINING.md) 里的 Miniconda 安装章节。

如果 conda 已经安装好，执行：

```bash
cd /home/rui/defect_project/code/yolo_defect_framework
chmod +x setup_env.sh run_infer.sh
./setup_env.sh defect-yolo
conda activate defect-yolo
```

环境准备完成后，你就可以直接推理。

## 三、最终模型在哪里

最终模型文件路径：

```text
artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt
```

模型说明文档：

- [最终模型说明](../artifacts/final_model/README.md)

## 四、检测单张图片

如果你只想检测一张图片，推荐直接使用 `infer_image.py`：

```bash
cd /home/rui/defect_project
python code/yolo_defect_framework/scripts/infer_image.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --image /path/to/your_sample.bmp \
  --save-annotated ./inference_output/one_image_result.bmp
```

执行后你会得到两类结果：

1. 终端打印一份 JSON
2. `--save-annotated` 指定的位置会保存一张带框的标注结果图

## 五、终端 JSON 里会有什么

单张图推理时，终端输出的大致内容包括：

- 输入图路径
- 聚合后的预测类别
- 每个类别的聚合分数
- 检测到的全部缺陷框
- 每个框的类别名、置信度和坐标
- 保存后的标注图路径

你可以把终端输出重定向到文件：

```bash
python code/yolo_defect_framework/scripts/infer_image.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --image /path/to/your_sample.bmp \
  --save-annotated ./inference_output/one_image_result.bmp \
  > ./inference_output/one_image_result.json
```

## 六、批量检测一个目录

为了让别人拿着模型更容易直接使用，我在仓库里补了一个批量检测脚本 `infer_directory.py`，并提供了一个 Linux 包装脚本 `run_infer.sh`。

### 方法 1：用包装脚本

```bash
cd /home/rui/defect_project/code/yolo_defect_framework
./run_infer.sh /path/to/your_images /home/rui/defect_project/inference_output
```

参数含义：

- 第 1 个参数：待检测图片或目录
- 第 2 个参数：输出目录，可省略，默认是仓库根目录下的 `inference_output`
- 第 3 个参数：模型路径，可省略，默认使用仓库里的最终模型

### 方法 2：直接调用 Python 脚本

```bash
cd /home/rui/defect_project
python code/yolo_defect_framework/scripts/infer_directory.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --source /path/to/your_images \
  --output-dir ./inference_output
```

这个脚本支持：

- 输入单张图片
- 输入一个图片目录
- 递归扫描目录中的常见图片格式
- 自动保存带框结果图
- 自动保存每张图的详细 JSON
- 自动保存汇总 `summary.json` 和 `summary.csv`

## 七、批量推理结果会输出到哪里

执行批量检测后，输出目录结构如下：

```text
inference_output/
  annotated/
    ...
  details/
    ...
  summary.csv
  summary.json
```

各文件的作用：

- `annotated/`
  - 保存带检测框和类别文字的结果图
- `details/`
  - 每张图片一份详细 JSON
- `summary.csv`
  - 适合 Excel / 表格软件查看
- `summary.json`
  - 适合程序读取或二次处理

## 八、怎么查看检测结果

最常见的查看方式有 3 种：

### 1. 直接看带框结果图

打开 `annotated/` 下保存的结果图片即可。这是最直观的查看方式。

### 2. 看 `summary.csv`

如果你想快速看一批样本分别被判成了什么类别，直接打开：

```text
inference_output/summary.csv
```

里面会包含：

- 图片相对路径
- 聚合后的预测类别
- 检测框数量
- 各类别分数
- 标注结果图路径
- 单张图详细 JSON 路径

### 3. 看单张图的详细 JSON

如果你想核对一张图里每个框的位置和置信度，去看：

```text
inference_output/details/xxx.json
```

里面会包含：

- 每个检测框的坐标
- 每个检测框的类别
- 每个检测框的置信度
- 聚合后的整图预测类别
- 保存后的标注图路径

## 九、常用参数怎么调

### `--imgsz`

表示推理时缩放到的输入尺寸。

- 默认脚本里单图推理是 `1280`
- 如果你的缺陷很小，可以尝试提高到 `1536`
- 如果你显存不够或推理太慢，可以降到 `1024` 或 `1280`

### `--conf`

表示置信度阈值。

- 默认 `0.25`
- 如果误报太多，可以提高到 `0.35` 或 `0.40`
- 如果漏检太多，可以降低到 `0.15` 或 `0.20`

### `--iou`

表示 NMS 的 IoU 阈值。

- 默认 `0.5`

### `--device`

表示推理设备。

常见写法：

- `--device 0`
  - 使用第 1 张 GPU
- `--device cpu`
  - 使用 CPU 推理

### `--pred-mode`

这个参数只影响“整张图聚合后的类别判定”，不影响检测框本身。

可选值：

- `max_conf`
- `sum_conf`
- `area_conf`

如果你只关心检测框，默认保持 `max_conf` 即可。

## 十、最推荐的两条命令

### 只检测一张图

```bash
python code/yolo_defect_framework/scripts/infer_image.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --image /path/to/test.bmp \
  --save-annotated ./inference_output/test_result.bmp
```

### 检测整个样本目录

```bash
python code/yolo_defect_framework/scripts/infer_directory.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --source /path/to/test_images \
  --output-dir ./inference_output
```

## 十一、评估无缺陷测试集

如果你手里有一套“理论上不应该检出任何缺陷”的测试集，可以直接评估模型的误检情况。

本项目已经提供了针对 zip 数据集的负样本评估脚本，适用于类似下面这种结构：

- zip 中包含图片
- zip 中包含同名 LabelMe JSON
- JSON 里的 `shapes` 为空数组，表示该图无缺陷

例如当前这套测试集：

```text
/home/rui/defect_project/raw_data/NoDefectTempSelect.zip
```

### 用包装脚本

```bash
cd /home/rui/defect_project/code/yolo_defect_framework
./run_evaluate_no_defect.sh \
  /home/rui/defect_project/raw_data/NoDefectTempSelect.zip \
  /home/rui/defect_project/output/no_defect_eval/NoDefectTempSelect \
  /home/rui/defect_project/artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt
```

### 直接用 Python

```bash
cd /home/rui/defect_project
python code/yolo_defect_framework/scripts/evaluate_no_defect_zip.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --zip-path raw_data/NoDefectTempSelect.zip \
  --output-dir output/no_defect_eval/NoDefectTempSelect \
  --save-fp-images
```

脚本会输出：

- `summary.json`
  - 汇总误检率、误检框数量、各类别误检统计
- `per_image_results.csv`
  - 每张图是否误检、误检了几个框、最大置信度是多少
- `false_positive_details/`
  - 每张误检图片的详细 JSON
- `false_positive_images/`
  - 如果启用了 `--save-fp-images`，这里会保存误检图的带框结果

你可以重点关注两个指标：

- `image_level_false_positive_rate`
  - 无缺陷图片里，有多少比例被误检
- `false_positive_boxes_per_class`
  - 哪个类别最容易在无缺陷图上误报

这次已经导出并整理到可提交目录的公开结果见：

- [NoDefectTempSelect 评估报告](./reports/NoDefectTempSelect/evaluation_report.md)
- [NoDefectTempSelect 汇总 JSON](./reports/NoDefectTempSelect/summary.json)
- [NoDefectTempSelect 逐图 CSV](./reports/NoDefectTempSelect/per_image_results.csv)

## 十二、相关文档

- [训练环境与训练流程](./TRAINING.md)
- [最终模型说明](../artifacts/final_model/README.md)
- [项目总览](../README.md)
