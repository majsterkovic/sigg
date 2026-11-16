# Backtest hipotez dla SIGG — 16.11.2026

## Wnioski

Najlepszy średni wynik ma **obecne podium z filtrem WIG > MA200**: +20,84% wobec +17,28%. Najgorsze okno poprawia się z -35,06% do -21,15%, a liczba stratnych lat spada z 8 do 5. Wyników >40% pozostaje tyle samo: 4/23. Filtr pomaga tu głównie ograniczyć straty; nie wykazano wzrostu szans na konkursowe podium.

Nominalne p=0,044 wygląda obiecująco, ale po kontroli 11 alternatyw wynosi **0,183**. W późniejszym okresie stały wariant z filtrem daje +17,29% wobec +13,99%; przedział różnicy 90% [-0,73 pp; +8,41 pp] obejmuje zero. To kandydat do dalszej obserwacji, nie udowodniona przewaga.

Wpływ kryzysów jest duży: okna zaczynające się w 2008 i 2019 odpowiadają za 77.7% sumy różnic. Bez 2019 średnia poprawa wynosi +2,13 pp; bez obu tych okien +0,87 pp. Filtr poprawia 7 lat, pogarsza 3 i pozostawia 13 bez zmiany. Nie jest to strategia lepsza w każdym roku.

Samo mom3 nie poprawia średniego wyniku w pełnej próbie; w późniejszych latach daje większą średnią niż bazowe combo, ale także głębokie straty. Ograniczenie korelacji do 0,70 nie zmienia żadnego rocznego wyniku bazowego podium; dla pozostałych sygnałów efekt jest mały. Nie obniżano progu po obejrzeniu tego rezultatu. Poszerzenie koszyka o największe spółki nie poprawia średniej przy porównaniu tych samych sygnałów i filtrów.

Wybór kroczący na podstawie wcześniejszych lat osiąga średnio +16,57% wobec +13,99% bazy w latach 2013–2025. Nie zastosowano do wszystkich tych lat jednego zwycięzcy wybranego po fakcie.

## Zakres i sposób oceny

Porównano 12 konfiguracji z góry określonych w `research/strategy_plan.md`: sygnał combo lub mom3, koszyk płynności 21–140 lub cały zbiór po odjęciu stałej listy NC, bez dodatków albo z filtrem korelacji albo z filtrem trendu WIG. Dla każdej wykonano 23 okna gry oraz powtórzenie przy wyższym koszcie: łącznie **552 symulacje**. Nie zmieniano parametrów po obejrzeniu wyników.

Każde okno zaczyna się z 20 000 zł: pierwsza sesja od 16 listopada do ostatniej sesji nie późniejszej niż 12 marca kolejnego roku. Trzy pozycje, bufor 6, min_n=5, przegląd co 21 sesji; sygnał do t−1, handel po open t, pełne sztuki i prowizja 0,39%. Dywidendy są należnością do końca gry. Wyniki są zwrotami za około cztery miesiące, nie roczną stopą i nie CAGR. „Najgorsze” to najgorszy wynik całego okna, nie maksymalne obsunięcie wewnątrz niego.

Filtr korelacji wybiera zachłannie kolejne spółki po sygnale z listy, wymagając korelacji ≤0,70 z każdą już zaakceptowaną. Okno to 126 sesji, minimum 84 wspólne obserwacje; brak korelacji nie oznacza niezależności. Filtr zmienia również ranking utrzymania w buforze. Wariant trendu na przeglądzie przechodzi do gotówki, gdy WIG nie jest powyżej średniej 200 sesji, i wraca dopiero na przeglądzie spełniającym warunek. Nie ma codziennych stopów. Nie łączono obu filtrów.

\* „Bez NC” oznacza odjęcie statycznej listy 2021–2024, a nie historycznie poprawne członkostwo rynku głównego. W wariancie szerokim dopuszczono również duże spółki. Historyczne listy instrumentów gry są nieznane, więc dzisiejszej listy ISIN nie przenoszono w przeszłość.

## Wszystkie warianty

| Wariant | Średnia 2003–2025 | Mediana | Najgorsze | Straty | Wynik >40% | Średnia 2013–2025 | Transakcje/okno |
|---|---:|---:|---:|---:|---:|---:|---:|
| combo / 21–140 / WIG > MA200 | +20,84% | +11,99% | -21,15% | 5/23 | 4/23 | +17,29% | 9.4 |
| combo / bez NC* / WIG > MA200 | +19,23% | +5,55% | -21,15% | 5/23 | 3/23 | +14,02% | 10.2 |
| mom3 / 21–140 / WIG > MA200 | +17,85% | +12,87% | -25,14% | 7/23 | 4/23 | +15,80% | 8.5 |
| combo / 21–140 / bez dodatków | +17,28% | +11,99% | -35,06% | 8/23 | 4/23 | +13,99% | 11.8 |
| combo / 21–140 / korelacja ≤0,70 | +17,28% | +11,99% | -35,06% | 8/23 | 4/23 | +13,99% | 11.8 |
| mom3 / 21–140 / korelacja ≤0,70 | +16,86% | +12,87% | -36,44% | 9/23 | 5/23 | +15,84% | 11.0 |
| mom3 / 21–140 / bez dodatków | +16,84% | +12,87% | -36,44% | 9/23 | 5/23 | +15,81% | 11.0 |
| combo / bez NC* / korelacja ≤0,70 | +16,67% | +9,72% | -35,06% | 8/23 | 3/23 | +12,27% | 12.7 |
| combo / bez NC* / bez dodatków | +16,66% | +9,72% | -35,06% | 8/23 | 3/23 | +12,25% | 12.7 |
| mom3 / bez NC* / WIG > MA200 | +13,24% | +6,96% | -24,91% | 6/23 | 3/23 | +10,64% | 8.6 |
| mom3 / bez NC* / korelacja ≤0,70 | +12,79% | +7,73% | -36,44% | 8/23 | 4/23 | +10,46% | 11.2 |
| mom3 / bez NC* / bez dodatków | +12,63% | +7,73% | -36,44% | 8/23 | 4/23 | +10,18% | 11.3 |

Progi +20% i +40% opisują ogon wyników, a nie szansę na top 3. Wyników pozostałych uczestników nie ma w danych. Wszystkie metryki, w tym +20%, opłaty, gotówka i braki wykonania, znajdują się w plikach CSV.

## Czy poprawa względem obecnego podium jest przekonująca?

Bazą jest combo / 21–140 / bez dodatków. Różnice są sparowane po latach, a przedziały to bootstrap 90% (100 000 losowań). Test jednostronny sprawdza poprawę średniej; korekta max-T obejmuje 11 alternatyw i zachowuje ich zależność w danym roku. Założenie: symetria niezależnych rocznych wektorów różnic. Korekta nie obejmuje wcześniejszych badań i wyboru samego momentum.

| Wariant | Różnica średniej | Bootstrap 90% | Lepsze lata | p | p po max-T |
|---|---:|---|---:|---:|---:|
| combo / 21–140 / WIG > MA200 | +3,56 pp | [+0,59 pp; +7,10 pp] | 7/23 | 0,044 | 0,183 |
| combo / bez NC* / WIG > MA200 | +1,95 pp | [-3,71 pp; +8,28 pp] | 9/23 | 0,311 | 0,738 |
| mom3 / 21–140 / WIG > MA200 | +0,57 pp | [-6,20 pp; +6,95 pp] | 15/23 | 0,446 | 0,871 |
| combo / 21–140 / korelacja ≤0,70 | +0,00 pp | [+0,00 pp; +0,00 pp] | 0/23 | 1,000 | 1,000 |
| mom3 / 21–140 / korelacja ≤0,70 | -0,42 pp | [-7,60 pp; +7,12 pp] | 13/23 | 0,534 | 1,000 |
| mom3 / 21–140 / bez dodatków | -0,44 pp | [-7,68 pp; +7,16 pp] | 13/23 | 0,536 | 1,000 |
| combo / bez NC* / korelacja ≤0,70 | -0,61 pp | [-5,19 pp; +4,83 pp] | 7/23 | 0,560 | 1,000 |
| combo / bez NC* / bez dodatków | -0,62 pp | [-5,20 pp; +4,82 pp] | 7/23 | 0,561 | 1,000 |
| mom3 / bez NC* / WIG > MA200 | -4,04 pp | [-10,25 pp; +2,27 pp] | 11/23 | 0,844 | 1,000 |
| mom3 / bez NC* / korelacja ≤0,70 | -4,49 pp | [-11,18 pp; +2,66 pp] | 9/23 | 0,841 | 1,000 |
| mom3 / bez NC* / bez dodatków | -4,65 pp | [-11,34 pp; +2,51 pp] | 9/23 | 0,849 | 1,000 |

Różnice i granice przedziałów w tej tabeli są w punktach procentowych.

## Kontrola na późniejszych latach

Lata 2003–2012 stanowią początkowy trening. W każdym roku 2013–2025 wybrano wariant o najwyższej średniej w latach 2003..y−1, a następnie zastosowano wyłącznie jego wynik w roku y. To retrospektywna walidacja krocząca: wcześniejsze badania obejmowały już te dane, więc nie jest to nienaruszona próba poza badaniem. Wybór maksymalizuje średnią, nie nieznaną szansę na nagrodę.

| Rok testowy | Wariant wybrany z przeszłości | Wynik wyboru | Wynik obecnego podium |
|---|---|---:|---:|
| 2013 | combo / bez NC* / WIG > MA200 | -21,15% | -21,15% |
| 2014 | combo / bez NC* / WIG > MA200 | -1,18% | +1,00% |
| 2015 | combo / bez NC* / WIG > MA200 | +0,00% | -13,05% |
| 2016 | combo / bez NC* / WIG > MA200 | +12,36% | +20,53% |
| 2017 | combo / 21–140 / WIG > MA200 | +5,81% | +7,01% |
| 2018 | combo / 21–140 / WIG > MA200 | -1,96% | -4,57% |
| 2019 | combo / bez NC* / WIG > MA200 | -0,21% | -35,06% |
| 2020 | combo / bez NC* / WIG > MA200 | +97,92% | +99,17% |
| 2021 | combo / 21–140 / WIG > MA200 | -11,78% | -16,28% |
| 2022 | combo / 21–140 / WIG > MA200 | +30,12% | +30,12% |
| 2023 | combo / 21–140 / WIG > MA200 | +38,17% | +38,17% |
| 2024 | combo / 21–140 / WIG > MA200 | +20,69% | +29,31% |
| 2025 | combo / 21–140 / WIG > MA200 | +46,60% | +46,60% |

Selektor kroczący: średnia **+16,57%**, baza **+13,99%**; różnica +2,58% (pp), przewaga w 4/13 latach, nominalny bootstrap 90% [-1,70%; +7,87%] (pp). Ten przedział jest orientacyjny: kolejne decyzje selektora korzystają z nakładających się okresów treningowych.
Najgorsze późniejsze okno: selektor -21,15%, baza -35,06%. Wynik >40%: 2/13 wobec 2/13.

## Wrażliwość na koszty

Prowizja 0,60% od transakcji zamiast 0,39% to jawny test droższego wykonania, nie model rzeczywistych spreadów i poślizgu. Wariant wybierany krocząco pozostaje wybrany według treningu przy 0,39%.

| Wariant | Średnia przy 0,39% | Średnia przy 0,60% |
|---|---:|---:|
| combo / 21–140 / WIG > MA200 | +20,84% | +20,11% |
| combo / bez NC* / WIG > MA200 | +19,23% | +18,31% |
| mom3 / 21–140 / WIG > MA200 | +17,85% | +17,22% |
| combo / 21–140 / bez dodatków | +17,28% | +16,44% |
| combo / 21–140 / korelacja ≤0,70 | +17,28% | +16,44% |
| mom3 / 21–140 / korelacja ≤0,70 | +16,86% | +16,09% |
| mom3 / 21–140 / bez dodatków | +16,84% | +16,07% |
| combo / bez NC* / korelacja ≤0,70 | +16,67% | +15,61% |
| combo / bez NC* / bez dodatków | +16,66% | +15,61% |
| mom3 / bez NC* / WIG > MA200 | +13,24% | +12,63% |
| mom3 / bez NC* / korelacja ≤0,70 | +12,79% | +12,03% |
| mom3 / bez NC* / bez dodatków | +12,63% | +11,86% |

## Ograniczenia i odtworzenie

Badanie dziedziczy ograniczenia poprawionego modelu (`results/model.json`): niepełna historia zdarzeń, źródłowa niepewność splitów/dywidend, proxy koszyka i brak wolumenu aukcji, częściowych realizacji oraz limitu +1,5% w symulacji. Korelacja dotyczy przeszłości i nie gwarantuje ochrony podczas przyszłego krachu. Wstrzymana sprzedaż może pozostawić skorelowane pozycje. Nie wykorzystywano obecnych sektorów jako historycznego filtra, by nie dodawać bieżącej klasyfikacji do dawnych decyzji.

Kontrola bazowego wariantu: maksymalna różnica względem opublikowanego `results/seg_years.csv` = 0. Pięć testów reguł potwierdza wybór nieskorelowanej spółki, politykę brakujących korelacji, brak odczytu przyszłego WIG, brak dostępu do roku testowego przy selekcji i przejście do gotówki na następnym otwarciu.

```bash
SIGG_DATA_DIR=/sciezka/do/snapshotu python research/backtest_hypotheses.py
python research/report_hypotheses.py
python -m unittest discover -s tests -p test_hypotheses.py -v
```

Pliki: `years.csv` — 552 wyników okien; `stats.csv` — oba koszty i trzy okresy; `paired_all.csv`, `paired_late.csv` — porównania sparowane; `walk_forward.csv` — wybory kroczące i ich wyniki; `manifest.json` — protokół i kontrola bazy. Nie zmieniono na podstawie eksperymentu strategii operacyjnej ani listy zakupów.
