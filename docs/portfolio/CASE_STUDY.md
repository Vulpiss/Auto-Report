# Auto-Report: od CSV do sprawdzalnego raportu

Projekt portfolio, stan 2026-10-04. Wszystkie przykłady poniżej są sztuczne.

## Zadanie

Zbudować aplikację Windows, która odczytuje powtarzalny eksport CSV,
sprawdza dane i pokazuje te same liczby na ekranie oraz w PDF. Przy błędzie
użytkownik ma dostać konkretne miejsce do poprawy, zamiast pozornie poprawnego
raportu z pominiętymi wierszami albo kwotami zamienionymi na zero.

HIPOTEZA zastosowania: cykliczne raportowanie w małej hurtowni.
Nie mamy potwierdzenia problemu, oszczędności czasu ani płatnego wdrożenia.
Przykład pokazuje rozwiązanie problemu inżynierskiego, nie historię klienta.

## Rozwiązanie

Lokalny program uruchamia interfejs Streamlit w przeglądarce na 127.0.0.1.
Pierwszy format wymaga konfiguracji kolumn i znaczenia kwot. Program zapisuje
profil bez wierszy CSV, aby następny zgodny eksport wymagał wyboru pliku
i przycisku. Prosty tryb przygotowuje PDF automatycznie; zaawansowany
udostępnia dodatkowe filtry, deklarację kompletności i eksport PPTX.

Przepływ bieżącej aplikacji:

`CSV + profil → walidacja → analiza w pamięci → wspólny model → dashboard / eksport`.

Najważniejsze moduły: `app/validation.py`, `app/analysis.py`,
`app/dashboard_model.py`, `app/pipeline.py`, `interfaces/simple_app.py`
i `dashboard_entry.py`. SQLite jest zachowany dla wcześniejszych adapterów,
nie jest silnikiem analizy bieżącego dashboardu.

## Decyzje techniczne i ich koszt

| Decyzja | Powód | Koszt lub ograniczenie |
|---|---|---|
| Całkowite setne jednostki i Decimal | Suma kwot zachowuje grosze; procenty liczymy przed zaokrągleniem do prezentacji | Kontrakt precyzji musi być jawny; float służy geometrii wykresu |
| Błędna pozycja blokuje cały raport | Użytkownik nie dostaje niepełnej sumy przedstawionej jako pełna | Najpierw musi poprawić źródło lub ustawienia importu |
| Profil zamiast zgadywania znaczenia pól | Ten sam zapis daty albo liczby może mieć różne interpretacje | Pierwsza konfiguracja wymaga świadomego wyboru |
| Oddzielna deklaracja kompletności | Pierwsza i ostatnia data nie dowodzą, że eksport jest pełny | Część porównań pozostaje N/A |
| Jeden wynik dla interfejsu i eksportu | Ogranicza rozbieżności filtrów, dat i mianowników | Zmiana danych lub filtrów unieważnia poprzedni eksport |
| Przetwarzanie lokalne | Analiza nie wymaga wysyłania eksportu do usługi zewnętrznej | Dystrybucję i pamięć trzeba sprawdzić na komputerze odbiorcy |
| Reguły deterministyczne | Wnioski i ograniczenia są sprawdzalne, bez potrzeby modelu językowego | Komentarze nie są dowodem przyczyn biznesowych |

## Jak sprawdzam poprawność

Oczekiwania liczbowe ustalam niezależnie od programu. Demonstracja używa
14 pozycji w `sample_data/pilot_demo.csv`: siedem wcześniejszych i siedem
będących podstawą raportu tygodniowego.

| Zakres | Liczba pozycji | Suma | Średnia |
|---|---:|---:|---:|
| 31.08–13.09.2026 | 14 | 2 250,00 PLN | 160,71 PLN |
| 31.08–06.09.2026 | 7 | 1 000,00 PLN | 142,86 PLN |
| 07–13.09.2026 | 7 | 1 250,00 PLN | 178,57 PLN |

Zmiana sumy wynosi 25% wyłącznie po zadeklarowaniu kompletności obu
okresów. Prosty tryb pokazuje brak podstaw do porównania. To zamierzone
ograniczenie wyniku, a nie błąd demonstracji.

Plik z błędną kwotą i pustą kategorią blokuje raport i wskazuje linie
10 oraz 14. Po wybraniu poprawnego źródła lista błędów znika, a suma
ponownie wynosi 2 250,00 PLN. PDF pobrany z aplikacji jest porównywany
z niezależnym wzorcem i renderowany do kontroli wizualnej.

POTWIERDZONE: pełna regresja obejmuje 129 testów, m.in. formaty zewnętrzne,
braki, dokładne sumy, zerową i ujemną bazę, granice pięciu lat, duży import,
stan interfejsu i unieważnianie starych eksportów. Szczegółowy zakres i
wynik bieżącego wydania są w VERIFICATION.md.

## Czego nie dowodzi portfolio

UNKNOWN: kompletność rzeczywistego eksportu, przydatność dla odbiorcy,
samodzielność nowego użytkownika, czysty Windows oraz rentowność usługi.
Lokalne uruchomienie EXE i automatyczny test przeglądarki nie zamykają tych bramek.

Znane ograniczenia: import zajmuje pamięć zależną od liczby rekordów;
nie ma przeliczania walut ani dowolnego zgadywania formatów. W niektórych
skrajnych przykładach PDF wymaga dalszej poprawy gęstości układu i osi
wykresu; przykład portfolio jest kontrolowany oddzielnie. Materiały
historyczne zachowano, a aktualną instrukcję wskazuje README.

Najmniejszy kolejny test poza portfolio: osoba nieznająca projektu
uruchamia paczkę na innym Windowsie i przygotowuje drugi poprawny raport
bez pomocy autora. Walidacja zastosowania wymaga następnie realnego
eksportu, uzgodnionego wzorca i pomiaru procesu odbiorcy.
