# Dataset Architecture Report

## Overall

| Dataset | Total Images | Single-Class Images | Mixed-Class Images | Mixed Ratio |
|---|---:|---:|---:|---:|
| ConvexPoint.zip | 1344 | 1344 | 0 | 0.00% |
| ExposeWhite.zip | 1050 | 811 | 239 | 22.76% |
| FiberNep.zip | 409 | 123 | 286 | 69.93% |
| FabricExposed.zip | 149 | 73 | 76 | 51.01% |
| All Datasets | 2952 | 2351 | 601 | 20.36% |

## ConvexPoint.zip

### Combination Distribution

| Label Combination | Count | Ratio of Dataset | Ratio of Mixed Images |
|---|---:|---:|---:|
| ConvexPoint | 1344 | 100.00% | 0.00% |

### Class Presence in Images

| Class | Images Containing This Class | Ratio of Dataset | Ratio of Mixed Images |
|---|---:|---:|---:|
| ConvexPoint | 1344 | 100.00% | 0.00% |
| ExposeWhite | 0 | 0.00% | 0.00% |
| FiberNep | 0 | 0.00% | 0.00% |
| FabricExposed | 0 | 0.00% | 0.00% |

## ExposeWhite.zip

### Combination Distribution

| Label Combination | Count | Ratio of Dataset | Ratio of Mixed Images |
|---|---:|---:|---:|
| ExposeWhite | 811 | 77.24% | 0.00% |
| ConvexPoint + ExposeWhite | 239 | 22.76% | 100.00% |

### Class Presence in Images

| Class | Images Containing This Class | Ratio of Dataset | Ratio of Mixed Images |
|---|---:|---:|---:|
| ConvexPoint | 239 | 22.76% | 100.00% |
| ExposeWhite | 1050 | 100.00% | 100.00% |
| FiberNep | 0 | 0.00% | 0.00% |
| FabricExposed | 0 | 0.00% | 0.00% |

## FiberNep.zip

### Combination Distribution

| Label Combination | Count | Ratio of Dataset | Ratio of Mixed Images |
|---|---:|---:|---:|
| ConvexPoint + FiberNep | 185 | 45.23% | 64.69% |
| FiberNep | 123 | 30.07% | 0.00% |
| ConvexPoint + ExposeWhite + FiberNep | 59 | 14.43% | 20.63% |
| ExposeWhite + FiberNep | 42 | 10.27% | 14.69% |

### Class Presence in Images

| Class | Images Containing This Class | Ratio of Dataset | Ratio of Mixed Images |
|---|---:|---:|---:|
| ConvexPoint | 244 | 59.66% | 85.31% |
| ExposeWhite | 101 | 24.69% | 35.31% |
| FiberNep | 409 | 100.00% | 100.00% |
| FabricExposed | 0 | 0.00% | 0.00% |

## FabricExposed.zip

### Combination Distribution

| Label Combination | Count | Ratio of Dataset | Ratio of Mixed Images |
|---|---:|---:|---:|
| FabricExposed | 73 | 48.99% | 0.00% |
| ConvexPoint + FabricExposed | 35 | 23.49% | 46.05% |
| ConvexPoint + FiberNep + FabricExposed | 15 | 10.07% | 19.74% |
| ExposeWhite + FabricExposed | 9 | 6.04% | 11.84% |
| ConvexPoint + ExposeWhite + FabricExposed | 9 | 6.04% | 11.84% |
| FiberNep + FabricExposed | 4 | 2.68% | 5.26% |
| ExposeWhite + FiberNep + FabricExposed | 2 | 1.34% | 2.63% |
| ConvexPoint + ExposeWhite + FiberNep + FabricExposed | 2 | 1.34% | 2.63% |

### Class Presence in Images

| Class | Images Containing This Class | Ratio of Dataset | Ratio of Mixed Images |
|---|---:|---:|---:|
| ConvexPoint | 61 | 40.94% | 80.26% |
| ExposeWhite | 22 | 14.77% | 28.95% |
| FiberNep | 23 | 15.44% | 30.26% |
| FabricExposed | 149 | 100.00% | 100.00% |

## Direct Takeaways

- ConvexPoint.zip is a pure single-class dataset.
- ExposeWhite.zip contains only two structures: pure ExposeWhite, or ConvexPoint + ExposeWhite.
- FiberNep.zip is heavily mixed and never appears with FabricExposed.
- FabricExposed.zip is also heavily mixed and is the most structurally complex dataset.
- This dataset collection is not a strict one-image-one-class classification dataset. It is a detection dataset with image-level ambiguity in several archives.
