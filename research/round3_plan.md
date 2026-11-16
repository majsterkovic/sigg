# Trzecia seria — ETF-y z listy gry: S&P 500 i złoto — 16.11.2026

Reguły zapisane przed uruchomieniem wyników serii. Powód: lista gry zawiera także ETF-y na S&P 500 i złoto, a seria 2 przetestowała tylko 7 funduszy z danymi w bazie. Seria jest eksploracyjna; nie zmieniamy operacyjnych list zakupów.

## Dane

- Źródłem jest Yahoo Finance (kod `<KOD>.WA`, notowania GPW w PLN), pobrane skryptem `research/fetch_yf_etf.py` do prywatnego katalogu `SIGG_DATA_DIR`. Surowe ceny nie trafiają do repo.
- Kontrola niezależności: dla 7 funduszy z serii 2 porównujemy zamknięcia, otwarcia i wolumeny Yahoo z bazą. Odrzucamy źródło, jeżeli więcej niż 1% wspólnych sesji różni się o ponad 0,5% w cenie.
- ETFSP500 (Lyxor S&P 500, ISIN LU0496786574) w bazie ma tylko notowanie XETRA. Użyjemy warszawskiego szeregu Yahoo (od 26.03.2010). Fundusz wypłaca dywidendy (wypłaty z Yahoo, od 2014); silnik księguje je gotówką. Sesje z wolumenem 0 oznaczają brak transakcji; cena z takich dni nie służy do zlecenia.
- Złoto: ETFPZUGOLD ma notowania dopiero od 11.05.2026 (brak zakończonego okna listopad–marzec). Nie testujemy go jako funduszu. Dla złota robimy tylko opis proxy: GC=F razy PLN=X (Yahoo), buy-and-hold w oknach 2003–2025. Proxy nie zawiera kosztów funduszu ani spreadu kursowego; nie służy do wyboru strategii.
- Bitcoin (ETFBTCPL) ma jedno zakończone okno; poza testem.

## Strategie (tylko 3, bez nowych parametrów)

Okna listopad–marzec, 2010–2025 (16 okien), koszt 0,39% i 0,60%, kapitał 20 tys., pełne jednostki, otwarcie t, decyzja t−1. Próg obrotu mediany 63 sesji (min. 40 obserwacji): 300 tys. zł (podstawowy) i 50 tys. zł (słabszy filtr). Okno bez transakcji zostaje w gotówce i jest liczone osobno.

1. `hold_sp500`: kup i trzymaj ETFSP500 na pierwszej sesji okna.
2. `mix50_sp500`: 10 tys. w podium + MA200 (silnik akcji z serii 1), 10 tys. w ETFSP500 kup i trzymaj. Oddzielne subportfele.
3. `wig_sp500`: gdy WIG > MA200, podium akcyjne (N=3, bufor=6, krok=21, koszyk 21–140, próg akcji 300 tys.); gdy WIG ≤ MA200, cały kapitał w ETFSP500 (jeżeli spełnia próg obrotu), w przeciwnym razie gotówka.

Punkty odniesienia z tych samych lat i kosztów, bez przeliczania: podium obecne i podium + MA200 z `results/experiments2/combined_years.csv`.

## Raport

Dla każdej strategii i progu: średnia, mediana, najgorsze okno, liczba strat, liczba okien bez transakcji, średnia różnica parowana wobec podium i podium + MA200 z 90% przedziałem bootstrap (seed 20261116, 100 tys. losowań, parowanie po latach) oraz liczba okien, w których strategia wygrywa. Nie podajemy p-wartości ani szans top 3: 16 okien, 3 strategie i 2 progi, nakładające się ze znanymi już latami. Dodatkowo: wynik osobno dla okien, w których ETFSP500 spełniał próg 300 tys. (okno wspólne), bo wcześniejsze lata mają tak mały obrót, że zlecenie 20 tys. nie jest realne.

Proxy złota: średnia, mediana, najgorsze okno, korelacja z wynikami podium (23 lata) i średni wynik złota w 5 najgorszych oknach podium oraz w oknach, w których WIG ≤ MA200 na starcie.

## Znane ograniczenia przed obliczeniami

Dane Yahoo nie są wolumenem aukcji. Brak spreadów, brak animatora, jedno źródło dla ETFSP500 (kontrola tylko dla 7 funduszy z bazy). Fundusz to jedna ekspozycja (USA), wybrana, ponieważ użytkownik wskazał go jako dostępny w grze. Lata przed 2020 mają niewielki obrót. Nie wyciągamy wniosku o najlepszym ETF z całej listy.

## Dodatek 16.11.2026, zapisany po wynikach S&P 500 i opisie proxy złota, przed testem strategii ze złotem

Opis proxy pokazał ujemną korelację złota z podium. Ponieważ ETFPZUGOLD nie ma historii, test ze złotem opiera się wyłącznie na proxy GC=F × PLN=X i jest oznaczony jako proxy. Dokładnie 3 strategie, bez nowych parametrów, okna 2003–2025 (23), koszt 0,39% i 0,60%, bez progu obrotu (proxy nie ma wolumenu):

1. `hold_gold`: cały kapitał w złocie na pierwszej sesji.
2. `mix50_gold`: 10 tys. w podium + MA200, 10 tys. w złocie kup i trzymaj.
3. `wig_gold`: gdy WIG > MA200, podium akcyjne; gdy WIG ≤ MA200, cały kapitał w złocie.

Cena wejścia = zamknięcie poprzedniej sesji proxy (brak otwarcia); wycena = zamknięcie. Brak kosztu funduszu i spreadu walutowego. Ten sam raport co dla S&P 500, bez p-wartości. Wynik nie służy do zmiany list zakupów: fundusz ma tylko 133 sesje historii.

## Dodatek 16.11.2026: dźwignia 2x na mWIG40 i WIG20, szereg syntetyczny, zapisany przed testem strategii

Powód: ETFBM40LV (od 08.04.2026) i ETFBNQ3LV nie mają historii, ETFBW20LV ma sześć okien. Użytkownik wskazał, że dźwignię można odtworzyć z dziennych zwrotów indeksu.

Szereg: zwrot dnia = 2 × (zwrot indeksu + d/252) − c/252. Indeks z `idx.parquet` (mWIG40 od 09.03.2011, WIG20 od 1994; to indeksy bez dywidend), d = 2,5% rocznie dla mWIG40 i 2,7% dla WIG20 (średnia różnica ETFBM40TR i ETFBW20TR wobec indeksu, 2019–2026). c (finansowanie + opłaty) kalibrujemy raz tak, by łączny wynik 2×WIG20 zgadzał się z ETFBW20LV w okresie 26.02.2020–26.10.2026; po kalibracji c jest stałe. Wrażliwość c = 3% i 10%. Walidacja poza próbą: ten sam wzór dla mWIG40 względem ETFBM40LV (08.04.–26.10.2026, 140 sesji).

Strategie (4, bez nowych parametrów): `lev_hold` (kup i trzymaj, cały kapitał), `lev_ma200` (co 21 sesji: gdy WIG > MA200 pozycja w funduszu, w przeciwnym razie gotówka). Dla mWIG40 i WIG20. Okna 2011–2025 (mWIG40) i 2003–2025 (WIG20), prowizja 0,39% przy każdym zakupie i sprzedaży w trakcie okna, bez sprzedaży końcowej, ułamki jednostek dozwolone (szereg nie ma ceny jednostki). Porównanie z podium i podium + MA200 w tych samych latach, 90% bootstrap parowany, bez p-wartości. Wynik jest opisowy: szereg syntetyczny nie jest funduszem, a ETFBM40LV nie ma jeszcze zakończonego okna.
