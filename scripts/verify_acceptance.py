"""Compare actual CSV analysis with separately approved expected numbers.

No PDF creation, no source mutation and no automatic expected-value generation.
This is a local acceptance aid, not evidence of customer approval or demand.
"""
import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.analysis import analyze
from app.workspace import profile_from


def check(raw, profile_data, expected):
    """Reject incomplete expectations; compare source, meaning, scope and numbers."""
    profile = profile_from(profile_data)
    required = ('data_kind', 'reference_note', 'source_sha256', 'start', 'end',
                'currency', 'amount_basis', 'rows', 'total', 'average', 'categories')
    missing = [key for key in required if expected.get(key) is None or expected.get(key) == '']
    if missing:
        raise ValueError('Uzupełnij niezależny wzorzec: ' + ', '.join(missing))
    if expected['data_kind'] not in ('synthetic', 'real'):
        raise ValueError('data_kind: synthetic albo real.')
    if not isinstance(expected['reference_note'], str) or not expected['reference_note'].strip():
        raise ValueError('Opisz pochodzenie niezależnego wzorca.')
    if not isinstance(expected['source_sha256'], str) or not re.fullmatch('[0-9a-f]{64}', expected['source_sha256']):
        raise ValueError('Wymagany SHA-256 źródła.')
    if type(expected['rows']) is not int or expected['rows'] < 1:
        raise ValueError('Wzorzec musi obejmować dodatnią liczbę pozycji.')
    if not isinstance(expected['categories'], dict) or not expected['categories']:
        raise ValueError('Podaj oczekiwane sumy wszystkich kategorii po filtrach.')
    def amount(value):
        if not isinstance(value, str) or not re.fullmatch(r'-?\d+\.\d{2}', value):
            raise ValueError('Kwoty wzorca zapisuj jako tekst z dwoma miejscami i kropką.')
        return Decimal(value)
    total, average = amount(expected['total']), amount(expected['average'])
    categories = {key: amount(value) for key, value in expected['categories'].items()}
    if sum(categories.values(), Decimal(0)) != total:
        raise ValueError('Sumy kategorii wzorca nie składają się na sumę ogólną.')
    start, end = date.fromisoformat(expected['start']), date.fromisoformat(expected['end'])
    if start > end:
        raise ValueError('Niepoprawny okres wzorca.')
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected['source_sha256']:
        raise ValueError('CSV ma inny SHA-256 niż niezależny wzorzec.')
    if profile.currency != expected['currency'] or profile.amount_basis != expected['amount_basis']:
        raise ValueError('Waluta lub netto/brutto nie odpowiada wzorcowi.')
    result = analyze(raw, profile=profile, start_date=start.isoformat(), end_date=end.isoformat())
    actual = dict(rows=result['kpis']['rows_cnt'], total=result['kpis']['total_value'],
                  average=result['kpis']['avg_value'],
                  categories={row['category']: row['total_value'] for row in result['categories'] if row['rows_cnt']})
    differences = []
    for key, value in dict(rows=expected['rows'], total=total, average=average, categories=categories).items():
        if actual[key] != value:
            differences.append(key)
    return dict(result='FAIL' if differences else 'PASS_NUMBERS_ONLY', data_kind=expected['data_kind'],
                source_sha256=digest, start=expected['start'], end=expected['end'],
                currency=profile.currency, amount_basis=profile.amount_basis,
                actual=actual, different_fields=differences,
                reference_note=expected['reference_note'], customer_acceptance='UNKNOWN',
                scope='CSV analysis only; PDF, optional business KPIs and comparison require separate acceptance.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--expected', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() in {p.resolve() for p in (args.csv, args.profile, args.expected)}:
        parser.error('Wybierz nową ścieżkę wyniku; istniejące pliki są zachowywane.')
    try:
        result = check(args.csv.read_bytes(), json.loads(args.profile.read_text(encoding='utf-8-sig')),
                       json.loads(args.expected.read_text(encoding='utf-8-sig')))
    except (ValueError, InvalidOperation) as error:
        result = dict(result='INCOMPLETE_OR_INVALID', error=str(error), customer_acceptance='UNKNOWN')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, default=str)
        stream.write('\n')
    print(json.dumps(dict(result=result['result'], output=str(args.output)), ensure_ascii=False))
    return 0 if result['result'] == 'PASS_NUMBERS_ONLY' else 2


if __name__ == '__main__':
    raise SystemExit(main())
