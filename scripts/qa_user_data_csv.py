"""Read-only QA of the user-designated CSV, with independent Decimal reference."""
import csv
import hashlib
import json
import sys
import time
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.validation import CsvProfile, load_csv
from app.analysis import analyze_parsed
from app.dashboard_model import make_model
from app.pipeline import export_analysis

source = Path(sys.argv[1] if len(sys.argv)>1 else r'D:\csv do testów\data.csv')
out = Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'build/five-years-20261001'
out.mkdir(parents=True, exist_ok=True)
digest = hashlib.sha256(source.read_bytes()).hexdigest()
profile = CsvProfile(date_col='InvoiceDate', value_col='UnitPrice', category_col='Country',
    quantity_col='Quantity', order_col='InvoiceNo', product_col='StockCode', customer_col='CustomerID',
    quantity_unit='szt.', encoding='cp1252', date_format='%m/%d/%Y %H:%M', currency='XXX',
    value_mode='unit_price', amount_precision='half_up', allow_negative=True)
(out/'profile.json').write_text(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')

# No project parser/aggregation is used for these expected values.
daily = {}
rows = missing_customers = negative_quantities = rounded = 0
raw_sum = Decimal(0)
started = time.perf_counter()
with source.open(encoding='cp1252', newline='') as stream:
    for row in csv.DictReader(stream):
        day = datetime.strptime(row['InvoiceDate'], '%m/%d/%Y %H:%M').date()
        qty = Decimal(row['Quantity']); price = Decimal(row['UnitPrice'])
        original = qty * price
        amount = original.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        stat = daily.setdefault(day, dict(total=Decimal(0), quantity=Decimal(0), rows=0, documents=set(), countries={}))
        stat['total'] += amount; stat['quantity'] += qty; stat['rows'] += 1
        stat['documents'].add(row['InvoiceNo'])
        stat['countries'][row['Country']] = stat['countries'].get(row['Country'], Decimal(0)) + amount
        rows += 1; missing_customers += not row['CustomerID'].strip()
        negative_quantities += qty < 0; rounded += amount != original; raw_sum += original
first, last = min(daily), max(daily)
def reference(start, end):
    selected = [x for day, x in daily.items() if start <= day <= end]
    return dict(total=sum((x['total'] for x in selected), Decimal(0)),
        quantity=sum((x['quantity'] for x in selected), Decimal(0)), rows=sum(x['rows'] for x in selected),
        documents=len(set().union(*(x['documents'] for x in selected))))
all_ref = reference(first, last)
e = dict(source=str(source), bytes=source.stat().st_size, sha256=digest, rows=rows,
    date_range=[str(first), str(last)], calendar_days=(last-first).days+1,
    full_reference=all_ref, missing_customers=missing_customers, negative_quantities=negative_quantities,
    rounded_rows=rounded, rounding_delta=all_ref['total']-raw_sum,
    reference_s=round(time.perf_counter()-started,3), periods={})
print('Independent reference complete:', rows, 'rows', flush=True)
started=time.perf_counter(); parsed=load_csv(source, profile); e['import_s']=round(time.perf_counter()-started,3)
assert len(parsed.rows)==rows
assert Decimal(sum(x['value_minor'] for x in parsed.rows))/100==all_ref['total']
assert parsed.source_sha256==digest
e['quality']=parsed.quality
print('Full import complete:', e['import_s'], 'seconds', flush=True)
e['whole_file_report']=dict(blocked=False)
for name,start,end in [('whole', first, last), ('year2011', datetime(2011,1,1).date(), last), ('last30', last-timedelta(days=29), last)]:
    expected=reference(start,end)
    started=time.perf_counter()
    result=analyze_parsed(parsed,profile=profile,start_date=str(start),end_date=str(end))
    assert result['kpis']['total_value']==expected['total']
    assert result['kpis']['rows_cnt']==expected['rows']
    assert result['business']['quantity']==expected['quantity']
    assert result['business']['orders']==expected['documents']
    assert result['business']['profit'] is None
    assert not result['comparison']['baseline_available']
    for grouping in ('Dzień','Tydzień','Miesiąc'):
        model=make_model(result,grouping)
        assert sum(x['rows_cnt'] for x in model['trend'])==expected['rows']
    e['periods'][name]=dict(start=str(start),end=str(end),expected=expected,analysis_and_models_s=round(time.perf_counter()-started,3))
    if name=='whole':
        e['source_pdf']=str(export_analysis(result,output_dir=out/'source-pdf',title='Test data.csv — cały plik'))
    if name=='last30':
        expected_countries={}
        for day,stat in daily.items():
            if start<=day<=end:
                for country,amount in stat['countries'].items():
                    expected_countries[country]=expected_countries.get(country,Decimal(0))+amount
        for country,amount in expected_countries.items():
            subset=analyze_parsed(parsed,profile=profile,start_date=str(start),end_date=str(end),categories=[country])
            assert subset['kpis']['total_value']==amount, country
        e['checked_country_filters']=len(expected_countries)
        pdf=Path(export_analysis(result,output_dir=out/'source-pdf',title='Test data.csv — ostatnie 30 dni'))
        e['last30_pdf']=str(pdf)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
e['source_unchanged']=True
(out/'evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print(json.dumps({k:v for k,v in e.items() if k!='quality'},ensure_ascii=False,indent=2,default=str),flush=True)
