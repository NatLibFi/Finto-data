PTVL
====

PTVL:n masterdata sijaitsee [google sheets -taulukossa](https://docs.google.com/spreadsheets/d/1s5h2QsNB6r0YIao_JEapbaeDIyXao-dWin6mdaPsW5A/edit#gid=1454719279).
Tästä syystä päivityksen oikeellisuuden tarkistamisessa on hyvä olla erittäin tarkkana.

### Sanaston päivittäminen

Aja ensin `ptvl-from-skos.py` -skripti, joka luo csv-tiedostot taulukon tiedoista. Tämän jälkeen ajetaan 
`ptvl-to-skos.py`, joka tuottaa triplejä CSV-tiedostoista. Kolmantena työvaiheena on sanaston ajaminen skosifyn läpi `toskos.sh`-skriptillä. Näiden vaiheiden jälkeen on erittäin tärkeää tarkistaa 
`git diff`-komennolla, että päivitys näyttäisi onnistuneen.
