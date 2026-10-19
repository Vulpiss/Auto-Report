# Audyt punktu startowego — 2026-09-14

Uwaga: historyczny zapis sprzed napraw wersji 0.2.0. Bieżące dowody i pozostałe zadania: IMPLEMENTATION_STATUS.md. Skrypt audit_baseline.py uruchamia teraz regresje zamiast odtwarzania naprawionych błędów.
Rodzaj pracy: audyt techniczny i decyzja produktowa.

## Werdykt
**STOP dla przekazania obecnej wersji jako wiarygodnego narzędzia klientowi.** Kontynuujemy naprawy i badanie problemu. To nie decyzja o porzuceniu projektu.

## Pięć najważniejszych ryzyk
| Priorytet | Potwierdzony dowód | Skutek / następny test |
|---|---|---|
| 1 | validation.py dopuszcza mieszaninę poprawnych i błędnych kwot; transform.py używa CAST. Próba 100 + tekst daje 2 wiersze i średnią 50. | Fałszywa średnia. Błędny rekord ma blokować raport z numerem i powodem. |
| 2 | calculate_pct_change(100, 0) daje 100.0. | Pozorny procent przy zerowym mianowniku. Wprowadzić N/A we wszystkich wyjściach. |
| 3 | Brak daty i brak kwoty w dwóch różnych wierszach na trzy daje szacunek 2 poprawnych zamiast 1. | Diagnostyka zaniża problem. Wspólna maska poprawności i dokładne liczniki. |
| 4 | Jeden rekord wystarcza dla baseline_available; wzrost >20% daje SCALE. Próba z jednym dniem bazy i dwoma dniami bieżącymi daje SCALE. | Kompletność eksportu UNKNOWN. Brak dnia może oznaczać brak sprzedaży albo brak danych; nie wolno tego zgadywać. Opisowa zmiana zamiast zalecenia skalowania. |
| 5 | Właściciel potwierdził brak dostępu do klienta. | Problem, cena i popyt UNKNOWN. Rozmowy i eksport przed rozbudową. |

Pierwsze cztery ryzyka odtworzono skryptem scripts/audit_baseline.py na sztucznych danych i osobnej bazie tymczasowej. Python 3.11.3, pandas 3.0.2. Końcowy przebieg: kod 0, cztery pola risk_reproduced = true. Pierwsza próba diagnostyki miała błąd zamknięcia tymczasowej bazy na Windows; poprawiono skrypt i powtórzono.

## Zakres dowodów
Przeczytano moduły app, oba interfejsy, README, konfigurację, spec PyInstaller i ograniczenia.
POTWIERDZONE: kod CSV → SQLite → KPI → wykresy → PDF, interfejs desktop i Streamlit oraz katalog dystrybucji.
UNKNOWN: działanie EXE na czystym Windows, wizualna jakość PDF, pełny przebieg, duże pliki, poprawność na danych odbiorcy. Nie wykonywano tych testów.
Nie zmieniono kodu produkcyjnego. Reprodukcja błędu nie jest jego naprawą.

## Pipeline i dalsze ustalenia statyczne
| Etap | Stan kodu | Luka |
|---|---|---|
| Import | pd.read_csv z domyślnymi ustawieniami; replace facts_raw przed walidacją | Jawny separator, kodowanie, profil; walidacja przed zapisem |
| Walidacja | Wystarcza co najmniej jedna data i liczba | Poprawność każdego rekordu i skończone kwoty |
| Transformacja | SQLite DATE i CAST; filtr wyłącznie na niepuste źródło daty | Jednoznaczne parsowanie wspólne z diagnostyką |
| Obliczenia | SUM/AVG/COUNT, poprzedni okres tej samej długości | Zerowa baza, kompletność, jednostki, znaczenie wiersza |
| Komentarz | SCALE i opcjonalny placeholder LLM | Opis bez nieuzasadnionych zaleceń |
| PDF | ReportLab, Helvetica, stałe sekcje | Render: polskie znaki, długie etykiety, podziały stron |
| Eksport | Stały outputs/report.pdf i wspólna baza | Unikalny i atomowy zapis; ochrona przed równoległym uruchomieniem |
| Dostarczenie | Spec PyInstaller; zapis obok programu | Powtarzalny build i zwykłe konto bez Pythona |

Dodatkowe obserwacje:
- Streamlit importuje transform zamiast app.transform, zapisuje data/input.csv, ale wywołuje domyślny pipeline z sample_data/input_with_baseline.csv. Wybrane daty nie są przekazywane. Sprawdzić dwoma rozróżnialnymi plikami.
- Desktop pozwala uruchamiać wiele wątków generacji, a baza i ścieżki są wspólne. Ryzyka kolizji nie odtworzono.
- Wyłączony LLM przechodzi przez retry: suma zaprogramowanych opóźnień wynosi 9 sekund. To analiza kodu, nie benchmark.
- README wskazuje nieistniejący entrypoint Streamlit app.py; zależności nie są przypięte.
- Nazwy kolumn są wstawiane bezpośrednio do SQL; wymagają bezpiecznej obsługi.
- Zastano zmodyfikowany .gitignore i nieśledzony Progress auto-report.txt; zachowano je.

## Plan z kryteriami ukończenia
Progi są robocze; kryteria pilota uzgadniamy z odbiorcą przed testem.

| Artefakt | Zależność | Test i mierzalne DoD | Ryzyko |
|---|---|---|---|
| P0: kontrakt, parser i regresje | Dane syntetyczne; później eksport | Daty ISO/PL w jawnych profilach, przecinek, brak, tekst, inf, duplikat, pusty plik. Każdy wiersz jawnie przyjęty lub odrzucony; kwoty zgodne do grosza. | Zgadnięta semantyka |
| P0: porównanie i komentarz | Kontrakt | Baza 0/brak/niepełna, ujemne kwoty, granice dat. Zero zmyślonych procentów i brak SCALE we wszystkich wyjściach. | Interpretacja zwrotów |
| P1: przebieg desktop i zapis | P0 | Dwa pliki, podwójne kliknięcie, błąd generacji. Właściwy plik w raporcie, brak kolizji i uszkodzenia starego wyniku. | Wspólna baza |
| P1: PDF referencyjny | P0 | Render każdej strony; polskie i długie kategorie. Zero ucięć/braków znaków, poprawne sumy, jawny zakres i jednostka. | Nietypowe dane |
| P1: build i instrukcja | Stabilny pipeline | Czysty Windows bez Pythona. Raport bez terminala i pomocy autora; zapis w dostępnym katalogu. | Zależności |
| R0: karty rozmów | Dotarcie do osób | 5 rozmów, minimum 2 podobne powtarzalne problemy i 1 zgoda na eksport/demonstrację. | Brak kupujących |
| R1: próbka klienta | R0 i P0 | Zgodność z jego wzorcem; zero niewyjaśnionych różnic sum. | Brak danych |
| R2: protokół płatnego pilota | R1, stabilny build | Dwa cykle, samodzielne ponowne użycie, uzgodniony wynik i płatność. | Uprzejme zainteresowanie |

Następny ruch techniczny: wspólny parser dat i kwot z testami regresji. Rynkowy: pierwsza rozmowa o rzeczywistym raporcie.
