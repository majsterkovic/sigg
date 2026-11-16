# Protokół porównania strategii — 16.11.2026

Zapisany przed uruchomieniem poniższych wariantów. Nie jest prerejestracją niezależnej próby: lata 2003–2025 były już oglądane w poprzednim badaniu.

Stałe: kapitał 20 tys. PLN, 3 pozycje, bufor 6, min_n=5 przed dodatkowym filtrem, próg obrotu 300 tys., przegląd co 21 sesji, reguły i dane poprawionego silnika. Dwa sygnały (combo, mom3), dwa koszyki (liquidity-21-140, main-proxy), trzy reguły portfela = 12 konfiguracji. Nie dodajemy parametrów po obejrzeniu wyników.

Reguły:
- base: obecne podium lub identyczna konstrukcja z mom3.
- corr: przy przeglądzie greedy po rankingu od najwyższego sygnału; dopuszczaj spółkę wyłącznie jeśli korelacja z każdą wcześniej dopuszczoną <=0,70, na zwrotach adjusted close z ostatnich 126 sesji. Wymagaj 84 wspólnych obserwacji; brak korelacji oznacza niedopuszczenie kolejnej spółki. Korelacje bez sztucznych zer po braku notowań. Bufor 6 stosowany do przefiltrowanego rankingu; niezależność wymagana w całej liście kandydatów. To może wymusić sprzedaż skorelowanego dotychczasowego składnika. Niewypełnione sloty zostają w gotówce; przy niewykonanej sprzedaży lub zawieszeniu limit korelacji nie jest gwarantowany.
- trend: na przeglądzie, gdy WIG zamknięcie <= średnia 200 sesji, sprzedaj dostępne pozycje na następnym otwarciu i pozostań w gotówce do kolejnego przeglądu z WIG powyżej średniej. Nie stosuj codziennego stopa. Nie łączymy filtra corr i trend.

Ocena: pełne 23 lata, wcześniejsze 2003–2012, późniejsze 2013–2025; średnia, mediana, najgorsze okno gry, udział strat i wyników >20%/>40%, transakcje, prowizje. Najgorsze okno nie jest maksymalnym obsunięciem w trakcie gry. Brak danych rywali uniemożliwia pomiar prawdopodobieństwa top 3.

Walk-forward: dla każdego roku 2013–2025 wybór wariantu o najwyższej średniej z lat 2003..y-1; deterministyczny remis po nazwie. Selekcja nie korzysta z wyniku roku y. Główna ocena: porównanie z bazowym combo/liquidity-21-140/base w tych samych latach. Średnia nie optymalizuje bezpośrednio szansy na podium.

Niepewność: sparowany bootstrap 90% i test zamiany znaków dla różnicy wobec bazowego podium, korekta max-T dla 11 alternatyw, 100 tys. losowań, seed 20261116. Założenie testu: symetria niezależnych rocznych wektorów różnic. Obejmuje tylko to badanie, nie wcześniejsze poszukiwania.

Wrażliwość kosztowa: wszystkie 12 wariantów dodatkowo przy 0,60% prowizji od transakcji; bez ponownego strojenia reguł. Te same sygnały t-1 i ten sam model braku wykonania. Nie stosujemy aktualnej listy instrumentów SIGG do historii, by nie dodawać selekcji ocalałych.
