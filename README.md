Norgesnett API-integrasjonen lar deg hente informasjon om strømpriser og kapasitetsledd direkte fra Norgesnett. Dette er nyttig for å overvåke strømforbruket ditt og forstå hvordan nettleien beregnes.

Hva gjør Norgesnett API-integrasjonen?
Integrasjonen henter følgende data:

Energipriser: Sanntidsinformasjon om billig (natt) og normal (dag) energipris.
Kapasitetsledd: Informasjon om hvilket kapasitetsledd (trinn) du befinner deg i, basert på ditt strømforbruk.
Tariffdetaljer: Opplysninger om gjeldende tariffer og priser.

Hvordan installere Norgesnett API-integrasjonen

Forutsetninger:  
API nøkkel fra Norgesnett (api_key): xxxxxxxxxxxxxxxxx  
Målepunkt ID (metering_point_id): xxxxxxxxxxxxxxxxx  
Oppdaterings interval i timer (update_interval): 24 timer  
Standard URL (api_url): "https://gridtariff-api.norgesnett.no/api/v1.01/Tariff"  
  
Trinn 1:  
  
Hent API nøkkel fra Norgesnett. https://gridtariff-api.norgesnett.no/swagger/index.html  
Du må ha Målepunkt ID klar for å hente ut denne.  
  
Trinn 2:  
Etter oppsettet vil en sensor, for eksempel sensor.norgesnett_tariff, oppdateres med energiprisene. Du kan se attributter som:  
cheap_total: Billig energipris (natt).  
normal_total: Normal energipris (dag).  
kapasitetsledd_trinn: Ditt nåværende kapasitetsledd.  
  
Norgesnett bruker en kapasitetsbasert nettleiemodell der nettleien består av to deler:  
Kapasitetsledd: Basert på hvor mye strøm du bruker samtidig.  
Energiledd: Basert på hvor mye strøm du totalt forbruker.  
  
  
  
Kapasitetsleddet er delt inn i 10 trinn:  
  
| Trinn | Effektområde (kW) | Kapasitetsledd (kr/mnd)|
|-------|-------------------|-------------------------|
| 1     | 0-1,99            | 102,51                  |
| 2     | 2-4,99            | 170,86                  |
| 3     | 5-9,99            | 280,97                  |
| 4     | 10-14,99          | 499,68                  |
| 5     | 15-19,99          | 663,70                  |
| 6     | 20-24,99          | 823,18                  |
| 7     | 25-49,99          | 1 275,76                |
| 8     | 50-74,99          | 1 997,18                |
| 9     | 75-99,99          | 2 718,59                |
| 10    | >100              | 4 405,95                |
  
  
  
Attributter og deres funksjon:  
  
| Attributt                        | Beskrivelse                                            |
|----------------------------------|--------------------------------------------------------|
| Tariff ID                        | Identifikator for tariffen.                            |
| Tariff key                       | Type tariff.                                           |
| Product                          | Navn på tariffproduktet.                               |
| Company name                     | Navnet på selskapet som leverer tariffen.              |
| Company org no                   | Organisasjonsnummeret til selskapet.                   |
| Title                            | Beskrivelse av tariffen.                               |
| Last updated                     | Når tariffdataene sist ble oppdatert.                  |
| Resolution                       | Oppdateringsintervall i minutter.                      |
| Cheap energy ID                  | ID for billig energiperiode.                           |
| Cheap total                      | Total pris per kWh i billig periode.                   |
| Cheap total ex vat               | Pris ekskl. mva i billig periode.                      |
| Cheap taxes                      | Mva for billig energi.                                 |
| Normal energy ID                 | ID for normal energiperiode.                           |
| Normal total                     | Total pris per kWh i normal periode.                   |
| Normal total ex vat              | Pris ekskl. mva i normal periode.                      |
| Normal taxes                     | Mva for normal energi.                                 |
| Kapasitetsledd value min         | Minimum strømforbruk for dette trinnet.                |
| Kapasitetsledd value max         | Maksimum strømforbruk for dette trinnet.               |
| Kapasitetsledd next down         | Forrige trinn.                                         |
| Kapasitetsledd next up           | Neste trinn.                                           |
| Kapasitetsledd unit              | Måleenhet for strømforbruk.                            |
| Kapasitetsledd monthly total     | Månedlig kostnad for kapasitetsleddet.                 |
| Kapasitetsledd monthly ex vat    | Månedlig kostnad uten mva.                             |
| Kapasitetsledd monthly taxes     | Mva for kapasitetsleddet.                              |
| Kapasitetsledd currency          | Valuta brukt i tariffen.                               |
| Kapasitetsledd unit measure      | Måleenhet for månedlig kostnad.                        |
| Kapasitetsledd trinn             | Trinnnummer basert på forbruk.                         |
| Oppdatering                      | Når data sist ble hentet fra API-et.                   |
  
Disse attributtene gir deg en detaljert oversikt over energikostnadene dine, kapasitetsnivået og hvordan tariffen beregnes.
  
Ved å bruke Norgesnett API-integrasjonen kan du få bedre innsikt i strømforbruket ditt og optimalisere kostnadene basert på gjeldende tariffer og kapasitetsledd.  
