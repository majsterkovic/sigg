# Druga seria eksperymentów — 16.11.2026

Reguły zapisane przed uruchomieniem wyników serii. Badanie jest eksploracyjne: wcześniejsze wyniki tych lat są znane. Nie zmieniamy operacyjnych list zakupów.

## Akcje

Punkty odniesienia: podium bez filtra i z WIG > MA200, N=3, bufor=6, krok=21. Zmieniamy pojedynczy element:
- N=1 lub 5 (bufor=2N), osobno bez filtra i z MA200: 4 warianty.
- Krok=10 lub 42 sesje, osobno bez filtra i z MA200: 4 warianty.
- Średnia WIG=100 lub 300, pozostałe parametry jak podium: 2 warianty.
- Combo z momentum 126 sesji albo momentum 63 sesji pomijającym ostatnie 21 (P[t-21]/P[t-84]-1), z MA200: 2 warianty.

Łącznie 14 konfiguracji, 23 okna listopad–marzec 2003–2025, dwa koszty 0,39% i 0,60% = 644 symulacje. Koszyk 21–140, próg 300 tys., min_n=max(5,N), ten sam silnik, sygnał t-1. Zapis wszystkich wyników, nie tylko zwycięzcy. Korekta max-T wspólna z pierwszą serią (po usunięciu powtórzonych konfiguracji), także późniejszy okres 2013–2025. Wybór kroczący wyłącznie z przeszłych lat. To nie obejmuje pierwotnych 88 koszyków ani wszystkich wcześniejszych prób.

## ETF-y

Najpierw audyt ISIN i historii. Dopuszczamy wyłącznie rzeczywiste szeregi GPW w PLN, bez podstawiania zagranicznej giełdy albo indeksu przed debiutem funduszu. Aktualna lista gry potwierdza dzisiejszą dostępność, nie historyczną. ETFBCASH przed 2024-01-02 odcinamy: był WIGtech, co potwierdza emitent. Fundusze debiutujące w 2026 nie mają pełnego zakończonego okna gry i pozostają w inwentaryzacji.

Koszyk akcyjny ETF bez dźwigni: ETFBW20TR, ETFBM40TR, ETFBS80TR, ETFBSPXPL, ETFBNDXPL. Nie stosujemy do nich rankingu obrotu akcji 21–140: ekspozycja WIG20 jest jawnym rozszerzeniem mandatu badawczego. Reguły:
- kup i trzymaj każdy dostępny fundusz (bez ponawiania zakupu w razie niewykonania na starcie);
- rotacja mom3: jeden najlepszy ETF (bufor 1), przegląd 21 sesji;
- rotacja mom3 dodatnie: jak wyżej, ujemny/niedostępny najlepszy sygnał oznacza gotówkę;
- mom3 dodatnie z parkowaniem w ETFBCASH; ETFBCASH musi mieć dodatni mom3;
- sam ETFBCASH i sam ETFBTBSP kup i trzymaj; TBSP nie jest odpowiednikiem gotówki;
- WIG > MA200: jeden najlepszy ETF akcyjny; poza trendem ETFBCASH (dodatni mom3) lub gotówka;
- pół kapitału w podium MA200, pół w rotacji ETF z dodatnim mom3 i ETFBCASH. Oddzielne subportfele po 10 tys., bez przesuwania środków między nimi w trakcie okna. To stała alokacja, nie inwestowanie całej gotówki podium w ETF.

ETF-y: min. 63 obserwacje do mom3, obrót mediana 63 sesji min40 obserwacji, dodatnie C/O/V. Podstawowy próg 300 tys. PLN; wrażliwość 50 tys. jest oznaczona jako słabszy filtr, a nie dowód realizowalności. Prowizje 0,39% i 0,60%, pełne jednostki, końcowa wycena bez przymusowej sprzedaży. Koszty funduszu zawarte w cenie, nie odejmujemy TER ponownie. Bez udawania wolumenu aukcji i bez dźwigni/short w tej serii.

Okna ETF 2022–2025 (wspólna historia starszego zestawu); porównania z parkowaniem BCASH i mix tylko 2024–2025, żeby nie przedstawiać WIGtech jako obligacji. Braki płynności oznaczają pozostawienie w gotówce; zapisujemy liczbę transakcji i faktyczne użycie BCASH. Nie dobieramy startu na podstawie wyników. Przy 2–4 oknach nie wyliczamy przekonującej istotności ani szans top3. Baza i MA200 porównywane w dokładnie tych samych latach.

## Znane ograniczenia przed obliczeniami

Baza ma 23 warszawskie mapowania spośród 32 pozycji ETF/ETP z listy gry, z czego 3 mają główne notowanie zagraniczne. Nie wolno uznać ich macierzy instrument_id za dane warszawskie. Brak pełnych danych części instrumentów będzie widoczny w tabeli dostępności. Dzienne OHLCV i niepełne zdarzenia korporacyjne zachowują ograniczenia poprzedniej serii. Nie wyciągamy z tej analizy wniosku o najlepszym ETF spośród wszystkich dostępnych.
