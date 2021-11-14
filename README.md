# snauwebAPI
API for snauweb. Autentisert med kerberos, autorisert i henhold til tilgangslister i postgres

## Struktur
App.py er scriptet som skal kjøres som endepunkt. Dette scriptet henter ut miljøvariabler satt av apache, og funker dermed kun om det kjøres av nettopp apache eller en annen CGI-kompatibel http-tjener. For lokal debugging kan konfigurasjonsflagget `debug` settes. Dette får API-et til å se etter CGI-headere i fila `./env.py` 

## Databasegrensenitt
For enkelt å kunne snakke med databasen man har valgt fra python kreves et bibliotek som har implementert den nødvendige kommunikasjonsprotokollen. For PostgreSQL bruker man `psycopg2` (https://www.psycopg.org/docs/install.html), for MySQL er det `Connector/Python` som gjelder (https://dev.mysql.com/doc/connector-python/en/connector-python-installation.html). Det eksister separate scripts som bruker hver av disse. Å sette `dbtype` til enten "PG" eller "MYSQL" i konfigurasjonsfilen velger hvilket som brukes. Om `dbtype` ikke er spesifisert er det "PG" som er standard. 

## Autentisering mot database
Databasehåndteringa forventer en konfigurasjonsfil. Denne fila skal se ut som følger, der <...> erstattes med de faktiske verdiene som kreves for å koble seg på databasen man har. Dette gjør det mulig å raskt bytte mellom testdatabaser og produksjon. Det er *veldig viktig* at denne fila *aldri* pushes til git, da den inneholder sensitiv informasjon. 
```
host=<internettadresse til databasetjener>
dbname=<navn på database>
user=<navn på databasebruker>
pswd=<passord>
dbtype=<"PG" for PosgtreSQL eller "MYSQL" for MySQL>
debug=<true | false>
```

Om du trenger en testdatabase og er student ved NTNU er det mulig å sette opp en på NTNU sine tjenere (https://innsida.ntnu.no/wiki/-/wiki/Norsk/Bruke+MySQL+ved+NTNU).

## Debugging
Om debug er satt til "true" leter rammeverket etter miljøvariabler i `./env.py` heller enn os.environ, og POST payload i `./payload.py`. I tillegg er det mulig å kjøre api.py som en enkel CGI-server vha `test/runCGI.py`. Om man kjører `python3 test/runCGI.py` fra rotmappa kjøres API-serveren på localhost:8000. Merk at `http.server` sin CGI-implementasjon ikke setter miljøvariabler. CGI-serveren kan dermed kun kjøres lokalt om `debug=true`
