"""Local import settings only: no CSV rows or completeness declarations are stored."""
import hashlib
import json
import os
import tempfile
from pathlib import Path
from app.workspace import profile_from

def library_path():
    override = os.environ.get("AUTOREPORT_PROFILE_DIR")
    if override:
        return Path(override)
    return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "AutoReport" / "profiles"

def signature(headers, encoding, delimiter):
    payload = json.dumps([list(headers), encoding, delimiter], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def recall(headers, encoding, delimiter):
    key = signature(headers, encoding, delimiter)
    path = library_path() / (key + ".json")
    if not path.exists():
        return None
    if path.stat().st_size > 200_000:
        raise ValueError("Zapisane ustawienia są uszkodzone. Ustaw format ponownie.")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1 or data.get("signature") != key:
        raise ValueError("Nie można odczytać zapisanych ustawień. Ustaw format ponownie.")
    p = profile_from(data.get("profile"))
    if p.encoding != encoding or p.delimiter != delimiter:
        raise ValueError("Zapisane ustawienia nie pasują do sposobu odczytu pliku.")
    required = [p.date_col, p.value_col, p.category_col, p.quantity_col, p.order_col,
                p.product_col, p.customer_col, p.cost_col, p.profit_col]
    if any(name and name not in headers for name in required):
        raise ValueError("Zapisane ustawienia wskazują nieistniejącą kolumnę.")
    return p

def remember(headers, profile):
    profile.validate()
    key = signature(headers, profile.encoding, profile.delimiter)
    folder = library_path()
    folder.mkdir(parents=True, exist_ok=True)
    body = json.dumps(dict(version=1, signature=key, profile=profile.to_dict()), ensure_ascii=False, indent=2)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=folder, suffix=".tmp", delete=False) as f:
            temporary = Path(f.name)
            f.write(body)
        os.replace(temporary, folder / (key + ".json"))
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
