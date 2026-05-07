# Methodology Report

## Aim

This project compares linear perceptrons with fully connected neural networks on Sign Language MNIST. The core aim is to understand how model capacity and optimisation design affect hand-sign image classification when the models are implemented from first principles in NumPy.

The project deliberately avoids high-level deep learning frameworks so that the learning rules, forward pass, backpropagation and optimisation choices remain transparent.

## Section 1 - Perceptron Baselines

The perceptron notebook implements step and sigmoid activation functions with both online and full-batch learning. Binary classification is evaluated as class C vs rest. Multi-class classification is handled with a one-vs-rest strategy across the available sign classes.

The binary perceptron performs strongly, which suggests that the selected target class is linearly separable enough in pixel space. The multi-class perceptron is much weaker, which is expected because a linear one-vs-rest strategy has limited representational capacity on flattened image pixels.

## Section 2 - Fully Connected Neural Network

The neural-network notebook implements a multi-layer feed-forward ANN with mini-batch gradient descent and backpropagation. It supports binary sigmoid output and multi-class softmax output. ReLU models use He initialisation, while sigmoid models use Xavier-style scaling.

The final ReLU model uses validation-based model selection, deterministic shift augmentation, dropout, L2 regularisation and early stopping. This gives a stronger non-linear baseline while keeping the implementation inspectable.

## Evaluation Design

The project reports accuracy, precision, recall, macro averages, confusion matrices and learning curves. The multi-class neural network is reported in two ways:

- raw test-label evaluation, using `sign_mnist_test.csv` exactly as provided;
- aligned-label diagnostic evaluation, used only to investigate the apparent class-index compression in the test split.

The raw-label result remains the primary held-out result. The aligned-label result is included as diagnostic evidence rather than as a replacement benchmark.

## Final Executed Run

After adding the local CSV files and executing both notebooks, the selected models produced the following key results:

- Best binary perceptron: step activation with online learning, accuracy `0.993028`, precision `0.967626`, recall `0.867742`.
- Best multi-class perceptron: sigmoid activation with online one-vs-rest learning, accuracy `0.378137`, macro precision `0.318149`, macro recall `0.305569`.
- Best binary neural network: ReLU with one hidden layer `[128]`, accuracy `0.998606`, precision `1.000000`, recall `0.967742`.
- Final multi-class neural network on raw test labels: ReLU `[512, 256]`, accuracy `0.458450`, macro precision `0.397588`, macro recall `0.382335`.
- Diagnostic aligned-label multi-class result: ReLU `[512, 256]`, accuracy `0.886224`, macro precision `0.869263`, macro recall `0.852403`.

## Limitations

The project uses flattened 28x28 images, so it does not exploit local spatial structure in the way a convolutional neural network would. A natural next step would be to compare these from-scratch dense models with a compact CNN and to analyse which signs remain most confusable.
