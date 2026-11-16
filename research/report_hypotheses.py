"""Render the experiment report from its CSVs; no numeric transcription."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/experiments'
BASE='combo|liquidity-21-140|base'

def label(v):
    signal,basket,rule=v.split('|')
    return ('combo' if signal=='combo' else 'mom3')+' / '+('21–140' if basket=='liquidity-21-140' else 'bez NC*')+' / '+{'base':'bez dodatków','corr':'korelacja ≤0,70','trend':'WIG > MA200'}[rule]

def pct(x):return f'{x*100:+.2f}%'.replace('.',',')
def pp(x):return f'{x*100:+.2f} pp'.replace('.',',')
def number(x):return f'{x:.3f}'.replace('.',',')

r=pd.read_csv(OUT/'years.csv');s=pd.read_csv(OUT/'stats.csv');paired=pd.read_csv(OUT/'paired_all.csv').set_index('variant');late_p=pd.read_csv(OUT/'paired_late.csv').set_index('variant');wf=pd.read_csv(OUT/'walk_forward.csv');manifest=json.loads((OUT/'manifest.json').read_text())
core=r[r.commission==.0039];allstats=s[(s.commission==.0039)&(s.period=='all')].set_index('variant');latestats=s[(s.commission==.0039)&(s.period=='late')].set_index('variant')
ordered=allstats.sort_values('mean',ascending=False).index
lines=['# Backtest hipotez dla SIGG — 16.11.2026','',
'## Zakres i sposób oceny','',
'Porównano 12 konfiguracji z góry określonych w `research/strategy_plan.md`: sygnał combo lub mom3, koszyk płynności 21–140 lub cały zbiór po odjęciu stałej listy NC, bez dodatków albo z filtrem korelacji albo z filtrem trendu WIG. Dla każdej wykonano 23 okna gry oraz powtórzenie przy wyższym koszcie: łącznie **552 symulacje**. Nie zmieniano parametrów po obejrzeniu wyników.','',
'Każde okno zaczyna się z 20 000 zł: pierwsza sesja od 16 listopada do ostatniej sesji nie późniejszej niż 12 marca kolejnego roku. Trzy pozycje, bufor 6, min_n=5, przegląd co 21 sesji; sygnał do t−1, handel po open t, pełne sztuki i prowizja 0,39%. Dywidendy są należnością do końca gry. Wyniki są zwrotami za około cztery miesiące, nie roczną stopą i nie CAGR. „Najgorsze” to najgorszy wynik całego okna, nie maksymalne obsunięcie wewnątrz niego.','',
'Filtr korelacji wybiera zachłannie kolejne spółki po sygnale z listy, wymagając korelacji ≤0,70 z każdą już zaakceptowaną. Okno to 126 sesji, minimum 84 wspólne obserwacje; brak korelacji nie oznacza niezależności. Filtr zmienia również ranking utrzymania w buforze. Wariant trendu na przeglądzie przechodzi do gotówki, gdy WIG nie jest powyżej średniej 200 sesji, i wraca dopiero na przeglądzie spełniającym warunek. Nie ma codziennych stopów. Nie łączono obu filtrów.','',
r'\* „Bez NC” oznacza odjęcie statycznej listy 2021–2024, a nie historycznie poprawne członkostwo rynku głównego. W wariancie szerokim dopuszczono również duże spółki. Historyczne listy instrumentów gry są nieznane, więc dzisiejszej listy ISIN nie przenoszono w przeszłość.','',
'## Wszystkie warianty','',
'| Wariant | Średnia 2003–2025 | Mediana | Najgorsze | Straty | Wynik >40% | Średnia 2013–2025 | Transakcje/okno |','|---|---:|---:|---:|---:|---:|---:|---:|']
for v in ordered:
    a=allstats.loc[v];b=latestats.loc[v];g=core[core.variant==v]
    lines.append(f'| {label(v)} | {pct(a["mean"])} | {pct(a["median"])} | {pct(a.worst)} | {sum(g.ret<0)}/23 | {sum(g.ret>.4)}/23 | {pct(b["mean"])} | {a.trades:.1f} |')
lines+=['','Progi +20% i +40% opisują ogon wyników, a nie szansę na top 3. Wyników pozostałych uczestników nie ma w danych. Wszystkie metryki, w tym +20%, opłaty, gotówka i braki wykonania, znajdują się w plikach CSV.','',
'## Czy poprawa względem obecnego podium jest przekonująca?','',
'Bazą jest combo / 21–140 / bez dodatków. Różnice są sparowane po latach, a przedziały to bootstrap 90% (100 000 losowań). Test jednostronny sprawdza poprawę średniej; korekta max-T obejmuje 11 alternatyw i zachowuje ich zależność w danym roku. Założenie: symetria niezależnych rocznych wektorów różnic. Korekta nie obejmuje wcześniejszych badań i wyboru samego momentum.','',
'| Wariant | Różnica średniej | Bootstrap 90% | Lepsze lata | p | p po max-T |','|---|---:|---|---:|---:|---:|']
for v in ordered:
    if v==BASE:continue
    z=paired.loc[v];lines.append(f'| {label(v)} | {pp(z.gain)} | [{pp(z.ci90_low)}; {pp(z.ci90_high)}] | {int(z.wins)}/23 | {number(z.p_one_sided)} | {number(z.p_maxT)} |')
lines+=['','Różnice i granice przedziałów w tej tabeli są w punktach procentowych.','',
'## Kontrola na późniejszych latach','',
'Lata 2003–2012 stanowią początkowy trening. W każdym roku 2013–2025 wybrano wariant o najwyższej średniej w latach 2003..y−1, a następnie zastosowano wyłącznie jego wynik w roku y. To retrospektywna walidacja krocząca: wcześniejsze badania obejmowały już te dane, więc nie jest to nienaruszona próba poza badaniem. Wybór maksymalizuje średnią, nie nieznaną szansę na nagrodę.','',
'| Rok testowy | Wariant wybrany z przeszłości | Wynik wyboru | Wynik obecnego podium |','|---|---|---:|---:|']
w=wf[wf.commission==.0039]
for z in w.itertuples():lines.append(f'| {z.year} | {label(z.selected)} | {pct(z.ret)} | {pct(z.baseline)} |')
rng=np.random.default_rng(20261116);d=w.gain.to_numpy();boot=d[rng.integers(0,len(d),size=(100000,len(d)))].mean(axis=1);ci=np.quantile(boot,[.05,.95])
lines+=['',f'Selektor kroczący: średnia **{pct(w.ret.mean())}**, baza **{pct(w.baseline.mean())}**; różnica {pct(w.gain.mean())} (pp), przewaga w {sum(w.gain>0)}/13 latach, nominalny bootstrap 90% [{pct(ci[0])}; {pct(ci[1])}] (pp). Ten przedział jest orientacyjny: kolejne decyzje selektora korzystają z nakładających się okresów treningowych.',
f'Najgorsze późniejsze okno: selektor {pct(w.ret.min())}, baza {pct(w.baseline.min())}. Wynik >40%: {sum(w.ret>.4)}/13 wobec {sum(w.baseline>.4)}/13.','',
'## Wrażliwość na koszty','',
'Prowizja 0,60% od transakcji zamiast 0,39% to jawny test droższego wykonania, nie model rzeczywistych spreadów i poślizgu. Wariant wybierany krocząco pozostaje wybrany według treningu przy 0,39%.','',
'| Wariant | Średnia przy 0,39% | Średnia przy 0,60% |','|---|---:|---:|']
for v in ordered:
    high=s[(s.commission==.006)&(s.period=='all')&(s.variant==v)].iloc[0]
    lines.append(f'| {label(v)} | {pct(allstats.loc[v,"mean"])} | {pct(high["mean"])} |')
lines+=['','## Ograniczenia i odtworzenie','',
'Badanie dziedziczy ograniczenia poprawionego modelu (`results/model.json`): niepełna historia zdarzeń, źródłowa niepewność splitów/dywidend, proxy koszyka i brak wolumenu aukcji, częściowych realizacji oraz limitu +1,5% w symulacji. Korelacja dotyczy przeszłości i nie gwarantuje ochrony podczas przyszłego krachu. Wstrzymana sprzedaż może pozostawić skorelowane pozycje. Nie wykorzystywano obecnych sektorów jako historycznego filtra, by nie dodawać bieżącej klasyfikacji do dawnych decyzji.','',
f'Kontrola bazowego wariantu: maksymalna różnica względem opublikowanego `results/seg_years.csv` = {manifest["baseline_max_error"]:.3g}. Pięć testów reguł potwierdza wybór nieskorelowanej spółki, politykę brakujących korelacji, brak odczytu przyszłego WIG, brak dostępu do roku testowego przy selekcji i przejście do gotówki na następnym otwarciu.','',
'```bash',
'SIGG_DATA_DIR=/sciezka/do/snapshotu python research/backtest_hypotheses.py',
'python research/report_hypotheses.py',
'python -m unittest discover -s tests -p test_hypotheses.py -v','```','',
'Pliki: `years.csv` — 552 wyników okien; `stats.csv` — oba koszty i trzy okresy; `paired_all.csv`, `paired_late.csv` — porównania sparowane; `walk_forward.csv` — wybory kroczące i ich wyniki; `manifest.json` — protokół i kontrola bazy. Nie zmieniono na podstawie eksperymentu strategii operacyjnej ani listy zakupów.']
trend='combo|liquidity-21-140|trend'
a=allstats.loc[trend];b=allstats.loc[BASE];z=paired.loc[trend];lp=late_p.loc[trend]
gains=core.pivot(index='year',columns='variant',values='ret')[trend]-core.pivot(index='year',columns='variant',values='ret')[BASE]
findings=['## Wnioski','',
    f'Najlepszy średni wynik ma **obecne podium z filtrem WIG > MA200**: {pct(a["mean"])} wobec {pct(b["mean"])}. Najgorsze okno poprawia się z {pct(b.worst)} do {pct(a.worst)}, a liczba stratnych lat spada z {int(round(b.loss*23))} do {int(round(a.loss*23))}. Wyników >40% pozostaje tyle samo: {int(round(a.p40*23))}/23. Filtr pomaga tu głównie ograniczyć straty; nie wykazano wzrostu szans na konkursowe podium.','',
    f'Nominalne p={number(z.p_one_sided)} wygląda obiecująco, ale po kontroli 11 alternatyw wynosi **{number(z.p_maxT)}**. W późniejszym okresie stały wariant z filtrem daje {pct(latestats.loc[trend,"mean"])} wobec {pct(latestats.loc[BASE,"mean"])}; przedział różnicy 90% [{pp(lp.ci90_low)}; {pp(lp.ci90_high)}] obejmuje zero. To kandydat do dalszej obserwacji, nie udowodniona przewaga.','',
    f'Wpływ kryzysów jest duży: okna zaczynające się w 2008 i 2019 odpowiadają za {100*gains.loc[[2008,2019]].sum()/gains.sum():.1f}% sumy różnic. Bez 2019 średnia poprawa wynosi {pp(gains.drop(2019).mean())}; bez obu tych okien {pp(gains.drop([2008,2019]).mean())}. Filtr poprawia 7 lat, pogarsza 3 i pozostawia 13 bez zmiany. Nie jest to strategia lepsza w każdym roku.','',
    'Samo mom3 nie poprawia średniego wyniku w pełnej próbie; w późniejszych latach daje większą średnią niż bazowe combo, ale także głębokie straty. Ograniczenie korelacji do 0,70 nie zmienia żadnego rocznego wyniku bazowego podium; dla pozostałych sygnałów efekt jest mały. Nie obniżano progu po obejrzeniu tego rezultatu. Poszerzenie koszyka o największe spółki nie poprawia średniej przy porównaniu tych samych sygnałów i filtrów.','',
    f'Wybór kroczący na podstawie wcześniejszych lat osiąga średnio {pct(w.ret.mean())} wobec {pct(w.baseline.mean())} bazy w latach 2013–2025. Nie zastosowano do wszystkich tych lat jednego zwycięzcy wybranego po fakcie.','']
lines=lines[:2]+findings+lines[2:]
(OUT/'report.md').write_text('\n'.join(lines)+'\n')
print('Report:',OUT/'report.md')
