## Idea

Skriptin on tarkoitus auttaa vastaamaan vuotuisten tilastointien yhteydessä esitettyyn kysymykseen, kuinka montaa suomen-, englannin-, saamen- ja ruotsinkielistä altLabelia on muokattu tai montako sellaista on lisätty vuoden aikana (YSO).

## Käyttö

Muokkaa skriptin _edited-altlabels-per-year.sh_ alussa olevien muuttujien arvot eli polut ja päivämäärät käyttöympäristösi ja ajankohdan mukaisiksi. Varmista, että skriptillä on ajo-oikeudet.

Aja:
```./edited-altlabels-per-year.sh```

Skripti ei ole kovin nopea, mutta tekee pyydetyt asiat 5-10 minuutissa ja tuottaa kielikohtaiset editointien määrät.

## Konepellin alla
Skripti hakee Finto-data-repositorystä commit-hashien perusteella vuoden viimeisen ja ensimmäisen yso-skos.ttl-tiedoston, lisää molemmista versiot graafeiksi trig-tiedostoon, vähentää vanhemmasta graafista uudemman altLabeleiden osalta ja tuottaa erotuksen pohjalta tiedoston, josta grepataan kullekin kielelle kuuluvat osat tulosteina skriptin lopussa.

## Tulevaa
Skriptiä kannattaa kehittää niin, että sille voi syöttää muitakin propertyjä, kuten hiddenLabel, prefLabel jne.

Jos on kysyttävää, lähetä viesti osoitteeseen:
mika.vaara@helsinki.fi
