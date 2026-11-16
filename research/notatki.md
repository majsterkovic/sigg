# Dziennik badań SIGG

## 16.11.2026 — seria 1 (zakończona)

12 konfiguracji, 552 symulacje. WIG > MA200 poprawił średnią podium z 17,28% do 20,84%, lecz max-T p=0,183 i duży udział dwóch okien kryzysowych nie pozwalają uznać przewagi za potwierdzoną. Korelacja 0,70 nie zmieniła wyników podium. Szczegóły: `results/experiments/report.md`. Wyników nie nadpisujemy kolejną serią.

## 16.11.2026 — seria 2, przed wynikami

Protokół: `research/round2_plan.md`. Celem jest zbadanie wrażliwości dotychczasowej poprawy oraz wykorzystania ETF-ów z listy SIGG. Nowe parametry nie będą dodawane po odczycie wyników.

Ustalenie danych: ETFBCASH ma ten sam ISIN co dawny WIGtech. Historia w bazie od 07.06.2021 nie jest historią funduszu obligacji. Odcięcie przed 02.01.2024 jest konieczne. Źródło: [komunikat emitenta](https://betaetf.pl/aktualnosci/beta-etf-obligacji-6m-nowy-fundusz-w-ofercie-beta-etf-juz-dziala).

Ustalenie danych: 3 instrumenty z warszawskim listingiem mają ref_ticker XETRA. Klucz instrument_id bez identyfikatora notowania nie wystarcza do potwierdzenia miejsca, waluty i płynności transakcji. Nie używamy tych szeregów do symulacji GPW.

## 16.11.2026 — seria 2, wyniki i decyzje

Zakończono 644 symulacje akcyjne i 160 wyników strategii ETF/mix (oraz 8 obliczeń akcyjnej połowy mix). Pełny raport: `results/experiments2/report.md`; zachowano parametry, wszystkie roczne wyniki, wybory ETF i sumy kontrolne wejść. 29 testów przeszło.

- Combo z mom6 + MA200: średnia +24,59%, mediana +4,13%, najgorsze okno −12,60%; późniejsze 2013–2025 +22,34%. Obiecujący kierunek, lecz wspólna korekta 23 alternatyw daje p=0,241. Brak podstaw do ogłoszenia zwycięzcy.
- Jedna spółka + MA200: średnia +27,55% zawiera +275,58% w oknie 2003 (BRS, potem MCI). Późniejsza średnia tylko +12,97%. Automatyczny wybór największej średniej z przeszłości również daje +12,97% wobec +13,99% bazy. Nie wybieramy koncentracji na jednej spółce na podstawie tej średniej.
- Częstszy przegląd (10 sesji) pogarsza wynik i zwiększa koszty. MA100 nie chroni podobnie jak MA200; wynik filtra trendu nie jest odporny na dowolny dobór okresu. Nie dostrajamy parametrów po tej obserwacji.
- 32 ETF-y z listy gry: 20 szeregów WAR/PLN, 3 z główną giełdą zagraniczną, 9 bez mapowania WAR. Nowe produkty PZU i część BETA mają za krótką historię. Inwentaryzacja nie jest rankingiem rekomendacji; dane obrotów kończą się 26.10, nie 13.11.
- ETF-y w testach nie pobiły akcji na tych samych latach. W 2022–2025 samo WIG20TR po prowizji dało średnio +10,20%, rotacja mom3 +6,86% (próg 300 tys.), podium +36,05%. To tylko 4 okna, a zwycięstwo akcji nie jest dowodem przyszłej przewagi.
- BCASH bez historii WIGtech ma dwa zakończone pełne okna. Przy progu 50 tys. kup i trzymaj dało średnio +1,07%; przy 300 tys. jeden rok pozostał w gotówce. W strategii dodatnie momentum / BCASH nie kupiono BCASH ani razu; wynik nie ocenia więc jego ochrony. W wariancie WIG / BCASH tylko jeden zakup przy progu 50 tys. Brakuje prób obejmujących pełny spadkowy okres rynku z istniejącym już ETFBCASH.
- Rzeczywista cena parkowania: prowizja 0,39% na wejściu i wyjściu wymaga wzrostu ceny o 0,783% do wyjścia na zero, przed spreadem. Nie zastępujemy automatycznie gotówki obligacjami na każdą krótką przerwę.

Operacyjne listy i strona pozostają oparte na dotychczasowych zasadach. Dalsza praca powinna dotyczyć niezależnej walidacji cen ETF, warszawskich danych brakujących funduszy, spreadów i aukcji oraz obserwacji reguł zapisanych teraz na nowych danych. Nie zwiększamy liczby parametrów tylko dlatego, że można uzyskać wyższą historyczną średnią.

## 16.11.2026 — seria 3 (S&P 500 i złoto z listy gry)

Protokół: `research/round3_plan.md` (dodatek ze złotem zapisany po wynikach S&P i opisie proxy, przed testem złota). Raport: `results/experiments3/report.md`.

- Dane: Yahoo `.WA` zgadza się z bazą dla 7 funduszy z serii 2 (0 różnic powyżej 0,5%). Warszawski szereg ETFSP500 (od 2010) pochodzi tylko z Yahoo; w bazie jest tylko XETRA.
- ETFSP500 miał przed 2018 r. zbyt mały obrót na zlecenie 20 tys. zł (8 z 16 okien bez transakcji przy progu 50 tys., 12 z 16 przy 300 tys.). W oknach 2018–2025 kup i trzymaj średnio −1,2%, podium +23,4%. wig_sp500 ≈ podium + MA200. Brak podstaw do dodawania S&P 500.
- ETFPZUGOLD ma 133 sesje, nie ma zakończonego okna. Na proxy GC=F × PLN=X: korelacja −0,31 z podium; wig_gold +23,4% wobec podium +17,3% (przedział 90% +0,9 do +12,7 pp) i podium + MA200 +20,8% (−0,3 do +6,5 pp). Hipoteza obrony, nie dowód (proxy, bez kosztów funduszu, rosnące złoto, kolejne warianty w rodzinie testów).
- Kolejny krok bez nowych parametrów: obserwować ETFPZUGOLD w grze na nowych danych i zebrać jego spread/animatora; dane warszawskie dla DAX, NATO i Bitcoin mają za krótką historię.
- Dźwignia 2x (syntetyczna, dodatek do serii 3): kalibracja c=5,4% na ETFBW20LV; poza próbą ETFBM40LV +49,0% rzeczywiście vs +44,8% w szeregu. 2×mWIG40: kup i trzymaj +10,1% (najgorsze −45,8%), z MA200 +11,8% (−19,9%), podium +13,2% w tych latach. 2×WIG20: +3,2% (−67,7%) i +8,4% z MA200 wobec podium +17,3%. Żadna wersja nie pobiła podium; dźwignia nie wchodzi do list zakupów.
