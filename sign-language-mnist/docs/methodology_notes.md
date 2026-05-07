# Methodology Notes

This file records the main design decisions used to make the analysis reproducible, interpretable and suitable for technical review.

| Area | Methodological choice | Rationale |
|---|---|---|
| Perceptron scoring | Use explicit vector/matrix multiplication with the `@` operator. | Keeps the implementation close to the mathematical formulation and consistent with the vectorised batch code. |
| Sigmoid stability | Clip sigmoid inputs before applying `np.exp`. | Prevents numerical overflow while leaving saturated binary decisions effectively unchanged. |
| Interpretability | Print weight summaries and visualise learned weight maps. | Helps connect learned parameters back to pixel-level evidence. |
| Data exploration | Visualise representative examples from each available sign class. | Makes class structure and image quality inspectable before modelling. |
| Neural-network initialisation | Use Xavier-style scaling for sigmoid models and He initialisation for ReLU models. | Matches the activation function to an appropriate variance-scaling strategy. |
| Optimisation | Use mini-batch training, momentum, L2 regularisation, dropout and early stopping. | Controls optimisation stability and reduces overfitting while keeping the implementation from scratch. |
| Evaluation | Report accuracy, precision, recall, macro metrics, confusion matrices and learning curves. | Gives a fuller view of binary and multi-class model behaviour than accuracy alone. |
| Data policy | Exclude raw CSV files and local cache files. | Keeps the repository lightweight and avoids redistributing dataset files. |
