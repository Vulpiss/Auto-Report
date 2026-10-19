"""Portable profiles and sessions, no source records embedded."""
import csv, io, json, hashlib
from dataclasses import fields
from app.validation import CsvProfile, MAX_BYTES
VERSION=1
PROFILE_STATE={"amount_basis":"basis","amount_precision":"precision","allow_negative":"negative"}
FILTER_KEYS={"start","end","all_categories","categories","coverage_start","coverage_end","grouping","comparison_mode","product_filter","customer_filter","view","pptx_title","pptx_comment","presentation_mode","pptx_style","export_dimension"}
ALIASES={"date_col":["date","order date","data","data sprzedaży"],"value_col":["value","sales","wartość","kwota"],"category_col":["category","sub-category","kategoria"],"quantity_col":["quantity","ilość"],"order_col":["order id","order","order_id","zamówienie"],"product_col":["product id","product","produkt"],"customer_col":["customer id","customer","klient"],"cost_col":["cost","koszt"],"profit_col":["profit","zysk"]}
def preview(raw,encoding,delimiter):
    if len(raw)>MAX_BYTES:raise ValueError("Limit 100 MiB.")
    reader=csv.reader(io.TextIOWrapper(io.BytesIO(raw),encoding=encoding,newline=""),delimiter=delimiter,strict=True)
    header=next(reader,[])
    header=[x.strip() for x in header]
    if not header or len(set(header))!=len(header) or any(not x for x in header):raise ValueError("Niepoprawne nagłówki.")
    rows=[]
    for _,row in zip(range(5),(row for row in reader if row)):
        if len(row)!=len(header):raise ValueError("Nieprawidłowa liczba pól.")
        rows.append(dict(zip(header,row)))
    return header,rows
def propose(header):
    lower={x.casefold():x for x in header}
    return {key:next((lower[a] for a in aliases if a in lower),"") for key,aliases in ALIASES.items()}
def profile_from(data):
    if not isinstance(data,dict) or set(data)-{f.name for f in fields(CsvProfile)}:raise ValueError("Nieznane pola profilu.")
    p=CsvProfile(**data);p.validate();return p
def profile_state(p):
    return {PROFILE_STATE.get(k,k):v for k,v in p.to_dict().items()}
def encode_session(raw,profile,state):
    return json.dumps(dict(version=VERSION,source_sha256=hashlib.sha256(raw).hexdigest(),profile=profile.to_dict(),
        settings={k:state[k] for k in FILTER_KEYS if k in state}),ensure_ascii=False,indent=2).encode("utf-8")
def decode_document(raw):
    if len(raw)>200_000:raise ValueError("Plik ustawień jest zbyt duży.")
    data=json.loads(raw)
    if not isinstance(data,dict):raise ValueError("Niepoprawny dokument.")
    if "source_sha256" not in data:return dict(profile=profile_from(data))
    if data.get("version")!=VERSION or not isinstance(data.get("settings"),dict) or set(data["settings"])-FILTER_KEYS:raise ValueError("Nieobsługiwana sesja.")
    digest=data["source_sha256"]
    if not isinstance(digest,str) or len(digest)!=64 or any(x not in "0123456789abcdef" for x in digest):raise ValueError("Niepoprawny identyfikator źródła.")
    settings=data["settings"]
    for key,value in settings.items():
        if key in ("all_categories","presentation_mode"):
            if type(value) is not bool:raise ValueError("Niepoprawne ustawienie logiczne.")
        elif key in ("categories","product_filter","customer_filter"):
            if not isinstance(value,list) or any(not isinstance(x,str) for x in value):raise ValueError("Niepoprawny filtr.")
        elif not isinstance(value,str) or len(value)>500:raise ValueError("Niepoprawne ustawienie tekstowe.")
    enums={"grouping":("Dzień","Tydzień","Miesiąc"),"comparison_mode":("Poprzedni okres","Rok do roku"),
           "view":("Wynik i trend","Kategorie i źródła zmiany","Jakość i pokrycie danych"),
           "pptx_style":("Dashboardy","Edytowalne wykresy"),"export_dimension":("category","product","customer")}
    if any(k in settings and settings[k] not in options for k,options in enums.items()):raise ValueError("Nieznana opcja sesji.")
    return dict(profile=profile_from(data["profile"]),settings=settings,source_sha256=digest)
def verify_source(document,raw):
    if document.get("source_sha256") and document["source_sha256"]!=hashlib.sha256(raw).hexdigest():
        raise ValueError("Sesja pochodzi z innego CSV. Wczytaj oryginalny plik; kompletność i filtry nie zostały przywrócone.")
