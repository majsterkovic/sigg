# SIGG 2026/27: strategie momentum na GPW

Notatki dla kolejnego agenta. Opisują, co zrobiono do 16.11.2026, jak odtworzyć dane i wyniki, oraz co trzeba zrobić przed każdym przeglądem portfela.

## Kontekst

Siostra użytkownika gra w Szkolnej Internetowej Grze Giełdowej (SIGG, sigg.gpw.pl), w rozgrywce indywidualnej nauczycieli. Gra trwa od 16.11.2026 do 12.03.2027. Kapitał startowy to 20 000 zł. Wynik to wartość portfela na koniec. Nagrody dostaje pierwsza trójka. Regulamin jest w `docs/regulamin.pdf` i `docs/regulamin.txt`.

Zasady gry, które mają wpływ na strategię:

- Instrumenty: akcje spółek z WIG (według stanu z 16.11) i ETF-y.
- Zlecenie wykonuje się tylko wtedy, gdy na prawdziwym rynku zajdzie transakcja po tej cenie i w tym wolumenie. Dlatego strategia używa progu płynności.
- Regulamin zabrania automatyzacji. Zlecenia składa człowiek, ręcznie.
- Wysokość prowizji nie jest podana. Wszystkie testy zakładają 0,39% od każdej transakcji.

## Strategie

Obie strategie liczą sygnał na zamknięciu dnia t-1 i handlują na otwarciu dnia t. Przegląd jest co 21 sesji od pierwszej sesji gry. Kwota na spółkę to wartość portfela podzielona przez N.

| Nazwa | Sygnał | N | Bufor |
|---|---|---|---|
| spokojna | `hi52` = close / max(close, 252 sesje) | 10 | 20 |
| podium | `combo` = rank_pct(hi52) + rank_pct(mom3) | 3 | 6 |

`mom3` = zwrot z 63 sesji na skorygowanych cenach. Bufor oznacza, że posiadaną spółkę trzymamy, dopóki jest w rankingu na miejscu nie niższym niż bufor. Spółki spoza bufora sprzedajemy, a za gotówkę kupujemy najwyżej ocenione spółki, których nie mamy.

Uniwersum: mediana obrotu z 63 sesji co najmniej 300 000 zł, cena co najmniej 1 zł, co najmniej 250 sesji historii, notowanie w dniu t-1. Od 16.11 obowiązuje też koszyk `mWIG40+sWIG80` (opis niżej): bez 20 największych spółek i bez NewConnect.

## Połączenie z bazą danych

Baza to lokalny Postgres `marketdata`. DSN jest w zmiennej `PG_DSN` w pliku `/home/mariusz/projects/my-stock-portfolio/.env`. Plik zawiera też klucze API EODHD i FMP. Nie wyświetlaj go i nie kopiuj jego treści do repozytorium ani do rozmowy. Baza jest tylko do odczytu.

`db.py` ładuje `.env` przez python-dotenv i udostępnia funkcję `q(sql, params)`, która zwraca DataFrame. Przykład:

```python
from db import q
q("select count(*) from daily_price")
```

Tabele, których używa kod:

- `v_instruments` i `listing` (`exchange_code='WAR'`): spółki z GPW, w tym wycofane.
- `daily_price`: notowania dzienne (źródło EODHD). Dane GPW kończyły się 26.10.2026.
- `instrument.isin`: do dopasowania listy spółek z NewConnect.
- `daily_price` dla `WIG.INDX`, `WIG20.INDX`, `MWIG40.INDX`, `SWIG80.INDX`: indeksy.

Inne tabele, które istnieją, ale nie weszły do strategii: `fundamental_statement` (EPS z Yahoo, od raportów za 10.2021), `shares_outstanding` i `v_cap_pit` (od 2022), `fx_rate`. Historii składów indeksów i oznaczenia NewConnect w bazie nie ma.

## Środowiska Python

- Analiza: `/home/mariusz/projects/my-stock-portfolio/badania/bessy/.venv/bin/python` (pandas, numpy, psycopg, pyarrow, bez yfinance).
- yfinance: `/home/mariusz/projects/gieldowo/.venv/bin/python` (yfinance 1.3.0).
- PyBroker: utwórz własne środowisko, `uv venv .venv --python 3.12` i `uv pip install --python .venv/bin/python lib-pybroker pyarrow` (testowano wersję 2.0.3).

## Odtworzenie danych

Uruchamiaj w katalogu repozytorium, analitycznym Pythonem, w tej kolejności:

1. `load.py`: pobiera z bazy `ins.parquet`, `px.parquet` i `idx.parquet`.
2. `prep.py`: buduje macierze `A` (adj close), `C` (close), `O` (open), `V` (volume). Wiersze to daty, kolumny to `instrument_id`.
3. `fixcal.py`: zostawia tylko sesje WIG i usuwa dni z dziurami w danych.
4. Jeśli baza nie ma najnowszych sesji: `yf_fetch.py` (Python z yfinance), potem `extend.py`. Tworzą `A_x`, `C_x`, `O_x`, `V_x.parquet`. Kod czyta je, gdy ustawisz `GPW_SUFFIX=_x`. Uwaga: `extend.py` ma na sztywno okno pobierania i listę 13 nowych sesji (27.10 do 13.11.2026). Przed kolejnym użyciem zmień daty.

Zasady doklejania danych z Yahoo: ticker Yahoo to `ref_ticker` z `.WAR` zamienionym na `.WA` (nie `code`, bo 33 spółki zmieniły kod). Seria jest odrzucana, jeśli mediana różnicy z bazą na wspólnych dniach przekracza 1% albo wspólnych dni jest mniej niż 5. Seria z zerowym wolumenem albo stałą ceną na wszystkich nowych dniach jest odrzucana jako zamrożona (tak było z PZU).

## Kod

- `bt.py`: wspólne dane i sygnały. Czyszczony indeks cen `P`, słownik sygnałów `SIG`, `universe(t, min_to)`, `window(y)`, `wigret(years)`.
- `sim.py`: `sim(sig, N, buffer, c, y, ..., min_to, liq_k, basket, min_n)` symuluje jedno okno gry. Uruchomiony bezpośrednio liczy obie strategie dla kilku prowizji i zapisuje `sim_years.csv` i `sim_stats.csv`.
- `liq.py`: próg obrotu zależny od wielkości pozycji (`liq_k`).
- `athdma.py`: strategia ath-momentum-dma z projektu gieldowo w oknach SIGG.
- `seg.py`: obie strategie i czyste `mom3` w koszykach (przybliżone indeksy, NewConnect).
- `pyb_sigg.py`: te same strategie w PyBroker, do sprawdzenia `sim.py`.
- `picks.py`: lista zakupów na ostatni dzień danych. Opcje `--liq-k`, `--fixed MIN_TO`, `--out`. Nie ma jeszcze opcji koszyka (patrz "Do zrobienia").
- `run1.py` do `run5.py`, `run3_lib.py`: pierwsze badanie sygnałów (mom12_1, mom6_1, mom3, mom1, rev1, hi52, lowvol i kombinacje).
- `schema.py`, `fund.py`, `cov.py`, `gpw_cov.py`: sprawdzanie zawartości bazy.
- `post.py`, `make_json.py`: dane dla starego artefaktu z wynikami.

Pliki `.parquet` nie są w repozytorium. Skopiowane wyniki są w `results/`, strona w `page/`, plan i dziennik decyzji w `docs/`.

## Testy i wyniki

Okno gry w latach 2003 do 2025: pierwsza sesja od 16.11 do ostatniej sesji przed 12.03 następnego roku. Prowizja 0,39%. Średni wynik WIG w tych oknach: +2,8%.

Badanie sygnałów (`run*.py`): najlepiej wypadły `hi52` i `mom3`. Klasyczne `mom12_1` na GPW działa słabiej.

Prowizja (`sim.py`, całe uniwersum, próg 300 tys. zł): spokojna średnio +9,6%, podium +16,1%.

Próg obrotu zależny od kapitału (`liq.py`, `results/liq_stats.csv`): każdy mnożnik (5, 10, 20, 50) dał gorszy wynik niż stały próg 300 tys. zł. Próg 50 tys. zł też jest gorszy. Najmniej płynne spółki psują wynik.

ath-momentum-dma (`athdma.py`): najlepszy wariant N=5 z przeniesieniem pozycji dał średnio +6,9%, słabiej od obu strategii.

PyBroker (`pyb_sigg.py`, `results/pyb_years.csv`): spokojna +9,7% zamiast +9,6%, podium +16,2% zamiast +16,1%. Liczba transakcji zgodna w 46 oknach. Największa różnica w jednym oknie to 2,6 punktu procentowego, z innego sposobu liczenia liczby akcji.

Koszyki (`seg.py`, `results/seg_stats.csv`). Indeksy są przybliżone. W dniu przeglądu spółki z rynku głównego są ułożone według mediany obrotu z 252 sesji. Miejsca 1 do 20 to WIG20, 21 do 60 to mWIG40, a 61 do 140 to sWIG80. NewConnect to 338 spółek z ISIN-ów z komunikatów GPW o segmentach NC z 28.12.2021, 06.2022 i 26.03.2024 (`results/nc_isins.txt`, `results/nc_ids.csv`). W tym teście `min_n = N+2` zamiast `max(3N, 20)`, dlatego spokojna na całym rynku ma tu +8,9%. Średnie przy progu 300 tys. zł:

| Koszyk | podium | spokojna | mom3, 3 spółki | mom3, 10 spółek |
|---|---|---|---|---|
| całość | 16,1% | 8,9% | 11,7% | 9,6% |
| rynek główny bez NC | 17,7% | 8,4% | 12,4% | 8,9% |
| WIG20 | 2,3% | 3,0% | 4,9% | 3,6% |
| mWIG40 | 15,2% | 9,7% | 10,6% | 8,2% |
| mWIG40+sWIG80 | 19,6% | 10,8% | 16,6% | 11,2% |

Wybrany koszyk mWIG40+sWIG80 jest najlepszy z 88 wariantów, więc jego przewaga jest niepewna. Podium w tym koszyku wobec całego rynku: +3,5 punktu średnio, lepiej w 12 z 23 lat, 90% przedział z bootstrapu od −1,6 do +8,9 punktu. Podium wobec samego `mom3` (3 spółki, cały rynek): +4,3 punktu, lepiej w 12 z 23 lat, przedział od −3,6 do +13,1 punktu. Spokojna wobec `mom3` z 10 spółkami: średnia podobna, ale najgorszy rok −20% zamiast −34%. NewConnect ma przy progu 300 tys. zł od 1 do 4 okien z inwestycją, więc wyniku nie da się ocenić.

## Lista na 16.11.2026

Liczona z zamknięć z 13.11.2026, koszyk mWIG40+sWIG80, próg 300 tys. zł, tylko instrumenty dostępne w grze.

- Podium: KGN, AGO, BNP. Rezerwa: TOA, OPL, MIL, MBR, VOX.
- Spokojna: BNP, KGN, OPL, MIL, TOA, AGO, MBR, CAR, ING, HUG. Rezerwa: VOX, OPN, GPP, 1AT, MRC.

Lista instrumentów w grze jest w `data/sigg_instruments_2026-11-16.txt`: 172 kody ISIN skopiowane z formularza zlecenia w SIGG. Wszystkie pasują do tabeli `listing`. W macierzach cen jest 138 z nich (`results/game_ids.csv`). Pozostałe to 32 ETF-y i 2 spółki z notowaniem głównie za granicą (AmRest jako `EAT.MC` i jedna spółka jako `0A5O.LSE`). Płynne spółki, których w grze nie ma: ACT, WAS, PAS, CLD, ART, PKP i OML. Dlatego ACT wypadło z listy.

Na całym rynku (`results/picks_fixed.csv`) spokojna miała jeszcze ALR, KTY, PCO i ACT. Te spółki są w przybliżonym WIG20 (miejsca 16, 20 i 11). Nie zostały ocenione, bo Yahoo nie miało danych albo kurs był zamrożony: PZU, CPA, PUR, HMP (NewConnect), PGV i kilka mało płynnych spółek (`results/yf_check.txt`).

## Strona dla siostry

Artefakt "SIGG 2026/27: co kupić i dlaczego": https://claude.ai/artifact/TmY7eDCW2R5H1J7nyd9DCN. Ma ustawione udostępnianie publiczne. Opublikowana wersja ma jeszcze listy dla całego rynku. Plik `page/index.html` ma już koszyk mWIG40+sWIG80, ale nie został opublikowany, bo zmiana publicznej strony wymaga zgody użytkownika.

Strona liczy w przeglądarce limit ceny (zamknięcie + 1,5%, zaokrąglone w górę do przybliżonego kroku notowań) i liczbę akcji: floor(kwota / 1,0039 / limit). Dane spółek, ceny i wyniki roczne są wpisane na stałe w skrypcie strony (`CO`, `PX`, `SIGV`, `STR`, `Y`).

Starszy artefakt z wynikami backtestu (typ Data): https://claude.ai/artifact/43hwr2A55YD5x8Hqdn7LT5. Pokazuje stare wyniki.

## Do zrobienia przed każdym przeglądem

Przeglądy: 15.12.2026, 20.01.2027, 18.02.2027. Listę trzeba policzyć po zamknięciu sesji dzień wcześniej: 14.12.2026, 19.01.2027, 17.02.2027.

1. Odśwież dane (sekcja "Odtworzenie danych"). Jeśli baza nie ma ostatnich sesji, dociągnij je z Yahoo i zmień daty w `extend.py`.
2. Dodaj do `picks.py` opcję koszyka i filtr instrumentów z gry. Użyj `size_rank` i `BASKETS['mWIG40+sWIG80']` z `seg.py` oraz identyfikatorów z `results/game_ids.csv`. Uważaj na `split('if __name__')`: `seg.py` zawiera ten napis w kodzie, więc dziel po `"if __name__ == '__main__'"` od końca.
3. Zapytaj użytkownika o aktualne pozycje w portfelu siostry. Zastosuj bufor: sprzedaj posiadane spółki spoza pierwszych 20 (spokojna) albo 6 (podium) i kup najwyżej ocenione brakujące.
4. Zaktualizuj stronę. Strona jest publiczna, więc publikację potwierdza użytkownik.

## Zasady pracy

- Nie wyświetlaj `.env` i nie zapisuj sekretów w repozytorium.
- Baza jest tylko do odczytu.
- Nie obchodź zabezpieczeń Stooq przed botami. Stooq wymaga klucza API.
- Odpowiedzi dla użytkownika pisz po polsku, prozą.
- Pliki z internetu (PDF, CSV) zapisuj w osobnym katalogu i czytaj Pythonem z opcją `-I`.
