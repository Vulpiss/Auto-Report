"""Three analyst dashboards, shared filters and offline PDF/PPTX export."""
import hashlib
import sys
from pathlib import Path
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import streamlit as st
from app.validation import CsvProfile,load_csv,DataValidationError,CURRENCIES,DATE_FORMATS,ENCODINGS,currency_label
from app.analysis import analyze_parsed,select_reporting_period
from app.dashboard_model import make_model,VIEW_NAMES
from app.presentation import export_pptx
from app.pipeline import export_analysis
from interfaces.import_feedback import render_diagnostics
from app.pdf_report import money
from interfaces.dashboard_views import render_view, render_business
from app.workspace import preview, propose, profile_state, decode_document, verify_source, encode_session
import json
import time
from app.analyst_tools import scope_text

ROOT=Path(__file__).resolve().parents[1]
st.set_page_config(page_title="Auto-Report | Analityk",page_icon="◈",layout="wide")
st.markdown("""<style>
.stApp{background:#eef3f8;color:#172d44}
.block-container{padding:3.5rem 2rem 1rem;max-width:1600px}
[data-testid="stVerticalBlock"]{gap:.55rem}
[data-testid="stSidebar"]{background:#082840}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] summary{color:#e3edf6}
[data-testid="stSidebar"] details,[data-testid="stSidebar"] summary{background:#10364f}
[class*="st-key-panel_"]{background:white;border-radius:10px}
[data-testid="stSidebar"] input{color:#172d44}
[data-testid="stSidebar"] button[kind="secondary"] p{color:#172d44}
[data-testid="stMetric"]{background:white;border:1px solid #dfe7ef;border-radius:10px;padding:12px 16px}
[data-testid="stMetricValue"]{font-size:1.8rem}
[data-testid="stVerticalBlockBorderWrapper"]{background:white;border-radius:10px}
[data-testid="stAppDeployButton"]{display:none}
h1{font-size:1.9rem !important;padding-bottom:.25rem !important}
h3{font-size:1rem !important;padding:.2rem 0 !important}
</style>""",unsafe_allow_html=True)
with st.sidebar:
    st.title("Auto-Report.")
    selected_view=st.radio("Dashboard",VIEW_NAMES,key="view")
    with st.expander("Dane i konfiguracja",expanded="parsed" not in st.session_state):
        demo=st.checkbox("Użyj danych demonstracyjnych",key="demo")
        upload=st.file_uploader("Eksport CSV",type=["csv"],help="100 MiB / 1 000 000 pozycji")
        raw_preview=(ROOT/"sample_data/pilot_demo.csv").read_bytes() if demo else upload.getvalue() if upload else None
        settings_upload=st.file_uploader("Profil lub sesja JSON",type=["json"],key="settings_upload")
        def restore_document():
            try:
                if settings_upload is None:raise ValueError("Wybierz plik ustawień.")
                document=decode_document(settings_upload.getvalue())
                if document.get("source_sha256"):
                    if raw_preview is None:raise ValueError("Najpierw wybierz oryginalny CSV.")
                    verify_source(document,raw_preview)
                st.session_state.update(profile_state(document["profile"]))
                pending=dict(document.get("settings",{}))
                if "view" in pending:st.session_state["view"]=pending.pop("view")
                st.session_state["pending_settings"]=pending
                pending_hash=hashlib.sha256(raw_preview) if raw_preview is not None else None
                if pending_hash is not None:pending_hash.update(repr(document["profile"]).encode())
                st.session_state["pending_identity"]=pending_hash.hexdigest() if pending_hash is not None else None
                st.session_state["restore_message"]="Ustawienia przywrócone. Wczytaj dane."
                st.session_state.pop("restore_error",None)
            except (ValueError,TypeError,KeyError) as exc:
                st.session_state["restore_error"]=str(exc)
                st.session_state.pop("restore_message",None)
        st.button("Przywróć profil / sesję",key="restore_settings",on_click=restore_document)
        if st.session_state.get("restore_error"):st.error(st.session_state["restore_error"])
        elif st.session_state.get("restore_message"):st.success(st.session_state["restore_message"])
        if st.button("Ustaw profil Kaggle Superstore",key="superstore_profile"):
            st.session_state.update(date_col="Order Date",value_col="Sales",category_col="Sub-Category",
                                    encoding="cp1252",date_format="%m/%d/%Y",currency="XXX",
                                    basis="nieokreślona",precision="strict",delimiter=",",decimal_separator=".",quantity_col="",order_col="",product_col="",customer_col="",cost_col="",profit_col="",quantity_unit="",value_is_sales=False,value_mode="amount")
        if st.button("Ustaw profil Kaggle Online Retail",key="retail_profile"):
            st.session_state.update(date_col="InvoiceDate",value_col="UnitPrice",category_col="Country",
                encoding="cp1252",date_format="%m/%d/%Y %H:%M",currency="XXX",basis="nieokreślona",
                precision="half_up",delimiter=",",decimal_separator=".",quantity_col="Quantity",
                order_col="InvoiceNo",product_col="StockCode",customer_col="CustomerID",cost_col="",
                profit_col="",quantity_unit="szt.",value_is_sales=False,value_mode="unit_price",negative=True)
        headers=[]; sample=[]
        if raw_preview is not None:
            try:
                headers,sample=preview(raw_preview,st.session_state.get("encoding","utf-8-sig"),st.session_state.get("delimiter",","))
                st.caption("Podgląd pierwszych 5 pozycji. Ustaw kodowanie i separator poniżej, jeśli podgląd jest niepoprawny.")
                st.dataframe(sample,hide_index=True)
                suggestion=propose(headers)
                if st.button("Zatwierdź proponowane kolumny",key="accept_mapping"):
                    st.session_state.update({k:v for k,v in suggestion.items() if v or k not in ("date_col","value_col","category_col")})
                    st.session_state["cost_col"]="" if suggestion.get("profit_col") else suggestion.get("cost_col","")
                st.caption("Propozycja: "+", ".join(k.replace("_col","")+" → "+v for k,v in suggestion.items() if v))
            except (ValueError,UnicodeError) as exc:st.caption("Podgląd niedostępny: "+str(exc))
        for field, default in (("date_col","date"),("value_col","value"),("category_col","category")):
            st.session_state.setdefault(field,default)
        def column_choice(label,key,optional=False):
            st.session_state.setdefault(key,"" if optional else headers[0] if headers else "")
            choices=list(dict.fromkeys(([""] if optional else [])+headers+[st.session_state[key]]))
            return st.selectbox(label,choices,key=key,format_func=lambda v:v or "Nie mapuj")
        date_col=column_choice("Kolumna daty","date_col")
        value_col=column_choice("Kolumna kwoty","value_col")
        value_mode=st.selectbox("Znaczenie kolumny kwoty",["amount","unit_price"],key="value_mode",format_func=lambda v:"Wartość całej pozycji" if v=="amount" else "Cena jednostkowa × ilość")
        st.caption("Daty z godziną są grupowane według daty zapisanej w pliku, bez zmiany strefy czasowej.")
        category_col=column_choice("Kolumna kategorii","category_col")
        delimiter=st.selectbox("Separator CSV",[",",";","\t"],key="delimiter")
        encoding=st.selectbox("Kodowanie",ENCODINGS,key="encoding")
        date_format=st.selectbox("Format daty",DATE_FORMATS,key="date_format",help="%m/%d/%Y = miesiąc/dzień/rok; %d/%m/%Y = dzień/miesiąc/rok. Nie zgadujemy kolejności.")
        decimal_separator=st.selectbox("Separator dziesiętny",[".",","],key="decimal_separator")
        currency=st.selectbox("Waluta źródła",CURRENCIES,key="currency",format_func=lambda c:"Nieokreślona (j.p.)" if c=="XXX" else c)
        basis=st.selectbox("Podstawa kwoty",["nieokreślona","netto","brutto"],key="basis")
        precision=st.selectbox("Precyzja kwot",["strict","half_up"],key="precision",
            format_func=lambda p:"Ścisła: maks. 2 miejsca" if p=="strict" else "Zaokrąglaj każdą pozycję HALF_UP do 2 miejsc")
        if precision=="half_up":st.caption("Jawna zmiana kwot wejściowych. Liczbę zmian i wpływ na sumę pokażemy po imporcie.")
        negative=st.checkbox("Dopuszczam kwoty ujemne",key="negative")
        with st.expander("Dodatkowe kolumny i znaczenie danych"):
            st.caption("Koszt / zysk to kwota całej pozycji w tej samej walucie i podstawie co wartość. Wybierz koszt ALBO zysk.")
            optional={key:column_choice(label,key,True) for key,label in [
                ("quantity_col","Ilość"),("order_col","Identyfikator dokumentu (np. faktury)"),("product_col","Produkt / ID"),
                ("customer_col","Klient / ID"),("cost_col","Koszt pozycji"),("profit_col","Zysk pozycji")]}
            quantity_unit=st.text_input("Wspólna jednostka ilości (np. szt.)",key="quantity_unit")
            value_is_sales=st.checkbox("Potwierdzam: kwota oznacza wartość sprzedaży; koszt/zysk ma zgodną podstawę",key="value_is_sales")

        load=st.button("Wczytaj dane",type="primary",key="load")
profile=CsvProfile(date_col,value_col,category_col,delimiter,encoding,date_format,decimal_separator,negative,currency=currency,amount_basis=basis,amount_precision=precision,**optional,quantity_unit=quantity_unit,value_is_sales=value_is_sales,value_mode=value_mode)
raw=(ROOT/"sample_data/pilot_demo.csv").read_bytes() if demo else upload.getvalue() if upload else None
source_hash=hashlib.sha256(raw) if raw is not None else None
if source_hash is not None:source_hash.update(repr(profile).encode())
identity=source_hash.hexdigest() if source_hash is not None else None
if st.session_state.get("source_identity")!=identity:
    st.session_state.pop("import_error",None)
    st.session_state.pop("advanced_problems_page",None)
    st.session_state.pop("advanced_optional_problems_page",None)
    for key in ("parsed","pdf","pptx","filter_identity","start","end","categories","coverage_start","coverage_end","product_filter","customer_filter","analysis_key","analysis_result","model_key","dashboard_model","details_open"):
        st.session_state.pop(key,None)
    st.session_state.update(coverage_start="",coverage_end="",all_categories=True,categories=[],product_filter=[],customer_filter=[])
    st.session_state["source_identity"]=identity
if "pending_settings" in st.session_state and st.session_state.get("pending_identity")!=identity:
    st.session_state.pop("pending_settings",None)
    st.session_state.pop("pending_identity",None)
with st.sidebar:
    st.download_button("Zapisz profil",json.dumps(profile.to_dict(),ensure_ascii=False,indent=2).encode("utf-8"),file_name="AutoReport-profil.json",mime="application/json")

if load and "parsed" in st.session_state:
    st.info("Ten plik i profil są już wczytane. Możesz zmienić filtry bez ponownego importu.")
if load and "parsed" not in st.session_state:
    st.session_state.pop("import_error",None)
    st.session_state.pop("advanced_problems_page",None)
    import_status=None
    for key in ("parsed","pdf","pptx"):st.session_state.pop(key,None)
    try:
        if raw is None:raise ValueError("Wybierz CSV.")
        started=time.perf_counter()
        with st.status("Sprawdzam CSV. Duży plik może wymagać kilkudziesięciu sekund.",expanded=True) as import_status:
            counter=st.empty()
            st.session_state["parsed"]=load_csv(raw,profile,progress=lambda n:counter.write(f"Sprawdzono {n:,} pozycji."))
            counter.write(f"Sprawdzono {len(st.session_state['parsed'].rows):,} pozycji w {time.perf_counter()-started:.1f} s.")
            import_status.update(label="Import zakończony",state="complete",expanded=False)
        st.success("Dane sprawdzone. Dashboard gotowy.")
    except (ValueError,OSError) as exc:
        if import_status is not None:import_status.update(label="Import zablokowany — sprawdź błędy poniżej",state="error",expanded=False)
        st.session_state["import_error"]=dict(message=str(exc),quality=getattr(exc,"quality",{}))
if "import_error" in st.session_state:
    failure=st.session_state["import_error"]
    st.error("Import zablokowany — dane wymagają poprawy." if failure["quality"].get("issues") else failure["message"])
    render_diagnostics(failure["quality"],key="advanced_problems")
st.title(selected_view)
if "parsed" not in st.session_state:
    st.info("Wczytaj CSV lub dane demonstracyjne w panelu „Dane i konfiguracja”.")
    st.stop()
parsed=st.session_state["parsed"]
if parsed.quality.get("warnings"):
    with st.expander("Braki w danych dodatkowych — sprawdź ograniczenia raportu"):
        render_diagnostics(parsed.quality,key="advanced_optional_problems")
# Apply restored widget values only when their widgets will render.
# Streamlit can discard values belonging to widgets hidden by st.stop().
if "pending_settings" in st.session_state:
    st.session_state.update(st.session_state.pop("pending_settings"))
    st.session_state.pop("pending_identity",None)
a,b=select_reporting_period(max(r["event_date"] for r in parsed.rows),7)
st.session_state.setdefault("start",a);st.session_state.setdefault("end",b)
options=sorted({r["category"] for r in parsed.rows})
def quick_range(days=None,year=False):
    from datetime import date
    maximum=max(r["event_date"] for r in parsed.rows)
    if year:st.session_state["start"]=maximum[:4]+"-01-01";st.session_state["end"]=maximum
    else:st.session_state["start"],st.session_state["end"]=select_reporting_period(maximum,days)
quick=st.columns(4)
for box,days in zip(quick[:3],(7,30,90)):
    box.button(f"Ostatnie {days} dni danych",on_click=quick_range,args=(days,))
quick[3].button("Rok do ostatniej daty",on_click=quick_range,kwargs={"year":True})
presentation_mode=st.checkbox("Tryb prezentacyjny",key="presentation_mode")
if presentation_mode:
    st.markdown("<style>[data-testid='stSidebar']{display:none}.block-container{max-width:1800px}</style>",unsafe_allow_html=True)
with st.container(border=True):
    c1,c2,c3,c4=st.columns([1,1,1.6,1])
    start=c1.text_input("Okres od (RRRR-MM-DD)",key="start")
    end=c2.text_input("Okres do (RRRR-MM-DD)",key="end")
    st.session_state.setdefault("all_categories",True)
    all_categories=c3.checkbox("Wszystkie kategorie",value=True,key="all_categories")
    categories=None if all_categories else c3.multiselect("Kategorie",options,key="categories")
    grouping=c4.selectbox("Grupowanie",["Dzień","Tydzień","Miesiąc"],key="grouping")
comparison_mode=st.selectbox("Porównanie",["Poprzedni okres","Rok do roku"],key="comparison_mode")
entity_filters={}
for field,label in (("product","Produkty"),("customer","Klienci")):
    choices=sorted({r[field] for r in parsed.rows if r.get(field) is not None})
    if choices:
        key=field+"_filter"
        st.session_state[key]=[x for x in st.session_state.get(key,[]) if x in choices]
        entity_filters[field]=st.multiselect(label+" (puste = wszystkie)",choices,key=key) or None
    else:entity_filters[field]=None
with st.sidebar,st.expander("Kompletność eksportu i porównanie"):
    st.caption("Potwierdź zakres u źródła. Daty pozycji nie dowodzą kompletności.")
    coverage_start=st.text_input("Pełny eksport od",key="coverage_start")
    coverage_end=st.text_input("Pełny eksport do",key="coverage_end")
filters=(identity,start,end,None if categories is None else tuple(categories),coverage_start,coverage_end,grouping,comparison_mode,tuple(entity_filters["product"] or []),tuple(entity_filters["customer"] or []))
if st.session_state.get("filter_identity")!=filters:
    st.session_state.pop("pdf",None);st.session_state.pop("pptx",None)
    st.session_state["filter_identity"]=filters
try:
    if st.session_state.get("analysis_key")!=filters:
        st.session_state["analysis_result"]=analyze_parsed(parsed,profile=profile,start_date=start,end_date=end,categories=categories,
                          coverage_start=coverage_start or None,coverage_end=coverage_end or None,comparison_mode=comparison_mode,products=entity_filters["product"],customers=entity_filters["customer"])
        st.session_state["analysis_key"]=filters
    result=st.session_state["analysis_result"]
except (ValueError,OverflowError) as exc:
    st.error(str(exc));st.stop()
q=result["quality"];comparison=result["comparison"]
unit=currency_label(profile)
status=("DEMO · " if demo else "")+unit+" / "+basis+" · "+str(q["total_rows"])+" rekordów źródła"
st.caption(status+" · "+("Porównanie: pełny zakres zadeklarowany" if comparison["baseline_available"] else "⚠ "+comparison["reason"]))
if comparison["baseline_available"]:st.caption("Poprzedni okres: "+comparison["previous"]["start_date"]+" / "+comparison["previous"]["end_date"])
if currency=="XXX":st.warning("Waluta źródła niepotwierdzona. j.p. = jednostki pieniężne źródła. Nie przeliczamy walut.")
if q.get("rounded_rows",0):
    st.warning(f"HALF_UP do 2 miejsc: zmieniono {q['rounded_rows']} pozycji źródła; wpływ na sumę {q['rounding_delta']} {unit}. W widoku: {q['view_rounded_rows']} pozycji; wpływ {q['view_rounding_delta']} {unit}.")
if basis=="nieokreślona":st.caption("⚠ Nie określono netto/brutto. Suma nie jest automatycznie miarą przychodu.")
if result["status"]=="empty":
    st.info("Brak pozycji po filtrach. Liczba: 0. Średnia i porównania: N/A. Eksport zablokowany.");st.stop()
view=VIEW_NAMES.index(selected_view)
if st.session_state.get("model_key")!=filters:
    st.session_state["dashboard_model"]=make_model(result,grouping)
    st.session_state["model_key"]=filters
model=st.session_state["dashboard_model"]
st.caption("Zakres widoku i eksportu: "+start+" – "+end+" / "+scope_text(result))
def clear_entity_filters():
    st.session_state["product_filter"]=[]
    st.session_state["customer_filter"]=[]
    st.session_state["all_categories"]=True
    st.session_state["details_open"]=False
st.button("Usuń filtry kategorii, produktów i klientów",on_click=clear_entity_filters,key="clear_entity_filters")
render_view(result,model,view)
if view!=0:render_business(result,view)
with st.expander("Definicje wskaźników i porównania"):
    st.markdown("""
- **Wartość pozycji:** suma kwot po filtrach, z uwzględnieniem wartości ujemnych.
- **Liczba pozycji:** liczba wierszy CSV po filtrach; nie liczba zamówień.
- **Średnia pozycji:** suma / liczba pozycji. Pusty zakres nie ma średniej.
- **Zmiana:** bieżący wynik minus poprzedni. Procent wymaga dodatniej bazy.
- **Poprzedni okres:** taka sama liczba dni bezpośrednio przed bieżącym; ten sam filtr kategorii.
- **Tygodnie:** poniedziałek–niedziela, przycięte do zakresu. Poprzednie dane wyrównujemy według kolejnych dni okresu.
- **N/A:** brak podstaw do obliczenia. Deklaracja pełnego eksportu nie jest automatycznie weryfikowana.
- **Powtórzenie:** identyczna data, kwota i kategoria po normalizacji; pozostaje w sumie.
""")
with st.expander("Szczegóły i wybór kategorii",expanded=st.session_state.get("details_open",False)):
    focus=st.selectbox("Przejdź do szczegółów kategorii",options,key="focus")
    def focus_category():
        st.session_state["all_categories"]=False
        st.session_state["categories"]=[st.session_state["focus"]]
    st.button("Zastosuj kategorię do całego dashboardu",on_click=focus_category,key="focus_apply")
    def reset_categories():
        st.session_state["all_categories"]=True
    st.button("Przywróć wszystkie kategorie",on_click=reset_categories,key="reset_categories")
    page=st.number_input("Strona tabeli (100 pozycji)",1,max(1,(len(result["rows"])+99)//100),1)
    for note in result["notes"]:st.caption(note)
    st.caption("SHA-256: "+result["source_sha256"])
    st.caption("Wiersz źródła pozwala odnaleźć pozycję w CSV. Szczegóły produktu/klienta poniżej.")
    details=[]
    for row in result["rows"][(page-1)*100:page*100]:
        item={"Wiersz CSV":row.get("source_line"),"Data":row["event_date"],"Kategoria":row["category"],"Wartość · "+unit:money(Decimal(row["value_minor"])/100)}
        for key,label in (("product","Produkt"),("customer","Klient"),("order_id","Dokument"),("quantity","Ilość")):
            if key in row:item[label]=str(row[key]) if row[key] is not None else "N/A"
        for key,label in (("cost_minor","Koszt pozycji"),("profit_minor","Zysk pozycji")):
            if key in row:item[label+" · "+unit]=money(Decimal(row[key])/100) if row[key] is not None else "N/A"
        details.append(item)
    st.dataframe(details,hide_index=True,width="stretch")
with st.sidebar:
    st.download_button("Zapisz sesję",encode_session(raw,profile,st.session_state),file_name="AutoReport-sesja.json",mime="application/json")
    st.caption("Sesja zapisuje filtry, profil i komentarze. Zachowaj CSV osobno; przywracanie sprawdza zgodność pliku.")

with st.sidebar:
    st.subheader("Eksport")
    st.caption(start+" – "+end+" / "+unit+" / "+basis)
    st.caption(scope_text(result))
    scope=st.selectbox("Slajdy",["Wszystkie trzy","Bieżący dashboard"],key="pptx_scope")
    export_title=st.text_input("Tytuł prezentacji (opcjonalnie)",max_chars=45,key="pptx_title")
    comment=st.text_area("Komentarz (opcjonalnie)",max_chars=160,key="pptx_comment")
    style=st.selectbox("Układ prezentacji",["Dashboardy","Edytowalne wykresy"],key="pptx_style")
    dimension=st.selectbox("Wymiar wykresu zmiany",["category"]+list(result.get("dimensions",{})),format_func=lambda v:{"category":"Kategorie","product":"Produkty","customer":"Klienci"}[v],key="export_dimension")
    export_identity=(filters,style,dimension,scope,view if scope=="Bieżący dashboard" else None,export_title,comment)
    if st.session_state.get("pptx_identity")!=export_identity:
        st.session_state.pop("pptx",None)
        st.session_state["pptx_identity"]=export_identity
    if st.button("Przygotuj PowerPoint",type="primary",key="export_pptx"):
        try:
            with st.spinner("Przygotowuję slajdy…"):
                if style=="Edytowalne wykresy":
                    from app.editable_presentation import export_editable
                    data=export_editable(result,(view,) if scope=="Bieżący dashboard" else (0,1,2),grouping=grouping,title=export_title,comment=comment,dimension=dimension)
                else:
                    data=export_pptx(result,(view,) if scope=="Bieżący dashboard" else (0,1,2),
                                  grouping=grouping,title=export_title,comment=comment)
                st.session_state["pptx"]=data
            st.success("Prezentacja gotowa.")
        except (ValueError,OSError,RuntimeError) as exc:st.error(str(exc))
    if "pptx" in st.session_state:
        st.download_button("Pobierz PowerPoint",st.session_state["pptx"],file_name="AutoReport-"+start+"-"+end+".pptx",
                           mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
    st.caption("Dashboardy: wykresy jako obrazy. Edytowalne wykresy: jeden duży wykres na slajd z osadzonymi danymi. Pełne filtry w notatkach.")
    if st.button("Przygotuj PDF z aktualnych filtrów",key="export"):
        try:
            path=Path(export_analysis(result))
            st.session_state["pdf"]={"bytes":path.read_bytes(),"name":"AutoReport-"+path.parent.name+".pdf"}
            st.success("PDF gotowy.")
        except (ValueError,OSError,RuntimeError) as exc:st.error(str(exc))
    if "pdf" in st.session_state:
        st.download_button("Pobierz PDF",st.session_state["pdf"]["bytes"],file_name=st.session_state["pdf"]["name"],mime="application/pdf")
