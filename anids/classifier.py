import json
import pickle
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


class ModelLoadError(RuntimeError):
    pass


def _load_pickle(path: Path) -> Any:
    if not path.exists():
        raise ModelLoadError(f"File not found: {path}")
    try:
        return joblib.load(path)
    except Exception:
        pass
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        raise ModelLoadError(f"Could not load '{path}' : {e}") from e


class FlowClassifier:
    def __init__(self, model_path: Path, encoder_path: Path, features_path: Path):
        self.model = _load_pickle(model_path)
        self.encoder = (
            _load_pickle(encoder_path)
            if encoder_path and encoder_path.exists()
            else None
        )

        self.feature_names: list[str] = []
        if features_path and features_path.exists():
            with open(features_path, "r") as f:
                data = json.load(f)
            self.feature_names = (
                data if isinstance(data, list) else data.get("features", [])
            )

    def predict(self, row: dict) -> dict:
        X = pd.DataFrame([row]).reindex(columns=self.feature_names)
        X = X.apply(pd.to_numeric, errors="coerce")
        raw_pred = self.model.predict(X)[0]
        confidence = None

        if hasattr(self.model, "predict_proba"):
            confidence = float(max(self.model.predict_proba(X)[0]))

        if self.encoder is not None:
            label = str(self.encoder.inverse_transform([raw_pred])[0])
        else:
            label = str(raw_pred)

        return {"label": label, "confidence": confidence}
