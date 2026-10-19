"""Guided entry point. Uses exactly the same validation, analysis and exports."""
import hashlib
import json
import runpy
import sys
import tempfile
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import streamlit as st
from app.simple_import import inspect_source, date_candidates, DATE_LABELS, error_help
from app.validation import CsvProfile, load_csv, currency_label, ENCODINGS
from app.workspace import decode_document, verify_source
from app.analysis import analyze_parsed, earliest_reporting_date
from app.dashboard_model import make_model, VIEW_NAMES
from app.pipeline import export_analysis
from app.profile_library import recall, remember
from interfaces.dashboard_views import render_view
from interfaces.import_feedback import render_diagnostics

def find_remembered(raw):
    # ASCII-only samples fit several encodings. Reuse a unique saved match,
    # rather than losing Windows settings when a later file has no accents.
    matches = []
    for encoding in ENCODINGS:
        try:
            detected = inspect_source(raw, encoding=encoding)
        except (ValueError, UnicodeError):
            continue
        candidate = recall(detected["headers"], encoding, detected["delimiter"])
        if candidate is not None:
            matches.append(candidate)
    if len(matches) > 1:
        raise ValueError("Do tego układu pasuje kilka zapisanych konfiguracji. Wybierz ustawienia dla właściwego eksportu.")
    return matches[0] if matches else None

def apply_profile(restored):
    st.session_state["easy_profile"] = restored
    st.session_state.update({"easy_config_" + key: getattr(restored, key)
        for key in ("date_col", "value_col", "category_col", "encoding", "delimiter", "currency")})
    st.session_state.update(easy_config_date=restored.date_format,
        easy_config_meaning=restored.value_mode, easy_config_quantity=restored.quantity_col,
        easy_config_unit=restored.quantity_unit, easy_config_decimal=restored.decimal_separator,
        easy_config_basis=restored.amount_basis, easy_config_negative=restored.allow_negative,
        easy_config_rounding=restored.amount_precision == "half_up")

st.set_page_config(page_title="Auto-Report — zrób raport", page_icon="📊", layout="wide")
mode = st.sidebar.radio("Sposób obsługi", ["Prosty — jeden przycisk", "Zaawansowany"], key="ui_mode")
if mode == "Zaawansowany":
    runpy.run_path(str(ROOT / "interfaces/streamlit_app.py"), run_name="__main__")
    st.stop()

st.markdown("""<style>
.block-container{max-width:1150px;padding-top:2rem}
[data-testid="stMetric"]{background:#edf5f7;border-radius:10px;padding:15px}
[data-testid="stAppDeployButton"]{display:none}
</style>""", unsafe_allow_html=True)
st.title("Wybierz CSV. Kliknij. Gotowe.")
st.caption("Raport pojawi się tutaj. PDF do pobrania przygotujemy automatycznie.")
st.sidebar.info("Dane są przetwarzane na tym komputerze. Nie musisz znać Excela ani programowania.")
with st.expander("Plik i ustawienia", expanded="easy_parsed" not in st.session_state):
    demo = st.checkbox("Chcę najpierw wypróbować program na przykładzie", key="easy_demo")
    upload = st.file_uploader("Wybierz plik CSV z komputera", type=["csv"], key="easy_upload")
    st.caption("Kliknij „Upload” / „Browse files”, aby wybrać plik. CSV to plik z tabelą: w swoim programie szukaj „Eksport” → „CSV”.")
    raw = (ROOT / "sample_data/pilot_demo.csv").read_bytes() if demo else upload.getvalue() if upload else None
    if raw is None:
        st.info("Zacznij od wybrania pliku albo zaznacz przykład powyżej. Potem pokażemy kolejny krok.")
        for key in ("easy_parsed", "easy_pdf", "easy_result", "easy_loaded"):
            st.session_state.pop(key, None)
        st.stop()
    source = hashlib.sha256(raw).hexdigest()
    if st.session_state.get("easy_source") != source:
        # Clear all source-dependent widget state as well as downloadable results.
        for key in list(st.session_state):
            if key.startswith("easy_") and key not in ("easy_demo", "easy_upload", "easy_saved_profile"):
                del st.session_state[key]
        st.session_state["easy_source"] = source
        st.session_state.update(easy_config_encoding=None, easy_config_delimiter=None,
            easy_config_currency="PLN" if demo else "XXX", easy_config_meaning="amount" if demo else "",
            easy_config_basis="nieokreślona", easy_config_negative=False, easy_config_rounding=False,
            easy_config_quantity="", easy_config_unit="")
        st.session_state["easy_reset_suggestions"] = True
        try:
            previous = CsvProfile() if demo else find_remembered(raw)
            if previous is not None:
                apply_profile(previous)
                st.session_state["easy_auto_profile"] = True
                st.session_state["easy_reset_suggestions"] = False
        except (ValueError, OSError, UnicodeError) as exc:
            st.session_state["easy_recall_note"] = str(exc)
    reset_suggestions = st.session_state.pop("easy_reset_suggestions", False)
    if st.session_state.get("easy_auto_profile"):
        if not demo:
            st.caption("Zapamiętany układ kolumn. Użyj go dla tego samego eksportu. Jeśli zmieniło się znaczenie kwot lub waluta, otwórz ustawienia poniżej.")
    else:
        st.info("Ten układ pliku wymaga pierwszej konfiguracji. Ustaw go raz — kolejne pliki o takim samym układzie odczytamy z zapamiętanymi ustawieniami.")
    if st.session_state.get("easy_recall_note"):
        st.caption("Nie zastosowano zapisanych ustawień: " + st.session_state["easy_recall_note"])

    with st.expander("Ustawienia pliku — tylko za pierwszym razem lub przy zmianie eksportu", expanded=not st.session_state.get("easy_auto_profile") and "easy_parsed" not in st.session_state):
        with st.expander("Mam zapisane ustawienia z poprzedniego raportu"):
            saved = st.file_uploader("Wybierz zapisane ustawienia JSON", type=["json"], key="easy_saved_profile")
            if st.button("Zastosuj zapisane ustawienia", key="easy_restore"):
                try:
                    if saved is None:
                        raise ValueError("Najpierw wybierz plik ustawień.")
                    document = decode_document(saved.getvalue())
                    verify_source(document, raw)
                    apply_profile(document["profile"])
                    reset_suggestions = False
                    st.success("Ustawienia zastosowane. Kliknij „Utwórz raport” pod ustawieniami.")
                except (ValueError, TypeError, KeyError) as exc:
                    st.error(str(exc))
        base = st.session_state.get("easy_profile")
        with st.expander("Popraw odczyt pliku — gdy litery lub kolumny wyglądają źle"):
            enc = st.selectbox("Sposób odczytania liter", [None, *ENCODINGS],
                index=([None, *ENCODINGS].index(base.encoding) if base else 0), key="easy_config_encoding",
                format_func=lambda v: {None:"Rozpoznaj automatycznie", "utf-8-sig":"UTF-8 — standardowy", "cp1250":"Windows — polskie litery", "cp1252":"Windows — zachodnioeuropejskie litery"}[v])
            sep = st.selectbox("Co rozdziela kolumny w pliku?", [None, ",", ";", "\t"],
                index=([None, ",", ";", "\t"].index(base.delimiter) if base else 0), key="easy_config_delimiter",
                format_func=lambda v: {None:"Rozpoznaj automatycznie", ",":"Przecinek", ";":"Średnik", "\t":"Tabulator"}[v])
        try:
            preview = inspect_source(raw, enc, sep)
        except (ValueError, UnicodeError) as exc:
            st.error("Nie udało się odczytać pliku. " + str(exc))
            for key in ("easy_loaded", "easy_parsed", "easy_pdf", "easy_result"):
                st.session_state.pop(key, None)
            render_diagnostics(getattr(exc, "quality", {}), key="easy_preview_problems")
            st.stop()
        st.dataframe(preview["rows"][:5], hide_index=True, width="stretch")
        st.caption("To pierwsze 5 wierszy. Cały plik sprawdzimy przed pokazaniem raportu.")
        if preview["uncertain_encoding"]:
            st.warning("Zaproponowano polskie kodowanie Windows. Sprawdź litery w tabeli; jeśli są przekręcone, popraw sposób odczytania liter powyżej.")
        headers = preview["headers"]
        cols = st.columns(3)
        mapped = {}
        for box, field, label in zip(cols, ("date_col", "value_col", "category_col"), ("Gdzie jest data?", "Gdzie jest kwota?", "Gdzie jest kategoria?")):
            suggested = getattr(base, field) if base else preview["mapping"].get(field, "")
            choices = ["", *headers]
            if reset_suggestions:
                st.session_state["easy_config_" + field] = suggested if suggested in choices else ""
            mapped[field] = box.selectbox(label, choices, index=choices.index(suggested) if suggested in choices else 0,
                format_func=lambda v: v or "Wybierz kolumnę…", key="easy_config_" + field)
        if not all(mapped.values()):
            st.info("Wybierz trzy kolumny powyżej. Kategoria to np. grupa towaru, dział lub kraj. Jeśli nie wiesz, co oznaczają kolumny, zapytaj osobę przygotowującą eksport.")
            st.session_state.pop("easy_pdf", None)
            st.stop()
        candidates = date_candidates(preview["rows"], mapped["date_col"])
        date_options = [None, *DATE_LABELS]
        suggested_date = base.date_format if base else candidates[0] if len(candidates) == 1 else None
        if reset_suggestions:
            st.session_state["easy_config_date"] = suggested_date
        fmt = st.selectbox("Jak zapisano daty? Wybierz pasujący przykład", date_options,
            index=date_options.index(suggested_date), key="easy_config_date",
            format_func=lambda v: DATE_LABELS.get(v, "Wybierz kolejność dnia i miesiąca…"))
        if fmt is None:
            st.warning("Nie można bezpiecznie rozpoznać daty. Na przykład 03/04/2026 może oznaczać 3 kwietnia albo 4 marca. Wybierz właściwy zapis powyżej.")
        currency = st.selectbox("W jakiej walucie są wszystkie kwoty?", ["XXX", "PLN", "EUR", "USD", "GBP"],
            index=["XXX", "PLN", "EUR", "USD", "GBP"].index(base.currency if base else "PLN" if demo else "XXX"),
            key="easy_config_currency", format_func=lambda v: "Nie wiem — raport bez określonej waluty" if v == "XXX" else v)
        st.caption("Program nie przelicza walut. Jeśli plik miesza waluty, wyeksportuj każdą osobno.")
        meaning = st.selectbox("Co oznacza kwota w jednym wierszu?", ["", "amount", "unit_price"],
            index=["", "amount", "unit_price"].index(base.value_mode if base else "amount" if demo else ""), key="easy_config_meaning",
            format_func=lambda v: {"":"Wybierz znaczenie kwoty…", "amount":"Wartość całej pozycji", "unit_price":"Cena jednej sztuki — trzeba pomnożyć przez ilość"}[v])
        quantity = base.quantity_col if base else ""
        quantity_unit = base.quantity_unit if base else ""
        if meaning == "unit_price":
            quantity = st.selectbox("Gdzie jest ilość?", ["", *headers], index=(["", *headers].index(quantity) if quantity in headers else 0),
                key="easy_config_quantity", format_func=lambda v: v or "Wybierz kolumnę…")
            quantity_unit = st.text_input("Jednostka ilości, np. szt. albo kg", value=quantity_unit, key="easy_config_unit")
        values = [r[mapped["value_col"]] for r in preview["rows"]]
        decimal = base.decimal_separator if base else "," if any("," in v for v in values) and not any("." in v for v in values) else "."
        if reset_suggestions:
            st.session_state["easy_config_decimal"] = decimal
        with st.expander("Dodatkowe ustawienia kwot i zwrotów"):
            decimal = st.selectbox("Zapis części groszowej", [".", ","], index=[".", ","].index(decimal), key="easy_config_decimal",
                format_func=lambda v: "123,45 — przecinek" if v == "," else "123.45 — kropka")
            basis = st.selectbox("Kwoty netto czy brutto?", ["nieokreślona", "netto", "brutto"],
                index=["nieokreślona", "netto", "brutto"].index(base.amount_basis if base else "nieokreślona"), key="easy_config_basis")
            negative = st.checkbox("Kwoty ujemne są prawidłowe, np. zwroty", value=base.allow_negative if base else False, key="easy_config_negative")
            rounding = st.checkbox("Zgadzam się na zaokrąglanie każdej pozycji do 2 miejsc po przecinku", value=base.amount_precision == "half_up" if base else False, key="easy_config_rounding")
            st.caption("Bez tej zgody zbyt dokładne kwoty zatrzymają import. Wpływ zaokrąglania będzie widoczny w raporcie.")
        profile = replace(base or CsvProfile(currency="XXX"), **mapped, encoding=preview["encoding"], delimiter=preview["delimiter"],
            date_format=fmt or "%Y-%m-%d", decimal_separator=decimal, currency=currency, amount_basis=basis,
            value_mode=meaning or "amount", quantity_col=quantity, quantity_unit=quantity_unit,
            allow_negative=negative, amount_precision="half_up" if rounding else "strict")
        identity = (source, repr(profile), fmt, meaning)
        if st.session_state.get("easy_loaded") != identity:
            for key in ("easy_parsed", "easy_pdf", "easy_result"):
                st.session_state.pop(key, None)
        if st.session_state.get("easy_attempted_identity") != identity:
            st.session_state.pop("easy_import_error", None)
            st.session_state.pop("easy_problems_page", None)
            st.session_state.pop("easy_optional_problems_page", None)
        remember_settings = st.checkbox("Zapamiętaj ustawienia tego układu kolumn na tym komputerze", value=True, key="easy_remember")
        st.caption("Zapamiętujemy ustawienia, bez danych z CSV. Dotyczy także następnego uruchomienia programu.")
    st.caption(f"Raport: {currency_label(profile)} · {profile.amount_basis} · "
        + ("cena × ilość" if profile.value_mode == "unit_price" else "wartość całej pozycji"))
    if st.button("Utwórz raport", type="primary", disabled=fmt is None or not meaning, key="easy_load"):
        st.session_state["easy_attempted_identity"] = identity
        for key in ("easy_import_error", "easy_parsed", "easy_pdf", "easy_result", "easy_problems_page"):
            st.session_state.pop(key, None)
        try:
            with st.spinner("Sprawdzam plik i przygotowuję raport…"):
                st.session_state["easy_parsed"] = load_csv(raw, profile)
                st.session_state["easy_loaded"] = identity
                if remember_settings and not demo:
                    try:
                        remember(headers, profile)
                        st.session_state["easy_save_note"] = "Ustawienia zapamiętane. Następnym razem wybierz CSV i kliknij „Utwórz raport”."
                    except (OSError, ValueError) as exc:
                        st.session_state["easy_save_note"] = "Raport jest dostępny, ale nie udało się zapamiętać ustawień: " + str(exc)
            st.rerun()
        except (ValueError, OSError) as exc:
            st.session_state["easy_import_error"] = dict(message=str(exc), help=error_help(exc), quality=getattr(exc, "quality", {}))
    if "easy_import_error" in st.session_state:
        failure = st.session_state["easy_import_error"]
        st.error("Nie przygotowaliśmy raportu, ponieważ dane wymagają poprawy.")
        st.info(failure["help"])
        if not failure["quality"].get("issues"):
            st.write(failure["message"])
        render_diagnostics(failure["quality"], key="easy_problems")
        st.stop()
    if "easy_parsed" not in st.session_state:
        st.stop()
parsed = st.session_state["easy_parsed"]
st.caption(f"Plik sprawdzony: {len(parsed.rows):,} pozycji.")
if parsed.quality.get("warnings"):
    with st.expander("Braki w danych dodatkowych — sprawdź ograniczenia raportu"):
        render_diagnostics(parsed.quality, key="easy_optional_problems")
with st.sidebar, st.expander("Zapamiętane ustawienia"):
    if st.session_state.get("easy_save_note"):
        st.caption(st.session_state["easy_save_note"])
    st.download_button("Zapisz ustawienia do kolejnych plików", json.dumps(profile.to_dict(), ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="AutoReport-ustawienia.json", mime="application/json")
st.subheader("Twój raport")
maximum = date.fromisoformat(max(r["event_date"] for r in parsed.rows))
minimum = date.fromisoformat(min(r["event_date"] for r in parsed.rows))
with st.expander("Zmień okres raportu (opcjonalnie)", expanded=minimum < earliest_reporting_date(maximum)):
    period = st.radio("Za jaki okres?", ["Cały plik", "Ostatnie 7 dni w pliku", "Ostatnie 30 dni w pliku", "Ostatnie 5 lat w pliku", "Wybieram daty"], horizontal=True, key="easy_period")
    st.caption("Maksymalnie 5 lat kalendarzowych od końca wybranego okresu, również dla danych historycznych.")
    if period == "Wybieram daty":
        left, right = st.columns(2)
        start = left.date_input("Od dnia", value=max(minimum, maximum-timedelta(days=6)), key="easy_start")
        end = right.date_input("Do dnia", value=maximum, key="easy_end")
    else:
        end = maximum
        start = minimum if period == "Cały plik" else earliest_reporting_date(maximum) if "5 lat" in period else maximum-timedelta(days=29 if "30" in period else 6)
st.caption(f"Raport obejmie {start:%d.%m.%Y} – {end:%d.%m.%Y}. Ostatnia data w pliku: {maximum:%d.%m.%Y}.")
result_key = (identity, str(start), str(end))
if st.session_state.get("easy_result_key") != result_key:
    st.session_state.pop("easy_pdf", None)
    st.session_state.pop("easy_result", None)
try:
    if "easy_result" not in st.session_state:
        st.session_state["easy_result"] = analyze_parsed(parsed, profile=profile, start_date=str(start), end_date=str(end))
        st.session_state["easy_result_key"] = result_key
    result = st.session_state["easy_result"]
except (ValueError, OverflowError) as exc:
    st.error(str(exc))
    st.info("Wybierz datę końcową nie wcześniejszą od początkowej. Jeden raport może obejmować maksymalnie 5 lat kalendarzowych. Możesz wybrać „Ostatnie 5 lat w pliku”.")
    st.stop()
if not result["rows"]:
    st.info("W tym okresie nie ma pozycji. Wybierz inny zakres dat.")
    st.stop()
if demo:
    st.warning("To dane przykładowe — nie jest to raport Twojej firmy.")
if currency == "XXX":
    st.warning("Waluta nie została określona. „j.p.” oznacza jednostki pieniężne z pliku.")
q = result["quality"]
if q.get("rounded_rows"):
    st.warning(f"Zaokrąglono {q['rounded_rows']} pozycji. Wpływ na sumę pliku: {q['rounding_delta']} {currency_label(profile)}.")
if q.get("duplicate_rows"):
    st.info(f"Podobne pozycje: {q['duplicate_rows']}. Pozostawiono je w sumie — mogą być prawidłowymi transakcjami.")
st.caption("Porównanie z poprzednim okresem wymaga potwierdzenia kompletności eksportu w trybie zaawansowanym. Brak wierszy nie oznacza zerowej sprzedaży.")
if "easy_pdf" not in st.session_state and st.session_state.get("easy_pdf_failed") != result_key:
    try:
        with st.spinner("Przygotowuję raport…"), tempfile.TemporaryDirectory(prefix="auto-report-export-") as folder:
            path = Path(export_analysis(result, output_dir=folder))
            st.session_state["easy_pdf"] = path.read_bytes()
    except (ValueError, OSError, RuntimeError) as exc:
        st.session_state["easy_pdf_failed"] = result_key
        st.error("Nie udało się przygotować PDF. " + str(exc))
if st.session_state.get("easy_pdf_failed") == result_key and "easy_pdf" not in st.session_state:
    st.warning("Raport ekranowy jest dostępny. Pobranie PDF wymaga ponowienia.")
    if st.button("Ponów przygotowanie PDF", key="easy_export"):
        st.session_state.pop("easy_pdf_failed", None)
        st.rerun()
if "easy_pdf" in st.session_state:
    st.download_button("Pobierz gotowy raport PDF", st.session_state["easy_pdf"],
        file_name=f"AutoReport-{start}-{end}.pdf", mime="application/pdf", type="primary")
view = st.radio("Co chcesz zobaczyć?", VIEW_NAMES, horizontal=True, key="easy_view")
render_view(result, make_model(result), VIEW_NAMES.index(view))
with st.expander("Co oznaczają liczby?"):
    st.write("Suma to wartości pozycji z wybranego okresu. Liczba pozycji oznacza wiersze tabeli, a nie liczbę zamówień. Średnia to suma podzielona przez liczbę pozycji. N/A oznacza brak podstaw do obliczenia.")
    st.write("Prezentację PowerPoint, dodatkowe filtry i porównania znajdziesz w trybie zaawansowanym. Po zmianie trybu wczytaj plik ponownie.")
