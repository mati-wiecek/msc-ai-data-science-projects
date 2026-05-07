from pathlib import Path
import numpy as np
import pandas as pd

LETTERS = list("ABCDEFGHIKLMNOPQRSTUVWXY")
LABEL_TO_LETTER = {i: letter for i, letter in enumerate(LETTERS)}
NUM_CLASSES = 24


def read_sign_csv(csv_path):
    """Read a Sign Language MNIST CSV with or without a header row."""
    csv_path = Path(csv_path)
    preview = pd.read_csv(csv_path, header=None, nrows=3)
    first_value = str(preview.iloc[0, 0]).strip().lower()
    return pd.read_csv(csv_path) if first_value == "label" else pd.read_csv(csv_path, header=None)


def load_sign_mnist(csv_path, normalize=True, add_bias=False):
    """Load Sign Language MNIST features and labels from a CSV file."""
    df = read_sign_csv(csv_path)
    y = pd.to_numeric(df.iloc[:, 0], errors="raise").to_numpy(dtype=np.int64)
    X = df.iloc[:, 1:].to_numpy(dtype=np.float32)
    if normalize:
        X = X / 255.0
    if add_bias:
        X = np.hstack([np.ones((X.shape[0], 1), dtype=np.float32), X]).astype(np.float32)
    return X, y


def make_binary_labels(y, positive_label):
    """Convert multi-class labels into 0/1 labels for one-vs-rest training."""
    return (np.asarray(y) == positive_label).astype(np.int64)


def one_hot_encode(y, num_classes=NUM_CLASSES):
    """One-hot encode integer labels."""
    y = np.asarray(y).astype(np.int64)
    encoded = np.zeros((len(y), num_classes), dtype=np.float32)
    encoded[np.arange(len(y)), y] = 1.0
    return encoded
