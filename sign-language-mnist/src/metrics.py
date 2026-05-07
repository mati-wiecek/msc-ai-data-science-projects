import numpy as np


def binary_metrics(y_true, y_pred):
    """Return accuracy, precision, recall, and confusion counts for binary labels."""
    y_true = np.asarray(y_true).astype(np.int64).ravel()
    y_pred = np.asarray(y_pred).astype(np.int64).ravel()
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": float((tp + tn) / len(y_true)),
        "precision": float(tp / (tp + fp)) if (tp + fp) else 0.0,
        "recall": float(tp / (tp + fn)) if (tp + fn) else 0.0,
    }


def confusion_matrix_manual(y_true, y_pred, num_classes):
    """Build a confusion matrix without using scikit-learn."""
    cm = np.zeros((num_classes, num_classes), dtype=np.int64)
    for true_label, pred_label in zip(np.asarray(y_true).ravel(), np.asarray(y_pred).ravel()):
        if 0 <= true_label < num_classes and 0 <= pred_label < num_classes:
            cm[int(true_label), int(pred_label)] += 1
    return cm


def macro_precision_recall(cm):
    """Macro-average precision and recall over active classes."""
    active_classes = [k for k in range(cm.shape[0]) if (cm[k, :].sum() + cm[:, k].sum()) > 0]
    precisions, recalls = [], []
    for k in active_classes:
        tp = cm[k, k]
        fp = cm[:, k].sum() - tp
        fn = cm[k, :].sum() - tp
        precisions.append(tp / (tp + fp) if (tp + fp) else 0.0)
        recalls.append(tp / (tp + fn) if (tp + fn) else 0.0)
    return float(np.mean(precisions)), float(np.mean(recalls))
