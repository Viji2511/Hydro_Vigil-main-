from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path


def resolve_db_path() -> Path:
    backend_candidate = Path(__file__).resolve().parent / "database" / "faults.db"
    root_candidate = Path(__file__).resolve().parent.parent / "database" / "faults.db"
    if backend_candidate.exists():
        return backend_candidate
    return root_candidate


DB_PATH = resolve_db_path()


def ensure_fault_table() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS faults (
                fault_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fault_type TEXT,
                mean_error REAL,
                max_error REAL,
                affected_sensor TEXT,
                severity TEXT,
                detected_at TEXT,
                solution TEXT,
                remarks TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _severity_for_decision(decision: str) -> str:
    if decision == "ATTACK":
        return "High"
    if decision == "SUSPICIOUS":
        return "Medium"
    return "Low"


def _default_solution(sensor: str, decision: str) -> str:
    if decision == "ATTACK":
        return f"Isolate channel around {sensor}, hold actuator changes, and escalate SOC response."
    if decision == "SUSPICIOUS":
        return f"Increase validation frequency for {sensor} and run redundancy cross-check."
    return "No corrective action required."


def _find_similar_fault(
    fault_type: str,
    mean_error: float,
    max_error: float,
    sensor: str,
    mean_tol: float = 0.05,
    max_tol: float = 0.1,
):
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT fault_id, fault_type, mean_error, max_error, affected_sensor, severity, detected_at, solution, remarks
            FROM faults
            WHERE fault_type = ?
              AND affected_sensor = ?
              AND ABS(mean_error - ?) <= ?
              AND ABS(max_error - ?) <= ?
            ORDER BY fault_id DESC
            LIMIT 1
            """,
            (fault_type, sensor, mean_error, mean_tol, max_error, max_tol),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def _insert_fault(
    fault_type: str,
    mean_error: float,
    max_error: float,
    sensor: str,
    severity: str,
    solution: str,
    remarks: str,
) -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO faults
            (fault_type, mean_error, max_error, affected_sensor, severity, detected_at, solution, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fault_type,
                mean_error,
                max_error,
                sensor,
                severity,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                solution,
                remarks,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def handle_fault_memory(signature: dict, decision: str) -> dict:
    ensure_fault_table()

    if decision == "NORMAL":
        return {
            "fault_detected": False,
            "reuse_hit": False,
            "memory_action": "N/A",
            "recommended_action": "No corrective action required.",
            "fault_id": None,
            "affected_sensor": signature["affected_sensor"],
        }

    mean_error = round(float(signature["mean_error"]), 6)
    max_error = round(float(signature["max_error"]), 6)
    sensor = str(signature["affected_sensor"])
    fault_type = f"{decision}_ANOMALY"
    severity = _severity_for_decision(decision)
    similar = _find_similar_fault(fault_type, mean_error, max_error, sensor)

    if similar:
        fault_id, _, _, _, matched_sensor, _, _, solution, _ = similar
        return {
            "fault_detected": True,
            "reuse_hit": True,
            "memory_action": "Reused from database",
            "recommended_action": solution or _default_solution(matched_sensor, decision),
            "fault_id": int(fault_id),
            "affected_sensor": matched_sensor,
        }

    solution = _default_solution(sensor, decision)
    remarks = f"Auto-logged by model. mean_error={mean_error}, max_error={max_error}"
    fault_id = _insert_fault(fault_type, mean_error, max_error, sensor, severity, solution, remarks)
    return {
        "fault_detected": True,
        "reuse_hit": False,
        "memory_action": "Stored for future reuse",
        "recommended_action": solution,
        "fault_id": fault_id,
        "affected_sensor": sensor,
    }
