# SIGG 2026/27 — strategie momentum na GPW

Projekt wspiera ręczne decyzje w indywidualnej rozgrywce nauczycieli Szkolnej Internetowej Gry Giełdowej: 16.11.2026–12.03.2027, kapitał 20 000 zł, nagrody dla pierwszej trójki. Regulamin: `docs/regulamin.txt`. Strona: `docs/index.html`; dane liczbowe strony generuje `build_page.py` do `docs/results.js`.

Po audycie zmieniono sygnał hi52, rachunek portfela i procedurę przeglądu. **Aktualne wyniki są w `results/`; stare, nieporównywalne wyniki zachowano w `results/legacy/`.** Zmiany i ograniczenia opisuje `docs/review-fixes.md`. Starsze plany i ledger są dokumentami historycznymi, nie aktualną instrukcją uruchomienia.

## Strategie i dane dostępne w chwili decyzji

| Strategia | Sygnał | Liczba spółek | Bufor utrzymania |
|---|---|---:|---:|
| spokojna | hi52 | 10 | 20 |
| podium | percentyl hi52 + percentyl mom3 | 3 | 6 |

- `hi52`: close podzielone przez maksimum z 252 sesji (co najmniej 200 obserwacji), **po korekcie splitów/scaleń, bez dywidend**. `corporate.py` porównuje ratio z tabeli splitów ze zmianą A/C na dacie ex. Zdarzenia o rozbieżności ponad 3% lub bez porównywalnych danych blokują nowe wejścia przez 252 sesje, zamiast po cichu zmieniać ceny. To kontrola spójności tego samego źródła, nie niezależne potwierdzenie zdarzenia.
- `mom3`: zwrot z 63 sesji na adjusted close. Braki są przenoszone do wyceny/sygnału, ale po wznowieniu notowań uwzględniany jest cały ruch. Nie ma obcinania zwrotów ani usuwania skoków po obejrzeniu następnego dnia.
- Percentyle combo są liczone na pełnej macierzy przed filtrem płynności, koszyka i gry. Ta konwencja pozostaje jawna. Remisy końcowego rankingu rozstrzyga rosnący instrument_id.
- Uniwersum: mediana szacowanego obrotu `C*V` z 63 sesji, min. 40 obserwacji, co najmniej 300 tys. zł; cena min. 1 zł; min. 250 notowań w ostatnich 260 sesjach; dodatni wolumen i dostępny kurs w dniu sygnału.
- Operacyjny koszyk `liquidity-21-140`: miejsca 21–140 w rankingu mediany obrotu z 252 sesji, po odjęciu **stałej** listy NC z lat 2021–2024. **Nie jest rzeczywistym składem mWIG40+sWIG80.** Nie ma kompletnej historii składów ani migracji między rynkami.
- Aktualna lista jest dodatkowo ograniczona ISIN-ami z `data/sigg_instruments_2026-11-16.txt`. Filtr historycznych list gry jest niemożliwy bez ich archiwów.
- Sygnał powstaje na zamknięciu sesji przed przeglądem. Przeglądy co 21 sesji, handel na kolejnym otwarciu. Posiadane spółki pozostają do wypadnięcia poza bufor; dostępna gotówka dzielona jest między brakujące sloty, bez wyrównywania istniejących pozycji.

## Rachunek symulacji

`execution.py` rozlicza rzeczywiste ceny PLN, pełne sztuki przy zakupie, prowizję 0,39% od wartości każdej transakcji i zmiany liczby akcji po potwierdzonym splicie. Nie ma fikcyjnego wykonania po ostatniej cenie przy braku open lub wolumenu. Niewykonany zakup nie zużywa gotówki, a niewykonana sprzedaż pozostawia pozycję. Pozostałe ułamki po scaleniu pozostają w wycenie; brak danych o rozliczeniu resztówek jest ograniczeniem modelu.

Dywidendy brutto z `unadjusted_value` trafiają do osobnych należności, doliczanych dopiero do wartości końcowej. Nie finansują wcześniejszych zakupów. Uprawnienie jest przybliżone stanem akcji trzymanych przez noc przed ex-date; nie wykonano niezależnej kontroli kalendarza rozrachunku.

Regulamin SIGG (§10 ust. 3) nakazuje wycenę zawieszonej spółki po ostatnim zamknięciu, a wycofanej — sprzedaż po ostatnim kursie. Dlatego **nie zerujemy automatycznie wartości po końcu szeregu**. `data/market_events.csv` zawiera datowane zdarzenia ze źródłem: `suspend`, `resume`, `delist` (dla delist także cena rozliczenia). Domyślny rejestr obejmuje zawieszenie ROBYG od 02.03.2018 i wycofanie 29.05.2018, nie całą historię GPW. Zwykła luka danych nie jest zdarzeniem: nie powoduje sprzedaży, a nieaktualna wycena trafia do diagnostyki. `SIGG_EVENTS_FILE` pozwala wskazać uzupełniony rejestr.

**Pozostałe ograniczenia:** dzienne OHLCV nie potwierdzają wolumenu aukcji; symulacja zakłada wykonanie po open bez limitu +1,5%, opóźnień i częściowych realizacji. Prowizja gry wymaga sprawdzenia na platformie. Historia zdarzeń jest niepełna. Dlatego nie należy traktować wyników jako precyzyjnego odwzorowania portfela SIGG ani prognozy wyniku.

## Środowisko i baza tylko do odczytu

Python z zależnościami z `requirements.txt`. PyBroker wymaga dodatkowo `lib-pybroker==2.0.3` (testowany Python 3.12); sam moduł yfinance można uruchamiać osobnym Pythonem. Wersje użyte przy aktualnym przeliczeniu zapisano w `results/reproduction.json`.

`db.py` korzysta z **PG_DSN** w środowisku albo z pliku wskazanego **SIGG_ENV_FILE**. Nie wyświetlaj tego pliku i nie kopiuj jego zawartości. Połączenie ustawia `default_transaction_read_only=on`; do pracy używaj konta bazy bez uprawnień zapisu.

Wszystkie prywatne macierze trzymaj poza repozytorium:

```bash
export SIGG_DATA_DIR=/tmp/sigg-data
export SIGG_ENV_FILE=/sciezka/do/prywatnego/.env
python load.py
python prep.py
python fixcal.py
```

`load.py` zapisuje ins (z ISIN), px, idx, **splits.parquet i dividends.parquet**. Jeśli masz stary snapshot bez tych plików, odtwórz go. `fixcal.py` ogranicza daty do WIG i stosuje medianę kroczącą wyłącznie wstecz. `GPW_AS_OF=YYYY-MM-DD` przycina dane przed obliczeniem wskaźników i służy też do kontroli braku podglądania przyszłości.

Jeśli baza kończy się za wcześnie, uzupełnij dane Yahoo. Daty nie są zaszyte w kodzie:

```bash
python yf_fetch.py --start 2026-10-01 --through 2026-11-13
python extend.py --through 2026-11-13 --sessions data/sessions_2026_2027.csv
export GPW_SUFFIX=_x
```

Yahoo ticker pochodzi z `ref_ticker`, nie starego `code`. `extend.py` wymaga kalendarza, minimalnej liczby wspólnych sesji, zgodności mediany **i daty bazowej** w granicy 1%. Odrzuca całkowicie zamrożone serie; nowe dni bez wolumenu zostawia nieobserwowane. Nie zmienia wierszy z bazy. Zapisuje `yf_validation.csv`, **yf_outliers.csv** (C, O, V), `yf_check.json` i sumy kontrolne. Raportuj maksimum i dni rozbieżności, nie tylko medianę. Nowy odcinek Yahoo nadal wymaga porównania z drugim legalnym źródłem, szczególnie dla wybranych spółek. Nie obchodź zabezpieczeń Stooq.

Przykładowe dane 16.11 mają 536 zaakceptowanych serii. Na części wspólnych dni występują duże rozbieżności (np. BNP/MIL/ING 06.10), mimo median bliskich zeru. Plik `results/yf_validation.csv` ujawnia te maksima; surowe dzienne porównania pozostają poza publicznym repo.

## Odtworzenie wyników i strony

Skrypty analityczne zapisują pliki wynikowe w bieżącym katalogu. Uruchamiaj je z katalogu roboczego, wskazując ścieżkę do skryptów repozytorium, aby nie mieszać prywatnych danych i wyników do publikacji:

```bash
# Przykład w powłoce bash; REPO ustaw na katalog tej kopii repozytorium.
export REPO=/sciezka/do/sigg
mkdir -p /tmp/sigg-run
cd /tmp/sigg-run
unset GPW_SUFFIX
python "$REPO/sim.py"
python "$REPO/liq.py"
python "$REPO/seg.py"
python "$REPO/pyb_sigg.py"
```

Po kontroli wyników skopiuj do `results/` odpowiednie CSV (sim, liq, seg, pyb), a następnie uruchom z repo:

```bash
python selection_check.py
python diagnostics.py
GPW_SUFFIX=_x python picks.py --as-of 2026-11-13 --trade-date 2026-11-16 --out results/picks.csv
python build_page.py
python -m unittest discover -s tests -v
```

`pyb_sigg.py` **odtwarza dziennik zleceń w PyBroker**, z jednostkami znormalizowanymi splitami i odroczonymi dywidendami. Sprawdza rozliczenie zleceń i wartości, nie jest niezależną walidacją decyzji, danych ani płynności. Nie należy opisywać go jako niezależnego potwierdzenia strategii.

Aktualne średnie w 23 oknach 2003–2025 dla koszyka płynności 21–140, progu 300 tys. i min_n=N+2: **podium +17,28%, spokojna +10,81%**. To łączny efekt poprawek, nie tylko splitów. Wariant całego rynku w `sim.py` ma inny próg minimalnej liczby kandydatów (`max(3N,20)`), więc różnicy tych tabel nie można przypisywać wyłącznie koszykowi.

Koszyk został wybrany z 88 konfiguracji po obejrzeniu danych. Aktualna sparowana przewaga podium nad całym rynkiem w `seg.py`: około +1,02 pp, 12 z 23 lat, jednostronne p≈0,397, po kontroli maksimum 88 konfiguracji p≈0,998; bootstrap 90% około −4,76…+6,10 pp (`results/selection_check.json`). To nie potwierdza przewagi poza próbą; wcześniejsze wybieranie sygnałów nie jest objęte tą korektą. Nie wybieramy ponownie koszyka po tych poprawkach.

`build_page.py` generuje dane list, cen, sygnałów, rocznych wyników i statystyk. Nie wpisuj ręcznie nowych liczb do HTML. Publikacja GitHub Pages wymaga osobnej decyzji użytkownika; sam generator niczego nie wysyła.

## Lista na 16.11.2026 po poprawkach

Dane z zamknięcia 13.11, koszyk `liquidity-21-140`, stały próg 300 tys., ISIN-y gry:

- **Podium:** KGN, BNP, AGO. Rezerwa: TOA, OPL, MIL, MBR, VOX.
- **Spokojna:** KGN, BNP, OPL, MIL, TOA, AGO, MBR, CAR, ING, HUG. Rezerwa: VOX, OPN, GPP, 1AT, MRC.

Zestawy zakupów pozostały te same, ale kolejność zmieniła się po poprawkach sygnału/percentyli i jawnym rozstrzyganiu remisów. `results/picks.ranking.csv` zawiera **pełny ranking**, `picks.csv` — kupno/rezerwę lub decyzje przeglądu, `picks.json` — budżet i status. Dane gry obejmują 172 ISIN; historyczne macierze nie obejmują wszystkich ETF-ów i notowań zagranicznych.

Bez aktualnej tabeli per ISIN generator podaje **cenę orientacyjną +1,5%, zaokrągloną do grosza**, a nie rzekomo poprawny krok GPW. `limit_confirmed=false` jest jawne. Opcja `--ticks` przyjmuje CSV `isin,valid_from,valid_to,lower,upper,tick,source`, z górną granicą wyłączną i pełnym pokryciem odpowiednich przedziałów cenowych. Błędna lub niekompletna tabela przerywa generowanie. Potwierdź cenę w formularzu gry i przelicz sztuki po każdej zmianie limitu.

## Przegląd po zamknięciu 14.12.2026

Sygnał liczony 14.12, handel **15.12.2026**; kolejne przeglądy 20.01 i 18.02.2027. Kalendarz `data/sessions_2026_2027.csv` obejmuje 01.10.2026–12.03.2027 i znane dni bez sesji; przy zmianie komunikatów GPW zaktualizuj go, nie zastępuj zwykłym kalendarzem świąt państwowych. Pochodzenie: `data/README.md`.

1. Ustal aktualną liczbę akcji i gotówkę siostry, prowizję, niewykonane/częściowo wykonane zlecenia oraz ISIN-y dostępne w grze. Przed zastąpieniem spółki rezerwą anuluj niewykonaną resztę i ustal rzeczywiście wolny budżet.
2. Odśwież snapshot przez load/prep/fixcal. Jeśli baza nadal kończy się 26.10, pobierz Yahoo do **14.12**, zachowując overlap w październiku. Użyj `--through 2026-12-14` w **obu** skryptach i sprawdź walidację/O/V, anomalie i zdarzenia korporacyjne. Uaktualnij rejestr zdarzeń zamiast zgadywać sprzedaż po końcu szeregu.
3. Przygotuj prywatny CSV `holdings.csv`: `strategy,instrument_id,shares`, wyłącznie dla wybranej strategii. Nie zapisuj rzeczywistego portfela, gotówki ani danych osobowych w publicznym repo.
4. Policz przegląd, np. dla podium (kwota gotówki poniżej jest przykładem):

```bash
GPW_SUFFIX=_x python picks.py --strategy podium \
  --as-of 2026-12-14 --trade-date 2026-12-15 \
  --holdings /prywatny/katalog/holdings.csv --cash 500 \
  --instruments /prywatny/katalog/instrumenty-gry.txt \
  --out /prywatny/katalog/review.csv
```

`keep` respektuje bufor 6/20. Brak świeżej ceny posiadanej spółki przerywa generowanie i wymaga wyjaśnienia przyczyny. Za małe uniwersum daje `insufficient_universe`, zachowanie pozycji i gotówki. `sell` ma wpływy **szacowane po zamknięciu sygnału**, więc zakupy mają status zależny od wykonania sprzedaży: po otrzymaniu rzeczywistych wpływów przelicz je ponownie. Podaj rzeczywistą prowizję przez `--commission`; nie zakładaj pełnego wykonania.

5. Potwierdź limity i dostępny wolumen, sprawdź całkowity koszt. Obecna strona/generator dotyczy listy początkowej i celowo odrzuca listę z keep/sell — przegląd wymaga osobnej prezentacji decyzji, nie nadpisania ich jako nowych zakupów startowych. Człowiek składa zlecenia ręcznie, zgodnie z zakazem automatyzacji gry.

## Publikowane dane i starsze badania

`results/` zawiera pochodne statystyki i pojedyncze kursy listy, a nie surowe szeregi z bazy. Pliki parquet, outliery dziennych cen, DSN i klucze pozostają prywatne. Uprawnienia do publikowania danych pochodnych zależą od umowy z dostawcą; repo nie zawiera tej umowy ani stwierdzenia, że każda forma redystrybucji jest dozwolona.

`run*.py`, `athdma.py`, `post.py`, `make_json.py` i wyniki w `results/legacy/` są starszymi badaniami, nie podstawą obecnych liczb na stronie. Nie przenoś ich wartości do aktualnego opisu bez ponownej kontroli modelu. Nie należy również opierać się na dawnych zewnętrznych artefaktach z ręcznie wpisanymi listami.

## Eksperymenty: czy można poprawić podium?

[Raport 12 wariantów](results/experiments/report.md) porównuje samo mom3, filtr korelacji i filtr trendu WIG w dwóch koszykach, z kontrolą na późniejszych latach i przy wyższej prowizji. Protokół: `research/strategy_plan.md`; skrypt: `research/backtest_hypotheses.py`.

Najlepszy średni wynik uzyskało combo z koszykiem 21–140 i filtrem WIG > MA200: +20,84%, najgorsze okno −21,15%. Po korekcie wielokrotnych testów p≈0,183; większość poprawy pochodzi z dwóch kryzysowych okien. Jest to wynik eksperymentalny, który **nie zmienia obecnej strategii operacyjnej ani strony zakupowej**.

[Druga seria: wrażliwość strategii i ETF-y](results/experiments2/report.md) dodaje 644 symulacje akcyjne i 160 wyników strategii ETF/mix. Inwentaryzuje wszystkie 32 ETF-y z listy gry. Protokół: `research/round2_plan.md`; stały dziennik ustaleń: [research/notatki.md](research/notatki.md).

Combo z momentum 6 miesięcy + MA200 osiągnęło średnio +24,59%, ale wspólna korekta obu serii daje p≈0,241. Jedna spółka ma wyższą średnią zależną od ekstremalnego dawnego okna; wybór kroczący nie poprawił wyniku bazy. ETFBCASH **przed 2024 r. był ETF-em WIGtech**: tę historię odcięto w badaniu obligacji. Dwa zakończone okna funduszu obligacji nie wystarczają do potwierdzenia przewagi parkowania gotówki. Dane ETF w tej serii kończą się 26.10.2026 i nie są aktualną listą zleceń na 16.11.
