import numpy as np
import matplotlib.pyplot as plt
from .data_utils import LABEL_TO_LETTER, NUM_CLASSES


def plot_confusion_matrix(cm, labels=None, title="Confusion matrix", figsize=(8, 8)):
    if labels is None:
        labels = [LABEL_TO_LETTER[i] for i in range(cm.shape[0])]
    plt.figure(figsize=figsize)
    plt.imshow(cm, cmap="Blues")
    plt.title(title)
    plt.xlabel("Predicted label")
    plt.ylabel("True label")
    plt.xticks(range(len(labels)), labels, rotation=90)
    plt.yticks(range(len(labels)), labels)
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.show()


def plot_weight_grid(weights_by_name, title="Learned weights", cols=4):
    names = list(weights_by_name.keys())
    rows = int(np.ceil(len(names) / cols))
    vectors = []
    for name in names:
        vec = np.asarray(weights_by_name[name], dtype=np.float32).ravel()
        vectors.append(vec[1:] if vec.shape[0] == 785 else vec)
    max_abs = max(float(np.max(np.abs(vec))) for vec in vectors)
    max_abs = max(max_abs, 1e-8)
    plt.figure(figsize=(cols * 3, rows * 3))
    for idx, (name, vec) in enumerate(zip(names, vectors), start=1):
        plt.subplot(rows, cols, idx)
        plt.imshow(vec.reshape(28, 28), cmap="coolwarm", vmin=-max_abs, vmax=max_abs)
        plt.title(name)
        plt.axis("off")
    plt.suptitle(title)
    plt.tight_layout()
    plt.show()
