from pathlib import Path
from threading import Lock

import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data_stream import REQUIRED_FEATURES, SwatCsvStream, ordered_values
from fault_memory import handle_fault_memory
from inference import build_fault_signature, predict

app = FastAPI(title="HydroVigil ML Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BACKEND_CSV_PATH = Path(__file__).resolve().parent / "data" / "swat_stream.csv"
ROOT_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "swat_stream.csv"
CSV_PATH = BACKEND_CSV_PATH if BACKEND_CSV_PATH.exists() else ROOT_CSV_PATH
SWAT_STREAM = SwatCsvStream(CSV_PATH)
EVENT_LOCK = Lock()
EVENT_SEQ = 0
ACTIVE_ALERT = None


def _next_event_id() -> str:
    global EVENT_SEQ
    EVENT_SEQ += 1
    return f"EVT-{EVENT_SEQ:06d}"


def _build_event_payload(result: dict, fault_memory: dict) -> dict | None:
    global ACTIVE_ALERT

    decision = result.get("final_decision")
    risk = int(result.get("risk_score", 0))
    confidence = str(result.get("confidence_score", "N/A"))
    sensor = str(fault_memory.get("affected_sensor", "N/A"))
    memory_action = str(fault_memory.get("memory_action", "N/A"))
    recommended_action = str(fault_memory.get("recommended_action", "No corrective action required."))

    if decision in ("ATTACK", "SUSPICIOUS"):
        severity = "critical" if decision == "ATTACK" else "medium"
        status = "Investigating"
        event_text = (
            f"Backend model flagged {decision} ({risk}% risk, {confidence} confidence)."
        )
        signature = (decision, sensor, memory_action)

        if ACTIVE_ALERT and ACTIVE_ALERT.get("signature") == signature:
            event_id = ACTIVE_ALERT["event_id"]
        else:
            event_id = _next_event_id()
            ACTIVE_ALERT = {"event_id": event_id, "signature": signature}

        return {
            "event_id": event_id,
            "prediction_type": "Threat",
            "severity": severity,
            "status": status,
            "sensor_id": sensor,
            "event": event_text,
            "countermeasure": recommended_action,
            "memory_action": memory_action,
        }

    if decision == "NORMAL" and ACTIVE_ALERT:
        event_id = f"{ACTIVE_ALERT['event_id']}-REC"
        ACTIVE_ALERT = None
        return {
            "event_id": event_id,
            "prediction_type": "Recovery",
            "severity": "low",
            "status": "Closed",
            "sensor_id": sensor,
            "event": f"Backend model returned to NORMAL ({risk}% risk, {confidence} confidence).",
            "countermeasure": "No corrective action required.",
            "memory_action": "N/A",
        }

    return None


@app.get("/")
def home():
    return {"message": "HydroVigil Backend Running"}


@app.get("/predict")
def run_prediction(window_size: int = Query(default=20, ge=2, le=200)):
    """
    Reads the next sequential window from backend data source and runs inference.
    No telemetry is accepted from frontend.
    """
    try:
        named_rows = SWAT_STREAM.next_window(window_size)
        ordered_rows = [ordered_values(row) for row in named_rows]
        sensor_data = np.array(ordered_rows, dtype=float)
        result = predict(sensor_data)
        signature = build_fault_signature(sensor_data)
        fault_memory = handle_fault_memory(signature, result["final_decision"])
        with EVENT_LOCK:
            event_payload = _build_event_payload(result, fault_memory)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    latest_row = named_rows[-1]
    result["features_used"] = REQUIRED_FEATURES
    result["window_size"] = window_size
    result["data_source"] = str(CSV_PATH)
    result["telemetry_point"] = {
        "pressure": latest_row["PIT501"],
        "flow": latest_row["FIT101"],
        "level": latest_row["LIT101"],
        "anomalyLevel": float(result["risk_score"]) / 100.0,
    }
    result["fault_memory"] = fault_memory
    result["fault_signature"] = {
        "mean_error": round(float(signature["mean_error"]), 6),
        "max_error": round(float(signature["max_error"]), 6),
        "affected_sensor": signature["affected_sensor"],
    }
    result["event"] = event_payload
    return result
