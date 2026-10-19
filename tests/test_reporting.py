import csv
from contextlib import closing
from dataclasses import replace
from decimal import Decimal
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from app.validation import CsvProfile, DataValidationError, inspect_records, load_csv, parse_date, parse_minor
from app.transform import write_facts
from app.queries import calculate_pct_change, compute_previous_period, kpi_summary, period_comparison
from app.decision import simple_decision
from app.pipeline import generate_report, select_reporting_period, _REPORT_LOCK
from app.profiles import save_profile, load_profile

ROOT = Path(__file__).resolve().parents[1]


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["date", "value", "category"])
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


class ParserTests(unittest.TestCase):
    def test_amounts_are_exact_minor_units(self):
        for text, expected in [("0.10", 10), ("123.45", 12345), ("001", 100), (" 2.5 ", 250)]:
            with self.subTest(text=text):
                self.assertEqual(parse_minor(text), expected)

    def test_invalid_numeric_is_never_zero(self):
        for text in ["not-a-number", "NaN", "inf", "1e3", "1,000", "1.234", "1 000", "", "10000000001"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_minor(text)

    def test_negative_requires_explicit_rule(self):
        with self.assertRaises(ValueError):
            parse_minor("-1.20")
        self.assertEqual(parse_minor("-1.20", allow_negative=True), -120)

    def test_date_formats_are_explicit(self):
        self.assertEqual(parse_date("29.02.2024", "%d.%m.%Y"), "2024-02-29")
        for text in ["2026-02-29", "01/02/2026", "2026-9-1", "2026-01-01T12:00:00"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_date(text)

    def test_mixed_bad_amount_blocks_entire_report(self):
        with self.assertRaises(DataValidationError) as caught:
            load_csv(csv_bytes([("2026-09-01", "100", "A"), ("2026-09-02", "broken", "B")]))
        self.assertEqual(caught.exception.quality["invalid_rows"], 1)
        self.assertEqual(caught.exception.quality["issues"][0]["line"], 3)

    def test_counts_use_union_of_invalid_rows(self):
        records = [{"date": None, "value": "10", "category": "A"},
                   {"date": "2026-09-01", "value": None, "category": "A"},
                   {"date": "2026-09-02", "value": "30", "category": "A"}]
        _, quality = inspect_records(enumerate(records, 2), CsvProfile())
        self.assertEqual((quality["valid_rows"], quality["invalid_rows"]), (1, 2))
        self.assertEqual(quality["total_rows"], 3)

    def test_multiple_errors_count_one_row(self):
        _, quality = inspect_records([(2, {})], CsvProfile())
        self.assertEqual(quality["invalid_rows"], 1)
        self.assertEqual(len(quality["issues"][0]["reasons"]), 3)

    def test_nan_category_from_dataframe_is_missing(self):
        _, quality = inspect_records([(2, {"date": "2026-09-01", "value": 1, "category": float("nan")})], CsvProfile())
        self.assertEqual(quality["invalid_rows"], 1)

    def test_duplicates_preserved(self):
        parsed = load_csv(csv_bytes([("2026-09-01", "10", "A")] * 2))
        self.assertEqual(len(parsed.rows), 2)
        self.assertEqual(parsed.quality["duplicate_rows"], 1)

    def test_polish_profile_matches_iso_fixture(self):
        profile = CsvProfile("data", "kwota", "kategoria", ";", "utf-8-sig", "%d.%m.%Y", ",")
        iso = load_csv(ROOT / "sample_data/pilot_demo.csv")
        polish = load_csv(ROOT / "sample_data/pilot_demo_pl.csv", profile)
        self.assertEqual(iso.rows, polish.rows)

    def test_windows_encoding(self):
        data = "date;value;category\n2026-09-01;1,23;Żółć\n".encode("cp1250")
        profile = CsvProfile(delimiter=";", decimal_separator=",", encoding="cp1250")
        self.assertEqual(load_csv(data, profile).rows[0]["category"], "Żółć")
        with self.assertRaises(DataValidationError):
            load_csv(data)

    def test_empty_and_bad_header_and_ragged_csv(self):
        cases = [b"", b"date,value,category\n", b"date,date,category\n1,2,A",
                 b"date,value\n2026-09-01,10", b"date,value,category\n2026-09-01,10,A,extra",
                 b'date,value,category\n2026-09-01,10,"unterminated']
        for data in cases:
            with self.subTest(data=data), self.assertRaises(DataValidationError):
                load_csv(data)

    def test_mapped_sql_like_header_is_plain_data(self):
        name = "value); DROP TABLE facts;--"
        data = f'date;{name};category\n2026-09-01;12;A\n'.encode()
        # Use comma so semicolon characters remain part of the quoted header.
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(["date", name, "category"])
        writer.writerow(["2026-09-01", "12", "A"])
        parsed = load_csv(stream.getvalue().encode(), CsvProfile(value_col=name))
        self.assertEqual(parsed.rows[0]["value_minor"], 1200)

    def test_file_limit(self):
        with patch("app.validation.MAX_BYTES", 10), self.assertRaises(DataValidationError):
            load_csv(b"x" * 11)

    def test_row_limit(self):
        with patch("app.validation.MAX_ROWS", 1), self.assertRaises(DataValidationError):
            load_csv(csv_bytes([("2026-09-01", "10", "A")] * 2))

    def test_invalid_profile(self):
        for profile in [CsvProfile(value_col="date"), CsvProfile(delimiter="|"), CsvProfile(currency="JPY")]:
            with self.subTest(profile=profile), self.assertRaises(DataValidationError):
                profile.validate()


class CalculationTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        write_facts(self.conn, load_csv(ROOT / "sample_data/pilot_demo.csv").rows)

    def tearDown(self):
        self.conn.close()

    def test_independent_reference_sums(self):
        # Manual fixture: previous 100+200+50+150+100+200+200=1000.
        # Current 150+200+100+150+250+150+250=1250; average 1250/7=178.57.
        kpis = kpi_summary(self.conn, "2026-09-07", "2026-09-13")
        self.assertEqual(kpis["total_minor"], 125000)
        self.assertEqual(kpis["rows_cnt"], 7)
        self.assertEqual(kpis["avg_value"], Decimal("178.57"))

    def test_zero_or_negative_base_has_no_percentage(self):
        for current, previous in [(0, 0), (100, 0), (-100, 0), (10, -10)]:
            self.assertIsNone(calculate_pct_change(current, previous))
        self.assertEqual(calculate_pct_change(1250, 1000), 25)
        self.assertEqual(calculate_pct_change(0, 100), -100)

    def test_unverified_coverage_blocks_comparison(self):
        result = period_comparison(self.conn, "2026-09-07", "2026-09-13")
        self.assertFalse(result["baseline_available"])
        self.assertIsNone(result["change_pct"]["total_value"])
        self.assertNotIn("SCALE", simple_decision(result))

    def test_verified_coverage_allows_comparison(self):
        result = period_comparison(self.conn, "2026-09-07", "2026-09-13", "2026-08-31", "2026-09-13")
        self.assertTrue(result["baseline_available"])
        self.assertEqual(result["change_pct"]["total_value"], 25)
        self.assertNotIn("SCALE", simple_decision(result))

    def test_one_baseline_record_does_not_prove_coverage(self):
        write_facts(self.conn, load_csv(csv_bytes([("2026-08-31", "100", "A"), ("2026-09-01", "100", "A"), ("2026-09-02", "100", "A")])).rows)
        self.assertFalse(period_comparison(self.conn, "2026-09-01", "2026-09-02")["baseline_available"])

    def test_period_edges_and_validation(self):
        self.assertEqual(compute_previous_period("2024-03-01", "2024-03-07"), ("2024-02-23", "2024-02-29"))
        for days in [0, -1, 1828, True]:
            with self.subTest(days=days), self.assertRaises(ValueError):
                select_reporting_period("2026-09-01", days)
        with self.assertRaises(ValueError):
            compute_previous_period("2026-09-02", "2026-09-01")

    def test_average_change_uses_unrounded_means(self):
        rows = [("2026-09-01", "0.01", "A"), ("2026-09-01", "0.02", "A"),
                ("2026-09-02", "0.03", "A"), ("2026-09-02", "0.03", "A")]
        write_facts(self.conn, load_csv(csv_bytes(rows)).rows)
        result = period_comparison(self.conn, "2026-09-02", "2026-09-02", "2026-09-01", "2026-09-02")
        self.assertEqual(result["change_pct"]["avg_value"], 100)

    def test_noncanonical_period_is_rejected(self):
        with self.assertRaises(ValueError):
            compute_previous_period("2026-9-1", "2026-09-02")

    def test_large_sum_preserves_last_cent(self):
        rows = [{"event_date": "2026-09-01", "value_minor": 10**12, "category": "A"} for _ in range(10000)]
        rows[-1]["value_minor"] -= 1
        write_facts(self.conn, rows)
        result = kpi_summary(self.conn, "2026-09-01", "2026-09-01")
        self.assertEqual(result["total_value"], Decimal("99999999999999.99"))

    def test_cents_and_half_up(self):
        write_facts(self.conn, load_csv(csv_bytes([("2026-09-01", "0.10", "A"), ("2026-09-01", "0.11", "A")])).rows)
        result = kpi_summary(self.conn, "2026-09-01", "2026-09-01")
        self.assertEqual(result["total_minor"], 21)
        self.assertEqual(result["avg_value"], Decimal("0.11"))


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="auto-report-test-")
        self.output = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def report(self, data=None, **kwargs):
        return generate_report(data if data is not None else ROOT / "sample_data/pilot_demo.csv",
                               output_dir=self.output, **kwargs)

    def test_real_pdf_and_independent_summary(self):
        path = Path(self.report(coverage_start="2026-08-31", coverage_end="2026-09-13"))
        self.assertTrue(path.read_bytes().startswith(b"%PDF"))
        summary = json.loads((path.parent / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["kpis"]["total_minor"], 125000)
        self.assertEqual(summary["quality"]["rows_outside_period"], 7)
        self.assertEqual(summary["comparison"]["change_pct"]["total_value"], 25)
        self.assertNotIn("input_csv", summary)
        self.assertEqual(len(summary["source_sha256"]), 64)

    def test_distinct_inputs_and_runs(self):
        first = Path(self.report(csv_bytes([("2026-09-01", "10", "A")])))
        original = first.read_bytes()
        second = Path(self.report(csv_bytes([("2026-09-01", "20", "B")])))
        self.assertNotEqual(first, second)
        self.assertEqual(first.read_bytes(), original)
        self.assertEqual(json.loads((second.parent / "summary.json").read_text())["kpis"]["total_minor"], 2000)

    def test_invalid_input_does_not_write_any_output(self):
        with self.assertRaises(DataValidationError):
            self.report(csv_bytes([("2026-09-01", "wrong", "A")]))
        self.assertEqual(list(self.output.iterdir()), [])

    def test_invalid_run_preserves_previous_pdf(self):
        first = Path(self.report())
        previous = first.read_bytes()
        with self.assertRaises(DataValidationError):
            self.report(b"")
        self.assertEqual(first.read_bytes(), previous)

    def test_custom_dates_are_applied(self):
        path = Path(self.report(start_date="2026-09-01", end_date="2026-09-02"))
        result = json.loads((path.parent / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(result["kpis"]["total_minor"], 25000)
        self.assertEqual(result["kpis"]["rows_cnt"], 2)

    def test_invalid_coverage_and_empty_period(self):
        for kwargs in [{"coverage_start": "2026-09-01"},
                       {"coverage_start": "2026-09-01", "coverage_end": "2026-09-13"},
                       {"start_date": "2020-01-01", "end_date": "2020-01-07"}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.report(**kwargs)

    def test_concurrent_request_rejected(self):
        with _REPORT_LOCK:
            with self.assertRaisesRegex(RuntimeError, "już"):
                self.report()

    def test_render_failure_never_publishes_partial_report(self):
        with patch("app.pipeline.build_pdf", side_effect=RuntimeError("render failed")):
            with self.assertRaises(RuntimeError):
                self.report()
        dirs = list(self.output.iterdir())
        self.assertTrue(all(p.name.startswith(".pending-") for p in dirs))
        self.assertTrue((dirs[0] / "failure.json").exists())
        # Lock is released even after failure.
        self.assertTrue(Path(self.report()).exists())

    def test_saved_profile_roundtrip(self):
        path = self.output / "profile.json"
        profile = CsvProfile(delimiter=";", decimal_separator=",", amount_basis="netto")
        save_profile(profile, path)
        self.assertEqual(load_profile(path), profile)
        path.write_text('{"allow_negative": "false"}', encoding="utf-8")
        with self.assertRaises(DataValidationError):
            load_profile(path)


if __name__ == "__main__":
    unittest.main()
