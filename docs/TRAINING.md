# 训练环境与训练流程

这份文档用于说明：

- `conda` 怎么安装
- 训练环境怎么创建
- 原始数据应该怎么放
- 数据集怎么准备
- 弱类增强怎么做
- 模型怎么训练
- 训练结果怎么看

本文档以 Ubuntu 为主，因为当前项目的主要目标环境就是 Ubuntu + conda + NVIDIA GPU。

## 一、推荐训练环境

项目当前推荐训练环境如下：

- 操作系统：Ubuntu
- 环境管理：conda
- Python：`3.10`
- PyTorch：通过 CUDA 12.8 官方 wheel 安装
- 主要依赖：
  - `ultralytics>=8.3.0`
  - `PyYAML>=6.0`
  - `Pillow>=10.0`
- 推荐 GPU：
  - NVIDIA GeForce RTX 5060 Ti 16 GB
- 推荐驱动：
  - `580.126.09`

## 二、如果系统还没有 conda，先安装 Miniconda

下面给出一套适用于 Ubuntu 的常见安装方式。

### 1. 下载 Miniconda 安装脚本

```bash
wget -O /tmp/Miniconda3-latest-Linux-x86_64.sh \
  https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

### 2. 安装到当前用户目录

```bash
bash /tmp/Miniconda3-latest-Linux-x86_64.sh -b -p "$HOME/miniconda3"
```

### 3. 让当前 shell 能使用 conda

```bash
eval "$("$HOME/miniconda3/bin/conda" shell.bash hook)"
conda init bash
```

### 4. 重新打开终端，或者执行

```bash
source ~/.bashrc
```

### 5. 验证 conda 是否安装成功

```bash
conda --version
```

如果这里能看到版本号，就说明 conda 已经可以用了。

## 三、进入项目目录

```bash
cd /home/rui/defect_project
```

如果你是从 GitHub 拉下来的项目，一般是：

```bash
git clone <你的仓库地址>
cd defect_project
```

## 四、创建训练环境

本项目已经提供了环境安装脚本：

```bash
cd code/yolo_defect_framework
chmod +x setup_env.sh run_prepare.sh run_augment.sh run_train.sh run_evaluate.sh run_infer.sh
./setup_env.sh defect-yolo
```

这个脚本会做以下几件事：

1. 检查系统里是否有 `conda`
2. 基于 `environment.yml` 创建名为 `defect-yolo` 的 conda 环境
3. 激活这个环境
4. 升级 `pip`
5. 从 CUDA 12.8 的 PyTorch 官方源安装 `torch`、`torchvision`、`torchaudio`
6. 安装 `requirements.txt` 中的其他依赖
7. 运行 `scripts/verify_env.py` 检查环境是否可用

## 五、手动创建环境的等价命令

如果你不想用脚本，也可以手动执行：

```bash
cd /home/rui/defect_project/code/yolo_defect_framework
conda env create -n defect-yolo -f environment.yml
conda activate defect-yolo
python -m pip install --upgrade pip
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r requirements.txt
python scripts/verify_env.py
```

## 六、激活环境

环境创建完成后，后续每次训练前都要先激活：

```bash
conda activate defect-yolo
```

## 七、原始数据应该怎么放

训练所需的原始数据是 4 个 zip 文件：

- `ConvexPoint.zip`
- `ExposeWhite.zip`
- `FiberNep.zip`
- `FabricExposed.zip`

你可以把它们放在任意目录，比如：

```text
/data/defect_raw/
  ConvexPoint.zip
  ExposeWhite.zip
  FiberNep.zip
  FabricExposed.zip
```

也可以直接放在仓库根目录下的：

```text
/home/rui/defect_project/raw_data/
```

## 八、第一步：准备数据集

### 用包装脚本

```bash
cd /home/rui/defect_project/code/yolo_defect_framework
./run_prepare.sh /home/rui/defect_project/raw_data /home/rui/defect_project/output/dataset
```

### 或者直接用 Python

```bash
cd /home/rui/defect_project
python code/yolo_defect_framework/scripts/prepare_dataset.py \
  --raw-dir ./raw_data \
  --output-dir ./output/dataset
```

这一步会做什么：

1. 读取 4 个 zip 包中的图片和 YOLO 标签
2. 自动匹配图片与标签
3. 进行 train / val / test 划分
4. 生成 `output/dataset/data.yaml`
5. 生成 `output/dataset/metadata/manifest.csv`
6. 生成 `output/dataset/metadata/summary.json`

当前这次训练使用的划分结果是：

- train：`2065`
- val：`588`
- test：`299`

## 九、第二步：执行弱类离线增强

本项目没有对所有类别一视同仁地做增强，而是有针对性地增强弱类：

- `FiberNep`
- `FabricExposed`

### 用包装脚本

```bash
cd /home/rui/defect_project/code/yolo_defect_framework
./run_augment.sh /home/rui/defect_project/output/dataset ./configs/augment_config.yaml
```

### 或者直接用 Python

```bash
cd /home/rui/defect_project
python code/yolo_defect_framework/scripts/augment_train_split.py \
  --dataset-root ./output/dataset \
  --config code/yolo_defect_framework/configs/augment_config.yaml
```

当前增强配置的核心参数是：

| 参数 | 当前值 |
| --- | --- |
| `target_classes` | `FiberNep`, `FabricExposed` |
| `crop_size` | `1536` |
| `context_scale` | `6.0` |
| `min_visible_fraction` | `0.35` |
| `min_box_size_px` | `6` |
| `copies_per_object` | `2` |
| `jitter_ratio` | `0.08` |

增强后当前训练集规模为：

- 原始 train 图像：`2065`
- 新增增强图像：`3040`
- 最终 train 目录图像：`5105`

## 十、第三步：开始训练

### 用包装脚本

```bash
cd /home/rui/defect_project/code/yolo_defect_framework
./run_train.sh /home/rui/defect_project/output/dataset ./configs/train_config.yaml
```

### 或者直接用 Python

```bash
cd /home/rui/defect_project
python code/yolo_defect_framework/scripts/train.py \
  --config code/yolo_defect_framework/configs/train_config.yaml \
  --data output/dataset/data.yaml
```

当前训练配置的核心参数如下：

| 参数 | 当前值 |
| --- | --- |
| 基础模型 | `yolov8m.pt` |
| 输入尺寸 | `1536` |
| 训练轮数 | `200` |
| batch size | `4` |
| workers | `4` |
| device | `"0"` |
| 随机种子 | `42` |
| patience | `60` |
| AMP | `true` |

当前启用的主要在线增强包括：

| 参数 | 当前值 |
| --- | --- |
| `degrees` | `4.0` |
| `translate` | `0.05` |
| `scale` | `0.15` |
| `fliplr` | `0.5` |
| `mosaic` | `0.10` |
| `close_mosaic` | `15` |
| `hsv_v` | `0.08` |

## 十一、训练输出会保存到哪里

当前这次训练保存到：

```text
code/yolo_defect_framework/runs/detect/runs/defect_yolov8m_1536_detect_all/
```

里面包含：

- `weights/best.pt`
- `weights/last.pt`
- `results.csv`
- `results.png`
- `confusion_matrix.png`
- 各类曲线图

## 十二、最终模型在哪里

为了方便 GitHub 发布，本仓库已经把最终模型整理到统一位置：

```text
artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt
```

你对外发布时，推荐把这个路径作为“最终模型路径”。

## 十三、怎么评估训练结果

### 1. 查看检测指标

当前训练日志中的关键结果为：

| 指标 | 最佳值 | 对应 epoch |
| --- | ---: | ---: |
| `precision(B)` | `0.72900` | `108` |
| `recall(B)` | `0.58531` | `14` |
| `mAP50(B)` | `0.63379` | `44` |
| `mAP50-95(B)` | `0.33113` | `94` |

### 2. 运行图像级聚合评估

#### 用包装脚本

```bash
cd /home/rui/defect_project/code/yolo_defect_framework
./run_evaluate.sh \
  /home/rui/defect_project/artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  /home/rui/defect_project/output/dataset
```

#### 或者直接用 Python

```bash
cd /home/rui/defect_project
python code/yolo_defect_framework/scripts/evaluate.py \
  --weights artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt \
  --dataset-root output/dataset \
  --split test \
  --gt-mode source_package \
  --pred-mode max_conf
```

当前仓库中已有一份保存好的图像级测试结果：

- 测试图像数：`299`
- 正确数：`268`
- 图像级准确率：`89.63%`

要注意的是：

- 这个结果是图像级聚合结果
- 它不是检测任务的唯一核心指标
- 真正的核心仍然应该看 detection 的 `precision / recall / mAP`

## 十四、训练完成后怎么检测自己的样本

如果训练完成后，你只是想拿最终模型去检测图片，不需要再准备训练数据。

请直接看：

- [推理与结果查看说明](./INFERENCE.md)

## 十五、常见问题

### 1. CUDA 显存不足怎么办

优先尝试：

1. 把 `imgsz` 从 `1536` 降到 `1280`
2. 如果还不行，再考虑减小 batch

### 2. 弱类召回还是低怎么办

优先尝试：

1. 增大 `configs/augment_config.yaml` 中的 `copies_per_object`
2. 继续针对 `FiberNep` 和 `FabricExposed` 做更强的离线增强

### 3. 只有 CPU 能不能跑

可以，但训练会明显变慢。推理时可以显式指定：

```bash
--device cpu
```

### 4. 基础模型 `yolov8m.pt` 不在仓库里怎么办

这是正常的。仓库通过 `.gitignore` 忽略了本地下载的基础权重。

如果本地没有该文件，Ultralytics 在训练时通常会自动下载，或者你也可以手动放到 `code/yolo_defect_framework/` 目录下。

## 十六、相关文档

- [项目总览](../README.md)
- [数据集说明](./DATASET.md)
- [推理与结果查看说明](./INFERENCE.md)
- [代码目录说明](../code/yolo_defect_framework/README.md)

