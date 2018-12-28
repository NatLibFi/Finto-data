# Finto-skos-to-marc-muunnin

Muuntaa Finton SKOS-muotoisen sanastotiedoston MARC-muotoiseksi (.mrcx).

## Ajaminen

Python3 finto-skos-to-marc.py --vocabulary_code="sanastotunnus" --input="tiedostopolku" --languages="fi" --output="tiedostopolku2"

Katso tarkemmat ohjeet --help-komennolla.

## Konfiguraatiotiedosto

config.ini sisältää perusmuotoisen tiedoston, jota voi käyttää pohjana.
DEFAULT-osiossa on määritelty kaikille sanastoille yhteiset ominaisuudet, joita voi yliajaa muissa osioissa.