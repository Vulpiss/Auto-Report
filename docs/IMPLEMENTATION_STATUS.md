# Aktualny stan — 2026-10-19

Przygotowano aktualizację GitHub w jednym repozytorium: archiwalne MVP
`v0.1.0` oraz bieżące wydanie testowe `v0.2.0-beta.1`. README prowadzi do
pobierania, różnic wersji i scenariusza próby. Wydanie beta zachowuje
niezmieniony runtime z 06.10.2026; 34 skróty plików aplikacji są zgodne
z wcześniejszym dowodem. Ponowna regresja: 146 testów OK. Paczki ZIP
przeszły kontrolę integralności. [Zakres i dowody](GITHUB_RELEASE_2026-10-19.md).

UNKNOWN: czysty Windows, samodzielność nowej osoby, eksport i wynik klienta,
popyt oraz ekonomika wdrożenia. Publikacja nie potwierdza tych elementów.

# Stan wcześniejszy — 2026-10-14

POTWIERDZONE: przygotowano [pakiet pierwszego testu](first-test/START_HERE.md):
konfigurację i instrukcję VM, kontrakt eksportu, kartę rozmowy, próbę użytkownika,
wzorzec liczb, pomiary pilota i kosztów oraz zasady ponowienia pracy.
Na prośbę właściciela przygotowano materiały; nie instalowano VM ani systemu gościa.

Dodano lokalny weryfikator liczb względem oddzielnie przygotowanych oczekiwań.
146 testów kodu przeszło; osiem nowych sprawdza także błędny okres, walutę,
zmienione źródło i niezgodne kategorie przy tej samej sumie ogólnej.
Skrypt Windows sprawdzono na obecnym hoście. Faktyczne wyniki i identyfikatory
artefaktów opisuje [TEST_RESULTS.md](first-test/TEST_RESULTS.md).

Runtime i ZIP aplikacji z 2026-10-06 zachowano bez zmian. Pakiet pierwszego
testu jest osobnym artefaktem, bez ponownej kompilacji EXE i bez publikacji.

UNKNOWN: czysty Windows, ręczna obsługa launchera, samodzielność nowej osoby,
rzeczywisty eksport, rozmowy, wynik i koszt pilota. Właściciel potwierdził brak
ISO/VM i dostępu do pierwszego rzeczywistego procesu. Przygotowane dokumenty
nie podnoszą tych bramek do stanu wykonanego. HIPOTEZA: odbiorca hurtowniany.

# Stan wcześniejszy — 2026-10-06

**POTWIERDZONE:** szablon PDF 4 poprawia oś kwot groszowych, podziały tabel
i długie tytuły. Trzy skrajne przykłady mają po dwie strony; wszystkie sześć
stron wyrenderowano i obejrzano. Naprawiono maskowanie pierwotnego błędu
eksportu przez nieudany zapis diagnostyki. 138 testów przeszło.

Nowe EXE z osobno rozpakowanego ZIP sprawdzono w Edge na 100 tys. i milionie
rekordów (pięć lat, 2 tys. kategorii). Sumy i pobrane PDF są zgodne. Próby
trwały ok. 6 i 55 s na tym komputerze. Przekroczone limity importu odrzucono.
Przerwanie importu/eksportu zachowuje wcześniejszy PDF i źródło; ponowienie działa.

Przypięto zależności kompilacji i przygotowano jedno polecenie testy → build →
kontrola ZIP i rozpakowanego EXE. Bieżące wydanie:
`release/AutoReportAnalyst-Windows-2026-10-06-hardening.zip`.
Dowody, zakres i ograniczenia: [LOCAL_HARDENING_RESULTS.md](LOCAL_HARDENING_RESULTS.md).

**UNKNOWN:** czysty Windows i obsługa launchera przez użytkownika. Sprzęt
obsługuje wirtualizację, ale brak aktywnego hypervisora i znalezionych narzędzi
VM; test nie został wykonany. **HIPOTEZA:** hurtownia jako odbiorca.
Popyt, samodzielność nowego użytkownika i wynik u klienta pozostają UNKNOWN.

# Stan wcześniejszy — 2026-10-04

**POTWIERDZONE: zakres lokalnego portfolio jest domknięty.** Jedno bieżące
wydanie: `release/AutoReportAnalyst-Windows-2026-10-04-portfolio.zip`.
Aktualny README prowadzi do instrukcji, opisu projektu, rzeczywistego nagrania
interfejsu, zrzutów, wzorcowego PDF i protokołu weryfikacji.

129 testów przeszło w nowym środowisku z `requirements-qa.txt`. Kontrola
przeglądarkowa przeszła dla kodu z tego środowiska i EXE rozpakowanego z nowego
ZIP: 2 250,00 PLN dla całego przykładu, 1 250,00 PLN dla tygodnia, błędy w
liniach 10 i 14, blokada PDF oraz usunięcie błędów po poprawnym imporcie.
PDF ma zgodne liczby i dwie wyrenderowane, obejrzane strony. MP4 trwa 41,76 s.
CRC ZIP oraz skróty EXE i materiałów są zgodne.

Materiały i zakres: [portfolio/VERIFICATION.md](portfolio/VERIFICATION.md),
[opis projektu](portfolio/CASE_STUDY.md), [demonstracja](portfolio/DEMO.md).
Wydanie zawiera niezmieniony runtime diagnostyki i nowe materiały portfolio;
kod aplikacji nie był ponownie kompilowany w tej aktualizacji. Zachowano
wcześniejsze wydania i raporty. Portfolio przygotowano lokalnie, bez publikacji.

**HIPOTEZA:** odbiorca hurtowniany. **UNKNOWN:** samodzielność nowego
użytkownika, czysty Windows, popyt, oszczędność u klienta i rentowność oferty.
Domknięcie portfolio nie zamyka etapów Side Hustle ani Grand Slam Offer.

# Stan wcześniejszy — 2026-10-03

POTWIERDZONE: wdrożono listę miejsc do poprawy w CSV w trybie prostym i zaawansowanym: linia, kolumna, podgląd wartości, problem i wskazówka. Pełny opis jest dostępny po kliknięciu wiersza, a wszystkie wykryte problemy można pobrać do CSV. Braki kolumn dodatkowych mają osobne ostrzeżenia. Kontrola niepełna jest jawnie oznaczana. Dane źródłowe nie są zmieniane ani uzupełniane estymacją.

129 testów automatycznych przeszło, w tym 16 nowych testów diagnostyki. Wersję źródłową i EXE rozpakowany z nowego ZIP sprawdzono w Edge na sztucznych danych: 75 błędnych rekordów, 150 problemów w pobranym CSV, działające strony i wybór wiersza, brak PDF po błędnym imporcie, poprawiony import z oczekiwaną sumą 60,00. Dowody i granice: [DATA_DIAGNOSTICS.md](DATA_DIAGNOSTICS.md).

Nowa paczka: `release/AutoReportAnalyst-Windows-2026-10-03-diagnostics.zip`. Wcześniejsze wydania i raporty zachowano. UNKNOWN: kompletność rzeczywistego eksportu klienta, samodzielność użytkownika, czysty Windows i pilot odbiorcy.

# Stan wcześniejszy — 2026-10-02

POTWIERDZONE: 113 testów przeszło; EXE rozpakowany z ZIP sprawdzony na pełnym CSV 541 909 pozycji oraz pięcioletnich danych sztucznych. Dowody i ograniczenia: [RETEST_2026-10-02.md](RETEST_2026-10-02.md).

Przygotowano [plan produktu i oferty według $100M Offers](HORMOZI_EXECUTION_PLAN.md) oraz [aktualny roboczy szkic pilota](HORMOZI_PILOT_OFFER_DRAFT.md). Są to materiały do wykonania i walidacji, nie zakończony pilot. Odbiorca hurtowniany i cena 790 zł są HIPOTEZAMI; oszczędność u klienta, samodzielność początkującego użytkownika i gotowość sprzedażowa pozostają UNKNOWN. Nie wysłano ani nie opublikowano oferty.

Poniżej wcześniejsze aktualizacje i historia projektu.

Aktualizacja 2026-10-01: raport obsługuje do 5 lat kalendarzowych od wybranej daty końcowej (także dane historyczne). Przykład: 02.10.2021–01.10.2026. Dla końca 29 lutego rocznicę sprzed pięciu lat przyjmujemy jako 28 lutego. Tryb prosty: „Cały plik” lub „Ostatnie 5 lat w pliku”. Dłuższy plik wymaga jawnego wyboru okresu; dane nie są obcinane automatycznie.

# Bieżący stan — 2026-09-30
Raport jednym przyciskiem dla zapamiętanego układu CSV; lokalna pamięć ustawień,
automatyczny PDF i cały plik jako domyślny zakres. 109 testów OK. Test EXE w Edge
potwierdził nową sesję i drugi CSV bez ponownej konfiguracji.
Dowody i ograniczenia: [ONECLICK_RESULTS.md](ONECLICK_RESULTS.md).
Paczka: AutoReportAnalyst-Windows-2026-09-30-oneclick.zip.
Pierwszy nieznany format wymaga konfiguracji. Samodzielność użytkownika i czysty Windows nadal UNKNOWN.

## Stan poprzedniego wydania — 2026-09-29
Prosty tryb krok po kroku i nowy launcher Windows. 103 testy OK; EXE sprawdzone jako
lokalny serwer w Edge, pobrane PDF-y zgodne i obejrzane. Paczka: AutoReportAnalyst-Windows-2026-09-29-simple.zip.
Dowody i ograniczenia: [SIMPLE_MODE_RESULTS.md](SIMPLE_MODE_RESULTS.md).
Samodzielność osoby nietechnicznej, czysty Windows i rzeczywista obsługa okna launchera pozostają UNKNOWN.

## Stan poprzedniego wydania — 2026-09-28
94 testy OK. Naprawiono odtwarzanie kompletności sesji i przetestowano dwa syntetyczne cykle w EXE. Aktualne dowody: [INTERNAL_ACCEPTANCE_RESULTS.md](INTERNAL_ACCEPTANCE_RESULTS.md). Paczka: AutoReportAnalyst-Windows-2026-09-28-internal-qa.zip. Czysty Windows i samodzielność nowego analityka nadal UNKNOWN.

Poniżej historia projektu; starsze limity i nazwy wydań nie opisują obecnej wersji.

# Stan 10 kroków — Auto-Report 0.2.0
Data: 2026-09-14. Wykonano zmiany techniczne, testy i przygotowanie eksperymentu rynkowego.
Werdykt: **GO do kontrolowanej demonstracji i kwalifikacji odbiorcy.** Gotowość sprzedażowa, oszczędność u klienta i skuteczność oferty pozostają UNKNOWN.

## Checklista według pierwotnych kryteriów
- [x] 1. Parser i walidacja: jawny profil, daty ISO/PL, UTF-8/Windows-1250, separator kwot, maksymalnie dwa miejsca; błędny rekord blokuje całość.
- [ ] 2. Rozmówcy i problem: znaleziono 20 firm na podstawie publicznych źródeł, przygotowano 10 wiadomości. Rozmów 0; potwierdzonych problemów 0; eksportów klienta 0. Do zamknięcia: 5 rozmów, 2 podobne problemy i 1 dostęp do procesu.
- [x] 3. Procenty i interpretacja: zerowa/ujemna baza daje N/A; porównanie wymaga deklaracji pełnego zakresu; brak SCALE; zmiana średniej liczona przed zaokrągleniem.
- [x] 4. Diagnostyka: dokładna liczba poprawnych i błędnych rekordów, powtórzenia zachowane, kwoty ujemne według reguły, liczba rekordów poza okresem.
- [x] 5. Zestaw wzorcowy: 37 testów przeszło, w tym niezależne sumy, średnie, granice dat i test bardzo dużej sumy z zachowaniem ostatniego grosza.
- [x] 6. Generowanie: własna baza w pamięci, unikalne katalogi, atomowa publikacja, blokada równoległego przebiegu i obsługa Tk na głównym wątku. Test różnych plików i awarii zachowuje poprzedni raport. Streamlit przekazuje przesłane bajty i wybrane daty.
- [ ] 7. PDF: polski szablon z osadzonym fontem gotowy; wyrenderowano i obejrzano wszystkie 2 strony próbki i 3 strony testu skrajnego. Brak ucięć i brakujących polskich znaków. Do zamknięcia: odbiorca potwierdza zrozumiałość i przydatność.
- [ ] 8. Samodzielny start: zbudowane EXE i ZIP, instrukcja, przykładowy CSV i zapis profilu. Test EXE na tym komputerze przeszedł. Do zamknięcia: czysty komputer bez Pythona i drugi raport przygotowany przez nową osobę bez autora.
- [ ] 9. Oferta: gotowy dokument PILOT_OFFER.md i szkice kontaktu. Cena 790 zł oraz cel 50% oszczędności są hipotezami. Do zamknięcia: dopasowanie do poznanego procesu i decyzja rzeczywistego kupującego.
- [ ] 10. Płatny pilot: gotowy pusty PILOT_PROTOCOL.md. Do zamknięcia: dwa rzeczywiste cykle, pomiary, ponowne użycie, rozliczenie i decyzja GO/PIVOT/STOP.

Zaznaczono wyłącznie kroki spełniające kryteria. Gotowy dokument nie jest wykonaną rozmową ani pilotem.

## Sprawdzone artefakty
- Kod: app/validation.py, transform.py, queries.py, data_quality.py, pipeline.py, charts.py, pdf_report.py, profiles.py; oba interfejsy.
- Testy: tests/test_reporting.py i tests/test_streamlit.py.
- Dane fikcyjne: sample_data/pilot_demo.csv i pilot_demo_pl.csv.
- Przykładowy raport: output/pdf/AutoReport-demo-v0.2.0.pdf.
- Dystrybucja: release/v0.2.0/AutoReport/AutoReport.exe; należy zachować cały katalog, w tym _internal.
- Paczka: release/AutoReport-v0.2.0-Windows.zip.
- Instrukcja: docs/QUICKSTART_PL.md.
- Firmy i źródła: docs/PROSPECTS_20.md.
- Wiadomości niewysłane: docs/OUTREACH_DRAFTS.md.
- Oferta i protokół: docs/PILOT_OFFER.md, docs/PILOT_PROTOCOL.md.

## Dowody techniczne
- 37 testów: wszystkie przeszły. Streamlit zgłosił jedynie ostrzeżenie o kontekście testowym; testy zakończyły się poprawnie.
- Wzorzec syntetyczny: 7 pozycji, 1 250,00 PLN, średnia 178,57 PLN, poprzednia suma 1 000,00 PLN, zmiana +25%.
- Końcowa generacja wzorca na tym komputerze: 0,206 s.
- Parsowanie 100 000 syntetycznych wierszy: 2,029 s; suma 100 000 groszy. To pomiar parsera na jednym pliku, nie całego procesu klienta ani gwarancja wydajności.
- Tkinter: generowanie w tle, podwójne kliknięcie, pobranie wyniku, brak pliku i zapis profilu sprawdzone automatycznie.
- PDF: kontrole tekstu i liczb przez pypdf, render przez Poppler; wszystkie 5 stron obejrzane po końcowych zmianach.
- EXE: zakończony kodem 0, wynik 125 000 groszy i +25%; kwoty JSON zachowane jako ciągi dziesiętne. Sprawdzono ścieżkę ze spacjami.
- SHA-256 EXE: 51936016b891e008056ea39a2b8b99c28e208eb0125a996480cc7b14aa0abebe.
- Surowe wyniki lokalne: build/qa/evidence.json i build/qa/frozen-evidence.json.
- Składnia Python i git diff --check przeszły.

## Granice obecnej wersji
Jeden profil i PLN; do 20 MB i 100 000 pozycji; okres do 366 dni; do 10 kategorii w tabeli. Poprawność znaczenia dat, kwoty netto/brutto i kompletności zależy od jawnego kontraktu eksportu.
Nie potwierdzono działania na czystym Windows ani przez niezależnego użytkownika.
Nie zmierzono jeszcze całego procesu klienta, popytu, akceptacji ceny ani kosztu rzeczywistego wdrożenia.
Nie wykonano kontaktów z firmami. Brakuje ustalonego nadawcy/podpisu i zatwierdzenia konkretnych wiadomości do wysłania.
Historyczne report.db i dist zachowano. Nie wykonywano commit, push, publikacji ani wysyłki.

## Następna czynność wymagająca właściciela
Przejrzeć OUTREACH_DRAFTS.md i wskazać konto nadawcy oraz podpis; zatwierdzić wybrane wiadomości przed wysyłką. Alternatywnie właściciel może przeprowadzić pierwsze rozmowy sam.
Po odpowiedzi pierwszej osoby: karta procesu → anonimowy eksport → uzgodniony wzorzec → dopasowanie oferty → dwa cykle pilota.

## Aktualizacja 2026-09-18 — dashboard
Wspólna analiza, trzy widoki i eksport PDF wdrożone. Aktualne dowody i granice: [DASHBOARD_STATUS.md](DASHBOARD_STATUS.md). Samodzielne użycie i czysty Windows pozostają UNKNOWN.


## Aktualizacja 2026-09-19 — widoki analityka i PPTX
POTWIERDZONE: trzy przełączane dashboardy, wspólne filtry dat/kategorii/kompletności, grupowanie dzień/tydzień, eksport jednego lub trzech slajdów PPTX 16:9. 57 testów automatycznych przeszło. Prezentacje syntetyczne przeszły kontrolę struktury, import i render; obejrzano układ, przypadek ujemnych kwot oraz długich etykiet. Instrukcja i granice: [ANALYST_QUICKSTART.md](ANALYST_QUICKSTART.md).
UNKNOWN: czysty Windows, PowerPoint odbiorcy i pilot klienta.


## Aktualizacja 2026-09-20 — przygotowanie do odbioru hurtowni
63 testy, poprawki etykiet grup i stronicowania, definicje KPI, benchmark 100 000 pozycji. EXE i eksport 1/3 slajdów sprawdzone lokalnie. Dowody: ANALYST_HARDENING_RESULTS.md. Protokół siedmiu kroków i niewykonane bramki zewnętrzne: ANALYST_ACCEPTANCE.md.

## Aktualizacja 2026-09-21 — większe wykresy
Wykresy aplikacji mają pełną szerokość i wysokość 380 px zamiast 260 px; tabela także zajmuje pełną szerokość. Większe etykiety osi i legend. W PPTX legenda struktury ma osobną przestrzeń nad słupkami. 63 testy przeszły, kontrola przeglądarkowa CSV 187 pozycji i eksportu 1/3 slajdów wykonana, render PPTX obejrzany. Wydanie: release/AutoReportAnalyst-Windows-2026-09-21-large.zip. Układ wymaga więcej przewijania pionowego.

## Aktualizacja 2026-09-22 — Kaggle Superstore
POTWIERDZONE: oryginalny CSV 9994 pozycji, obsługa cp1252, jawnych dat ukośnikowych, waluty profilu oraz opcjonalnego HALF_UP z audytem wpływu. 71 testów przeszło. Dashboard, PDF i PPTX zgodne z niezależnym wzorcem. Szczegóły i ograniczenia: [KAGGLE_SUPERSTORE_TEST.md](KAGGLE_SUPERSTORE_TEST.md). Starsze ograniczenie do PLN jest nieaktualne. UNKNOWN: kompletność i waluta źródła, czysty Windows oraz pilot odbiorcy.

Wydanie 2026-09-22-kaggle: lokalny test EXE oraz ZIP przeszły; brak ostrzeżenia Session State. 3 slajdy z EXE przeszły walidację i render, PDF ma 2 strony. SHA-256 ZIP: e4a4192ce85c8f2e0b07ec94a0036874d27cdaee4720b4e4403d23e1f88131f7.

## Aktualizacja 2026-09-23 — rozszerzenie analityka
POTWIERDZONE: 84 testy, rozszerzone metryki z bramkami dostępności, importer z podglądem, profile/sesje, analiza wkładów produktów i klientów, miesiące i rok do roku oraz natywne wykresy PPTX z osadzonymi arkuszami. PDF obejmuje metryki biznesowe. Szczegóły: [ANALYST_UPGRADE.md](ANALYST_UPGRADE.md). UNKNOWN: klient, czysty Windows i natywna edycja w PowerPoint odbiorcy.

Wydanie Windows: release/AutoReportAnalyst-Windows-2026-09-23-business.zip. 84/84 testów; pełny scenariusz EXE z przejściem do produktu i odtworzeniem sesji przeszedł. ZIP poprawny. Trzy natywne wykresy i trzy osadzone arkusze zgodne; trzy slajdy oraz trzy strony PDF z EXE obejrzane. SHA-256 ZIP: 62b6bca9de4b9cc390bc5e87b79495b41bb039d712401972743a7880f3d64607. Dowody: build/upgrade-20260923/delivery.

## 2026-09-24 — duży import
Bieżące dowody: docs/LARGE_IMPORT_UPGRADE.md. Import pełnego Kaggle 541 909 rekordów, cena × ilość, daty z godzinami, osobne liczniki powtórzeń, neutralne nazwy dokumentów. 88 testów OK. Limity 100 MiB / 1 mln rekordów; pamięć nadal zależy od liczby wierszy. Nowe wydanie: 2026-09-24-large-import.

## 2026-09-26 — dopracowanie dashboardów
93 testy OK. Dowody i ograniczenia: docs/DASHBOARD_POLISH_RESULTS.md. Nowe wydanie: 2026-09-25-dashboard-polish. Test pełnego CSV w EXE i Edge przeszedł; test analityka pozostaje nieprzeprowadzony.
