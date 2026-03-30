# 数据集结构分析报告

## 一、整体情况

| 数据集 | 总图像数 | 单类别图像数 | 混合类别图像数 | 混合比例 |
|---|---:|---:|---:|---:|
| ConvexPoint.zip | 1344 | 1344 | 0 | 0.00% |
| ExposeWhite.zip | 1050 | 811 | 239 | 22.76% |
| FiberNep.zip | 409 | 123 | 286 | 69.93% |
| FabricExposed.zip | 149 | 73 | 76 | 51.01% |
| 全部数据 | 2952 | 2351 | 601 | 20.36% |

## 二、ConvexPoint.zip

### 类别组合分布

| 类别组合 | 数量 | 占该数据集比例 | 占混合图比例 |
|---|---:|---:|---:|
| ConvexPoint | 1344 | 100.00% | 0.00% |

### 类别出现情况

| 类别 | 含该类别的图像数 | 占该数据集比例 | 占混合图比例 |
|---|---:|---:|---:|
| ConvexPoint | 1344 | 100.00% | 0.00% |
| ExposeWhite | 0 | 0.00% | 0.00% |
| FiberNep | 0 | 0.00% | 0.00% |
| FabricExposed | 0 | 0.00% | 0.00% |

## 三、ExposeWhite.zip

### 类别组合分布

| 类别组合 | 数量 | 占该数据集比例 | 占混合图比例 |
|---|---:|---:|---:|
| ExposeWhite | 811 | 77.24% | 0.00% |
| ConvexPoint + ExposeWhite | 239 | 22.76% | 100.00% |

### 类别出现情况

| 类别 | 含该类别的图像数 | 占该数据集比例 | 占混合图比例 |
|---|---:|---:|---:|
| ConvexPoint | 239 | 22.76% | 100.00% |
| ExposeWhite | 1050 | 100.00% | 100.00% |
| FiberNep | 0 | 0.00% | 0.00% |
| FabricExposed | 0 | 0.00% | 0.00% |

## 四、FiberNep.zip

### 类别组合分布

| 类别组合 | 数量 | 占该数据集比例 | 占混合图比例 |
|---|---:|---:|---:|
| ConvexPoint + FiberNep | 185 | 45.23% | 64.69% |
| FiberNep | 123 | 30.07% | 0.00% |
| ConvexPoint + ExposeWhite + FiberNep | 59 | 14.43% | 20.63% |
| ExposeWhite + FiberNep | 42 | 10.27% | 14.69% |

### 类别出现情况

| 类别 | 含该类别的图像数 | 占该数据集比例 | 占混合图比例 |
|---|---:|---:|---:|
| ConvexPoint | 244 | 59.66% | 85.31% |
| ExposeWhite | 101 | 24.69% | 35.31% |
| FiberNep | 409 | 100.00% | 100.00% |
| FabricExposed | 0 | 0.00% | 0.00% |

## 五、FabricExposed.zip

### 类别组合分布

| 类别组合 | 数量 | 占该数据集比例 | 占混合图比例 |
|---|---:|---:|---:|
| FabricExposed | 73 | 48.99% | 0.00% |
| ConvexPoint + FabricExposed | 35 | 23.49% | 46.05% |
| ConvexPoint + FiberNep + FabricExposed | 15 | 10.07% | 19.74% |
| ExposeWhite + FabricExposed | 9 | 6.04% | 11.84% |
| ConvexPoint + ExposeWhite + FabricExposed | 9 | 6.04% | 11.84% |
| FiberNep + FabricExposed | 4 | 2.68% | 5.26% |
| ExposeWhite + FiberNep + FabricExposed | 2 | 1.34% | 2.63% |
| ConvexPoint + ExposeWhite + FiberNep + FabricExposed | 2 | 1.34% | 2.63% |

### 类别出现情况

| 类别 | 含该类别的图像数 | 占该数据集比例 | 占混合图比例 |
|---|---:|---:|---:|
| ConvexPoint | 61 | 40.94% | 80.26% |
| ExposeWhite | 22 | 14.77% | 28.95% |
| FiberNep | 23 | 15.44% | 30.26% |
| FabricExposed | 149 | 100.00% | 100.00% |

## 六、结论

- `ConvexPoint.zip` 是纯单类别数据集。
- `ExposeWhite.zip` 只出现两种结构：纯 `ExposeWhite`，或者 `ConvexPoint + ExposeWhite`。
- `FiberNep.zip` 的混合类别比例非常高，而且不会与 `FabricExposed` 同时出现。
- `FabricExposed.zip` 也有较高比例的混合类别图片，并且结构最复杂。
- 从整体上看，这批数据并不是严格的一图一类分类数据，而是一批更适合做目标检测的数据。

