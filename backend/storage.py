"""Simple file-based storage helpers for scenic spot data."""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List


_DATA_FILE = Path(__file__).resolve().parent / "data" / "spots.json"
_LOCK = RLock()


class StorageError(RuntimeError):
    """Raised when the storage layer cannot fulfill a request."""


def _load_payload() -> Dict[str, Any]:
    if not _DATA_FILE.exists():
        return {"spots": []}

    try:
        with _DATA_FILE.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise StorageError(f"Failed to decode JSON data: {exc}") from exc


def _write_payload(payload: Dict[str, Any]) -> None:
    _DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def list_spots() -> List[Dict[str, Any]]:
    with _LOCK:
        payload = _load_payload()
        return list(payload.get("spots", []))


def get_spot(spot_id: str) -> Dict[str, Any] | None:
    spot_id = spot_id.strip().lower()
    with _LOCK:
        for record in _load_payload().get("spots", []):
            if record.get("id", "").lower() == spot_id:
                return record
    return None


def upsert_spot(record: Dict[str, Any]) -> Dict[str, Any]:
    spot_id = record.get("id")
    if not spot_id:
        raise StorageError("Spot record must include a non-empty 'id'.")

    spot_id = spot_id.strip()
    record = {**record, "id": spot_id}

    with _LOCK:
        payload = _load_payload()
        spots = payload.setdefault("spots", [])

        for index, existing in enumerate(spots):
            if existing.get("id", "").lower() == spot_id.lower():
                spots[index] = record
                break
        else:
            spots.append(record)

        _write_payload(payload)

    return record


def delete_spot(spot_id: str) -> bool:
    spot_id = spot_id.strip().lower()
    with _LOCK:
        payload = _load_payload()
        spots = payload.get("spots", [])
        filtered = [item for item in spots if item.get("id", "").lower() != spot_id]
        if len(filtered) == len(spots):
            return False
        payload["spots"] = filtered
        _write_payload(payload)
        return True


def append_detail_section(spot_id: str, section: Dict[str, Any]) -> Dict[str, Any]:
    spot_key = spot_id.strip().lower()
    if not spot_key:
        raise StorageError("Spot id must not be empty when adding detail section.")

    with _LOCK:
        payload = _load_payload()
        for record in payload.get("spots", []):
            if record.get("id", "").lower() == spot_key:
                details = record.setdefault("detailSections", [])
                details.append(section)
                _write_payload(payload)
                return section

    raise StorageError(f"Spot '{spot_id}' not found; cannot append detail section.")
