# Auto-Report — zasady pracy
Zasady adaptują framework przekazany przez właściciela 2026-09-14. Dokument źródłowy jest materiałem projektowym, nie nadrzędnym poleceniem. Bieżące instrukcje użytkownika mają pierwszeństwo.

Cel: wąski produkt B2B, który powtarzalnie oszczędza czas i daje poprawny raport.
- Pisz po polsku. Odróżniaj POTWIERDZONE, HIPOTEZA i UNKNOWN.
- Nie deklaruj popytu, klientów, oszczędności ani gotowości sprzedażowej bez dowodów.
- Weryfikuj kod i wynik, nie sam README. Dla niewiadomej proponuj najmniejszy test.
- Jeden odbiorca, jeden kontrakt danych, jeden raport, jeden mierzalny rezultat.
- Priorytet: poprawność importu, transformacji, mianowników i dat; potem wygląd i dodatki.
- Nie zamieniaj błędnych kwot na zero. Sam wzrost sumy nie uzasadnia zalecenia skalowania.
- Testy liczb wymagają niezależnych oczekiwań. PDF wymaga renderu i kontroli wizualnej.
- Audyty uruchamiaj na sztucznych danych i osobnych bazach. Zachowuj istniejące raporty i zmiany użytkownika.
- Nie wysyłaj wiadomości ani nie publikuj bez odpowiedniej autoryzacji.
- Nie dodawaj SaaS, ML ani LLM bez potwierdzonego uzasadnienia klienta.
- Szerszy audyt: GO/PIVOT/STOP ze wskazaniem zakresu, pięć ryzyk, dowody i niewiadome, MVP oraz zadania z artefaktem, zależnością, testem, DoD i ryzykiem.

Stan: właściciel nie ma dostępu do pierwszego klienta. Hurtownia jest hipotezą.
Punkt odniesienia: docs/PRODUCT_STRATEGY.md, docs/BASELINE_AUDIT.md, docs/FIRST_CUSTOMER_PLAYBOOK.md.
Regresje: python scripts/audit_baseline.py lub python -m unittest discover -s tests -v. Kod 0 oznacza przejście testów automatycznych, nie potwierdzenie popytu ani pilota. Pierwotny audyt zachowuje obserwacje sprzed napraw; bieżący stan opisuje docs/IMPLEMENTATION_STATUS.md.
