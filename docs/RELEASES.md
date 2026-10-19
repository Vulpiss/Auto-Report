# Wersje Auto-Report

Stan: 2026-10-19. Jedno repozytorium zachowuje obie generacje projektu.
Gałąź `main` zawiera bieżący kod; tagi oznaczają konkretne stany historii.

| Obszar | Wersja 1: `v0.1.0` | Wersja 2: `v0.2.0-beta.1` |
|---|---|---|
| Stan kodu | MVP z 21.06.2026, commit `20f3146` | Lokalnie rozwijana aplikacja opublikowana 19.10.2026 |
| Główne wejście | `main.py`, wcześniejszy interfejs desktop | `dashboard_entry.py`, tryb prosty i zaawansowany |
| Import | Podstawowe kolumny `date,value,category` | Jawny profil dat, kwot, separatora, kodowania i waluty |
| Poprawność | Historyczna implementacja, znane ograniczenia | Ścisła walidacja, kwoty w setnych jednostki, niezależne wzorce |
| Diagnostyka | Podstawowe komunikaty | Linia, kolumna, wartość, przyczyna, wskazówka i eksport błędów |
| Wynik | KPI, wykresy i PDF | Trzy dashboardy, PDF i PPTX, także edytowalne wykresy |
| Powtórne użycie | Ręczna konfiguracja | Zapis profilu i ponowne użycie zgodnego formatu |
| Testy | Brak zestawu regresji w tym tagu | 146 testów zaliczonych lokalnie 19.10.2026 |
| Dostarczenie | Kod źródłowy do uruchomienia z Pythonem | Kod i sprawdzona lokalnie paczka Windows ZIP |

## Pobieranie

- [Wersja 2: wydanie testowe](https://github.com/Vulpiss/Auto-Report/releases/tag/v0.2.0-beta.1)
  i [scenariusz próby](TRY_IT.md).
- [Wersja 1: archiwalne MVP](https://github.com/Vulpiss/Auto-Report/releases/tag/v0.1.0)
  i [instrukcja historyczna](LEGACY_MVP.md).

Wersja 1 jest punktem odniesienia do nauki i porównania. Znane ograniczenia
poprawności opisuje [historyczny audyt](BASELINE_AUDIT.md); sprawdzaj ją
wyłącznie na sztucznych danych, w osobnym folderze i środowisku.

Wersja 2 jest publiczną betą. POTWIERDZONE: lokalna regresja, wcześniejsze
kontrole liczb, eksportów i EXE. UNKNOWN: czysty Windows, samodzielność nowej
osoby, przydatność i oszczędność u klienta oraz rentowność wdrożenia.

Tag `v0.1.0` nadano historycznemu stanowi podczas publikacji 19.10.2026;
nie oznacza, że w czerwcu istniało formalne wydanie o tym numerze.
Tag beta obejmuje kod, którego pliki aplikacji odpowiadają sprawdzonemu
runtime z 06.10.2026. Wewnętrzny numer `0.2.0` zachowano bez ponownej kompilacji.
Nowe instrukcje i testy nie zmieniają bajtów istniejącej paczki.
