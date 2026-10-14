# Tillväxtverket – inkvartering, Luleå kommun

Automatisk hämtning av **Gästnätter per hemland och månad** för Luleå kommun från Tillväxtverkets öppna API.

## Datakälla

Tillväxtverkets öppna API:

```text
https://oppnadata.tillvaxtverket.se/api/api/query/inkvartering/data/GuestNights_Country_Month.cbase
```

API-frågan filtrerar på:

- `KOMMUN_NAMN = Luleå`
- `NIVA_NAMN = Kommun`
- `AR >= 2010`

och grupperar på:

- år
- månad
- hemland

`ANLAGGNINGSTYP_NAMN` används inte som dimension. Därmed sammanfattas `ANTAL_GASTNATTER` över alla anläggningstyper, vilket är avsett att motsvara **Alla värden** för anläggningstyp i Tillväxtverkets portal.

## Filer

### `data/history.csv`
Aktuell komplett tidsserie. En rad per kombination av månad och hemland.

Kolumner:

```text
Ar,Manad,ArManad,Kommun,Hemland,Gastnatter
```

Det är den fil som i första hand är tänkt att kopplas till Power BI.

### `data/latest.csv`
Endast senast publicerade `ArManad`.

### `data/revisions.csv`
Loggar värden som Tillväxtverket ändrar eller tar bort efter att de redan har funnits i `history.csv`.
Den initiala backfillen loggas inte som revision.

## Automatisk körning

GitHub Actions-workflowen `.github/workflows/daily-tillvaxtverket.yml` körs en gång per dag samt manuellt via **Actions → Daily Tillvaxtverket guest nights → Run workflow**.

Om inget i datat har förändrats görs ingen Git-commit.

## Första körningen

1. Skapa ett tomt repository, exempelvis `LuleaRobert2/Tillvaxtverket-inkvartering`.
2. Ladda upp innehållet i denna ZIP till repositoryts rot.
3. Öppna **Actions** i GitHub.
4. Kör workflowen manuellt med **Run workflow**.
5. Kontrollera att `data/history.csv` skapas och att första perioden är `201001` eller tidigare.

Scriptet är medvetet inställt på att **misslyckas** om Tillväxtverkets API för Luleå börjar senare än 2010. Det förhindrar att en ofullständig tidsserie ser komplett ut.

## Säkerhetskontroller

Scriptet ersätter inte `history.csv` om:

- API:t inte längre innehåller minst år 2010,
- senaste publicerade period plötsligt går bakåt,
- antalet rader plötsligt minskar med mer än 10 %, eller
- API-svaret saknar de nödvändiga kolumnerna.

Detta är avsiktligt för att skydda den historiska filen mot tillfälliga eller förändrade API-svar.

## API-teknik

Tillväxtverkets tjänst använder Diver/DivePort Web API. Den stödjer server-side-filter som exempelvis:

```text
filter:KOMMUN_NAMN=Luleå
filter:NIVA_NAMN=Kommun
filter:AR:gte=2010
```

och gruppering med upprepade `dimension=`-parametrar. Därför behöver workflowen inte ladda ned hela Sveriges dataset vid varje kontroll.


## Interaktiv webbplats

`docs/index.html` visar motsvarande huvudvyer som Power BI-rapporten: Start, Enskilda år, Över flera år, Procentuell utveckling, Antalsutveckling och Månad 1–3 samt Metod & data. Filen läser `docs/data/history.csv` (automatiskt synkroniserad från `data/history.csv`) direkt och fungerar med statisk GitHub Pages-publicering från `docs/`.

### Årsdata

`build_annual.py` skriver `data/annual.csv` med en rad per år och hemland. Den körs av det befintliga dagliga arbetsflödet efter API-hämtningen. Kolumnerna `Manader_i_underlaget` och `Komplett_ar` används för att förhindra att ofullständiga år behandlas som helår. Årsfilen är **summerad månadsstatistik**, inte separat verifierad årsstatistik från myndighetens årsserie. En separat avstämning mot officiell årsstatistik återstår.

### Publicering

GitHub Pages behöver vara aktiverat under **Settings → Pages → Deploy from a branch → main → /docs**. Sidan publiceras därefter normalt på https://lulea-statistik.github.io/Tillvaxtverket-inkvartering/ .

### Källkritik

Den uppladdade Excel-ZIP-filen innehåller komplett årstäckning för 2019–2025 men också en felmärkt fil (`1990 januari.xlsx`, med september 2025 som faktisk period) samt 2026-filer som redovisar grupperade månader. GitHub-arkivets eget API-utdrag i `data/history.csv` används därför som huvudkälla. Ländernas världsdelar i webbvyn är en preliminär manuell klassificering och ska kvalitetssäkras innan filtreringen betraktas som fullständig.
