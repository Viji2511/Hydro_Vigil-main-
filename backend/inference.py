import warnings
from pathlib import Path

import joblib
import numpy as np
from data_stream import REQUIRED_FEATURES

# Required for unpickling the scaler
from sklearn.preprocessing import StandardScaler

MODEL_BUNDLE_PATH = Path(__file__).resolve().parent / "model" / "deployment_bundle.pkl"
bundle = joblib.load(MODEL_BUNDLE_PATH)

scaler = bundle["scaler"]
T1 = bundle["T1"]
T2 = bundle["T2"]

mu = bundle["mahal_mu"]
cov_inv = bundle["mahal_cov_inv"]

_scaler_feature_names = list(getattr(scaler, "feature_names_in_", []))
if _scaler_feature_names and _scaler_feature_names != REQUIRED_FEATURES:
    raise RuntimeError(
        "Model/scaler feature order does not match REQUIRED_FEATURES. "
        f"Scaler={_scaler_feature_names}"
    )


def predict(sensor_data: np.ndarray):
    """
    sensor_data shape:
    (time_steps, num_features)
    """
    if sensor_data.ndim != 2:
        raise ValueError("sensor_data must be a 2D array.")

    expected_features = int(getattr(scaler, "n_features_in_", sensor_data.shape[1]))
    observed_features = int(sensor_data.shape[1])

    if observed_features != expected_features:
        raise ValueError(
            f"X has {observed_features} features, but trained scaler expects {expected_features}."
        )

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="X does not have valid feature names, but StandardScaler was fitted with feature names",
            category=UserWarning,
        )
        X = scaler.transform(sensor_data)

    score = float(np.mean(np.abs(X)))

    if score < T1:
        decision = "NORMAL"
        confidence = "LOW"
        risk_score = int(np.clip((score / max(T1, 1e-6)) * 33.0, 0, 33))
    elif score < T2:
        decision = "SUSPICIOUS"
        confidence = "MEDIUM"
        band = (score - T1) / max(T2 - T1, 1e-6)
        risk_score = int(np.clip(34.0 + band * 32.0, 34, 66))
    else:
        decision = "ATTACK"
        confidence = "HIGH"
        band = (score - T2) / max(T2, 1e-6)
        risk_score = int(np.clip(67.0 + band * 33.0, 67, 100))

    return {
        "final_decision": decision,
        "risk_score": risk_score,
        "mahal_score": round(score, 4),
        "confidence_score": confidence,
        "input_features": observed_features,
        "model_features": expected_features,
        "input_adapted": False,
        "model_variant": "bundle_44f",
    }


def build_fault_signature(sensor_data: np.ndarray) -> dict:
    if sensor_data.ndim != 2:
        raise ValueError("sensor_data must be a 2D array.")

    expected_features = int(getattr(scaler, "n_features_in_", sensor_data.shape[1]))
    observed_features = int(sensor_data.shape[1])
    if observed_features != expected_features:
        raise ValueError(
            f"X has {observed_features} features, but trained scaler expects {expected_features}."
        )

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="X does not have valid feature names, but StandardScaler was fitted with feature names",
            category=UserWarning,
        )
        x_norm = scaler.transform(sensor_data)

    abs_norm = np.abs(x_norm)
    mean_error = float(np.mean(abs_norm))
    max_error = float(np.max(abs_norm))
    feature_names = list(getattr(scaler, "feature_names_in_", REQUIRED_FEATURES))
    per_feature_mean = np.mean(abs_norm, axis=0)

    # Prefer process sensors for signature attribution to avoid repetitive
    # actuator-only fault IDs dominating the incident stream.
    process_indices = [
        i
        for i, name in enumerate(feature_names)
        if name.startswith(("FIT", "LIT", "AIT", "PIT", "DPIT"))
    ]
    if process_indices:
        proc_scores = per_feature_mean[process_indices]
        top_proc_local = int(np.argmax(proc_scores))
        top_idx = process_indices[top_proc_local]
    else:
        top_idx = int(np.argmax(per_feature_mean))
    affected_sensor = feature_names[top_idx]

    return {
        "mean_error": mean_error,
        "max_error": max_error,
        "affected_sensor": affected_sensor,
    }
