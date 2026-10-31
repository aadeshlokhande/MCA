"""
Machine Learning Pipeline for Disease Prediction Based on Patient Symptoms.
Implements Decision Tree, Random Forest, and Naive Bayes classifiers with
statistical evaluation (Accuracy, Precision, Recall, F1, Confusion Matrix)
and Joblib serialization.
"""

import os
import joblib
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

try:
    from sklearn.tree import DecisionTreeClassifier as SklearnDT
    from sklearn.ensemble import RandomForestClassifier as SklearnRF
    from sklearn.naive_bayes import MultinomialNB as SklearnNB
    from sklearn.metrics import (
        accuracy_score as sk_acc,
        precision_recall_fscore_support as sk_prf,
        confusion_matrix as sk_cm,
    )
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# =====================================================================
# Native High-Performance Vectorized Classifiers (NumPy + Joblib)
# =====================================================================

class DecisionNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, *, value=None, probas=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value
        self.probas = probas

    @property
    def is_leaf(self):
        return self.value is not None


class NativeDecisionTree:
    """CART Decision Tree with Gini Impurity for binary symptom matrices."""
    def __init__(self, max_depth: int = 15, min_samples_split: int = 2, max_features: Optional[int] = None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.root = None
        self.classes_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.int32)
        self.classes_ = np.unique(y)
        self.n_classes_ = len(self.classes_)
        self.root = self._grow_tree(X, y, depth=0)
        return self

    def _gini(self, y: np.ndarray) -> float:
        m = len(y)
        if m == 0:
            return 0.0
        counts = np.bincount(y, minlength=self.n_classes_)
        probs = counts / m
        return 1.0 - np.sum(probs ** 2)

    def _grow_tree(self, X: np.ndarray, y: np.ndarray, depth: int) -> DecisionNode:
        n_samples, n_features = X.shape
        counts = np.bincount(y, minlength=self.n_classes_)
        probas = counts / max(n_samples, 1)

        # Stopping criteria
        if (depth >= self.max_depth or
            n_samples < self.min_samples_split or
            len(np.unique(y)) <= 1):
            return DecisionNode(value=np.argmax(counts), probas=probas)

        # Feature subsampling
        if self.max_features and self.max_features < n_features:
            feat_idxs = np.random.choice(n_features, self.max_features, replace=False)
        else:
            feat_idxs = np.arange(n_features)

        best_feat, best_thresh = None, None
        best_gain = -1.0
        current_gini = self._gini(y)

        for feat in feat_idxs:
            col = X[:, feat]
            thresholds = np.unique(col)
            if len(thresholds) <= 1:
                continue

            for thresh in thresholds:
                left_mask = col <= thresh
                right_mask = ~left_mask
                if not np.any(left_mask) or not np.any(right_mask):
                    continue

                p_left = np.sum(left_mask) / n_samples
                p_right = 1.0 - p_left
                gain = current_gini - (p_left * self._gini(y[left_mask]) + p_right * self._gini(y[right_mask]))

                if gain > best_gain:
                    best_gain = gain
                    best_feat = feat
                    best_thresh = thresh

        if best_gain <= 0.0 or best_feat is None:
            return DecisionNode(value=np.argmax(counts), probas=probas)

        left_mask = X[:, best_feat] <= best_thresh
        left_child = self._grow_tree(X[left_mask], y[left_mask], depth + 1)
        right_child = self._grow_tree(X[~left_mask], y[~left_mask], depth + 1)

        return DecisionNode(
            feature=best_feat,
            threshold=best_thresh,
            left=left_child,
            right=right_child,
            probas=probas
        )

    def _predict_sample_proba(self, x: np.ndarray, node: DecisionNode) -> np.ndarray:
        if node.is_leaf:
            return node.probas
        if x[node.feature] <= node.threshold:
            return self._predict_sample_proba(x, node.left)
        return self._predict_sample_proba(x, node.right)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float32)
        return np.array([self._predict_sample_proba(x, self.root) for x in X])

    def predict(self, X: np.ndarray) -> np.ndarray:
        probas = self.predict_proba(X)
        return np.argmax(probas, axis=1)


class NativeRandomForest:
    """Bagging Ensemble of CART Decision Trees with random feature subsampling."""
    def __init__(self, n_estimators: int = 25, max_depth: int = 15, min_samples_split: int = 2, max_features: str = 'sqrt'):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.trees = []
        self.classes_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.int32)
        n_samples, n_features = X.shape
        self.classes_ = np.unique(y)
        self.n_classes_ = len(self.classes_)

        if self.max_features == 'sqrt':
            max_feat_val = max(1, int(np.sqrt(n_features)))
        elif isinstance(self.max_features, int):
            max_feat_val = self.max_features
        else:
            max_feat_val = n_features

        self.trees = []
        for _ in range(self.n_estimators):
            # Bootstrap sample
            boot_idxs = np.random.choice(n_samples, n_samples, replace=True)
            tree = NativeDecisionTree(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                max_features=max_feat_val
            )
            tree.fit(X[boot_idxs], y[boot_idxs])
            self.trees.append(tree)

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float32)
        tree_probas = [tree.predict_proba(X) for tree in self.trees]
        # Average probability distributions across all trees
        return np.mean(tree_probas, axis=0)

    def predict(self, X: np.ndarray) -> np.ndarray:
        probas = self.predict_proba(X)
        return np.argmax(probas, axis=1)


class NativeNaiveBayes:
    """Multinomial/Bernoulli Naive Bayes with Laplace smoothing for symptom frequency."""
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.classes_ = None
        self.class_priors_ = None
        self.feature_probs_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.int32)
        n_samples, n_features = X.shape
        self.classes_ = np.unique(y)
        n_classes = len(self.classes_)

        self.class_priors_ = np.zeros(n_classes)
        self.feature_probs_ = np.zeros((n_classes, n_features))

        for c_idx, c in enumerate(self.classes_):
            X_c = X[y == c]
            count_c = len(X_c)
            self.class_priors_[c_idx] = (count_c + self.alpha) / (n_samples + n_classes * self.alpha)
            
            # Smoothed feature probability conditioned on disease class
            symptom_sums = np.sum(X_c, axis=0)
            self.feature_probs_[c_idx, :] = (symptom_sums + self.alpha) / (count_c + 2.0 * self.alpha)

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float32)
        n_samples, _ = X.shape
        n_classes = len(self.classes_)

        log_priors = np.log(self.class_priors_)
        log_probs = np.zeros((n_samples, n_classes))

        eps = 1e-9
        pos_probs = np.clip(self.feature_probs_, eps, 1.0 - eps)
        neg_probs = 1.0 - pos_probs

        for c_idx in range(n_classes):
            # Bernoulli likelihood
            log_lik = np.sum(X * np.log(pos_probs[c_idx]) + (1.0 - X) * np.log(neg_probs[c_idx]), axis=1)
            log_probs[:, c_idx] = log_priors[c_idx] + log_lik

        # Safe Softmax normalization for calibrated probabilities
        max_logs = np.max(log_probs, axis=1, keepdims=True)
        exp_logs = np.exp(log_probs - max_logs)
        return exp_logs / np.sum(exp_logs, axis=1, keepdims=True)

    def predict(self, X: np.ndarray) -> np.ndarray:
        probas = self.predict_proba(X)
        return np.argmax(probas, axis=1)


# =====================================================================
# Statistical Evaluation Suite
# =====================================================================

def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int) -> Dict[str, Any]:
    """
    Computes rigorous Accuracy, Precision, Recall, F1-Score, and Confusion Matrix.
    """
    y_true = np.asarray(y_true, dtype=np.int32)
    y_pred = np.asarray(y_pred, dtype=np.int32)
    n_samples = len(y_true)

    if n_samples == 0:
        return {'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0, 'confusion_matrix': []}

    # Accuracy
    accuracy = float(np.mean(y_true == y_pred))

    # Confusion matrix
    cm = np.zeros((n_classes, n_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        if 0 <= t < n_classes and 0 <= p < n_classes:
            cm[t, p] += 1

    # Per-class metrics
    precisions, recalls, f1s = [], [], []
    weights = []

    for c in range(n_classes):
        tp = cm[c, c]
        fp = np.sum(cm[:, c]) - tp
        fn = np.sum(cm[c, :]) - tp
        class_samples = np.sum(cm[c, :])
        weights.append(class_samples)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)

    weights = np.array(weights)
    total_w = np.sum(weights)
    if total_w > 0:
        w_prec = float(np.sum(np.array(precisions) * weights) / total_w)
        w_rec = float(np.sum(np.array(recalls) * weights) / total_w)
        w_f1 = float(np.sum(np.array(f1s) * weights) / total_w)
    else:
        w_prec = float(np.mean(precisions))
        w_rec = float(np.mean(recalls))
        w_f1 = float(np.mean(f1s))

    return {
        'accuracy': round(accuracy, 4),
        'precision': round(w_prec, 4),
        'recall': round(w_rec, 4),
        'f1': round(w_f1, 4),
        'confusion_matrix': cm.tolist(),
    }


# =====================================================================
# Factory & Serialization Helper
# =====================================================================

def get_classifier(algorithm: str, random_state: int = 42):
    """Returns the requested algorithm instance with standard hyperparameter tuning."""
    algo = algorithm.upper()
    if algo == 'RANDOM_FOREST':
        return NativeRandomForest(n_estimators=30, max_depth=16, min_samples_split=2)
    elif algo == 'DECISION_TREE':
        return NativeDecisionTree(max_depth=16, min_samples_split=2)
    elif algo in ('NAIVE_BAYES', 'MULTINOMIAL_NB'):
        return NativeNaiveBayes(alpha=1.0)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def save_ml_pipeline(model, symptom_names: List[str], disease_mapping: Dict[int, str], filepath: str):
    """Serializes the trained classifier and symptom vocabulary to a Joblib file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    payload = {
        'model': model,
        'symptom_features': symptom_names,
        'disease_mapping': disease_mapping,
        'version': '1.0.0',
    }
    joblib.dump(payload, filepath)


def load_ml_pipeline(filepath: str) -> Optional[Dict[str, Any]]:
    """Loads a serialized model and feature mapping pipeline from disk."""
    if not os.path.exists(filepath):
        return None
    return joblib.load(filepath)
