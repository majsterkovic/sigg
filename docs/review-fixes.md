# Poprawki po audycie SIGG — 16.11.2026

Zmiany wykonano lokalnie, bez commitów i publikowania. Oryginalny raport pozostaje poza repozytorium w katalogu audytu. Baza była używana tylko do odczytu, przez `db.py`. Surowe snapshoty są poza repozytorium; publiczne wyniki zawierają agregaty i pojedyncze ceny listy. Zewnętrzne dane, których nie udało się potwierdzić, nie zostały zastąpione zgadywanymi wartościami.

## Zakres zmian

| Problem z audytu | Wdrożona poprawka | Pozostały limit wiarygodności |
|---|---|---|
| P1: nieskorygowane hi52 | `load.py` pobiera splity; `corporate.py` tworzy serię split-only. Kontrola ratio względem zmiany A/C, blokada nowych wejść przy niezgodności; diagnostyka 309 zdarzeń, 55 odrzuconych. | Kontrola spójności jednego dostawcy nie zastępuje niezależnej historii splitów i praw poboru. Odrzuconych zdarzeń nie „naprawiono” arbitralnie. |
| P2: wycofania i brak danych | `execution.py` rozróżnia zdarzenie od luki. Brak open/wolumenu nie daje wykonania. Rejestr suspend/resume/delist z datą i źródłem; zamrożona wycena lub jawne rozliczenie. | Rejestr jest niepełny; dopisano potwierdzony przypadek ROBYG, nie fikcyjną historię wszystkich wycofań. |
| P3: przyszłość w czyszczeniu | Usunięto clip i filtr z shift(-1). Mom3 używa zmian A także po wznowieniu danych. Główny silnik handluje po raw O, nie skali P zależnej od zamknięcia t. `fixcal.py` używa mediany wstecz. | Błędy dostawcy nie znikają automatycznie; jawnie raportujemy anomalie i nieaktualne wyceny. |
| P4: realizm wykonania | Zakupy w pełnych sztukach, prowizja, gotówka, brak fikcyjnych otwarć, dziennik niewykonań. | Brak danych tickowych/aukcyjnych: nadal idealizowane wykonanie po open, bez częściowych realizacji i limitu ceny w backteście. |
| P5: koszyki | Wspólne `baskets.py`, jawne nazwy koszyków płynności zamiast deklarowania rzeczywistych indeksów. | Lista NC jest statyczna; historia indeksów i migracji rynku nadal wymaga pozyskania. Nie wprowadzono nowego „zwycięskiego” koszyka po ponownym obejrzeniu wyników. |
| P6: wielokrotne testy | `selection_check.py`, wynik w `results/selection_check.json`; opis in-sample na stronie i w README. | Nie jest to walk-forward ani walidacja poza próbą; wcześniejszy wybór sygnału nadal zwiększa selekcję. |
| P7: Yahoo | Parametry dat w obu skryptach, jawny kalendarz, kontrola daty bazowej, mediany/maksimum/kwantyla, outliery C/O/V i nowe dni bez wolumenu. | Rozbieżności 05–06.10 nie zostały rozstrzygnięte drugim źródłem. Nie twierdzimy, że mediana bliska zeru certyfikuje wszystkie ceny. |
| P8: kolejne przeglądy | `picks.py`: daty, koszyk, ISIN, stan portfela/gotówka, prowizja, bufor, pełny ranking, status zbyt małego uniwersum i budżet. Sprawdza następną sesję kalendarza; znane zawieszenie zachowuje pozycję. | Wpływy ze sprzedaży są szacowane po t-1: zakupy trzeba przeliczyć po wykonaniu. Generator strony startowej nie udaje widoku późniejszego przeglądu. |
| P9: kroki notowań | Brak zgadywanej siatki z samej ceny. Cena orientacyjna jest oznaczona jako niepotwierdzona. `--ticks` wymaga datowanej, źródłowej tabeli per ISIN i przedział ceny. | Aktualne przypisania GPW nie zostały pozyskane dla całej listy. Manualna walidacja w SIGG nadal konieczna. |
| P10: dywidendy | Raw PLN i osobne należności brutto, dostępne dopiero w wyniku końcowym, bez reinwestowania dywidend w trakcie gry. | Uprawnienie po ex-date jest przybliżeniem konwencjonalnego rozrachunku; brak niezależnej kontroli dat record i resztówek po scaleniach. |
| P11: opis/duplikaty | Opis percentyli odpowiada kodowi, jawne remisy; generator `docs/results.js` zamiast ręcznych tablic i liczb w HTML; normalne importy zamiast exec/split plików w seg i athdma. | Starsze badania run*/athdma nie są niezależnym potwierdzeniem nowego rachunku. |
| Prywatne ścieżki | `db.py` używa PG_DSN lub SIGG_ENV_FILE; README nie zawiera prywatnej ścieżki użytkownika. | Nie przepisywano historii git; stare plany pozostają oznaczonymi dokumentami historycznymi. |

## ROBYG: dlaczego nie wyzerowano pozycji

[Raport emitenta 22/2018](https://ri.robyg.pl/storage/public/files/current-report-no-22-robyg-sa-information-about-suspension-of-trading-in-shares-of-robyg-sa-HcMcLkqP-1621941987.pdf) potwierdza zawieszenie od **02.03.2018**. [Raport 48/2018](https://ri.robyg.pl/storage/public/files/raport-biezacy-nr-48-robyg-sa-uchwala-zarzadu-gpw-w-sprawie-wykluczenia-z-obrotu-gieldowego-akcji-robyg-sa-7wCerkJT-1620729669.pdf) potwierdza wycofanie dopiero **29.05.2018**. W oknie kończącym się w marcu stosujemy więc zawieszenie i ostatni kurs 3,98, nie bankructwo ani fikcyjną marcową sprzedaż. Odpowiada to §10 ust. 3 regulaminu. Ogłoszony przymusowy wykup nie został automatycznie utożsamiony z datą wycofania.

## Nowe wyniki

W 23 oknach, w zamrożonym koszyku płynności 21–140 i przy progu 300 tys. zł:

| Miara | Podium | Spokojna |
|---|---:|---:|
| Średni zwrot | +17,28% | +10,81% |
| Mediana | +11,99% | +8,69% |
| Stratne lata | 8/23 | 7/23 |
| Najgorsze okno | −35,06% | −15,80% |
| Lepszy wynik od WIG | 15/23 | 15/23 |

Źródło: `results/seg_stats.csv` i `seg_years.csv`. Zmiana średniej podium z dawnych 19,61% do 17,28% jest łącznym efektem nowej serii hi52, kontroli zdarzeń, braku czyszczenia, pełnych sztuk, rzeczywistego rachunku i odroczonych dywidend. Nie należy przedstawiać jej jako samego efektu splitów (w audycie izolowany test splitów dawał 18,52%).

Obecna sparowana przewaga koszyka podium nad analogicznym pełnym rynkiem wynosi +1,02 pp, wygrane 12/23; p jednostronne około 0,397, p po kontroli maksimum 88 konfiguracji około 0,998. Nie jest to dowód przewagi poza próbą.

Zakupy 16.11 pozostają tym samym zestawem spółek. Podium ma kolejność **KGN, BNP, AGO**, spokojna **KGN, BNP, OPL, MIL, TOA, AGO, MBR, CAR, ING, HUG**. Zmieniła się kolejność; rezerwy pozostały te same. Kwoty na stronie wynikają z cen orientacyjnych, które trzeba potwierdzić na platformie.

## Weryfikacja

- Odtworzono load/prep/fixcal i doklejenie Yahoo z prywatnego snapshotu audytu; wykonano sim, liq i 88 konfiguracji seg po poprawkach. Surowych macierzy nie dołączono do repo.
- 20 testów syntetycznych (`python -m unittest discover -s tests -v`): split/scalenie, dywidenda bez reinwestowania, zawieszenie/wycofanie, brak otwarcia i wolumenu, cena open zamiast close t, budżet, bufor, aktualny kalendarz i brak danych dla trzymanej pozycji.
- Wskaźniki hi52, mom3 i combo identyczne po obcięciu danych na 14.12.2009, 15.11.2013 i 14.12.2016: przetestowano daty, w których poprzedni filtr sięgał do następnego zamknięcia.
- PyBroker odtworzył liczbę zleceń w 46 oknach; maksymalna różnica zwrotu **2,479×10⁻⁷** (około 0,005 zł na kapitale 20 tys.). To test dziennika wykonania, nie niezależne generowanie decyzji. Wyłączono domyślne zaokrąglanie przez PyBroker znormalizowanych cen do grosza.
- Stopy zwrotu w `liq` przy stałym progu są dokładnie zgodne z odpowiednimi oknami `sim`.
- `node tests/page-smoke.cjs`: wykonanie rzeczywistego skryptu strony w adapterze DOM; obie zakładki, wszystkie 23 wiersze, wygenerowane statystyki, budżety ≤20 tys. i ręczna zmiana ceny z separatorem tysięcy. Nie jest to test wyglądu w pełnej przeglądarce.
- `git diff --check`: bez błędów. Lista wersji i hashe prywatnych wejść: `results/reproduction.json`. Diagnostyka modelu: `results/model.json`; niewykonania i nieaktualne wyceny: `results/execution_warnings.csv`.

Prace nie potwierdzają historycznych składów indeksów, kompletności zdarzeń, prawidłowości każdego rekordu splitów/dywidend, wolumenu na otwarciu ani aktualnej siatki cen. Te ograniczenia są teraz jawne w kodzie, plikach wynikowych i opisie strony; do pełnej walidacji potrzebne są dodatkowe dane, nie kolejna arbitralna korekta cen.
