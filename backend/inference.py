import warnings
import math
from pathlib import Path

import joblib
import numpy as np
import torch
import torch.nn as nn

from data_stream import REQUIRED_FEATURES

# Required for unpickling the scaler
from sklearn.preprocessing import StandardScaler


# ==========================================
# PYTORCH MODEL ARCHITECTURES
# ==========================================

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 500):
        super().__init__()
        pe = torch.zeros(1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


class CustomTransformerEncoderLayer(nn.Module):
    def __init__(self, d_model=128, nhead=8, dim_feedforward=256):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(embed_dim=d_model, num_heads=nhead, batch_first=True)
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(0.0)
        self.linear2 = nn.Linear(dim_feedforward, d_model)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(0.0)
        self.dropout2 = nn.Dropout(0.0)

    def forward(self, src, src_mask=None, src_key_padding_mask=None):
        attn_output, attn_weights = self.self_attn(src, src, src, need_weights=True)
        x = src + self.dropout1(attn_output)
        x = self.norm1(x)
        
        x2 = self.linear2(self.dropout(torch.relu(self.linear1(x))))
        x = x + self.dropout2(x2)
        x = self.norm2(x)
        return x, attn_weights


class TransformerAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.embedding = nn.Linear(44, 128)
        self.pos_encoding = PositionalEncoding(d_model=128, max_len=500)
        self.layers = nn.ModuleList([
            CustomTransformerEncoderLayer(d_model=128, nhead=8, dim_feedforward=256),
            CustomTransformerEncoderLayer(d_model=128, nhead=8, dim_feedforward=256)
        ])
        self.output_layer = nn.Linear(128, 44)

    def forward(self, x):
        x = self.embedding(x)
        x = self.pos_encoding(x)
        attns = []
        for layer in self.layers:
            x, attn = layer(x)
            attns.append(attn)
        return self.output_layer(x), attns


class LSTMAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.LSTM(input_size=44, hidden_size=64, batch_first=True)
        self.decoder = nn.LSTM(input_size=64, hidden_size=44, batch_first=True)

    def forward(self, x):
        h_enc, _ = self.encoder(x)
        h_dec, _ = self.decoder(h_enc)
        return h_dec


# ==========================================
# DEPLOYMENT ASSET INITIALIZATION
# ==========================================

MODEL_BUNDLE_PATH = Path(__file__).resolve().parent / "model" / "deployment_bundle.pkl"
bundle = joblib.load(MODEL_BUNDLE_PATH)

scaler = bundle["scaler"]
T1 = bundle["T1"]
T2 = bundle["T2"]

mu = bundle["mahal_mu"]
cov_inv = bundle["mahal_cov_inv"]

# Instantiate and load PyTorch model weights
trans_model = TransformerAutoencoder()
lstm_model = LSTMAutoencoder()

TRANS_MODEL_PATH = Path(__file__).resolve().parent / "model" / "transformer_model.pt"
LSTM_MODEL_PATH = Path(__file__).resolve().parent / "model" / "lstm_model.pt"

try:
    trans_sd = torch.load(TRANS_MODEL_PATH, map_location="cpu")
    # Map standard keys
    new_sd = {k.replace("encoder.layers.", "layers."): v for k, v in trans_sd.items()}
    trans_model.load_state_dict(new_sd)
    trans_model.eval()
    
    lstm_sd = torch.load(LSTM_MODEL_PATH, map_location="cpu")
    lstm_model.load_state_dict(lstm_sd)
    lstm_model.eval()
except Exception as e:
    import warnings
    warnings.warn(f"Failed to load PyTorch model weights: {e}")


# ==========================================
# PREDICTION AND INFERENCE PIPELINE
# ==========================================

def predict(sensor_data: np.ndarray):
    """
    sensor_data shape: (time_steps, num_features)
    """
    if sensor_data.ndim != 2:
        raise ValueError("sensor_data must be a 2D array.")

    num_steps = sensor_data.shape[0]
    if num_steps < 100:
        pad_size = 100 - num_steps
        padding = np.repeat(sensor_data[0:1], pad_size, axis=0)
        sensor_data = np.vstack([padding, sensor_data])
    elif num_steps > 100:
        sensor_data = sensor_data[-100:]

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
        X_scaled = scaler.transform(sensor_data)

    x_in = torch.tensor(X_scaled, dtype=torch.float).unsqueeze(0) # (1, 100, 44)
    fallback_activated = False
    
    # Run PyTorch models
    with torch.no_grad():
        try:
            x_pred, attns = trans_model(x_in)
            x_pred_np = x_pred.squeeze(0).numpy()
            mse_R = float(np.mean((X_scaled - x_pred_np) ** 2))
            
            # Average attention weights across self-attention layers
            attn_mean_pkl = bundle["attention_mean"].numpy()
            attn_std_pkl = bundle["attention_std"].numpy()
            attn_actual = (attns[0] + attns[1]).squeeze(0).numpy() / 2.0
            
            attn_diff = float(np.mean(np.abs(attn_actual - attn_mean_pkl) / (attn_std_pkl + 1e-8)))
            
            # Compute average attention row entropy
            entropies = []
            for i in range(100):
                row = attn_actual[i]
                row = np.clip(row, 1e-12, 1.0)
                row = row / np.sum(row)
                entropy_row = -np.sum(row * np.log(row))
                entropies.append(entropy_row)
            mean_entropy = float(np.mean(entropies))
            
            mu_R, std_R = bundle["mu_R"], bundle["std_R"]
            mu_A, std_A = bundle["mu_A"], bundle["std_A"]
            mu_E, std_E = bundle["mu_E"], bundle["std_E"]
            entropy_mean_val = float(bundle["entropy_mean"].item())
            
            z_R = (mse_R - mu_R) / std_R
            z_A = (attn_diff - mu_A) / std_A
            z_E = (abs(mean_entropy - entropy_mean_val) - mu_E) / std_E
            
            # LSTM Fallback Arbitration Trigger
            if z_A > 3.0 or z_E > 2.0:
                fallback_activated = True
                x_pred_lstm = lstm_model(x_in)
                x_pred_lstm_np = x_pred_lstm.squeeze(0).numpy()
                mse_R = float(np.mean((X_scaled - x_pred_lstm_np) ** 2))
                z_R = (mse_R - mu_R) / std_R
                x_pred_np = x_pred_lstm_np
            
            # Compute Mahalanobis Distance anomaly score
            v = np.array([z_R, z_A, z_E])
            diff_vec = v - mu
            score = float(math.sqrt(np.dot(np.dot(diff_vec, cov_inv), diff_vec)))
            
        except Exception as e:
            # Safe statistical fallback
            score = float(np.mean(np.abs(X_scaled)))
            z_R, z_A, z_E = 0.0, 0.0, 0.0
            x_pred_np = np.zeros_like(X_scaled)

    # Classification logic
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

    # Feature Attribution (affected sensor)
    try:
        feature_errors = np.mean(np.abs(X_scaled - x_pred_np), axis=0)
        top_idx = int(np.argmax(feature_errors))
        affected_sensor = REQUIRED_FEATURES[top_idx]
    except Exception:
        affected_sensor = "Unknown"

    # AI Reasoning Explanation
    if decision == "NORMAL":
        reason = "All telemetry variables and cross-signal attention maps align with learned baseline."
    else:
        reasons = []
        if z_R > 2.0:
            reasons.append("large value reconstruction deviation")
        if z_A > 2.0:
            reasons.append("irregular cross-sensor temporal dependency correlations")
        if z_E > 2.0:
            reasons.append("irregular concentrated signal attention mapping (low entropy)")
        
        reason = f"Flagged {decision.lower()} state due to: " + ", ".join(reasons) + f" on sensor {affected_sensor}."

    return {
        "final_decision": decision,
        "risk_score": risk_score,
        "mahal_score": round(score, 4),
        "confidence_score": confidence,
        "input_features": observed_features,
        "model_features": expected_features,
        "input_adapted": True,
        "model_variant": "pytorch_transformer_lstm",
        "fallback_activated": fallback_activated,
        "affected_sensor": affected_sensor,
        "detection_reason": reason,
        "z_scores": {
            "reconstruction": round(float(z_R), 4),
            "attention": round(float(z_A), 4),
            "entropy": round(float(z_E), 4)
        }
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

