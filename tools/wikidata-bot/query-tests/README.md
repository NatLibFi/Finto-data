# Ajo-ohje:

## Ymmärräthän, etteivät tässä kansiossa olevat skriptit ole tarkoitettu yso-botin käyttöön sellaisenaan, vaan niiden avulla voidaan hahmottaa dataa ja etsiä testimielessä parhaita tapoja käsitellä dataa.

Skriptit eivät esimerkiksi puutu lainkaan siihen, kuka päivityksiä Wikidataan on tehnyt, koska käyttäjätiedot pitää hakea Wikidatan rajapinnasta

Rq-tiedostojen nimistä saa suunnilleen kuvan, mitä kyselyllä yritetään saavuttaa

Kun olet hakenut Wikidatasta tarvittavat asiat, niin voit käyttää tulostiedostoa sekä yson julkaisutiedostoa arq:lla tehtävässä haussa esim seuraavasti:

```/SPARQL/apache-jena-4.5.0/bin/arq --data wikidata_ysomap.ttl --data /Finto-data/vocabularies/yso/yso-skos.ttl --query yso-references-wikidata-but-wikidata-does-not-reciprocate.rq```
