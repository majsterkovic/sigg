# Seria 3: ETF-y na S&P 500 i złoto — 16.11.2026

Protokół: [round3_plan.md](../../research/round3_plan.md) (dodatek ze złotem zapisany przed jego testem). Kod: `research/fetch_yf_etf.py`, `validate_yf_etf.py`, `backtest_round3.py`. Okna listopad–marzec, koszt 0,39% (0,60% w plikach CSV, wnioski te same). Mała próba i znane już lata: wyniki eksploracyjne, bez p-wartości.

## Wnioski

Lista gry zawiera ETF-y na S&P 500 i złoto, ale nie dają one na razie podstaw do zmiany listy zakupów. ETFSP500 (Lyxor, GPW, PLN) miał przed 2018 r. zbyt mały obrót, żeby kupić 20 tys. zł; przy progu 50 tys. zł zleceń nie dałoby się złożyć w 8 z 16 okien, przy progu 300 tys. zł w 12 z 16. W 8 oknach 2018–2025 z wystarczającym obrotem kup i trzymaj dało średnio −1,2% (najgorsze −17,6%), podczas gdy podium w tych samych latach +23,4%. Pół na pół z podium + MA200 obniża wynik o 8,7 pp (próg 50 tys.) wobec samego podium + MA200 i ma przedział 90% wobec podium obejmujący zero (−12,8 do +0,9 pp), czyli efekt jest niepewny, ale kierunek jest ujemny.

Złota nie da się przetestować jako funduszu: ETFPZUGOLD notuje od 11.05.2026 (133 sesje) i nie ma zakończonego okna. Na proxy (GC=F × PLN=X) złoto w latach 2003–2025 miało korelację −0,31 z podium. W pięciu najgorszych oknach podium (średnio −22,8%) złoto zyskało średnio +17,8%; w 7 oknach, gdy WIG ≤ MA200 na starcie, średnio +13,0%. Strategia „podium gdy WIG > MA200, złoto gdy poniżej” dała średnio +23,4% wobec +17,3% podium (+6,1 pp, 90% przedział +0,9 do +12,7 pp) i +20,8% podium + MA200 (+2,6 pp, przedział −0,3 do +6,5 pp). Najgorsze okno −21,2%, tak samo jak podium + MA200. To obiecująca hipoteza obrony, ale nie dowód: proxy nie ma kosztów funduszu ani spreadu walutowego, złoto w PLN rosło mocno w tym okresie, a po tej serii łączna liczba przetestowanych wariantów jeszcze wzrosła.

## Kontrola danych

Yahoo (`.WA`) zgadza się z bazą dla 7 funduszy z serii 2: 0 różnic zamknięć lub otwarć powyżej 0,5% i 0 różnic wolumenu powyżej 20% na 1195–1950 wspólnych sesjach (największa różnica zamknięcia 0,014%). To zamyka zastrzeżenie o braku drugiego źródła dla tych funduszy; `yf_vs_db.csv`. ETFSP500 ma w bazie tylko szereg XETRA, więc jego warszawski szereg pochodzi wyłącznie z Yahoo (bez kontroli drugim źródłem). Cena ETFSP500 skacze około 5 razy w oknie 2012 bez splitu w danych Yahoo; to okno i tak nie ma obrotu, więc nie wpływa na wyniki. Niezależne przeliczenie kup i trzymaj bez silnika zgadza się z silnikiem we wszystkich 8 oknach z transakcją (próg 50 tys.).

## Tabele (koszt 0,39%)

| Strategia | Próg | Okna | Średnia | Najgorsze | Okna bez transakcji | Podium (średnia tych lat) | Podium + MA200 |
|---|---:|---:|---:|---:|---:|---:|---:|
| hold_sp500 | 50 tys. | 16 | −0,6% | −17,6% | 8 | +13,2% | +16,0% |
| mix50_sp500 | 50 tys. | 16 | +7,3% | −10,7% | 8 | +13,2% | +16,0% |
| wig_sp500 | 50 tys. | 16 | +15,0% | −21,9% | 8 | +13,2% | +16,0% |
| hold_sp500 | 300 tys. | 16 | −0,1% | −10,5% | 12 | +13,2% | +16,0% |
| mix50_sp500 | 300 tys. | 16 | +7,6% | −10,7% | 12 | +13,2% | +16,0% |
| wig_sp500 | 300 tys. | 16 | +16,3% | −21,2% | 12 | +13,2% | +16,0% |

wig_sp500 prawie nie różni się od podium + MA200 (−1,0 pp przy 50 tys., +0,4 pp przy 300 tys.), bo S&P 500 był w użyciu rzadko. Okna bez transakcji mają zwrot 0, więc średnie hold i mix są sztucznie zaniżone; pełne wiersze dla okien z obrotem są w `sp500_stats.csv` (próbka `floor_met_at_start`).

| Strategia (proxy złota, 23 okna) | Średnia | Mediana | Najgorsze | Podium (średnia) | Podium + MA200 (średnia) |
|---|---:|---:|---:|---:|---:|
| hold_gold | +5,1% | +3,7% | −8,9% | +17,3% | +20,8% |
| mix50_gold | +12,2% | +7,7% | −9,2% | +17,3% | +20,8% |
| wig_gold | +23,4% | +18,6% | −21,2% | +17,3% | +20,8% |

## Ograniczenia

Jeden fundusz S&P 500 i jedno proxy złota; nie zbadano pozostałych 25 ETF-ów z listy (DAX, NATO, Bitcoin, nowe fundusze PZU, górnicy i inne bez warszawskich danych). Yahoo nie podaje wolumenu aukcji ani spreadów. ETFSP500 wypłaca dywidendy (księgowane gotówką), podatki pominięto. Najgorsze okno S&P 500 (2019/20, −17,6%) obejmuje początek krachu z lutego–marca 2020; nie rozdzielono wpływu kursu walutowego i indeksu. Nie zmieniono listy zakupów ani strony.

```bash
export SIGG_DATA_DIR=/prywatny/katalog/snapshotu
python research/fetch_yf_etf.py        # z pakietem yfinance
python research/validate_yf_etf.py
OPENBLAS_NUM_THREADS=1 python research/backtest_round3.py
```

## Dodatek: dźwignia 2x na mWIG40 i WIG20 (szereg syntetyczny)

Protokół: ostatni dodatek w [round3_plan.md](../../research/round3_plan.md); kod `research/backtest_leverage.py`; pliki `leverage_*.csv`, `leverage_validation.json`. Szereg: 2 × (dzienny zwrot indeksu + dywidendy) − koszt finansowania i opłat. Koszt c = 5,4% rocznie wyznaczono raz tak, by 2×WIG20 zgadzało się z ETFBW20LV (+217% od 26.02.2020); wrażliwość 3% i 10%.

Walidacja poza próbą: ETFBM40LV (08.04–26.10.2026, 140 sesji) +49,0% rzeczywiście, +44,8% w szeregu syntetycznym; dzienna korelacja 0,95. Szereg zaniża wynik o 4 pp na tej krótkiej próbie, nie jest więc wiernym odpowiednikiem funduszu, tylko przybliżeniem.

Koszt 5,4%, prowizja 0,39% przy każdym zakupie i sprzedaży w trakcie okna:

| Szereg | Strategia | Okna | Średnia | Mediana | Najgorsze | Najlepsze | Podium (średnia tych lat) | Różnica wobec podium (90%) |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 2× mWIG40 | kup i trzymaj | 15 | +10,1% | +14,6% | −45,8% | +44,9% | +13,2% | −3,1 pp (−12,7 do +5,7) |
| 2× mWIG40 | MA200 | 15 | +11,8% | +5,5% | −19,9% | +44,9% | +13,2% | −1,5 pp (−11,1 do +7,5) |
| 2× WIG20 | kup i trzymaj | 23 | +3,2% | +3,0% | −67,7% | +55,2% | +17,3% | −14,1 pp (−22,4 do −6,0) |
| 2× WIG20 | MA200 | 23 | +8,4% | +1,8% | −14,8% | +55,2% | +17,3% | −8,9 pp (−18,0 do −0,1) |

Wniosek: żadna z czterech wersji nie pobiła podium. 2× mWIG40 jest zbliżone do podium w średniej (różnica obejmuje zero), ale ma najgorsze okno −45,8% bez filtra; filtr MA200 ogranicza je do −19,9% (nie obniża średniej). 2× WIG20 wypada wyraźnie gorzej (kup i trzymaj −67,7% w 2008 r.). Wyniki są mało zależne od c (3–10%). Wniosek o mWIG40 wobec WIG20 jest opisowy: te same 15 lat vs 23 lata, więc okresy nie są porównywalne wprost. Nie testowano Nasdaq (brak szeregu indeksu w bazie).
