# Sign Language MNIST Classification

## Overview

This project focuses on classifying grayscale hand sign images from the Sign Language MNIST dataset using a deep learning image classification pipeline.

It is designed to demonstrate practical computer vision skills: data loading, preprocessing, model training, evaluation, and visual communication of model performance.

## Problem

The task is to classify images of hand signs into their corresponding alphabet classes. This is a supervised multi-class classification problem with small grayscale images.

## Approach

1. Load and inspect the Sign Language MNIST dataset.
2. Normalise image pixel values.
3. Split data into training and validation sets.
4. Train a convolutional neural network.
5. Track accuracy and loss during training.
6. Evaluate the model using validation accuracy and a confusion matrix.
7. Visualise training curves and sample predictions in the README.

## Technologies

- Python
- PyTorch or TensorFlow
- NumPy
- pandas
- matplotlib / seaborn
- scikit-learn
- Jupyter Notebook

## Repository Structure

```text
sign-language-mnist/
  README.md
  requirements.txt
  notebooks/
  src/
  reports/
    figures/
```

## Reproducibility

Suggested setup:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

The final version should include a notebook or training script that can reproduce the reported accuracy and generate the training curves.

## Results to Include

- Training accuracy curve
- Validation accuracy curve
- Training and validation loss curves
- Confusion matrix
- Example predictions

## Status

README and project structure prepared. Model code, notebook, figures, and final metrics should be added next.
