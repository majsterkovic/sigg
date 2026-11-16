"""Generate Polish notes from the saved second-series results."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/experiments2'
BASE='combo|liquidity-21-140|base';TREND='combo|liquidity-21-140|trend'
LABELS={BASE:'podium obecne',TREND:'podium + MA200','n1_ma200':'1 spółka + MA200','n1_ma0':'1 spółka','n5_ma200':'5 spółek + MA200','n5_ma0':'5 spółek','step10_ma200':'przegląd 10 sesji + MA200','step10_ma0':'przegląd 10 sesji','step42_ma200':'przegląd 42 sesje + MA200','step42_ma0':'przegląd 42 sesje','ma100':'podium + MA100','ma300':'podium + MA300','combo6':'combo z mom6 + MA200','combo_skip1':'combo z mom3 bez ostatniego miesiąca + MA200'}
ELABELS={'mom3':'rotacja mom3','positive':'rotacja dodatnie mom3','positive_cash':'dodatnie mom3 / BCASH','wig_cash':'WIG MA200: rotacja / BCASH','mix50':'50% podium MA200 + 50% ETF / BCASH'}
def pct(x):return f'{x*100:+.2f}%'.replace('.',',')
def pp(x):return f'{x*100:+.2f} pp'.replace('.',',')
def num(x):return f'{x:.3f}'.replace('.',',')
def elabel(v):return ELABELS.get(v,v.replace('hold_','kup i trzymaj '))
s=pd.read_csv(OUT/'stock_stats.csv');r=pd.read_csv(OUT/'stock_years.csv');paired=pd.read_csv(OUT/'combined_paired_all.csv').set_index('variant');late=pd.read_csv(OUT/'combined_paired_late.csv').set_index('variant')
a=s[(s.commission==.0039)&(s.period=='all')].set_index('variant');b=s[(s.commission==.0039)&(s.period=='late')].set_index('variant');core=r[r.commission==.0039]
wf=pd.read_csv(OUT/'combined_walk_forward.csv');w=wf[wf.commission==.0039]
es=pd.read_csv(OUT/'etf_stats.csv');er=pd.read_csv(OUT/'etf_years.csv');inv=pd.read_csv(OUT/'etf_inventory.csv');manifest=json.loads((OUT/'stock_manifest.json').read_text());em=json.loads((OUT/'etf_manifest.json').read_text())
best=core[(core.variant=='n1_ma200')].sort_values('ret',ascending=False).iloc[0]
cash_url='https://betaetf.pl/aktualnosci/beta-etf-obligacji-6m-nowy-fundusz-w-ofercie-beta-etf-juz-dziala'
lines=['# Kolejne eksperymenty i ETF-y — 16.11.2026','',
'## Wnioski','',
f'Wykonano **{manifest["simulations"]} symulacje akcyjne i {em["outcomes"]} wyników strategii ETF/mix**. Mix wymaga dodatkowo ośmiu obliczeń akcyjnego subportfela 10 tys. zł. Zapisano wszystkie wyniki i zachowano serię pierwszą. Protokół: [round2_plan.md](../../research/round2_plan.md); dziennik: [notatki.md](../../research/notatki.md). Okna trwają około czterech miesięcy, nie rok.','',
f'Najciekawszym kolejnym kandydatem jest **combo z momentum 126 sesji i WIG > MA200**: średnia {pct(a.loc["combo6","mean"])}, najgorsze okno {pct(a.loc["combo6","worst"])}, wobec {pct(a.loc[BASE,"mean"])} i {pct(a.loc[BASE,"worst"])} obecnego podium. Ma jednak niższą medianę ({pct(a.loc["combo6","median"])} wobec {pct(a.loc[BASE,"median"])}). Po wspólnej korekcie dla obu serii p={num(paired.loc["combo6","p_maxT"])} — przewaga nie została potwierdzona.','',
f'Jedna spółka + MA200 ma najwyższą średnią {pct(a.loc["n1_ma200","mean"])}, ale wynik {pct(best.ret)} w oknie {int(best.year)} silnie ją podnosi. W latach 2013–2025 średnia wynosi tylko {pct(b.loc["n1_ma200","mean"])}. Wybór najlepszego wariantu na wcześniejszych latach również osiąga {pct(w.ret.mean())}, mniej od {pct(w.baseline.mean())} bazy. Dalsze przeszukiwanie parametrów nie musi poprawiać przyszłych decyzji.','',
'ETF-y są użyteczne do dywersyfikacji i badania defensywnej części portfela. W porównywalnych oknach 2022–2025 badane strategie ETF nie pobiły podium. Dla ETFBCASH dostępne są tylko dwa pełne okna po zmianie polityki, a w rotacji dodatnie mom3 / BCASH **nie doszło do żadnego zakupu BCASH**: ten wariant nie przetestował skuteczności ochrony w bessie. Nie ma podstaw do wnioskowania o szansach na konkursowe top 3.','',
'## Akcje: pełna siatka wrażliwości','',
'Wszystkie reguły poza jedną zmienianą cechą zachowują koszyk płynności 21–140, próg 300 tys. zł, pełne akcje, prowizję 0,39%, decyzję t−1 i open t. Bufor=2N. Wariant mom6 zmienia wyłącznie składnik momentum w combo: rank(hi52)+rank(P/P.shift(126)−1), a filtr MA200 pozostaje taki jak w punkcie odniesienia.','',
'| Wariant | Średnia 2003–2025 | Mediana | Najgorsze okno | Straty / 23 | >40% / 23 | Średnia 2013–2025 | Średnia przy koszcie 0,60% |','|---|---:|---:|---:|---:|---:|---:|---:|']
for v in a.sort_values('mean',ascending=False).index:
 z=a.loc[v];high=s[(s.commission==.006)&(s.period=='all')&(s.variant==v)].iloc[0]
 lines.append(f'| {LABELS[v]} | {pct(z["mean"])} | {pct(z["median"])} | {pct(z.worst)} | {round(z.loss*23)} | {round(z.p40*23)} | {pct(b.loc[v,"mean"])} | {pct(high["mean"])} |')
lines+=['','Najgorsze okno nie jest maksymalnym obsunięciem w trakcie gry. Próg +40% nie jest prawdopodobieństwem nagrody. Zwiększenie kosztu to test wrażliwości, nie model konkretnego spreadu.','',
'### Wielokrotne testy i wynik spoza lat treningowych','',
f'Łączna rodzina ma {manifest["combined_unique_configurations"]} unikalne konfiguracje, czyli 23 alternatywy wobec podium. Punkty odniesienia wspólne dla obu serii są usunięte z duplikatów. Test zamiany znaków/max-T i bootstrap: 100 tys. losowań, seed 20261116, parowanie po latach. Zakładają niezależne roczne wektory różnic i symetrię pod hipotezą zerową. Korekta **nie obejmuje** pierwotnych 88 koszyków ani wszystkich dawnych badań.','',
'| Wariant | Zmiana średniej wobec podium | 90% bootstrap | p nominalne | p max-T (obie serie) | Zmiana 2013–2025 | p max-T 2013–2025 |','|---|---:|---|---:|---:|---:|---:|']
for v in ['n1_ma200','combo6','combo_skip1',TREND]:
 z=paired.loc[v];l=late.loc[v]
 lines.append(f'| {LABELS[v]} | {pp(z.gain)} | [{pp(z.ci90_low)}; {pp(z.ci90_high)}] | {num(z.p_one_sided)} | {num(z.p_maxT)} | {pp(l.gain)} | {num(l.p_maxT)} |')
worst_dropped=core[(core.variant=='n1_ma200')&(core.year!=best.year)].ret.mean();baseline_dropped=core[(core.variant==BASE)&(core.year!=best.year)].ret.mean()
lines+=['',f'Po wyłączeniu **tego samego** najlepszego roku {int(best.year)}: jedna spółka + MA200 {pct(worst_dropped)}, podium {pct(baseline_dropped)}. W ekstremalnym oknie silnik kupował Boryszew (BRS), a potem MCI. Sprawdzenie dziennika nie wykazało zdarzenia split/delist w tym portfelu; nie jest to niezależne potwierdzenie cen dostawcy. Nie usuwano tego okna z głównego wyniku.','',
f'Walk-forward z treningiem 2003..y−1, testy 2013–2025, wybór najwyższej średniej z całych 24 konfiguracji: {pct(w.ret.mean())} wobec {pct(w.baseline.mean())} podium, różnica {pp(w.gain.mean())}. Każdorazowo wybrana została jedna spółka + MA200, głównie wskutek mocnego dawnego wyniku. Wyniki i wybory: `combined_walk_forward.csv`. To retrospektywna walidacja, nie nienaruszona próba; parametry obu serii powstały po wcześniejszym oglądaniu rynku.','',
'## Które ETF-y są dostępne i co mamy w danych?','',
'Lista gry zawiera 32 ISIN-y ETF. Inwentaryzacja obejmuje wszystkie: 20 warszawskich szeregów PLN, 3 mapowania WAR z głównym tickerem zagranicznym (ETFDAX, ETFSP500, ETFNATO) i 9 instrumentów bez warszawskiego mapowania w bazie. **Brak mapowania/danych nie znaczy, że ETF jest niedostępny w grze.** Obce notowania nie są użyte jako warszawskie open lub obrót. Pełna tabela: `etf_inventory.csv`.','',
'- Akcje polskie: BETA na WIG20, mWIG40, sWIG80 oraz dywidendy; są także produkty PZU. WIG20 w tym eksperymencie to jawne rozszerzenie koszyka akcyjnego, który wykluczał największe spółki.',
'- Akcje zagraniczne: m.in. BETA S&P500 i Nasdaq-100 PLN-Hedged, ETFDAX, ETFSP500, PZU MSCI World. PLN w cenie notowania samo w sobie nie oznacza zabezpieczenia walutowego; oba testowane fundusze BETA mają PLN-Hedged w nazwie. [Emitent BETA](https://betaetf.pl/nasze-fundusze).',
f'- Obligacje: ETFBCASH (zmiennokuponowe) i ETFBTBSP (stałokuponowe/zerokuponowe), a także nowe ETFPZUCASH i ETFPZULONGDUR. TBSP oraz długoterminowe obligacje mogą tracić przy wzroście rentowności; nie są gotówką. [Karta TBSP](https://agiofunds.pl/wp-content/uploads/2026/01/Factsheet-BETA-ETF-TBSP.pdf), [debiut PZU 03.08.2026](https://in.pzu.pl/aktualnosci/szczegoly/debiut-etfow-obligacyjnych-tfi-pzu-na-gpw).',
'- Produkty tematyczne i alternatywne: obronność, drony, górnicy miedzi/złota/uranu, odbudowa Ukrainy, infrastruktura energii, strategie opcyjne, złoto i Bitcoin. Lista ISIN obejmuje te ekspozycje, ale nie zbadaliśmy ich wszystkich. Fundusz kopalń złota nie jest tym samym co fizyczne złoto. [Dokument emitenta funduszu górniczego](https://hanetf.com/wp-content/assets/upload/12-25-Factsheet-ESGO-IE00BNTVVR89-en.pdf).',
'- Dźwignia i short są dostępne, ale pozostają poza tym testem. Dźwignia indeksu dotyczy dziennych zwrotów; trzymanie kilka miesięcy nie daje po prostu 2× lub 3× skumulowanego wyniku. [Metodyka Nasdaq](https://indexes.nasdaqomx.com/docs/methodology_NDXLeveragedInverse.pdf).','',
f'**Pułapka ETFBCASH:** ISIN PLBETWT00010 był wcześniej ETF-em WIGtech. Dane zaczynają się 07.06.2021, lecz historię obligacji dopuszczamy dopiero od 02.01.2024 i od nowa liczymy okres momentum. [Komunikat emitenta]({cash_url}), [potwierdzenie daty](https://betasecurities.pl/beta-etf-obligacji-6m-juz-na-rynku). Zastosowanie starej historii WIGtech jako „bezpiecznej gotówki” zafałszowałoby eksperyment.','',
'### Płynność testowanych funduszy','',
'Poniżej mediana C×V z ostatnich 63 sesji **do 26.10.2026**, nie bieżący stan 13.11. To wartość przybliżona, nie wolumen aukcji otwarcia ani dzisiejsza oferta animatora. W backteście próg liczymy każdorazowo do t−1.','',
'| ETF | Mediana obrotu (tys. zł) | Początek szeregu |','|---|---:|---|']
for z in inv[inv.tested].sort_values('code').itertuples():lines.append(f'| {z.code} | {z.median_turnover63/1000:.1f} | {str(z.first_bar)[:10]}'+(' (WIGtech; obligacje od 2024)' if z.code=='ETFBCASH' else '')+' |')
lines+=['','Dzienne wolumeny nie potwierdzają, że zlecenie całych 20 tys. zł wykonałoby się na otwarciu. Próg 50 tys. zł oznacza pozycję równą nawet 40% tej mediany obrotu; płynność na konkretnej aukcji może być znacznie mniejsza. Dla ETF potrzebujemy również spreadów, kwotowań animatora i rzeczywistych transakcji. Filtr 300 tys. jest ostrożniejszy, ale historycznie często eliminuje fundusze. Nie dodajemy TER do kosztów ponownie: opłaty są już w cenie/NAV.','',
'## Backtesty ETF na wspólnych okresach','',
'Rotacja wybiera jeden ETF, inwestując dostępny kapitał w jeden slot, z przeglądem co 21 sesji i buforem 1. Momentum liczone na 63 sesjach, minimum 64 ceny; nie ma sztucznego przedłużania historii przed debiutem. Dodatnie momentum odrzuca wartości ≤0. BCASH jest dopuszczony jako zastępstwo tylko z dodatnim momentum i odpowiednią płynnością. Wariant WIG używa MA200 do przełączenia ekspozycji akcyjnej na BCASH/gotówkę. Nie jest to pełny zamiennik gotówki w portfelu trzech spółek. Mix to dwa subportfele po 10 tys. zł, bez transferów pomiędzy nimi.','',
'Wyniki poniżej uwzględniają koszt 0,39%. **Kup i trzymaj jest warunkowe:** jeżeli na pierwszym sygnale fundusz nie spełnia progu obrotu, całe okno pozostaje w gotówce. Kolumna „okna bez transakcji” ujawnia te zera, które nie są stopą zwrotu samego ETF. Wycenę końcową wykonujemy po close bez wymuszonej sprzedaży. Nie są to roczne stopy zwrotu.','']
for period,start in [('2022-2025',2022),('2024-2025',2024)]:
 lines += [f'### Okna {period}','',
 '| Wariant | Średnia: próg 300 tys. | Najgorsze: 300 tys. | Okna bez transakcji | Średnia: próg 50 tys. | Najgorsze: 50 tys. |','|---|---:|---:|---:|---:|---:|']
 sub=es[(es.commission==.0039)&(es.min_to==300000)&(es.period==period)]
 for z in sub.itertuples():
  low=es[(es.commission==.0039)&(es.min_to==50000)&(es.period==period)&(es.variant==z.variant)].iloc[0]
  lines.append(f'| {elabel(z.variant)} | {pct(z.mean)} | {pct(z.worst)} | {z.idle_windows}/{z.n} | {pct(low["mean"])} | {pct(low.worst)} |')
 for v in [BASE,TREND]:
  g=core[(core.variant==v)&(core.year>=start)]
  lines.append(f'| Porównanie: {LABELS[v]} | {pct(g.ret.mean())} | {pct(g.ret.min())} | {sum(g.trades==0)}/{len(g)} | — | — |')
 lines+=['']
lines += ['### Czy ETFBCASH poprawił parkowanie środków?','',
'Nie wykazaliśmy tego. W `positive_cash` liczba zakupów BCASH wyniosła zero przy obu progach płynności: w datach przeglądów pozostał przynajmniej jeden dopuszczalny ETF z dodatnim momentum. W `wig_cash` BCASH został kupiony raz przy progu 50 tys. i ani razu przy 300 tys. Zbyt mało obserwacji, by oszacować efekt ochrony. Wyniki „rotacji z BCASH” nie są dowodem korzyści z BCASH.','',
'W obu pełnych oknach 2024 i 2025 samo kup i trzymaj BCASH przy progu 50 tys. dało około +1,07% średnio po prowizji zakupu. Przy progu 300 tys. jedno okno zostało całkowicie w gotówce. Przy koszcie 0,39% wejście i wyjście wymagają wzrostu ceny o (1+0,0039)/(1−0,0039)−1 = **0,783%**, żeby wyjść na zero (bez spreadu). To istotne przy parkowaniu tylko na kilka tygodni; końcowy portfel gry nie musi być sprzedany, więc wtedy pozostaje tylko koszt zakupu.','',
'## Kontrole, pliki i ograniczenia','',
f'- Punkty odniesienia odtworzone dla obu kosztów: maksymalna różnica {manifest["baseline_max_error"]:.3g} (92 porównania).',
f'- Diagnostyka części ETF: stare wyceny {int(er.stale_marks.sum())}, niewykonane sprzedaże {int(er.unfilled_sells.sum())}, niewykonane zakupy {int(er.unfilled_buys.sum())}. Są to kontrole dziennych danych, nie potwierdzenie wykonania w grze.',
'- Niezależne przeliczenie 104 wariantów kup i trzymaj bez silnika: floor(20000/(open×(1+c))), reszta w gotówce, końcowe close. Maksymalna różnica zwrotu 2,22e−16. Wynik kontroli: `validation.json`.',
'- 29 testów jednostkowych zaliczonych, w tym odcięcie WIGtech, brak niepłynnego fallbacku i przełączenie całego pojedynczego slotu po cenie otwarcia następnej sesji.',
'- Surowe dane EODHD z prywatnej bazy pozostają poza repo. Repo zawiera metadane, pochodne statystyki i listę decyzji bez dziennych cen. Dołączenie ETF nie oznacza zgody dostawcy na redystrybucję jego szeregów.',
'- Wykorzystano aktualnie wybrane fundusze, nie kompletną historyczną listę SIGG. Występuje ryzyko selekcji instrumentów, które przetrwały; nie symulowano wszystkich dawnych ETF. Dane cen ETF nie zostały niezależnie uzgodnione z drugim źródłem. Nowe fundusze z 2026 nie mają zakończonego okna gry.',
'- Dziedziczone ograniczenia akcji: niepełny rejestr zawieszeń/wycofań, niepewność danych i korekt, proxy indeksów/NC, brak częściowych wykonań i wolumenu aukcji. Zwiększenie liczby eksperymentów nie usuwa tych ograniczeń.',
'- Nie zmieniono na podstawie eksperymentów operacyjnego podium, listy zakupów ani strony. Brak danych konkurentów uniemożliwia obliczenie prawdopodobieństwa top 3.','',
'Pliki: `stock_years.csv` (644 wiersze), `stock_stats.csv`, `combined_years.csv` (obie serie bez powtórzeń), `combined_paired_all.csv`, `combined_paired_late.csv`, `combined_walk_forward.csv`, `etf_years.csv` (160 wierszy), `etf_stats.csv`, `etf_inventory.csv` (32 ISIN), `etf_trade_choices.csv`; manifesty zawierają SHA256 protokołu, kodu i prywatnych wejść.','',
'```bash',
'export SIGG_DATA_DIR=/prywatny/katalog/snapshotu',
'export SIGG_ENV_FILE=/sciezka/do/prywatnego/.env',
'# Bez GPW_SUFFIX; historyczne macierze A/C/O/V oraz idx z README.',
'python research/load_etfs.py',
'OPENBLAS_NUM_THREADS=1 python research/backtest_round2.py',
'OPENBLAS_NUM_THREADS=1 python research/backtest_etfs.py',
'python research/report_round2.py',
'python -m unittest discover -s tests -p "test_*.py" -v',
'```','',
'Wynik: momentum 6 miesięcy + MA200 warto obserwować dalej, lecz nie ogłaszamy nowego zwycięzcy. ETF-y są sensowną odrębną hipotezą dywersyfikacji/ochrony; obecne próbki nie dowodzą, że zwiększają szansę na nagrodę.']
(OUT/'report.md').write_text('\n'.join(lines)+'\n')
print(OUT/'report.md')
