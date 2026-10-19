import unittest
from dataclasses import replace
from decimal import Decimal
from unittest.mock import patch
from app.validation import CsvProfile,load_csv,DataValidationError
from app.workspace import preview
P=CsvProfile(value_mode="unit_price",quantity_col="qty",quantity_unit="szt.",date_format="%m/%d/%Y %H:%M",amount_precision="half_up",allow_negative=True)
RAW=b"date,value,category,qty,id\r\n\r\n12/1/2010 8:26,1.235,A,3,x\r\n12/1/2010 9:26,1.235,A,3,y\r\n12/1/2010 9:26,1.235,A,3,y\r\n"
class LargeImportTests(unittest.TestCase):
    def test_decimal_multiply_before_rounding_and_duplicates(self):
        p=load_csv(RAW,P)
        self.assertEqual([r["value_minor"] for r in p.rows],[371,371,371])
        self.assertEqual(p.quality["exact_duplicate_rows"],1)
        self.assertEqual(p.quality["duplicate_rows"],2)
        self.assertEqual(p.quality["blank_lines"],1)
        self.assertEqual(Decimal(p.quality["rounding_delta"]),Decimal(".015"))
        self.assertEqual(len(preview(RAW,"utf-8-sig",",")[1]),3)
    def test_missing_invalid_and_negative_quantity(self):
        for data in (RAW.replace(b",3,",b",,"), RAW.replace(b"1.235",b"NaN"), RAW.replace(b",3,",b",abc,")):
            with self.assertRaises(DataValidationError):load_csv(data,P)
        self.assertEqual(load_csv(RAW.replace(b",3,",b",-3,"),P).rows[0]["value_minor"],-371)
        with self.assertRaises(DataValidationError):load_csv(RAW.replace(b",3,",b",-3,"),replace(P,allow_negative=False))
    def test_limits_and_late_encoding(self):
        with patch("app.validation.MAX_ROWS",2),self.assertRaises(DataValidationError):load_csv(RAW,P)
        with patch("app.validation.MAX_BYTES",5),self.assertRaises(DataValidationError):load_csv(RAW,P)
        with self.assertRaises(DataValidationError):load_csv(RAW+b"\xff",P)
    def test_ui_native_retail(self):
        import io
        from streamlit.testing.v1 import AppTest
        data=b"InvoiceDate,UnitPrice,Country,Quantity,InvoiceNo,StockCode,CustomerID\n12/1/2010 8:26,1.235,UK,3,N1,P1,C1\n"
        with patch("streamlit.file_uploader",return_value=io.BytesIO(data)):
            app=AppTest.from_file("interfaces/streamlit_app.py",default_timeout=30).run()
            app.button(key="retail_profile").click().run()
            app.button(key="load").click().run()
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            self.assertEqual(app.session_state["parsed"].rows[0]["value_minor"],371)
