# Samodzielna próba Auto-Report
Dane są fikcyjne. Test techniczny jest wykonany; próba użytkownika pozostaje niewykonana.

## Przygotowanie
Uruchom aplikację zgodnie z ANALYST_QUICKSTART.md. Pliki są w folderze internal_acceptance paczki (w repozytorium: sample_data/internal_acceptance).
Zapisuj czas, liczbę podpowiedzi i uwagi w SELF_TEST_OBSERVATIONS.csv. Nie wpisuj wyniku przed wykonaniem zadania.

## Zadania
1. Wczytaj cycle1.csv oraz cycle1.session.json. Przywróć sesję, potem wczytaj dane. Sprawdź okres 07–13.09.2026 i wszystkie trzy widoki.
2. Wskaż produkt z największym spadkiem, przejdź do jego pozycji, a następnie usuń filtry.
3. Przygotuj PDF i trzy slajdy PowerPoint w obu wariantach. Otwórz pliki i sprawdź zakres oraz liczby.
4. Zapisz sesję, odśwież aplikację i odtwórz ją na tym samym CSV.
5. Wczytaj cycle2.csv i cycle2.session.json. Przygotuj następny raport i upewnij się, że poprzedni nadal można otworzyć.
6. Spróbuj przywrócić cycle1.session.json na cycle2.csv. Aplikacja powinna odmówić.
7. Na domyślnym profilu date/value/category sprawdź mixed_valid_invalid.csv. Cały plik powinien zostać zablokowany.
8. Wczytaj polish.csv z polish.profile.json. Sprawdź polskie nazwy i sumę.

## Klucz kontrolny — sprawdź po samodzielnym wykonaniu
| Wynik | Cykl 1 | Cykl 2 |
|---|---:|---:|
| Okres | 07–13.09.2026 | 14–20.09.2026 |
| Wartość PLN | 600 | 700 |
| Poprzedni okres PLN | 300 | 600 |
| Zmiana PLN | +300 | +100 |
| Koszt PLN | 370 | 415 |
| Zysk PLN | 230 | 285 |
| Dokumenty | 2 | 3 |
| Ilość szt. | 12 | 14 |
| Zmiana P1 PLN | +400 | +250 |
| Zmiana P2 PLN | −100 | −150 |

polish.csv: 13,00 PLN, kategorie Żółć i Łączniki.
duplicates.csv: dwie pozycje, 20,00 PLN, jedno powtórzenie. Powtórzenia nie są automatycznie usuwane.
Ujemna pozycja cyklu 2 jest syntetycznym zwrotem. Deklaracja kompletności dotyczy wyłącznie tych sztucznych danych.

## Kryteria przyjęte przed próbą
- Wszystkie kwoty i zakresy zgodne z kluczem.
- Żaden niepoprawny plik nie daje pozornie poprawnego raportu.
- Zmiana źródła usuwa możliwość pobrania starego eksportu z interfejsu.
- Odtworzenie sesji na innym CSV jest blokowane.
- Prezentacja nie wymaga poprawiania liczb ani zakresu.
- Czas i pomoc są mierzone, lecz bez arbitralnej obietnicy oszczędności.
Próba wykonana przez autora nie zastępuje próby niezależnego analityka.

## Pozostałe pliki
empty, headers_only, duplicate_headers, missing_column, extra_field, unclosed_quote, invalid_date, nan, missing_amount, negative_without_rule, excess_precision, missing_category, wrong_encoding i mixed_valid_invalid powinny zostać odrzucone na domyślnym profilu. wrong_encoding jest poprawnym CP1250, lecz celowo nie pasuje do domyślnego UTF-8.
