import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

MODELS_DIR = Path("../models")


def train(X, y, num_class):
    clf = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        objective="multi:softmax",
        num_class=num_class,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X, y)
    return clf


def encode(target):
    le = LabelEncoder()
    y = le.fit_transform(target)
    return le, y


def main():
    df = pd.read_csv("../data/processed/train.csv", low_memory=False)
    X = df.drop(columns=["label"])
    le, y = encode(df["label"])
    clf = train(X, y, len(le.classes_))  # type:ignore

    os.makedirs(MODELS_DIR, exist_ok=True)

    joblib.dump(clf, os.path.join(MODELS_DIR, "xgb_model.pkl"))
    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder.pkl"))

    import json

    with open(os.path.join(MODELS_DIR, "expected_features.json"), "w") as f:
        json.dump(list(X.columns), f)

    print(
        f"\nSaved to {MODELS_DIR}/: xdb_model.pkl, label_encoder.pkl, expected_features.json"
    )


if __name__ == "__main__":
    main()
