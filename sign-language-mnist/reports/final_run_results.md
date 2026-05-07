# Final Run Results

This file records the final execution results after running the project with the provided CSV files:

- `data/raw/sign_mnist_train.csv`
- `data/raw/sign_mnist_test.csv`

## Dataset loaded successfully

| Split | Samples | Features |
|---|---:|---:|
| Train | 27,455 | 784 |
| Test | 7,172 | 784 |

The perceptron notebook uses an added bias feature, therefore its input matrix is `(samples, 785)`. The neural-network notebook uses the original 784 pixel features.

## Section 1 - Perceptron

| Experiment | Best configuration | Accuracy | Precision | Recall |
|---|---|---:|---:|---:|
| Binary C vs rest | Step activation + online learning | 0.993028 | 0.967626 | 0.867742 |
| Multi-class One-vs-Rest | Sigmoid activation + online learning | 0.378137 | 0.318149 macro | 0.305569 macro |

## Section 2 - Neural Network

| Experiment | Best configuration | Accuracy | Precision | Recall |
|---|---|---:|---:|---:|
| Binary C vs rest | ReLU, hidden layer `[128]`, momentum `0.9` | 0.998606 | 1.000000 | 0.967742 |
| Multi-class, raw test labels | ReLU, hidden layers `[512, 256]` | 0.458450 | 0.397588 macro | 0.382335 macro |
| Multi-class, aligned-label diagnostic | ReLU, hidden layers `[512, 256]` | 0.886224 | 0.869263 macro | 0.852403 macro |

## Final interpretation

The official raw-label held-out test result for the final multi-class neural network is **45.84% accuracy**. The aligned-label diagnostic reaches **88.62% accuracy**, which supports the documented hypothesis that the provided test labels are compressed from class 10 onward. The raw-label result is kept as the official result because it uses `sign_mnist_test.csv` exactly as provided.
