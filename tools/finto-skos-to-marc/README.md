# Finto-skos-to-marc-muunnin

Muuntaa Finton SKOS-muotoisen sanastotiedoston MARC-muotoiseksi (.mrcx).

Tukee tällä hetkellä `yso`-, `yso-paikat`- ja `slm`-sanastojen erikoisominaisuuksia.

### Ajaminen ja muunnos
Yksinkertaisimmillaan muunnos tapahtuu esimerkiksi seuraavalla komennolla:
`python3 finto-skos-to-marc.py --vocabulary_code="sanastotunnus" --input="tiedostopolku" --languages="fi" --output="tiedostopolku2" --log_file="tiedostopolku3"`
Tämä luo `tiedostopolku2`-tiedostopolkuun tiedoston, jossa on kompaktissa MARCXML-muodossa ohjelman muuntamat käsitteet. __Osa käsitteistä voi jäädä muuntamatta esimerkiksi puutteellisen tiedon vuoksi__ (näin mm. tapahtuu, jos käsitteellä ei ole muunnettavalla kielellä skos:prefLabel-ominaisuutta) tai esimerkiksi `--keep_deprecated_after="None"`-rajoitteen vuoksi. Rajoitteita on asetettavissa enemmän `config`-komentoriviparametrillä annettavassa konfiguraatiotiedostossa. __Käsitteiden suodattuminen on tarkoituksenmukaista. Jos sanaston käsitteillä on viittauksia toisiin sanastoihin, tulee näiden graafit saattaa ohjelman tietoon__ `--endpoint` ja `--endpoint_graphs`__-parametreilla.__ Yhdysvaltojen Kongressin kirjaston `LCSH`- ja `LCGF`-viitteitä ei kuitenkaan tarvitse asettaa näin: ne haetaan ja tallennetaan myöhempää käyttöä varten ohjelman toimesta automaattisesti, jos `--loc_directory="tiedostopolku"`-parametri on asetettu (varmistathan, että tällainen tiedostopolun mukainen kansio on olemassa ja siihen on ohjelmalla käyttö- ja kirjoitusoikeus).

Muunnettavan tiedosto on myös mahdollista putkittaa ohjelmalle, ja muunnettu tiedosto sekä lokitiedosto edelleenputkittaa UNIX-käytänteiden mukaisesti. Putkituksella ei kuitenkaan ole mahdollista ulostulostaa useita erikielisiä tiedostoja yhdellä kertaa - `--output`-parametria käytettäessä eri kieliversiot eritellään toisistaan `nimi-kielitarkenne`-erotuksilla.

Katso tarkemmat ohjeet --help-komennolla.

### Konfiguraatiotiedosto
Kaikille (paitsi pakolliselle `vocabulary_code`-komentoriviparametrille) on olemassa oma vastaava konfiguraatiotiedostossa asetettava kohtansa. `config.ini` sisältää perusmuotoisen konfiguraatiotiedoston, jota voi käyttää pohjana.
`[DEFAULT]`-osiossa on määritelty kaikille sanastoille yhteiset ominaisuudet, joita voi yliajaa muissa osioissa. __Komentoriviparametrit kuitenkin AINA yliajavat asetettuina konfiguraatiotiedoston vastaavat määritykset.__ Huomaathan, että kaikkia ominaisuuksia ei voi asettaa komentoriviltä. Listojen ilmaisemisessa välimerkkinä käytetään pilkkua. __Ohjelma käyttää oletusarvoisesti pakollista sanastokoodia vastaavaa osiota__, mutta tämän voi yliajaa asettamalla `config_section`-komentoriviparametrin (tarpeen esimerkiksi yso-paikkojen tapauksessa, jos haluaa pitää samassa konfiguraatiotiedossa kaikki sanastot).
