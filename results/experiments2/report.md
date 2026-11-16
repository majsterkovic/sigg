# Kolejne eksperymenty i ETF-y — 16.11.2026

## Wnioski

Wykonano **644 symulacje akcyjne i 160 wyników strategii ETF/mix**. Mix wymaga dodatkowo ośmiu obliczeń akcyjnego subportfela 10 tys. zł. Zapisano wszystkie wyniki i zachowano serię pierwszą. Protokół: [round2_plan.md](../../research/round2_plan.md); dziennik: [notatki.md](../../research/notatki.md). Okna trwają około czterech miesięcy, nie rok.

Najciekawszym kolejnym kandydatem jest **combo z momentum 126 sesji i WIG > MA200**: średnia +24,59%, najgorsze okno -12,60%, wobec +17,28% i -35,06% obecnego podium. Ma jednak niższą medianę (+4,13% wobec +11,99%). Po wspólnej korekcie dla obu serii p=0,241 — przewaga nie została potwierdzona.

Jedna spółka + MA200 ma najwyższą średnią +27,55%, ale wynik +275,58% w oknie 2003 silnie ją podnosi. W latach 2013–2025 średnia wynosi tylko +12,97%. Wybór najlepszego wariantu na wcześniejszych latach również osiąga +12,97%, mniej od +13,99% bazy. Dalsze przeszukiwanie parametrów nie musi poprawiać przyszłych decyzji.

ETF-y są użyteczne do dywersyfikacji i badania defensywnej części portfela. W porównywalnych oknach 2022–2025 badane strategie ETF nie pobiły podium. Dla ETFBCASH dostępne są tylko dwa pełne okna po zmianie polityki, a w rotacji dodatnie mom3 / BCASH **nie doszło do żadnego zakupu BCASH**: ten wariant nie przetestował skuteczności ochrony w bessie. Nie ma podstaw do wnioskowania o szansach na konkursowe top 3.

## Akcje: pełna siatka wrażliwości

Wszystkie reguły poza jedną zmienianą cechą zachowują koszyk płynności 21–140, próg 300 tys. zł, pełne akcje, prowizję 0,39%, decyzję t−1 i open t. Bufor=2N. Wariant mom6 zmienia wyłącznie składnik momentum w combo: rank(hi52)+rank(P/P.shift(126)−1), a filtr MA200 pozostaje taki jak w punkcie odniesienia.

| Wariant | Średnia 2003–2025 | Mediana | Najgorsze okno | Straty / 23 | >40% / 23 | Średnia 2013–2025 | Średnia przy koszcie 0,60% |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 spółka + MA200 | +27,55% | +3,59% | -30,93% | 6 | 7 | +12,97% | +26,51% |
| combo z mom6 + MA200 | +24,59% | +4,13% | -12,60% | 4 | 5 | +22,34% | +23,86% |
| 1 spółka | +23,77% | +6,01% | -31,22% | 11 | 7 | +9,86% | +22,49% |
| combo z mom3 bez ostatniego miesiąca + MA200 | +22,18% | +5,56% | -16,76% | 4 | 4 | +18,75% | +21,46% |
| podium + MA200 | +20,84% | +11,99% | -21,15% | 5 | 4 | +17,29% | +20,11% |
| podium + MA300 | +17,92% | +7,01% | -21,15% | 4 | 4 | +12,13% | +17,24% |
| podium obecne | +17,28% | +11,99% | -35,06% | 8 | 4 | +13,99% | +16,44% |
| podium + MA100 | +17,23% | +11,99% | -44,80% | 6 | 4 | +12,58% | +16,53% |
| przegląd 42 sesje + MA200 | +17,23% | +14,23% | -32,95% | 5 | 5 | +12,69% | +16,82% |
| 5 spółek + MA200 | +16,85% | +7,00% | -16,99% | 6 | 4 | +15,01% | +16,25% |
| przegląd 42 sesje | +16,17% | +14,34% | -24,32% | 8 | 5 | +12,01% | +15,66% |
| 5 spółek | +16,01% | +16,78% | -27,36% | 9 | 4 | +14,20% | +15,30% |
| przegląd 10 sesji + MA200 | +14,96% | +6,12% | -25,58% | 6 | 3 | +13,14% | +13,78% |
| przegląd 10 sesji | +13,63% | +7,70% | -29,37% | 9 | 3 | +12,63% | +12,25% |

Najgorsze okno nie jest maksymalnym obsunięciem w trakcie gry. Próg +40% nie jest prawdopodobieństwem nagrody. Zwiększenie kosztu to test wrażliwości, nie model konkretnego spreadu.

### Wielokrotne testy i wynik spoza lat treningowych

Łączna rodzina ma 24 unikalne konfiguracje, czyli 23 alternatywy wobec podium. Punkty odniesienia wspólne dla obu serii są usunięte z duplikatów. Test zamiany znaków/max-T i bootstrap: 100 tys. losowań, seed 20261116, parowanie po latach. Zakładają niezależne roczne wektory różnic i symetrię pod hipotezą zerową. Korekta **nie obejmuje** pierwotnych 88 koszyków ani wszystkich dawnych badań.

| Wariant | Zmiana średniej wobec podium | 90% bootstrap | p nominalne | p max-T (obie serie) | Zmiana 2013–2025 | p max-T 2013–2025 |
|---|---:|---|---:|---:|---:|---:|
| 1 spółka + MA200 | +10,27 pp | [-4,29 pp; +27,71 pp] | 0,189 | 0,783 | -1,02 pp | 1,000 |
| combo z mom6 + MA200 | +7,30 pp | [+1,49 pp; +13,19 pp] | 0,029 | 0,241 | +8,36 pp | 0,473 |
| combo z mom3 bez ostatniego miesiąca + MA200 | +4,90 pp | [-0,56 pp; +10,54 pp] | 0,087 | 0,566 | +4,76 pp | 0,765 |
| podium + MA200 | +3,56 pp | [+0,59 pp; +7,10 pp] | 0,044 | 0,367 | +3,31 pp | 0,783 |

Po wyłączeniu **tego samego** najlepszego roku 2003: jedna spółka + MA200 +16,28%, podium +14,41%. W ekstremalnym oknie silnik kupował Boryszew (BRS), a potem MCI. Sprawdzenie dziennika nie wykazało zdarzenia split/delist w tym portfelu; nie jest to niezależne potwierdzenie cen dostawcy. Nie usuwano tego okna z głównego wyniku.

Walk-forward z treningiem 2003..y−1, testy 2013–2025, wybór najwyższej średniej z całych 24 konfiguracji: +12,97% wobec +13,99% podium, różnica -1,02 pp. Każdorazowo wybrana została jedna spółka + MA200, głównie wskutek mocnego dawnego wyniku. Wyniki i wybory: `combined_walk_forward.csv`. To retrospektywna walidacja, nie nienaruszona próba; parametry obu serii powstały po wcześniejszym oglądaniu rynku.

## Które ETF-y są dostępne i co mamy w danych?

Lista gry zawiera 32 ISIN-y ETF. Inwentaryzacja obejmuje wszystkie: 20 warszawskich szeregów PLN, 3 mapowania WAR z głównym tickerem zagranicznym (ETFDAX, ETFSP500, ETFNATO) i 9 instrumentów bez warszawskiego mapowania w bazie. **Brak mapowania/danych nie znaczy, że ETF jest niedostępny w grze.** Obce notowania nie są użyte jako warszawskie open lub obrót. Pełna tabela: `etf_inventory.csv`.

- Akcje polskie: BETA na WIG20, mWIG40, sWIG80 oraz dywidendy; są także produkty PZU. WIG20 w tym eksperymencie to jawne rozszerzenie koszyka akcyjnego, który wykluczał największe spółki.
- Akcje zagraniczne: m.in. BETA S&P500 i Nasdaq-100 PLN-Hedged, ETFDAX, ETFSP500, PZU MSCI World. PLN w cenie notowania samo w sobie nie oznacza zabezpieczenia walutowego; oba testowane fundusze BETA mają PLN-Hedged w nazwie. [Emitent BETA](https://betaetf.pl/nasze-fundusze).
- Obligacje: ETFBCASH (zmiennokuponowe) i ETFBTBSP (stałokuponowe/zerokuponowe), a także nowe ETFPZUCASH i ETFPZULONGDUR. TBSP oraz długoterminowe obligacje mogą tracić przy wzroście rentowności; nie są gotówką. [Karta TBSP](https://agiofunds.pl/wp-content/uploads/2026/01/Factsheet-BETA-ETF-TBSP.pdf), [debiut PZU 03.08.2026](https://in.pzu.pl/aktualnosci/szczegoly/debiut-etfow-obligacyjnych-tfi-pzu-na-gpw).
- Produkty tematyczne i alternatywne: obronność, drony, górnicy miedzi/złota/uranu, odbudowa Ukrainy, infrastruktura energii, strategie opcyjne, złoto i Bitcoin. Lista ISIN obejmuje te ekspozycje, ale nie zbadaliśmy ich wszystkich. Fundusz kopalń złota nie jest tym samym co fizyczne złoto. [Dokument emitenta funduszu górniczego](https://hanetf.com/wp-content/assets/upload/12-25-Factsheet-ESGO-IE00BNTVVR89-en.pdf).
- Dźwignia i short są dostępne, ale pozostają poza tym testem. Dźwignia indeksu dotyczy dziennych zwrotów; trzymanie kilka miesięcy nie daje po prostu 2× lub 3× skumulowanego wyniku. [Metodyka Nasdaq](https://indexes.nasdaqomx.com/docs/methodology_NDXLeveragedInverse.pdf).

**Pułapka ETFBCASH:** ISIN PLBETWT00010 był wcześniej ETF-em WIGtech. Dane zaczynają się 07.06.2021, lecz historię obligacji dopuszczamy dopiero od 02.01.2024 i od nowa liczymy okres momentum. [Komunikat emitenta](https://betaetf.pl/aktualnosci/beta-etf-obligacji-6m-nowy-fundusz-w-ofercie-beta-etf-juz-dziala), [potwierdzenie daty](https://betasecurities.pl/beta-etf-obligacji-6m-juz-na-rynku). Zastosowanie starej historii WIGtech jako „bezpiecznej gotówki” zafałszowałoby eksperyment.

### Płynność testowanych funduszy

Poniżej mediana C×V z ostatnich 63 sesji **do 26.10.2026**, nie bieżący stan 13.11. To wartość przybliżona, nie wolumen aukcji otwarcia ani dzisiejsza oferta animatora. W backteście próg liczymy każdorazowo do t−1.

| ETF | Mediana obrotu (tys. zł) | Początek szeregu |
|---|---:|---|
| ETFBCASH | 1876.0 | 2021-06-07 (WIGtech; obligacje od 2024) |
| ETFBM40TR | 2445.2 | 2019-09-05 |
| ETFBNDXPL | 635.1 | 2021-02-08 |
| ETFBS80TR | 1050.1 | 2021-12-14 |
| ETFBSPXPL | 406.5 | 2021-03-15 |
| ETFBTBSP | 515.6 | 2022-01-17 |
| ETFBW20TR | 2576.9 | 2019-01-08 |

Dzienne wolumeny nie potwierdzają, że zlecenie całych 20 tys. zł wykonałoby się na otwarciu. Próg 50 tys. zł oznacza pozycję równą nawet 40% tej mediany obrotu; płynność na konkretnej aukcji może być znacznie mniejsza. Dla ETF potrzebujemy również spreadów, kwotowań animatora i rzeczywistych transakcji. Filtr 300 tys. jest ostrożniejszy, ale historycznie często eliminuje fundusze. Nie dodajemy TER do kosztów ponownie: opłaty są już w cenie/NAV.

## Backtesty ETF na wspólnych okresach

Rotacja wybiera jeden ETF, inwestując dostępny kapitał w jeden slot, z przeglądem co 21 sesji i buforem 1. Momentum liczone na 63 sesjach, minimum 64 ceny; nie ma sztucznego przedłużania historii przed debiutem. Dodatnie momentum odrzuca wartości ≤0. BCASH jest dopuszczony jako zastępstwo tylko z dodatnim momentum i odpowiednią płynnością. Wariant WIG używa MA200 do przełączenia ekspozycji akcyjnej na BCASH/gotówkę. Nie jest to pełny zamiennik gotówki w portfelu trzech spółek. Mix to dwa subportfele po 10 tys. zł, bez transferów pomiędzy nimi.

Wyniki poniżej uwzględniają koszt 0,39%. **Kup i trzymaj jest warunkowe:** jeżeli na pierwszym sygnale fundusz nie spełnia progu obrotu, całe okno pozostaje w gotówce. Kolumna „okna bez transakcji” ujawnia te zera, które nie są stopą zwrotu samego ETF. Wycenę końcową wykonujemy po close bez wymuszonej sprzedaży. Nie są to roczne stopy zwrotu.

### Okna 2022-2025

| Wariant | Średnia: próg 300 tys. | Najgorsze: 300 tys. | Okna bez transakcji | Średnia: próg 50 tys. | Najgorsze: 50 tys. |
|---|---:|---:|---:|---:|---:|
| kup i trzymaj ETFBM40TR | +3,71% | +0,00% | 2/4 | +11,10% | +2,51% |
| kup i trzymaj ETFBNDXPL | +0,00% | +0,00% | 4/4 | +1,72% | -5,32% |
| kup i trzymaj ETFBS80TR | +0,52% | +0,00% | 3/4 | +10,54% | +2,06% |
| kup i trzymaj ETFBSPXPL | +0,00% | +0,00% | 4/4 | +1,57% | -5,63% |
| kup i trzymaj ETFBTBSP | -0,05% | -0,21% | 3/4 | +1,59% | -0,21% |
| kup i trzymaj ETFBW20TR | +10,20% | +3,29% | 0/4 | +10,20% | +3,29% |
| rotacja mom3 | +6,86% | +2,44% | 0/4 | +4,83% | +0,66% |
| rotacja dodatnie mom3 | +6,53% | +2,44% | 0/4 | +4,83% | +0,66% |
| Porównanie: podium obecne | +36,05% | +29,31% | 0/4 | — | — |
| Porównanie: podium + MA200 | +33,89% | +20,69% | 0/4 | — | — |

### Okna 2024-2025

| Wariant | Średnia: próg 300 tys. | Najgorsze: 300 tys. | Okna bez transakcji | Średnia: próg 50 tys. | Najgorsze: 50 tys. |
|---|---:|---:|---:|---:|---:|
| kup i trzymaj ETFBCASH | +0,50% | +0,00% | 1/2 | +1,07% | +1,00% |
| kup i trzymaj ETFBM40TR | +7,41% | +2,51% | 0/2 | +7,41% | +2,51% |
| kup i trzymaj ETFBNDXPL | +0,00% | +0,00% | 2/2 | -3,96% | -5,32% |
| kup i trzymaj ETFBS80TR | +1,03% | +0,00% | 1/2 | +6,04% | +2,06% |
| kup i trzymaj ETFBSPXPL | +0,00% | +0,00% | 2/2 | -3,23% | -5,63% |
| kup i trzymaj ETFBTBSP | -0,10% | -0,21% | 1/2 | -0,02% | -0,21% |
| kup i trzymaj ETFBW20TR | +13,98% | +9,10% | 0/2 | +13,98% | +9,10% |
| 50% podium MA200 + 50% ETF / BCASH | +21,86% | +15,94% | 0/2 | +17,58% | +10,63% |
| rotacja mom3 | +10,86% | +9,10% | 0/2 | +1,61% | +0,66% |
| rotacja dodatnie mom3 | +10,19% | +9,10% | 0/2 | +1,61% | +0,66% |
| dodatnie mom3 / BCASH | +10,19% | +9,10% | 0/2 | +1,61% | +0,66% |
| WIG MA200: rotacja / BCASH | +6,96% | +4,81% | 0/2 | +1,48% | +0,40% |
| Porównanie: podium obecne | +37,95% | +29,31% | 0/2 | — | — |
| Porównanie: podium + MA200 | +33,64% | +20,69% | 0/2 | — | — |

### Czy ETFBCASH poprawił parkowanie środków?

Nie wykazaliśmy tego. W `positive_cash` liczba zakupów BCASH wyniosła zero przy obu progach płynności: w datach przeglądów pozostał przynajmniej jeden dopuszczalny ETF z dodatnim momentum. W `wig_cash` BCASH został kupiony raz przy progu 50 tys. i ani razu przy 300 tys. Zbyt mało obserwacji, by oszacować efekt ochrony. Wyniki „rotacji z BCASH” nie są dowodem korzyści z BCASH.

W obu pełnych oknach 2024 i 2025 samo kup i trzymaj BCASH przy progu 50 tys. dało około +1,07% średnio po prowizji zakupu. Przy progu 300 tys. jedno okno zostało całkowicie w gotówce. Przy koszcie 0,39% wejście i wyjście wymagają wzrostu ceny o (1+0,0039)/(1−0,0039)−1 = **0,783%**, żeby wyjść na zero (bez spreadu). To istotne przy parkowaniu tylko na kilka tygodni; końcowy portfel gry nie musi być sprzedany, więc wtedy pozostaje tylko koszt zakupu.

## Kontrole, pliki i ograniczenia

- Punkty odniesienia odtworzone dla obu kosztów: maksymalna różnica 0 (92 porównania).
- Diagnostyka części ETF: stare wyceny 0, niewykonane sprzedaże 0, niewykonane zakupy 0. Są to kontrole dziennych danych, nie potwierdzenie wykonania w grze.
- Niezależne przeliczenie 104 wariantów kup i trzymaj bez silnika: floor(20000/(open×(1+c))), reszta w gotówce, końcowe close. Maksymalna różnica zwrotu 2,22e−16. Wynik kontroli: `validation.json`.
- 29 testów jednostkowych zaliczonych, w tym odcięcie WIGtech, brak niepłynnego fallbacku i przełączenie całego pojedynczego slotu po cenie otwarcia następnej sesji.
- Surowe dane EODHD z prywatnej bazy pozostają poza repo. Repo zawiera metadane, pochodne statystyki i listę decyzji bez dziennych cen. Dołączenie ETF nie oznacza zgody dostawcy na redystrybucję jego szeregów.
- Wykorzystano aktualnie wybrane fundusze, nie kompletną historyczną listę SIGG. Występuje ryzyko selekcji instrumentów, które przetrwały; nie symulowano wszystkich dawnych ETF. Dane cen ETF nie zostały niezależnie uzgodnione z drugim źródłem. Nowe fundusze z 2026 nie mają zakończonego okna gry.
- Dziedziczone ograniczenia akcji: niepełny rejestr zawieszeń/wycofań, niepewność danych i korekt, proxy indeksów/NC, brak częściowych wykonań i wolumenu aukcji. Zwiększenie liczby eksperymentów nie usuwa tych ograniczeń.
- Nie zmieniono na podstawie eksperymentów operacyjnego podium, listy zakupów ani strony. Brak danych konkurentów uniemożliwia obliczenie prawdopodobieństwa top 3.

Pliki: `stock_years.csv` (644 wiersze), `stock_stats.csv`, `combined_years.csv` (obie serie bez powtórzeń), `combined_paired_all.csv`, `combined_paired_late.csv`, `combined_walk_forward.csv`, `etf_years.csv` (160 wierszy), `etf_stats.csv`, `etf_inventory.csv` (32 ISIN), `etf_trade_choices.csv`; manifesty zawierają SHA256 protokołu, kodu i prywatnych wejść.

```bash
export SIGG_DATA_DIR=/prywatny/katalog/snapshotu
export SIGG_ENV_FILE=/sciezka/do/prywatnego/.env
# Bez GPW_SUFFIX; historyczne macierze A/C/O/V oraz idx z README.
python research/load_etfs.py
OPENBLAS_NUM_THREADS=1 python research/backtest_round2.py
OPENBLAS_NUM_THREADS=1 python research/backtest_etfs.py
python research/report_round2.py
python -m unittest discover -s tests -p "test_*.py" -v
```

Wynik: momentum 6 miesięcy + MA200 warto obserwować dalej, lecz nie ogłaszamy nowego zwycięzcy. ETF-y są sensowną odrębną hipotezą dywersyfikacji/ochrony; obecne próbki nie dowodzą, że zwiększają szansę na nagrodę.
