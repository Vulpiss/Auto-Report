import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app.profile_library import recall, remember, signature
from app.validation import CsvProfile

class ProfileLibraryTests(unittest.TestCase):
    def test_roundtrip_schema_separation_and_no_rows(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"AUTOREPORT_PROFILE_DIR": folder}):
            p = CsvProfile(currency="EUR", amount_basis="netto")
            header = ["date", "value", "category"]
            remember(header, p)
            self.assertEqual(recall(header, p.encoding, p.delimiter), p)
            self.assertIsNone(recall(["date", "price", "category"], p.encoding, p.delimiter))
            self.assertIsNone(recall(header, p.encoding, ";"))
            body = json.loads(next(Path(folder).glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(set(body), {"version", "signature", "profile"})

    def test_corrupt_or_inconsistent_profile_is_not_used(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"AUTOREPORT_PROFILE_DIR": folder}):
            header = ["date", "value", "category"]
            p = CsvProfile()
            key = signature(header, p.encoding, p.delimiter)
            path = Path(folder)/(key+".json")
            path.write_text("broken", encoding="utf-8")
            with self.assertRaises(ValueError): recall(header, p.encoding, p.delimiter)
            remember(header, p)
            body = json.loads(path.read_text(encoding="utf-8"))
            body["profile"]["value_col"] = "missing"
            path.write_text(json.dumps(body), encoding="utf-8")
            with self.assertRaises(ValueError): recall(header, p.encoding, p.delimiter)
