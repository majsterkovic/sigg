# Dane referencyjne

- `sigg_instruments_2026-11-16.txt`: 172 ISIN-y skopiowane z formularza SIGG; nie zastępują przyszłej listy gry.
- `sessions_2026_2027.csv`: sesje od 01.10.2026 do 12.03.2027; dni robocze bez 11.11, 24/25/31.12.2026 oraz 1/6.01.2027. Wykaz 2026 powołujący uchwałę GPW 753/2025: https://www.pekao.com.pl/biuro-maklerskie/inne-regulacje/dni-bez-sesji-na-GPW-2026.html . Przed kolejnym uruchomieniem sprawdź aktualne komunikaty GPW i daty przyszłych sesji.
- `market_events.csv`: niepełny, jawny rejestr zdarzeń. Zawieszenie ROBYG od 02.03.2018: raport emitenta 22/2018; wycofanie od 29.05.2018: raport 48/2018. URL-e do oryginałów w kolumnie source. Cena rozliczenia 3,98 zł pochodzi z ostatniego zamknięcia w snapshotcie DB (01.03; identyczny przeniesiony kurs 02.03). Sam koniec danych nie stanowi dowodu delistingu. Rejestr nie modeluje odrębnie przymusowego wykupu; daty zawieszenia i wycofania nie są zamienne.
- `company_descriptions.json`: opisy branżowe dla listy początkowej; nie są elementem sygnału ani rankingiem inwestycyjnym.

Surowe szeregi OHLCV, pełne dane dostawcy, rzeczywisty portfel i sekrety nie powinny trafiać do tego katalogu.
