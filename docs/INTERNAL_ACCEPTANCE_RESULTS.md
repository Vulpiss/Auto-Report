# Kontrola wewnętrzna — 2026-09-28
Werdykt: GO do samodzielnej próby właściciela. Gotowość do sprzedaży pozostaje UNKNOWN.

## Wykonane kontrole
- 94/94 testów unittest przeszło (build/internal-regression-final.log).
- 14 niepoprawnych CSV zablokowanych: puste dane, nagłówki, struktura, data, kwota, precyzja, kodowanie i brak kategorii.
- Poprawne CP1250 z polskimi nazwami daje 13,00 PLN.
- Duplikaty zachowane: dwie pozycje, suma 20,00 PLN, jedno powtórzenie.
- Dwa syntetyczne cykle hurtowni: 600 i 700 PLN, poprzednie okresy 300 i 600 PLN, zysk 230 i 285 PLN.
- Sumy dashboardów, PDF i natywnych wykresów PPTX zgodne z oczekiwaniami.
- Oba warianty PPTX mają po trzy slajdy; natywny wariant zawiera trzy wykresy i trzy osadzone arkusze.
- Cztery prezentacje otwarto w lokalnym PowerPoint; obejrzano 12 slajdów i sześć stron PDF. Bez widocznych ucięć i nakładania treści.
- Powtórne wygenerowanie PDF tworzy osobny raport i zachowuje wcześniejszy. Przejście do drugiego cyklu nie zmienia zapisanych prezentacji.
- Zapis sesji powiązany z CSV; odtworzenie na innym źródle jest blokowane.
- Przeglądarka + nowa paczka EXE: oba cykle, trzy widoki, pobranie PDF/PPTX, odtworzona kompletność, blokada starej sesji i usunięcie przycisków starego eksportu po niepoprawnym imporcie.
- Wartości wszystkich trzech natywnych wykresów z EXE zgodne z eksportami kodu źródłowego w obu cyklach.
- Poprawność składni zmienionych plików sprawdzona.

## Znalezione problemy i poprawki
1. Rzeczywisty błąd sesji: po przywróceniu ustawień przed importem przeglądarka gubiła zakres kompletności. Suma pozostawała poprawna, lecz eksport nie zawierał porównania. Ustawienia są teraz stosowane dopiero po imporcie, kiedy ich kontrolki zostaną wyrenderowane. Oczekujące ustawienia są powiązane ze źródłem i profilem; zmiana któregokolwiek je usuwa.
2. Test AppTest miał domyślny limit 3 sekund, krótszy niż pozostałe testy. Ujednolicono go do 20 sekund. Nie jest to deklaracja czasu uruchomienia produktu.
3. Test przeglądarkowy wymagał jawnego rozwinięcia panelu konfiguracji po eksporcie. Poprawiono scenariusz, nie aplikację.

Istniejący test AppTest nie odtwarzał utraty zakresu. Dowód błędu i skuteczności poprawki pochodzi z porównania eksportów prawdziwej przeglądarki. Rozszerzono asercje odtwarzania sesji oraz dodano regresję zmiany źródła przed importem.

## Dostarczenie
Paczka: AutoReportAnalyst-Windows-2026-09-28-internal-qa.zip.
Zawiera START_HERE.txt, aktualną instrukcję, SELF_TEST.md, pusty arkusz obserwacji i folder internal_acceptance.
Launcher EXE i biblioteki pozostają z wcześniejszej paczki. Zaktualizowano dostarczany jako osobny plik interfejs _internal/interfaces/streamlit_app.py. Taką paczkę uruchomiono i przetestowano.
Skrypt build_analyst.py uwzględnia instrukcje i próbki w kolejnych pełnych buildach.

## Artefakty
- scripts/qa_internal_acceptance.py — generuje próbki i sprawdza liczby oraz eksporty.
- scripts/qa_internal_browser.cjs — scenariusz przeglądarkowy; wymaga lokalnego Playwright/Edge i uruchomionej aplikacji.
- build/internal-acceptance/evidence.json — szczegóły kontroli źródłowych.
- build/internal-acceptance/browser-evidence.json — końcowy test EXE.
- build/internal-acceptance/exe-export-evidence.json — porównanie wykresów EXE.
- build/internal-acceptance/cycle1 i cycle2 — PDF, PPTX, zrzuty i rendery.
- docs/SELF_TEST.md — instrukcja próby bez pomocy autora.

## UNKNOWN / niewykonane
- Czysty Windows: brak dostępnego środowiska Sandbox/VM. Izolowany PATH i ustawienia na obecnym komputerze nie zastępują czystego systemu.
- Samodzielność użytkownika: przygotowano scenariusz, lecz nie ma obserwacji rzeczywistej osoby.
- Rzeczywiste dwa cykle hurtowni, oszczędność czasu, akceptacja ceny i popyt: syntetyczny test ich nie potwierdza.
- Nie powtarzano dużego Kaggle po poprawce cyklu życia sesji; wcześniejsze wyniki wydajności pozostają historycznymi pomiarami.
