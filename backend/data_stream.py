from __future__ import annotations

import csv
from pathlib import Path


REQUIRED_FEATURES = [
    "FIT101",
    "LIT101",
    "P101",
    "P102",
    "AIT202",
    "AIT203",
    "FIT201",
    "P203",
    "P205",
    "P206",
    "DPIT301",
    "FIT301",
    "LIT301",
    "MV301",
    "MV302",
    "MV304",
    "P301",
    "P302",
    "AIT401",
    "AIT402",
    "FIT401",
    "LIT401",
    "P401",
    "P402",
    "P403",
    "P404",
    "UV401",
    "AIT501",
    "AIT502",
    "AIT503",
    "AIT504",
    "FIT501",
    "FIT502",
    "FIT503",
    "FIT504",
    "P501",
    "P502",
    "PIT501",
    "PIT502",
    "PIT503",
    "FIT601",
    "P601",
    "P602",
    "P603",
]


def _validate_headers(headers: list[str]) -> None:
    if headers != REQUIRED_FEATURES:
        missing = [name for name in REQUIRED_FEATURES if name not in headers]
        extras = [name for name in headers if name not in REQUIRED_FEATURES]
        raise ValueError(
            "CSV schema mismatch. "
            f"Expected exact 44-feature order. Missing={missing}, Extras={extras}, "
            f"Received={headers}"
        )


def ordered_values(row: dict[str, float]) -> list[float]:
    row_keys = list(row.keys())
    if row_keys != REQUIRED_FEATURES:
        missing = [name for name in REQUIRED_FEATURES if name not in row]
        extras = [name for name in row if name not in REQUIRED_FEATURES]
        raise ValueError(
            "Named row schema mismatch before inference. "
            f"Missing={missing}, Extras={extras}, Received={row_keys}"
        )
    return [float(row[name]) for name in REQUIRED_FEATURES]


class SwatCsvStream:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.rows = self._load_rows(csv_path)
        self.cursor = 0

    @staticmethod
    def _load_rows(csv_path: Path) -> list[dict[str, float]]:
        if not csv_path.exists():
            raise FileNotFoundError(f"SWaT stream file not found: {csv_path}")

        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header row.")
            headers = [str(name).strip() for name in reader.fieldnames]
            _validate_headers(headers)

            rows: list[dict[str, float]] = []
            for line_no, raw_row in enumerate(reader, start=2):
                ordered_row: dict[str, float] = {}
                for feature in REQUIRED_FEATURES:
                    raw_value = raw_row.get(feature)
                    if raw_value is None or str(raw_value).strip() == "":
                        raise ValueError(f"Empty value for '{feature}' at line {line_no}.")
                    try:
                        ordered_row[feature] = float(raw_value)
                    except ValueError as exc:
                        raise ValueError(
                            f"Non-numeric value for '{feature}' at line {line_no}: {raw_value}"
                        ) from exc
                rows.append(ordered_row)

        if not rows:
            raise ValueError("CSV contains no data rows.")
        return rows

    def next_window(self, window_size: int) -> list[dict[str, float]]:
        if window_size < 2:
            raise ValueError("window_size must be at least 2.")

        end = self.cursor + window_size
        total = len(self.rows)
        window = [self.rows[idx % total] for idx in range(self.cursor, end)]
        self.cursor = end % total
        return window
