"""Train and compare baseline heart-risk models on a UCI-style CSV dataset.

The CSV must contain the 13 feature names in preprocessing.FEATURES and a
binary target column named `target`.
"""
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from .preprocessing import FEATURES


def train(dataset_path: str, output_dir: str):
    import csv

    with open(dataset_path, newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    x = [[float(row[name]) for name in FEATURES] for row in rows]
    y = [int(row["target"]) for row in rows]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler().fit(x_train)
    x_train_scaled, x_test_scaled = scaler.transform(x_train), scaler.transform(x_test)
    candidates = {
        "LogisticRegression": LogisticRegression(max_iter=2000),
        "RandomForest": RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced"),
        "SVM": SVC(probability=True, random_state=42),
    }
    scores = {}
    best_name, best_score, best_model = None, -1, None
    for name, model in candidates.items():
        model.fit(x_train_scaled, y_train)
        probabilities = model.predict_proba(x_test_scaled)[:, 1]
        predictions = model.predict(x_test_scaled)
        scores[name] = {
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(y_test, predictions, zero_division=0),
            "recall": recall_score(y_test, predictions, zero_division=0),
            "f1": f1_score(y_test, predictions, zero_division=0),
            "roc_auc": roc_auc_score(y_test, probabilities),
        }
        if scores[name]["roc_auc"] > best_score:
            best_name, best_score, best_model = name, scores[name]["roc_auc"], model
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, destination / "heart_model.pkl")
    joblib.dump(scaler, destination / "scaler.pkl")
    return best_name, scores
