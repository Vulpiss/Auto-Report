# Auto-Report: plan produktu i oferty według $100M Offers

Data: 2026-10-02. Status: plan i oferta robocza, bez publikacji, wysyłki ani nowych zobowiązań wobec klientów. Przygotowanie dokumentu nie oznacza wykonania zadań.

## Decyzja i definicja celu

**GO do dopracowania pierwszego użycia, kwalifikacji odbiorcy i ograniczonego pilota. Gotowość do powtarzalnej sprzedaży: UNKNOWN.**

Celem jest dostarczenie konkretnej osobie poprawnego, użytecznego raportu z jej powtarzalnego eksportu, przy mniejszej ilości pracy. Wybranie CSV i naciśnięcie przycisku ma być całą obsługą kolejnego raportu w uzgodnionym formacie. Pierwszą konfigurację możemy wykonać za klienta.

Zakres decyzji: lokalny program Windows, jeden typ odbiorcy, jeden uzgodniony kontrakt eksportu, jeden raport i jeden mierzalny rezultat. Zakres do pięciu lat pozostaje funkcją produktu; oferta zaczyna się od jednego cyklicznego raportu. Szerszy horyzont danych sam w sobie nie potwierdza większej wartości dla klienta.

Hormozi pomaga ułożyć atrakcyjną ofertę. Nie zastępuje sprawdzenia, czy klient potrzebuje raportu i czy zapłaci za jego dostarczenie.

## Dowody i niewiadome

POTWIERDZONE przez [ponowny test](RETEST_2026-10-02.md):

- 113 testów automatycznych przeszło. Sprawdzono serwer rzeczywistego EXE rozpakowanego z ZIP-a.
- Cały plik testowy: 541 909 pozycji, suma 9 747 747,93 j.p., niezależne obliczenie csv/Decimal, zachowany SHA-256 źródła.
- Import i automatyczny PDF w EXE: około 38 sekund na tym komputerze. To czas przetwarzania tego pliku, nie zmierzona oszczędność klienta.
- Dashboard, pamięć ustawień, PDF, pięcioletni zakres, blokowanie błędnej kwoty i usuwanie starego PDF po zmianie pliku zostały sprawdzone.
- Kod dopuszcza 100 MiB i 1 000 000 wierszy. Są to limity walidacji; test 541 909 pozycji nie potwierdza wydajności dla każdego pliku dochodzącego do limitu.
- Pierwszy nieznany układ wymaga konfiguracji. W PDF są drobne problemy czytelności: dużo pustego miejsca oraz powtarzające się etykiety osi przy małych wartościach.

HIPOTEZA odbiorcy: właściciel małej hurtowni, któremu pracownik co tydzień ręcznie przygotowuje raport sprzedaży z tego samego eksportu CSV.

UNKNOWN: aktualny czas pracy klienta, przydatność raportu, znaczenie kwot, gotowość zakupu, cena, koszt wdrożenia i wsparcia, samodzielność początkującego użytkownika oraz uruchomienie na czystym Windowsie. Według dotychczasowych dokumentów brak pierwszego klienta; lokalny testowy CSV nie jest dowodem wdrożenia u klienta.

## 1. Wybrać odbiorcę i problem

Roboczy odbiorca zakupowy: właściciel hurtowni. Użytkownik: pracownik przygotowujący zestawienie. Ich potrzeby badamy osobno: pierwszy musi chcieć używać raportu, drugi musi móc go przygotować.

Sprawdzić cztery kryteria rynku: dotkliwość problemu, możliwość zapłaty, dostęp do właściwych osób i perspektywę rynku. Dodatkowo: powtarzalność eksportu i brak wystarczającego rozwiązania w obecnym systemie. To adaptacja [oficjalnej checklisty wyboru niszy](https://www.acquisition.com/files/pick-your-niche-checklist.pdf).

W pięciu rozmowach obejrzeć ostatni raport i rzeczywisty proces. Zapisać: odbiorcę, decyzję podejmowaną na podstawie raportu, częstotliwość, kolejne czynności, czas, błędy, obecne narzędzie, osobę zatwierdzającą zakup i możliwość próbki. Zapytać, czy obecny Excel lub raport systemowy już wystarcza. Nie zaliczać deklaracji „fajny program” jako dowodu potrzeby.

Próg roboczy do rozpoczęcia dopasowania produktu: dwa podobne, udokumentowane problemy oraz jeden dostęp do eksportu i obecnego raportu. To nasz próg eksperymentu, nie zalecenie liczbowe Hormoziego ani prognoza.

Jeżeli brakuje dostępu do danych, obejrzeć proces przy udziale właściciela danych lub uzgodnić sztuczny plik odzwierciedlający strukturę. Realnego pilota i jego oszczędności nie potwierdzimy samym plikiem sztucznym.

## 2. Ustalić rezultat i wartość

Roboczy rezultat: „Przed spotkaniem masz sprawdzony raport tygodniowy, który kolejny raz przygotujesz samodzielnie z uzgodnionego CSV”.

Równanie wartości jest ramą projektowania: zwiększamy znaczenie rezultatu i wiarygodność jego osiągnięcia, zmniejszamy czas oczekiwania i wysiłek klienta. Nie jest kalkulatorem ceny. Źródło: [oficjalna checklista wartości](https://www.acquisition.com/hubfs/Offer%20Checklists%20-%20PDF%20Downloads/Pricing-Value-Checklist.pdf?hsLang=en).

| Element | Nasze wykonanie | Dowód potrzebny do zamknięcia |
|---|---|---|
| Pożądany rezultat | Raport odpowiada na konkretną potrzebę właściciela | Odbiorca użył raportu w swoim procesie i wskazał przydatne elementy |
| Wiarygodność | Próbka na jego eksporcie, zgodność liczb, jawne ograniczenia | Zatwierdzony wzorzec, podpisany protokół odbioru, później opis wdrożenia za zgodą |
| Czas oczekiwania | Konfiguracja przez nas, gotowy profil, automatyczny PDF | Pomiar od otrzymania kompletu materiałów do próbki oraz czas obu cykli |
| Wysiłek | Jedna instrukcja eksportu, wybór CSV, jeden przycisk | Nowy użytkownik wykonuje drugi raport bez pomocy autora |

Główny miernik pilota: aktywny czas całego procesu przed i po. Liczyć eksport, czyszczenie, obliczenia, kontrolę, poprawki i zapis; wdrożenie osobno. Roboczy cel: co najmniej 50% mniej czasu w obu cyklach, przy zachowaniu poprawności. Próg wymaga uzgodnienia i kwalifikacji przed rozpoczęciem, a nie publicznej obietnicy teraz.

Korzyść w godzinach miesięcznie = (minuty przed − minuty po) × raporty miesięcznie / 60. Jeśli klient przypisuje czasowi wartość, zapisać jej źródło. Odzyskany czas nie jest automatycznie oszczędnością gotówki.

## 3. Usunąć przeszkody przed, podczas i po użyciu

Podejście: spisać przeszkody, dobrać sposób ich rozwiązania, a następnie zachować składniki dające dużą wartość przy rozsądnym koszcie dostarczenia. Początkowa indywidualna konfiguracja może być częścią oferty; po pilotach oceniamy jej powtarzalność. Źródło: [oficjalna checklista budowy oferty](https://www.acquisition.com/files/offer-creation-checklist.pdf).

| Przeszkoda | Rozwiązanie do wykonania | Test odbioru |
|---|---|---|
| „Nie wiem, jak wyeksportować dane” | Jednostronicowa instrukcja konkretnego systemu klienta | Użytkownik eksportuje poprawny CSV bez pomocy |
| „Nie umiem zainstalować” | Jedna wskazana paczka i jasny sposób uruchomienia | Nowy komputer Windows bez Pythona: start, import, PDF, zamknięcie i ponowny start |
| „Nie rozumiem kolumn” | Profil przygotowany przez nas; krótki kreator przy niezgodnym pliku | Następny zgodny plik bez mapowania; niezgodny plik wymaga jawnego potwierdzenia |
| „Nie wiem, czy to cena czy kwota” | Przykład wartości i wyjaśnienie cena × ilość albo kwota pozycji | Profil zatwierdzony przez osobę rozumiejącą eksport; zgodność z ręcznym wzorcem |
| „Nie wiem, gdzie jest błąd” | Wiersz, kolumna, wartość i przykład poprawnego zapisu | Błędny rekord blokuje wynik i prowadzi użytkownika do poprawki; brak zastępowania zerem |
| „Nie widzę wyniku” | Suma, liczba pozycji, okres i główny wykres na początku | Na uzgodnionej rozdzielczości użytkownik znajduje wynik i PDF bez instrukcji autora |
| „Nie rozumiem liczb” | Proste nazwy i krótkie definicje; informacja o niepełnych danych | Użytkownik rozróżnia pozycje i dokumenty oraz rozumie N/A |
| „Pięć lat jest nieczytelne” | Grupowanie długiego okresu po miesiącach, możliwość zmiany | Suma po grupowaniu zgodna; niepełne miesiące opisane; brak danych nie staje się zerem |
| „PDF wygląda dziwnie” | Uporządkowane strony, poprawne ticki, czytelne daty | Render wszystkich stron dla małych kwot, ujemnych wartości, długich nazw i pięciu lat |
| „Czy to stary raport?” | Widoczna nazwa źródła i zakres, jednoznaczny status importu | Zmiana pliku, profilu lub dat nie udostępnia poprzedniego PDF jako nowego wyniku |
| „Co zrobię, gdy coś się zmieni?” | Zapis profilu, instrukcja przywrócenia i określony kanał wsparcia | Nowa sesja odtwarza profil; zmiana schematu jest wykryta i ma jasną ścieżkę obsługi |

Informacje o błędach, brakującej walucie, zwrotach i niepotwierdzonym porównaniu muszą pozostać widoczne. Szczegóły techniczne można schować pod „Szczegóły danych”.

## 4. Zamknąć kontrakt danych i MVP

Przed konfiguracją uzgodnić: system eksportu, nagłówki, kodowanie, separator, definicję wiersza i daty, strefę/czas lokalny jeśli występuje godzina, znaczenie kwoty, walutę, netto/brutto, ilość i jednostkę, identyfikator dokumentu jeśli potrzebny, zwroty, powtórzenia, zaokrąglenia oraz źródło potwierdzenia kompletności. Jeden wzorcowy plik i jeden celowy plik błędny stanowią załączniki kontraktu.

MVP dla pierwszego pilota:

- Jeden uzgodniony eksport, jedna firma i jedna waluta.
- Jeden raport cykliczny: zakres, suma wartości pozycji, liczba pozycji, potrzebny podział, trend i PDF. Pozostałe KPI tylko po uzgodnieniu znaczenia danych.
- Porównanie wyłącznie przy poprawnej bazie i potwierdzonej kompletności. Nie obiecujemy zysku ani marży bez potrzebnych danych.
- Lokalny Windows, gotowy profil, automatyczny PDF, łatwa ponowna obsługa, poprawne komunikaty.
- Zakres dat do pięciu lat; parametry obsługi komputera i pliku określone testem, nie uniwersalna gwarancja czasu.

SaaS, ML, LLM, integracje API i rozszerzenia na wiele branż nie są warunkiem odbioru tego MVP. Kolejne funkcje rozpatrujemy, gdy konkretna przeszkoda w pilocie uzasadnia ich koszt.

## 5. Zbudować pakiet i sposób dostarczenia

Roboczy pakiet: **Auto-Report — wdrożenie raportu tygodniowego dla hurtowni**.

W pakiecie: ustalenie kontraktu, konfiguracja jednego profilu, program Windows, jeden szablon dashboardu/PDF, sprawdzenie liczb z obecnym raportem, instrukcja eksportu, krótkie przekazanie obsługi, dwa rzeczywiste cykle oraz jedna korekta w ustalonym zakresie.

Podział pracy: pierwszy format ustawiamy za klienta; odbiór wykonujemy wspólnie; kolejny raport klient przygotowuje sam. Na starcie ważniejszy jest skuteczny wynik niż całkowite wyeliminowanie naszej pracy. Zapisujemy jednak każdą godzinę, aby zobaczyć koszt dostarczenia.

Wsparcie pilota kończy się po drugim cyklu, maksymalnie 30 dni od przekazania, jeśli taki harmonogram uzgodnią strony. Przy rzadszych raportach harmonogram należy zmienić przed przyjęciem pilota. Roboczy termin pierwszej odpowiedzi: następny dzień roboczy; nie oznacza terminu naprawy. Właściciel potwierdza dostępność przed podaniem tego w ofercie.

Składniki dodatkowe usuwające obawy: karta zgodności liczb, jednostronicowa instrukcja eksportu, kopia ustawień i checklista odczytu raportu. Ich wartość sprawdzamy w użyciu. Cenę składnika przypisujemy dopiero, gdy mamy uczciwą podstawę, np. jego faktyczną osobną cenę. Źródło idei bonusów: [oficjalna checklista bonusów](https://www.acquisition.com/files/bonus-creation-checklist.pdf). Nie wyceniono ich tutaj fikcyjnie.

## 6. Cena, ekonomika i ograniczenie ryzyka

HIPOTEZA pierwszej ceny: 790 zł za cały opisany pilot, odziedziczona z wcześniejszej strategii. Nie ustalono, jak ma być przedstawiony podatek ani rozliczenie. Cena nie wynika z potwierdzonej wartości ani marży; nie traktujemy jej jako finalnej.

Przed ofertą wpisać do karty ekonomiki: cenę i sposób rozliczenia, godziny wdrożenia, godziny wsparcia, koszt naszej godziny, pozostałe koszty, rezerwę na poprawkę oraz maksymalny koszt obsługi. Nadwyżka operacyjna = przychód po uwzględnieniu sposobu rozliczenia − koszt dostarczenia. Koszt pozyskania zapisać osobno; podatki i pełny zysk firmy nie są tu policzone.

Używać trzech perspektyw: wartość mierzalnego problemu dla klienta, koszt rentownego dostarczenia, rzeczywista decyzja zakupowa. Po każdym pilocie zapisać, czy klient przyjął cenę, zapłacił i ponownie użył produktu. Pochwała i akceptacja próbki nie są płatnym zakupem.

Roboczy wariant ograniczenia ryzyka: płatność za pilot po spełnieniu uzgodnionych kryteriów. W zakresie jednego eksportu i jednego raportu: zgodność liczb, drugi raport samodzielnie, uzgodniony próg czasu w obu cyklach. Jedna korekta i termin ponownego odbioru wpisane przed startem; gdy kryteria nadal nie są spełnione, brak opłaty za pilot. To propozycja, nie aktywna gwarancja klientom.

Warunki dotyczą czynności niezbędnych do wyniku: klient dostarcza uzgodniony eksport, wzorzec, definicje i uczestniczy w dwóch cyklach. Gwarancja nie obejmuje wzrostu sprzedaży, zysku ani dowolnego nowego formatu. Koncepcję powiązania gwarancji z wykonaniem niezbędnych kroków wspiera [oficjalna checklista gwarancji](https://www.acquisition.com/files/unbeatable-guarantee-checklist.pdf). Konkretne warunki handlowe wymagają ustalenia przed sprzedażą.

## 7. Nazwa, dostępność i komunikat

Nazwę i opis oprzeć na odbiorcy, celu, rzeczywistym czasie dostarczenia i nazwie pakietu. Roboczo: „Auto-Report — wdrożenie raportu tygodniowego dla hurtowni”. „Tygodniowy” opisuje rytm raportowania, a nie obietnicę ukończenia wdrożenia w siedem dni. Po potwierdzeniu terminu można dodać termin próbki. Źródło: [oficjalna checklista nazewnictwa](https://www.acquisition.com/files/product-naming-checklist.pdf).

Dostępność ograniczyć tylko rzeczywistą liczbą godzin na wdrożenia. Liczba równoległych pilotów = dostępne godziny / ostrożnie oszacowane godziny pilota, z rezerwą. Nie ogłaszamy teraz liczby miejsc, której nie policzono. Termin naboru ma odpowiadać rzeczywistemu kalendarzowi startu; jeżeli takiego terminu nie ma, nie dodajemy odliczania. Mechanikę ograniczania liczby wdrożeń i terminu opisuje [oficjalna checklista dostępności](https://www.acquisition.com/files/scarcity-urgency-checklist.pdf).

Materiały do przygotowania: jednostronicowa oferta, krótka demonstracja na oznaczonych sztucznych danych, próbka PDF, karta odbioru i opis tego, co klient dostarcza. Strona sprzedażowa może powstać po dopasowaniu oferty do poznanego problemu. Żadna publikacja ani wysyłka nie jest częścią niniejszego planowania.

## 8. Zadania z zależnościami i kryteriami ukończenia

DoD oznacza warunek uznania zadania za zakończone. Wszystkie poniższe zadania są otwarte; istniejący kod i dokumenty są materiałem wejściowym.

| ID / priorytet / wykonawca | Artefakt | Zależność | Test i DoD | Główne ryzyko |
|---|---|---|---|---|
| H01 / P0 / właściciel | 5 kart rozmów i wybór odbiorcy | Dostęp do rozmówców | Obejrzane realne raporty; dwa podobne problemy, jeden dostęp do procesu; w innym przypadku decyzja PIVOT | Rozwój dla osoby bez potrzeby |
| H02 / P0 / właściciel + klient | Podpisany kontrakt eksportu, wzorzec i baseline czasu | H01 | Znaczenie pól wyjaśnione; ręczne oczekiwania liczb i pomiar obecnego procesu zaakceptowane | Poprawne rachunki na błędnie zrozumianych danych |
| H03 / P0 / Codex + właściciel | Aktualne instrukcje i materiały oferty | Test 2026-10-02 | Stare limity oznaczone historycznie; jeden wskazany ZIP; obietnice mają status i źródło | Sprzeczne materiały |
| H04 / P0 / Codex | Profil konkretnego eksportu i prosty pierwszy import | H02 | Następny zgodny plik: wybór + przycisk; nieznane znaczenie kwoty/waluty wymaga potwierdzenia; niezależne liczby zgodne | Zbyt agresywne zgadywanie |
| H05 / P0 / Codex | Czytelna diagnostyka błędnych danych | Wzorcowy i błędny plik H02 | Wiersz/kolumna/przykład poprawki; błędna kwota nie daje PDF ani zera; stary wynik znika | Użytkownik nie umie naprawić źródła |
| H06 / P0 / Codex | Ekran najważniejszego wyniku | H02 | Odbiorca znajduje sumę, okres, ostrzeżenia i PDF; źródło wyniku jednoznaczne | Ukrycie ważnego ograniczenia |
| H07 / P1 / Codex | Poprawiony PDF i długie wykresy | Obecne testy; docelowy szablon z H02 | Poprawne osie i układ, sumy grupowań zgodne; render skrajnych przypadków; odbiorca akceptuje czytelność | Miesięczne grupowanie maskuje brak danych |
| H08 / P0 / Codex + niezależny tester | Paczka Windows i protokół czystego startu | H04–H07 i build | Bez Pythona: start/import/PDF/zamknięcie/ponowny start; zapisany profil działa; poprzednie dane zachowane | Środowisko autora ukrywa zależności |
| H09 / P0 / właściciel + 3 testerów | 3 protokoły pierwszego użycia | H08 | Osoby nietechniczne samodzielnie generują drugi raport i poprawnie odczytują sumę, okres, N/A; każda prośba o pomoc zapisana i przeszkoda usunięta | Testują tylko osoby znające projekt |
| H10 / P0 / właściciel | Karta ekonomiki i cena konkretnej oferty | H01–H02, oszacowanie H08–H09 | Koszt wdrożenia/wsparcia/rezerwy policzony; ustalone rozliczenie i limit zakresu; cena przedstawiona decydentowi | Cena nie pokrywa pracy |
| H11 / P0 / właściciel + klient | Oferta i protokół z ograniczeniem ryzyka | H02, H08–H10 | Kryteria liczb/czasu/samodzielności i warunki odbioru uzgodnione przed startem | Obietnica, której nie kontrolujemy |
| H12 / P1 / Codex + właściciel | Instrukcja eksportu, karta liczb, kopia profilu | H02, H04 | Tester korzysta z materiałów; zbędne składniki usunięte; podstawowe elementy nie udają osobnych bonusów | Pakiet zwiększa zamiast zmniejszać wysiłek |
| H13 / P1 / właściciel | Nazwa, opis, limit wdrożeń i termin | H10–H12, rzeczywisty kalendarz | Komunikat opisuje wynik; liczba miejsc wynika z pojemności; brak niepotwierdzonych dowodów lub wycen | Sztuczna presja zamiast wartości |
| H14 / P0 / właściciel + klient | Dwa rzeczywiste cykle pilota i odbiór | H11–H12 | Brak niewyjaśnionych różnic do 0,01 jednostki, zgodna liczba pozycji, drugi raport samodzielny, ustalony próg czasu w obu cyklach; odbiór i płatność zapisane | Testowy sukces bez korzyści klienta |
| H15 / P0 / właściciel + Codex | Koszt obsługi i opis wdrożenia | H14 | Czas konfiguracji/poprawek policzony; decyzja klienta o ponownym użyciu; opis tylko za zgodą; dane zanonimizowane | Droga ręczna usługa bez marży |
| H16 / P0 / właściciel + druga firma | Powtórzony pilot dla tego samego zastosowania | H15 | Druga niezależna firma uzyskuje zgodny wynik bez nowej architektury; koszt dostarczenia mieści się w limicie | Każdy klient wymaga osobnego programu |
| H17 / P1 / właściciel | Finalna oferta i proces sprzedaży/obsługi | H16 | Cena, zakres, dowody, wsparcie, warunki, dostarczenie i odnawianie/utrzymanie zgodne z realnymi wynikami | Skalowanie przed powtarzalnością |

Prace niezależne do rozpoczęcia teraz: H03, diagnostyka na istniejących danych testowych, poprawa znanych problemów PDF i przygotowanie protokołu czystego Windowsa. Nie muszą czekać na klienta. Profil klienta, konkretny rezultat i obietnice handlowe wymagają H01–H02.

Nie wymuszamy abonamentu. Po pilotach sprawdzić, czy występuje stała wartość utrzymania: np. regularne aktualizacje, obsługa zmian eksportu i potrzebne wsparcie. W przeciwnym razie rozważyć jednorazowy pakiet z jasno opisanym utrzymaniem osobno.

## 9. Pięć najważniejszych ryzyk

| Ryzyko | Dowód / status | Najmniejszy test | Decyzja po teście |
|---|---|---|---|
| R1. Nie ma istotnego problemu | Brak potwierdzonego klienta; HIPOTEZA hurtowni | H01: pięć rozmów z ostatnim raportem | Przy braku dwóch podobnych problemów zmienić hipotezę |
| R2. Raport źle interpretuje eksport | Kwoty w testowym CSV policzone, ale waluta/kompletność UNKNOWN | H02: kontrakt i niezależny wzorzec | Bez wyjaśnionych definicji nie przyjmować pilota |
| R3. Nowy użytkownik nie daje rady | Druga sesja automatyczna sprawdzona; ludzkie pierwsze użycie UNKNOWN | H08–H09: czysty Windows i trzy osoby | Usunąć każdą blokującą przeszkodę przed samodzielnym pilotem |
| R4. Wdrożenie kosztuje więcej niż cena | 790 zł jest HIPOTEZĄ; koszt wsparcia UNKNOWN | H10, H14–H15: pomiar każdej godziny | Zmienić zakres/cenę/dostarczenie, jeśli wynik ekonomiczny nie spełnia ustalonego minimum |
| R5. Brak wiarygodnej i bezpiecznie dostarczanej obietnicy | Testy programu nie są dowodem wyniku biznesowego; wsparcie UNKNOWN | H11–H16: uzgodnione kryteria, dwa cykle, druga firma | Dopiero wtedy opierać komunikat na rzeczywistych wynikach |

## 10. Bramki GO / PIVOT / STOP

- **GO teraz:** wykonanie planu przygotowawczego i kwalifikacja odbiorcy. Nie oznacza zakończonych rozmów.
- **GO do pilota:** H01–H02 potwierdziły problem, próbka liczb jest zaakceptowana, program uruchamia się u odbiorcy, a zakres/cena/kryteria są uzgodnione.
- **GO do powtarzalnej sprzedaży:** opłacony i odebrany pilot, ponowne użycie, drugi podobny odbiorca oraz koszt obsługi zgodny z ekonomią oferty. To nasza bramka operacyjna, nie uniwersalny próg z książki.
- **PIVOT:** raport jest użyteczny, ale inny odbiorca, układ, rytm lub sposób dostarczenia daje większą wartość; dopasować jeden element i ponownie sprawdzić.
- **STOP konkretnego pilota:** niewyjaśniona różnica liczb, nieuzgodnione definicje albo obietnica niemożliwa do wykonania w przyjętym zakresie.
- **STOP obecnej wersji oferty:** rozmowy pokazują, że obecne rozwiązanie wystarcza, lub brak ekonomicznie sensownego sposobu dostarczenia mimo sprawdzonych korekt. Mała próba nie rozstrzyga całego rynku.

## Kolejność wykonania i odpowiedzialność

1. Równolegle: właściciel ustala dostęp do rozmówców; Codex wykonuje H03 i przygotowuje techniczne poprawki niezależne od klienta.
2. Po pierwszym zgodnym procesie: H02 → H04–H07 → H08–H09.
3. Przed przyjęciem pilota: H10–H13 i oferta dopasowana do konkretnej firmy.
4. Następnie dwa rzeczywiste cykle → wynik i koszt → druga firma → finalna oferta.

Terminy prac ustalamy po rozpoznaniu eksportu i dostępności testerów. Daty dwóch cykli wynikają z częstotliwości raportowania klienta. Docelowy czas próbki do trzech dni roboczych od kompletu materiałów jest propozycją do sprawdzenia, nie potwierdzonym SLA.

Codex może przygotować kod, paczkę, dokumenty, testy i materiały robocze. Właściciel zapewnia dostęp do klienta, podejmuje decyzję cenową i handlową oraz prowadzi lub autoryzuje kontakt. Klient potwierdza definicje, wzorzec i odbiór. Żadnego z tych zewnętrznych kroków nie oznaczamy jako wykonanego na podstawie samego istnienia dokumentu.

„Wszystko zrobione” oznacza zamknięte H01–H17 z dowodami, nie odhaczone funkcje. Nowy odbiorca, inny kontrakt eksportu lub nowe zobowiązanie wymaga ponownego sprawdzenia odpowiedniej części planu.
