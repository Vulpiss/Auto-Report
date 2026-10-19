from dataclasses import fields
import json
import os
from pathlib import Path
from uuid import uuid4
from app.config import DATA_DIR
from app.validation import CsvProfile, DataValidationError


def save_profile(profile, path=None):
    profile.validate()
    target = Path(path) if path else DATA_DIR / "profile.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + "." + uuid4().hex + ".tmp")
    temporary.write_text(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, target)


def load_profile(path=None):
    target = Path(path) if path else DATA_DIR / "profile.json"
    if not target.exists():
        return CsvProfile()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        valid_keys = {field.name for field in fields(CsvProfile)}
        if not isinstance(data, dict) or set(data) - valid_keys:
            raise ValueError("Nieznane pola profilu.")
        result = CsvProfile(**data)
        result.validate()
        return result
    except (ValueError, TypeError) as exc:
        raise DataValidationError("Niepoprawny zapisany profil. Ustaw parametry ponownie.") from exc
