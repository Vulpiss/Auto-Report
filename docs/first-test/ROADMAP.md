# Droga do odbioru — stan 2026-10-14

Portfolio: lokalny zakres domknięty. Poniższe bramki dotyczą użycia do pracy
i zweryfikowanej oferty. PREPARED oznacza gotowy materiał; wykonanie testu
lub uzyskanie zgody wymaga osobnego dowodu. Nie wyliczamy nowego procentu
z liczby przygotowanych formularzy.

## Wersja do pracy

| ID / artefakt / odpowiedzialny | Zależność | Test i DoD | Stan / ryzyko |
|---|---|---|---|
| W1: VM i FIRST_USE; właściciel + Codex | ISO, VirtualBox, czysta instalacja | Start/PDF/zamknięcie/restart/profil w gościu bez Pythona | PREPARED; wykonanie UNKNOWN / inne środowisko |
| W2: DISCOVERY i jeden proces; właściciel | Dostęp do rozmówcy | Obejrzany raport, odbiorca i zastosowanie | UNKNOWN / nietrafny problem |
| W3: DATA_AGREEMENT; właściciel danych + Codex | W2 i eksport | Potwierdzone definicje, reguły braków i kompletności | PREPARED; zatwierdzenie UNKNOWN / zła semantyka |
| W4: expected.json i odbiór PDF; Codex + właściciel danych | W3 i niezależny wzorzec | Zgodne liczby, zakres, mianowniki; PDF obejrzany | Narzędzie przygotowane; realny CSV UNKNOWN / poprawne rachunki na złych definicjach |
| W5: FIRST_USE; nowa osoba + obserwator | W1, potem W3–W4 dla realnego pliku | Drugi raport i poprawa błędu bez pomocy; poprawna interpretacja | PREPARED; wykonanie UNKNOWN / autor ukrywa trudności |
| W6: dwa cykle i OPERATIONS; odbiorca + właściciel | W4–W5 | Dwa odebrane raporty, samodzielny drugi cykl, uzgodniona obsługa | PREPARED; wykonanie UNKNOWN / niepowtarzalny proces |

## Grand Slam Offer

| ID / artefakt / odpowiedzialny | Zależność | Test i DoD | Stan / ryzyko |
|---|---|---|---|
| O1: pięć kart DISCOVERY; właściciel | Dostęp do rozmówców | Dwa podobne problemy i jeden dostęp do procesu | PREPARED; rozmowy UNKNOWN / brak potrzeby |
| O2: pomiar przed; właściciel + odbiorca | O1 | Zmierzony cały porównywalny proces | PREPARED; pomiary UNKNOWN / nieporównywalne zakresy |
| O3: oferta jednego wdrożenia; właściciel | O1–O2, W3 | Zakres, rezultat i kryteria uzgodnione z kupującym | Szkic istnieje; uzgodnienie UNKNOWN / niekontrolowana obietnica |
| O4: karta kosztów i cena; właściciel | O3 | Znany koszt, rezerwa i zaakceptowana cena | PREPARED; ekonomika UNKNOWN / cena poniżej kosztu |
| O5: płatny pilot, dwa cykle; klient + właściciel | O4, W1–W5 | Zgodność liczb, uzgodniona korzyść, odbiór i płatność | PREPARED; wykonanie UNKNOWN / brak korzyści |
| O6: koszt i ponowne użycie; właściciel | O5 | Rzeczywiste godziny i kolejny raport odbiorcy | UNKNOWN / kosztowne wsparcie |
| O7: drugi niezależny odbiorca; właściciel + druga firma | O6 | Podobny rezultat bez nowej architektury i przy akceptowalnym koszcie | UNKNOWN / osobny program dla każdego |
| O8: finalna oferta i obsługa; właściciel | O7 | Cena, zakres, dowody, wsparcie, utrzymanie i pojemność wynikają z wykonanych wdrożeń | UNKNOWN / sprzedaż przed powtarzalnością |

W6 i O5 mogą korzystać z tych samych cykli, jeśli przed startem uzgodniono
wszystkie kryteria. Jeden dowód może zamknąć kilka bramek; nie tworzymy
fikcyjnych dodatkowych klientów ani płatności.

GO do prób i kwalifikacji odbiorcy. PIVOT po dowodach innej potrzeby lub
nieopłacalnego zakresu. STOP przy niewyjaśnionych liczbach lub braku problemu.
MVP: jeden odbiorca, jeden kontrakt danych, jeden raport i jeden mierzony rezultat.
Pięć głównych ryzyk: brak potrzeby, błędna semantyka danych, trudność pierwszego
użycia, koszt obsługi oraz niepowtarzalność. Najmniejsze testy to odpowiednio
O1, W3–W4, W1/W5, O4–O6 i O7.
