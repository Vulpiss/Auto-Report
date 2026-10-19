"""Independent acceptance expectations must not silently become passing results."""
import hashlib
import unittest
from scripts.verify_acceptance import check

RAW = b'date,value,category\n2026-10-01,1.00,A\n2026-10-02,2.00,B\n'


class AcceptanceVerifierTests(unittest.TestCase):
    def setUp(self):
        self.profile = dict(currency='PLN', amount_basis='netto')
        self.expected = dict(data_kind='synthetic', reference_note='Ręczny wzorzec: 1 + 2 = 3, 3 / 2 = 1.50.',
                             source_sha256=hashlib.sha256(RAW).hexdigest(), start='2026-10-01', end='2026-10-02',
                             currency='PLN', amount_basis='netto', rows=2, total='3.00', average='1.50',
                             categories={'A': '1.00', 'B': '2.00'})

    def test_independent_fixed_expectations_pass_without_claiming_customer_approval(self):
        result = check(RAW, self.profile, self.expected)
        self.assertEqual(result['result'], 'PASS_NUMBERS_ONLY')
        self.assertEqual(result['customer_acceptance'], 'UNKNOWN')

    def test_wrong_category_assignment_fails_even_when_grand_total_matches(self):
        self.expected['categories'] = {'A': '2.00', 'B': '1.00'}
        result = check(RAW, self.profile, self.expected)
        self.assertEqual(result['result'], 'FAIL')
        self.assertEqual(result['different_fields'], ['categories'])

    def test_changed_source_with_same_totals_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            check(RAW + b'\n', self.profile, self.expected)

    def test_same_numbers_in_different_currency_or_basis_are_rejected(self):
        for field, value in [('currency', 'EUR'), ('amount_basis', 'brutto')]:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Waluta'):
                check(RAW, dict(self.profile, **{field: value}), self.expected)

    def test_blank_reference_is_incomplete(self):
        self.expected['total'] = None
        with self.assertRaisesRegex(ValueError, 'total'):
            check(RAW, self.profile, self.expected)

    def test_wrong_period_cannot_pass_matching_source_hash(self):
        self.expected['start'] = '2026-10-02'
        result = check(RAW, self.profile, self.expected)
        self.assertEqual(result['result'], 'FAIL')
        self.assertIn('rows', result['different_fields'])

    def test_inconsistent_expected_category_totals_are_rejected(self):
        self.expected['categories']['A'] = '9.00'
        with self.assertRaisesRegex(ValueError, 'nie składają'):
            check(RAW, self.profile, self.expected)

    def test_average_mismatch_is_detected_separately(self):
        self.expected['average'] = '1.49'
        self.assertEqual(check(RAW, self.profile, self.expected)['different_fields'], ['average'])


if __name__ == '__main__':
    unittest.main()
