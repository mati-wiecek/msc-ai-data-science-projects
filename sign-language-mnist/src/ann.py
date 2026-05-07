import numpy as np
import pandas as pd
from .metrics import binary_metrics, confusion_matrix_manual, macro_precision_recall


class ANN:
    """Fully connected neural network implemented from scratch in NumPy."""

    def __init__(self, no_inputs, hidden_layers=None, output_nodes=1, max_iterations=20,
                 learning_rate=0.01, batch_size=128, activation="sigmoid", random_state=42,
                 l2_lambda=0.0, momentum=0.0, lr_decay=0.0, dropout_rate=0.0):
        if hidden_layers is None:
            hidden_layers = [128, 64]
        self.no_inputs = int(no_inputs)
        self.hidden_layers = list(hidden_layers)
        self.output_nodes = int(output_nodes)
        self.max_iter = int(max_iterations)
        self.learning_rate = float(learning_rate)
        self.initial_lr = float(learning_rate)
        self.batch_size = int(batch_size)
        self.activation_name = activation.lower()
        self.random_state = int(random_state)
        self.l2_lambda = float(l2_lambda)
        self.momentum = float(momentum)
        self.lr_decay = float(lr_decay)
        self.dropout_rate = float(dropout_rate)
        self.history = []
        if self.activation_name not in {"sigmoid", "relu"}:
            raise ValueError("activation must be 'sigmoid' or 'relu'")
        self.layer_sizes = [self.no_inputs] + self.hidden_layers + [self.output_nodes]
        self.rng = np.random.default_rng(self.random_state)
        self.weights, self.biases, self.velocity_w, self.velocity_b = [], [], [], []
        for layer_idx, (fan_in, fan_out) in enumerate(zip(self.layer_sizes[:-1], self.layer_sizes[1:])):
            is_hidden = layer_idx < len(self.hidden_layers)
            scale = np.sqrt(2.0 / fan_in) if (is_hidden and self.activation_name == "relu") else np.sqrt(1.0 / fan_in)
            W = self.rng.normal(0.0, scale, size=(fan_in, fan_out)).astype(np.float32)
            b = np.zeros((1, fan_out), dtype=np.float32)
            self.weights.append(W)
            self.biases.append(b)
            self.velocity_w.append(np.zeros_like(W))
            self.velocity_b.append(np.zeros_like(b))

    def describe_architecture(self):
        return pd.DataFrame([
            {"layer": i + 1, "fan_in": fan_in, "fan_out": fan_out, "weights_shape": self.weights[i].shape}
            for i, (fan_in, fan_out) in enumerate(zip(self.layer_sizes[:-1], self.layer_sizes[1:]))
        ])

    def activate(self, a, activation=None):
        act = self.activation_name if activation is None else activation.lower()
        if act == "sigmoid":
            return 1.0 / (1.0 + np.exp(-np.clip(a, -40, 40)))
        if act == "relu":
            return np.maximum(0.0, a)
        raise ValueError(f"Unknown activation: {act}")

    def activation_derivative(self, a, activation=None):
        act = self.activation_name if activation is None else activation.lower()
        if act == "sigmoid":
            s = self.activate(a, "sigmoid")
            return s * (1.0 - s)
        if act == "relu":
            return (a > 0).astype(np.float32)
        raise ValueError(f"Unknown activation: {act}")

    def softmax(self, z):
        z = z - np.max(z, axis=1, keepdims=True)
        exp_z = np.exp(z)
        return exp_z / np.sum(exp_z, axis=1, keepdims=True)

    def do_predict(self, x, return_cache=False, training=False):
        X = np.asarray(x, dtype=np.float32)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        activations, pre_activations, dropout_masks = [X], [], []
        current = X
        for layer in range(len(self.hidden_layers)):
            z = current @ self.weights[layer] + self.biases[layer]
            pre_activations.append(z)
            h = self.activate(z)
            if training and self.dropout_rate > 0.0:
                mask = (self.rng.random(h.shape) > self.dropout_rate).astype(np.float32)
                h = h * mask / (1.0 - self.dropout_rate)
            else:
                mask = np.ones_like(h)
            dropout_masks.append(mask)
            current = h
            activations.append(current)
        z_out = current @ self.weights[-1] + self.biases[-1]
        pre_activations.append(z_out)
        output = self.activate(z_out, "sigmoid") if self.output_nodes == 1 else self.softmax(z_out)
        activations.append(output)
        if return_cache:
            return output, {"activations": activations, "pre_activations": pre_activations, "dropout_masks": dropout_masks}
        return output

    def do_train(self, training_data, labels):
        X = np.asarray(training_data, dtype=np.float32)
        y = np.asarray(labels, dtype=np.float32)
        if self.output_nodes == 1 and y.ndim == 1:
            y = y.reshape(-1, 1)
        elif self.output_nodes > 1 and y.ndim == 1:
            tmp = np.zeros((len(y), self.output_nodes), dtype=np.float32)
            tmp[np.arange(len(y)), y.astype(np.int64)] = 1.0
            y = tmp
        self.history = []
        n_samples = len(X)
        for epoch in range(self.max_iter):
            current_lr = self.initial_lr / (1.0 + self.lr_decay * epoch)
            idx = self.rng.permutation(n_samples)
            X_shuf, y_shuf = X[idx], y[idx]
            epoch_loss, epoch_correct = 0.0, 0
            for start in range(0, n_samples, self.batch_size):
                Xb = X_shuf[start:start + self.batch_size]
                yb = y_shuf[start:start + self.batch_size]
                bs = len(Xb)
                out, cache = self.do_predict(Xb, return_cache=True, training=True)
                acts, pre, masks = cache["activations"], cache["pre_activations"], cache["dropout_masks"]
                eps = 1e-7
                if self.output_nodes == 1:
                    batch_loss = -np.mean(yb * np.log(out + eps) + (1.0 - yb) * np.log(1.0 - out + eps))
                    delta = out - yb
                    epoch_correct += int(np.sum((out >= 0.5).astype(np.int64) == yb.astype(np.int64)))
                else:
                    batch_loss = -np.mean(np.sum(yb * np.log(out + eps), axis=1))
                    delta = out - yb
                    epoch_correct += int(np.sum(np.argmax(out, axis=1) == np.argmax(yb, axis=1)))
                if self.l2_lambda > 0:
                    batch_loss += 0.5 * self.l2_lambda * sum(np.sum(w * w) for w in self.weights)
                epoch_loss += float(batch_loss) * bs
                grad_w, grad_b = [None] * len(self.weights), [None] * len(self.biases)
                for layer in reversed(range(len(self.weights))):
                    grad_w[layer] = (acts[layer].T @ delta) / bs
                    grad_b[layer] = np.mean(delta, axis=0, keepdims=True)
                    if self.l2_lambda > 0:
                        grad_w[layer] += self.l2_lambda * self.weights[layer]
                    if layer > 0:
                        delta = (delta @ self.weights[layer].T) * self.activation_derivative(pre[layer - 1])
                        if self.dropout_rate > 0.0:
                            delta = delta * masks[layer - 1] / (1.0 - self.dropout_rate)
                for layer in range(len(self.weights)):
                    if self.momentum > 0:
                        self.velocity_w[layer] = self.momentum * self.velocity_w[layer] - current_lr * grad_w[layer]
                        self.velocity_b[layer] = self.momentum * self.velocity_b[layer] - current_lr * grad_b[layer]
                        self.weights[layer] += self.velocity_w[layer]
                        self.biases[layer] += self.velocity_b[layer]
                    else:
                        self.weights[layer] -= current_lr * grad_w[layer]
                        self.biases[layer] -= current_lr * grad_b[layer]
            self.history.append({"epoch": epoch + 1, "loss": epoch_loss / n_samples, "accuracy": epoch_correct / n_samples})
        return self.history

    def test(self, testing_data, labels):
        X = np.asarray(testing_data, dtype=np.float32)
        y = np.asarray(labels)
        outputs = self.do_predict(X)
        if self.output_nodes == 1:
            y_true = y.reshape(-1).astype(np.int64)
            y_pred = (outputs >= 0.5).astype(np.int64).reshape(-1)
            metrics = binary_metrics(y_true, y_pred)
            cm = np.array([[metrics["tn"], metrics["fp"]], [metrics["fn"], metrics["tp"]]], dtype=np.int64)
            return {"confusion_matrix": cm, **metrics, "y_pred": y_pred, "outputs": outputs}
        y_true = np.argmax(y, axis=1).astype(np.int64) if y.ndim == 2 else y.astype(np.int64)
        y_pred = np.argmax(outputs, axis=1).astype(np.int64)
        cm = confusion_matrix_manual(y_true, y_pred, self.output_nodes)
        precision, recall = macro_precision_recall(cm)
        return {"confusion_matrix": cm, "accuracy": float(np.mean(y_pred == y_true)), "precision": precision, "recall": recall, "y_pred": y_pred, "outputs": outputs}
