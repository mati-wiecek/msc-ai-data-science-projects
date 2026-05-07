import numpy as np
import pandas as pd
from .metrics import binary_metrics


class Perceptron:
    """From-scratch binary perceptron with step/sigmoid activation."""

    def __init__(self, no_inputs, max_iterations=20, learning_rate=0.1, random_state=42):
        self.no_inputs = int(no_inputs)
        self.max_iterations = int(max_iterations)
        self.learning_rate = float(learning_rate)
        self.random_state = int(random_state)
        rng = np.random.default_rng(self.random_state)
        self.weights = rng.normal(0.0, 0.01, size=self.no_inputs).astype(np.float32)
        self.history = []

    def sigmoid(self, a):
        clipped = np.clip(a, -40, 40)
        return 1.0 / (1.0 + np.exp(-clipped))

    def step(self, a):
        return np.where(np.asarray(a) > 0, 1.0, 0.0)

    def decision_function(self, x):
        x = np.asarray(x, dtype=np.float32)
        score = x @ self.weights
        return float(score) if np.ndim(score) == 0 else score

    def predict_score(self, x, activation="step"):
        activation = activation.lower()
        score = self.decision_function(x)
        if activation == "step":
            return score
        if activation == "sigmoid":
            return float(self.sigmoid(score))
        raise ValueError("activation must be 'step' or 'sigmoid'")

    def predict(self, x, activation="step"):
        activation = activation.lower()
        score = self.decision_function(x)
        if activation == "step":
            return int(self.step(score))
        if activation == "sigmoid":
            return int(self.sigmoid(score) >= 0.5)
        raise ValueError("activation must be 'step' or 'sigmoid'")

    def print_weights(self, top_n=10):
        weight_vector = np.asarray(self.weights, dtype=np.float32).ravel()
        pixel_weights = weight_vector[1:] if weight_vector.shape[0] == 785 else weight_vector
        top_positive = np.argsort(pixel_weights)[-top_n:][::-1]
        top_negative = np.argsort(pixel_weights)[:top_n]
        return pd.DataFrame({
            "rank": np.arange(1, top_n + 1),
            "positive_pixel": top_positive,
            "positive_weight": pixel_weights[top_positive],
            "negative_pixel": top_negative,
            "negative_weight": pixel_weights[top_negative],
        })

    def train(self, training_data, labels, activation="step", shuffle=True):
        activation = activation.lower()
        X = np.asarray(training_data, dtype=np.float32)
        y = np.asarray(labels, dtype=np.float32).ravel()
        rng = np.random.default_rng(self.random_state)
        self.history = []
        for epoch in range(self.max_iterations):
            indices = np.arange(len(X))
            if shuffle:
                rng.shuffle(indices)
            squared_error = 0.0
            updates = 0
            for idx in indices:
                x = X[idx]
                target = y[idx]
                score = self.decision_function(x)
                if activation == "step":
                    output = float(self.step(score))
                    delta = target - output
                elif activation == "sigmoid":
                    output = float(self.sigmoid(score))
                    delta = (target - output) * output * (1.0 - output)
                else:
                    raise ValueError("activation must be 'step' or 'sigmoid'")
                self.weights += self.learning_rate * delta * x
                squared_error += float((target - output) ** 2)
                updates += int(abs(delta) > 0)
            self.history.append({"epoch": epoch + 1, "mse": squared_error / len(X), "updates": updates})
        return self.history

    def train_batch(self, training_data, labels, activation="step", shuffle=True):
        activation = activation.lower()
        X = np.asarray(training_data, dtype=np.float32)
        y = np.asarray(labels, dtype=np.float32).ravel()
        rng = np.random.default_rng(self.random_state)
        self.history = []
        for epoch in range(self.max_iterations):
            indices = np.arange(len(X))
            if shuffle:
                rng.shuffle(indices)
            X_epoch = X[indices]
            y_epoch = y[indices]
            scores = X_epoch @ self.weights
            if activation == "step":
                outputs = self.step(scores).astype(np.float32)
                errors = y_epoch - outputs
            elif activation == "sigmoid":
                outputs = self.sigmoid(scores).astype(np.float32)
                errors = (y_epoch - outputs) * outputs * (1.0 - outputs)
            else:
                raise ValueError("activation must be 'step' or 'sigmoid'")
            update = self.learning_rate * (errors[:, None] * X_epoch).mean(axis=0)
            self.weights += update.astype(np.float32)
            self.history.append({"epoch": epoch + 1, "mse": float(np.mean((y_epoch - outputs) ** 2)), "update_norm": float(np.linalg.norm(update))})
        return self.history

    def test(self, testing_data, labels, activation="step"):
        X = np.asarray(testing_data, dtype=np.float32)
        y_true = np.asarray(labels).astype(np.int64).ravel()
        y_pred = np.array([self.predict(x, activation=activation) for x in X], dtype=np.int64)
        return binary_metrics(y_true, y_pred), y_pred
