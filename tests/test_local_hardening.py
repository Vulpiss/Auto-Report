"""Regression for financial chart labels and export recovery under IO faults."""
import errno
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from decimal import Decimal
from matplotlib.backends.backend_agg import FigureCanvasAgg
from app.charts import trend_figure
from app.pipeline import generate_report
from app.profile_library import remember, recall, signature
from app.validation import CsvProfile

RAW = b"date,value,category\n2026-10-06,12.34,A\n"


class ChartPrecisionTests(unittest.TestCase):
    def test_rounded_negative_zero_is_presented_as_zero(self):
        from app.pdf_report import money, percent
        self.assertEqual(money(Decimal("-0.004")), "0,00")
        self.assertEqual(money(Decimal("-0.005")), "-0,01")
        self.assertEqual(percent(Decimal("-0.04")), "+0,0%")

    def test_cent_ticks_are_distinct_and_show_the_sign(self):
        fig = trend_figure([dict(event_date=f"2026-10-0{i+1}", total_value=Decimal(v)) for i,v in enumerate(["0.01", "0.02", "-0.01"])])
        FigureCanvasAgg(fig).draw()
        labels = [t.get_text() for t in fig.axes[0].get_yticklabels()]
        self.assertEqual(len(labels), len(set(labels)))
        self.assertIn("0,01", labels)
        self.assertIn("-0,01", labels)

    def test_zero_chart_has_distinct_ticks_and_no_negative_zero(self):
        fig = trend_figure([dict(event_date="2026-10-06", total_value=Decimal(0))])
        FigureCanvasAgg(fig).draw()
        labels = [t.get_text() for t in fig.axes[0].get_yticklabels()]
        self.assertEqual(len(labels), len(set(labels)))
        self.assertIn("0,00", labels)
        self.assertNotIn("-0,00", labels)

    def test_large_chart_does_not_hide_an_offset(self):
        fig = trend_figure([dict(event_date="2026-10-06", total_value=Decimal("99999999999999.99"))])
        FigureCanvasAgg(fig).draw()
        self.assertFalse(fig.axes[0].yaxis.get_offset_text().get_text())
        self.assertTrue(any("100 000 000 000 000" in t.get_text() for t in fig.axes[0].get_yticklabels()))


class ExportRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="auto-report-recovery-")
        self.root = Path(self.temp.name)
        self.first = Path(generate_report(RAW, output_dir=self.root))
        self.original = self.first.read_bytes()

    def tearDown(self):
        self.temp.cleanup()

    def assert_preserved_and_retry(self):
        self.assertEqual(self.first.read_bytes(), self.original)
        published = [p for p in self.root.iterdir() if not p.name.startswith(".pending-")]
        self.assertEqual(len(published), 1)
        retry = Path(generate_report(RAW, output_dir=self.root))
        self.assertTrue(retry.read_bytes().startswith(b"%PDF"))
        self.assertEqual(json.loads((retry.parent / "summary.json").read_text())["kpis"]["total_minor"], 1234)

    def test_publish_permission_error_preserves_old_report_and_releases_lock(self):
        with patch("app.pipeline.os.replace", side_effect=PermissionError("Destination unavailable")):
            with self.assertRaises(PermissionError):
                generate_report(RAW, output_dir=self.root)
        self.assert_preserved_and_retry()

    def test_full_disk_diagnostics_does_not_mask_the_original_failure(self):
        original = RuntimeError("PDF renderer failed first")
        with patch("app.pipeline.build_pdf", side_effect=original), patch("pathlib.Path.write_text", side_effect=OSError(errno.ENOSPC, "Disk full")):
            with self.assertRaises(RuntimeError) as caught:
                generate_report(RAW, output_dir=self.root)
        self.assertIs(caught.exception, original)
        self.assert_preserved_and_retry()

    def test_summary_write_failure_does_not_publish_partial_report(self):
        write = Path.write_text
        def fail_summary(path, *args, **kwargs):
            if path.name == "summary.json":
                raise OSError(errno.ENOSPC, "Disk full")
            return write(path, *args, **kwargs)
        with patch("pathlib.Path.write_text", new=fail_summary), self.assertRaises(OSError):
            generate_report(RAW, output_dir=self.root)
        self.assert_preserved_and_retry()

    def test_output_root_is_file_then_a_good_directory_still_works(self):
        blocked = self.root / "blocked"
        blocked.write_bytes(b"Do not modify")
        with self.assertRaises(FileExistsError):
            generate_report(RAW, output_dir=blocked)
        self.assertEqual(blocked.read_bytes(), b"Do not modify")
        self.assertTrue(Path(generate_report(RAW, output_dir=self.root)).exists())

    def test_failed_profile_replace_preserves_previous_settings(self):
        import os
        with patch.dict(os.environ, AUTOREPORT_PROFILE_DIR=str(self.root / "profiles")):
            headers = ["date", "value", "category"]
            old = CsvProfile(currency="EUR")
            remember(headers, old)
            file = self.root / "profiles" / (signature(headers, old.encoding, old.delimiter) + ".json")
            before = file.read_bytes()
            with patch("app.profile_library.os.replace", side_effect=PermissionError("No write access")), self.assertRaises(PermissionError):
                remember(headers, CsvProfile(currency="USD"))
            self.assertEqual(file.read_bytes(), before)
            self.assertEqual(recall(headers, old.encoding, old.delimiter).currency, "EUR")
            self.assertEqual(list(file.parent.glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
