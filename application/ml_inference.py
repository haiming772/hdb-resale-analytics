import os
import json
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "final_hdb_model.joblib")
FEATURE_PATH = os.path.join(BASE_DIR, "..", "models", "final_feature_list.json")

# Lazy load model (prevents startup crash)
_model = None
_feature_list = None


def load_model():
    global _model, _feature_list
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        with open(FEATURE_PATH, "r") as f:
            _feature_list = json.load(f)


def build_input_row(**kwargs) -> pd.DataFrame:
    load_model()
    df = pd.DataFrame([kwargs])
    df = df[_feature_list]
    return df


def predict_resale_price(**kwargs) -> float:
    X = build_input_row(**kwargs)
    pred = _model.predict(X)[0]
    return float(np.round(pred, 0))
