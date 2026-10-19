import unittest
from datetime import date
from decimal import Decimal

from app.analysis import analyze_parsed, earliest_reporting_date, select_reporting_period
from app.validation import load_csv
from app.dashboard_model import make_model


class FiveYearTests(unittest.TestCase):
    def test_all_dashboard_views_with_five_years_and_five_categories(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_string('''
from datetime import date, timedelta
from app.validation import load_csv
from app.analysis import analyze_parsed
from app.dashboard_model import make_model
from interfaces.dashboard_views import render_view
raw = 'date,value,category\\n' + ''.join(f'{date(2021,10,2)+timedelta(days=i)},1,{c}\\n' for i in range(1826) for c in 'ABCDE')
result = analyze_parsed(load_csv(raw.encode()), start_date='2021-10-02', end_date='2026-10-01')
for view in range(3):
    render_view(result, make_model(result), view)
''', default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '9 130,00')

    def test_calendar_boundaries(self):
        for end, start, days in [
            ('2026-10-01', '2021-10-02', 1826),
            ('2025-01-01', '2020-01-02', 1827),
            ('2024-02-29', '2019-03-01', 1827),
        ]:
            with self.subTest(end=end):
                self.assertEqual(str(earliest_reporting_date(date.fromisoformat(end))), start)
                self.assertEqual(select_reporting_period(end, days), (start, end))
                with self.assertRaisesRegex(ValueError, '5 lat'):
                    select_reporting_period(end, days + 1)

    def test_five_year_totals_filters_and_previous_period(self):
        parsed = load_csv(b'date,value,category\n2016-10-02,7,A\n2021-10-01,13,A\n2021-10-02,10,A\n2024-02-29,20,B\n2026-10-01,30,A\n')
        result = analyze_parsed(parsed, start_date='2021-10-02', end_date='2026-10-01',
                                coverage_start='2016-10-02', coverage_end='2026-10-01')
        self.assertEqual(result['kpis']['total_value'], Decimal('60'))
        self.assertEqual(result['kpis']['rows_cnt'], 3)
        self.assertEqual(len(result['daily']), 1826)
        self.assertTrue(result['comparison']['baseline_available'])
        self.assertEqual(result['comparison']['previous']['total_value'], Decimal('20'))
        self.assertEqual(result['comparison']['change_pct']['total_value'], 200)
        for grouping in ('Dzień', 'Tydzień', 'Miesiąc'):
            model = make_model(result, grouping)
            self.assertEqual(sum(x['current'] for x in model['trend']), Decimal('60'))
        filtered = analyze_parsed(parsed, start_date='2021-10-02', end_date='2026-10-01', categories=['A'])
        self.assertEqual(filtered['kpis']['total_value'], Decimal('40'))
        with self.assertRaisesRegex(ValueError, '5 lat'):
            analyze_parsed(parsed, start_date='2021-10-01', end_date='2026-10-01')

    def test_historical_file_longer_than_year(self):
        parsed = load_csv(b'date,value,category\n2010-12-01,12.34,A\n2011-12-09,56.78,B\n')
        result = analyze_parsed(parsed, start_date='2010-12-01', end_date='2011-12-09')
        self.assertEqual(result['kpis']['total_value'], Decimal('69.12'))
        self.assertEqual(len(result['daily']), 374)
        self.assertFalse(result['comparison']['baseline_available'])
