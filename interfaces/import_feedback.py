"""Shared repair list for the simple and advanced importers."""
import streamlit as st
from app.import_diagnostics import diagnostic_rows, diagnostics_csv


def render_diagnostics(quality, *, key):
    count = sum(len(issue.get("problems", [])) for group in ("issues", "warnings")
                for issue in quality.get(group, []))
    if not count:
        return
    st.subheader("Miejsca do poprawy w danych")
    if quality.get("total_rows"):
        prefix = "Rekordy w pliku" if quality.get("scan_complete") else "Rekordy odczytane przed przerwaniem kontroli"
        st.caption(f"{prefix}: {quality['total_rows']}. Poprawne: {quality['valid_rows']}. "
                   f"Błędne: {quality['invalid_rows']}. Problemów w polach: {count}.")
    if not quality.get("scan_complete", True):
        st.warning("Kontrola nie objęła całego pliku. Popraw wskazany problem odczytu i sprawdź plik ponownie; dalsze rekordy mogą zawierać kolejne błędy.")
    st.caption("Linia CSV to numer linii w pliku tekstowym, z nagłówkiem jako linią 1. "
               "Pole z przejściem do nowej linii może zajmować kilka linii. Wartości pokazujemy do 200 znaków.")
    page_size = 100
    pages = (count + page_size - 1) // page_size
    page = 1
    if pages > 1:
        page = st.number_input("Strona listy problemów", min_value=1, max_value=pages, value=1,
                               step=1, key=key + "_page")
    rows = diagnostic_rows(quality, page_size, (page - 1) * page_size)
    selection = st.dataframe(rows, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row",
                            key=key + "_table_" + str(page), column_config={
        name: st.column_config.TextColumn(width=width) for name, width in
        (("Typ", 75), ("Linia CSV", 90), ("Kolumna", 110), ("Wartość (podgląd)", 135),
         ("Problem", 240), ("Co poprawić", 265))})
    st.caption("Kliknij wiersz tabeli, aby przeczytać pełny opis i wskazówkę poniżej.")
    selected = selection.selection.rows[0] if selection.selection.rows else 0
    item = rows[selected]
    st.text(f"{item['Typ']} · linia CSV: {item['Linia CSV']} · kolumna: {item['Kolumna']}")
    st.write("Problem: " + item["Problem"])
    st.info(item["Co poprawić"])
    st.caption(f"Pokazano {min(page_size, count - (page - 1) * page_size)} z {count} problemów. "
               "Plik do pobrania zawiera wszystkie wykryte problemy, także z pozostałych stron.")
    st.download_button("Pobierz listę miejsc do poprawy (CSV)", diagnostics_csv(quality),
                       file_name="AutoReport-miejsca-do-poprawy.csv", mime="text/csv", key=key + "_download",
                       on_click="ignore")
    st.info("Popraw dane w programie źródłowym lub w kopii CSV. Następnie wybierz poprawiony plik i ponów import. "
            "Program nie zmienia pliku źródłowego ani nie uzupełnia brakujących kwot.")
