Slik Bruker Du Norgesnett API
Denne guiden hjelper deg steg-for-steg med å komme i gang med Norgesnett sitt API. Du får tilgang til data om nettleie, kapasitetsledd og strømpriser. Dette kan være nyttig for å holde oversikt over forbruk og optimalisere energikostnadene dine.

Hva trenger du?
En nettleser (f.eks. Chrome eller Firefox).
En internettilkobling.
Tilgang til Norgesnett sitt API-dokumentasjonsverktøy via Swagger.
Steg 1: Åpne Norgesnett API-dokumentasjon
Start med å åpne følgende lenke i nettleseren din:

https://gridtariff-api.norgesnett.no/swagger/index.html

Dette tar deg til Norgesnett sitt Swagger-grensesnitt, som lar deg teste og utforske de tilgjengelige API-endepunktene.

Steg 2: Forstå Swagger-grensesnittet
Når du åpner lenken, vil du se en side med mange forskjellige endepunkter listet opp, som f.eks. GET /tariffs, GET /capacity, etc. Her kan du teste de ulike forespørslene for å hente informasjon om nettleie og kapasitetsledd.

Steg 3: Generer en API-nøkkel
Før du kan hente data fra API-et, trenger du en API-nøkkel. Følg disse trinnene:

Logg inn eller registrer deg på Norgesnett sine nettsider for å få tilgang til API-nøkkelen.
Etter registrering, gå til seksjonen for API-tilgang.
Generer en ny API-nøkkel, som du deretter kan bruke til å autentisere forespørslene dine.
Steg 4: Test et Endepunkt i Swagger
Eksempel: Hente Kapasitetsledd Informasjon
Gå til endepunktet:
bash
Kopier kode
GET /tariffs
Klikk på "Try it out"-knappen for å teste forespørselen.
I Authorization-feltet, skriv inn API-nøkkelen din slik:
Kopier kode
Bearer DIN_API_NOKKEL
Klikk på "Execute" for å sende forespørselen.
Du vil nå få en respons som viser informasjon om kapasitetsledd, månedlige kostnader, og strømpriser.

Feilsøking
Hvis du opplever problemer:

Sjekk at API-nøkkelen din er gyldig og at du har lagt den inn riktig.
Sørg for at du bruker riktig URL og at du har inkludert Bearer før nøkkelen din.
