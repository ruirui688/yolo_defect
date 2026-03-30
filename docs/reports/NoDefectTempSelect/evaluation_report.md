# NoDefectTempSelect 无缺陷测试集评估报告

## 1. 评估对象

- 测试集压缩包：`/home/rui/defect_project/raw_data/NoDefectTempSelect.zip`
- 模型文件：`/home/rui/defect_project/artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt`
- 评估脚本：`code/yolo_defect_framework/scripts/evaluate_no_defect_zip.py`
- 输出目录：`/home/rui/defect_project/output/no_defect_eval/NoDefectTempSelect`

本次评估将 `NoDefectTempSelect.zip` 视为一套“无缺陷负样本测试集”。

评估前提：

- zip 内共包含 `1099` 张图片
- zip 内共包含 `1099` 个同名 JSON
- 所有参与评估的样本均要求 JSON 中 `shapes` 为空
- 本次实际参与评估的图像数为 `1099`

## 2. 评估配置

| 项目 | 值 |
| --- | --- |
| `imgsz` | `1280` |
| `device` | `0` |
| `conf` | `0.25` |
| `iou` | `0.5` |
| `save_fp_images` | `true` |

## 3. 核心结果

### 3.1 图像级结果

| 指标 | 数值 |
| --- | ---: |
| 评估图像数 | `1099` |
| 真负样本图像数 | `226` |
| 误检图像数 | `873` |
| 图像级真负率 | `20.56%` |
| 图像级误检率 | `79.44%` |

结论：

- 当前模型在这套无缺陷测试集上的图像级误检率很高
- 约 `79.44%` 的无缺陷图像被检出了至少一个缺陷框

### 3.2 误检框结果

| 指标 | 数值 |
| --- | ---: |
| 误检框总数 | `4111` |
| 平均每张评估图像误检框数 | `3.74` |
| 平均每张误检图像误检框数 | `4.71` |
| 单张图最大误检框数 | `25` |
| 误检框数 `>= 10` 的图像数 | `141` |

## 4. 按类别统计误检情况

### 4.1 误检框数量分布

| 类别 | 误检框数 | 占全部误检框比例 |
| --- | ---: | ---: |
| `ConvexPoint` | `3568` | `86.79%` |
| `ExposeWhite` | `334` | `8.12%` |
| `FiberNep` | `197` | `4.79%` |
| `FabricExposed` | `12` | `0.29%` |

### 4.2 出现在误检图像中的类别分布

注意：一张图可能同时误检出多个类别，因此下面的比例之和可能超过 `100%`。

| 类别 | 出现在误检图像中的次数 | 占误检图像比例 |
| --- | ---: | ---: |
| `ConvexPoint` | `770` | `88.20%` |
| `ExposeWhite` | `166` | `19.01%` |
| `FiberNep` | `119` | `13.63%` |
| `FabricExposed` | `7` | `0.80%` |

结论：

- 当前误检几乎主要由 `ConvexPoint` 驱动
- `ExposeWhite` 是第二大误检来源
- `FabricExposed` 在无缺陷图上的误检相对较少

## 5. 误检置信度情况

### 5.1 误检框置信度统计

| 指标 | 数值 |
| --- | ---: |
| 最小值 | `0.2502` |
| 平均值 | `0.6172` |
| 中位数 | `0.6582` |
| 最大值 | `0.9463` |

### 5.2 误检图像最大置信度统计

| 指标 | 数值 |
| --- | ---: |
| 最小值 | `0.2515` |
| 平均值 | `0.7296` |
| 中位数 | `0.7832` |
| 最大值 | `0.9463` |

### 5.3 高置信误检图像数量

| 条件 | 图像数 |
| --- | ---: |
| 最大置信度 `>= 0.5` | `778` |
| 最大置信度 `>= 0.7` | `610` |
| 最大置信度 `>= 0.8` | `388` |
| 最大置信度 `>= 0.9` | `10` |

结论：

- 当前模型不只是“低置信度轻微误报”
- 高置信误检也不少，尤其是最大置信度 `>= 0.8` 的误检图像有 `388` 张

## 6. 重点误检样本

以下样本值得优先人工复核：

| 图像名 | 误检框数 | 最大置信度 | 误检类别 |
| --- | ---: | ---: | --- |
| `NoDefectTempSelect_0073.bmp` | `17` | `0.9463` | `ConvexPoint`, `FiberNep` |
| `NoDefectTempSelect_0079.bmp` | `10` | `0.9337` | `ConvexPoint`, `FiberNep` |
| `NoDefectTempSelect_0975.bmp` | `1` | `0.9318` | `ExposeWhite` |
| `NoDefectTempSelect_0728.bmp` | `9` | `0.9230` | `ConvexPoint`, `FiberNep` |
| `NoDefectTempSelect_0712.bmp` | `7` | `0.9198` | `ConvexPoint`, `ExposeWhite`, `FiberNep` |
| `NoDefectTempSelect_0735.bmp` | `4` | `0.9124` | `ExposeWhite`, `FiberNep` |
| `NoDefectTempSelect_0277.bmp` | `4` | `0.9112` | `ExposeWhite`, `FiberNep` |
| `NoDefectTempSelect_0400.bmp` | `17` | `0.9093` | `ConvexPoint` |
| `NoDefectTempSelect_0242.bmp` | `7` | `0.9084` | `ExposeWhite`, `FiberNep` |
| `NoDefectTempSelect_0680.bmp` | `5` | `0.9038` | `ConvexPoint`, `ExposeWhite` |

这些样本对应的标注图和详细 JSON 已导出，可直接查看。

## 7. 已导出的结果文件

### 7.1 汇总结果

- `summary.json`
  - 汇总指标、类别分布、置信度统计、重点误检样本
- `per_image_results.csv`
  - 每张图像的评估结果

### 7.2 误检样本详情

- `false_positive_images/`
  - 共导出 `873` 张误检标注图
- `false_positive_details/`
  - 共导出 `873` 份误检详情 JSON

## 8. 结果解读

从这次负样本评估来看，当前模型在“无缺陷样本上的误报控制”方面还有明显问题。

主要表现为：

1. 图像级误检率很高，接近 `80%`
2. `ConvexPoint` 是最主要的误报来源
3. 高置信误检并不少，不是简单调高一点阈值就能完全解决

## 9. 建议的后续优化方向

建议优先做下面几件事：

1. 把这套 `NoDefectTempSelect` 作为正式负样本集纳入训练或验证流程。
2. 在训练数据中加入足量“无缺陷”样本，显式训练模型学会“不报框”。
3. 单独分析 `ConvexPoint` 的误检样本，排查是否存在纹理、光照、噪声或边缘结构触发误检。
4. 重新评估不同 `conf` 阈值下的误检率，尤其对 `ConvexPoint` 进行阈值敏感性测试。
5. 如果业务允许，考虑增加后处理规则，例如最小框尺寸、区域过滤、类别特定阈值。

## 10. 文件位置

本报告文件路径：

```text
/home/rui/defect_project/output/no_defect_eval/NoDefectTempSelect/evaluation_report.md
```

