# Finto-skos-to-marc-muunnin

Muuntaa Finton SKOS-muotoisen sanastotiedoston MARC-muotoiseksi (.mrcx).

Tukee tällä hetkellä `yso`-, `yso-paikat`- ja `slm`-sanastojen erikoisominaisuuksia.

### Ajaminen ja muunnos
Ohjelma edellyttää vähintään Python versiota 3.4.
Ohjelmaa voidaan ajaa kolmella tavalla:
1. Tuotetaan sanaston kaikki käsitteet MARC21-muodossa
2. Tuotetaan sanaston kaikki käsitteet ja ylläpidetään tiedostoa MARC21-tietueiden muutospäivämääristä
3. Haetaan vain muuttuneet käsitteet

Yksinkertaisimmillaan eli 1. tavalla muunnos tapahtuu esimerkiksi seuraavalla komennolla:
`python3 finto-skos-to-marc.py --vocabulary_code="sanastotunnus" --input="tiedostopolku" --languages="fi" --output="tiedostopolku2" --log_file="tiedostopolku3"`
Tämä luo `tiedostopolku2`-tiedostopolkuun tiedoston, jossa on kompaktissa MARCXML-muodossa ohjelman muuntamat käsitteet. __Osa käsitteistä voi jäädä muuntamatta esimerkiksi puutteellisen tiedon vuoksi__ (näin mm. tapahtuu, jos käsitteellä ei ole muunnettavalla kielellä skos:prefLabel-ominaisuutta) tai esimerkiksi `--keep_deprecated_after="None"`-rajoitteen vuoksi. Rajoitteita on asetettavissa enemmän `config`-komentoriviparametrillä annettavassa konfiguraatiotiedostossa. __Käsitteiden suodattuminen on tarkoituksenmukaista. Jos sanaston käsitteillä on viittauksia toisiin sanastoihin, tulee näiden graafit saattaa ohjelman tietoon__ `--endpoint` ja `--endpoint_graphs`__-parametreilla.__ Yhdysvaltojen Kongressin kirjaston `LCSH`- ja `LCGF`-viitteitä ei kuitenkaan tarvitse asettaa näin: ne haetaan ja tallennetaan myöhempää käyttöä varten ohjelman toimesta automaattisesti, jos `--loc_directory="tiedostopolku"`-parametri on asetettu (varmistathan, että tällainen tiedostopolun mukainen kansio on olemassa ja siihen on ohjelmalla käyttö- ja kirjoitusoikeus).

Toisella tavalla komentoon on lisättävä --modification_dates-parametri, joka on tiedostopolku tietueiden muutospäivämäärät sisältävään tietueeseen. Tiedosto on muotoa '{käsitteen URI: (muutospäivämäärä, tietueen MD5-tiiviste)}. Jos tiedostoa ei ole olemassa ennestään, tiedosto luodaan ja viimeiseksi muutospäivämääräksi jokaiselle käsitteelle annetaan ajon aikainen päivämäärä.

Kolmannella tavalla on --modification_dates-parametrin lisäksi tarvitaan --keep_modified_after-parametrin, jonka avulla haetaan parametrin päivämääränä ja sen jälkeen muuttuneet käsitteet.

Muunnettava tiedosto on myös mahdollista putkittaa ohjelmalle, ja muunnettu tiedosto sekä lokitiedosto edelleenputkittaa UNIX-käytänteiden mukaisesti. Putkituksella ei kuitenkaan ole mahdollista ulostulostaa useita erikielisiä tiedostoja yhdellä kertaa - `--output`-parametria käytettäessä eri kieliversiot eritellään toisistaan `nimi-kielitarkenne`-erotuksilla.

Katso tarkemmat ohjeet --help-komennolla.

### Konfiguraatiotiedosto
Osalle komentoriviparametreistä on olemassa oma vastaava konfiguraatiotiedostossa asetettava kohtansa. `config.ini` sisältää perusmuotoisen konfiguraatiotiedoston, jota voi käyttää pohjana.
`[DEFAULT]`-osiossa on määritelty kaikille sanastoille yhteiset ominaisuudet, joita voi yliajaa muissa osioissa. __Komentoriviparametrit kuitenkin AINA yliajavat asetettuina konfiguraatiotiedoston vastaavat määritykset.__ Huomaathan, että kaikkia ominaisuuksia ei voi asettaa komentoriviltä. Listojen ilmaisemisessa välimerkkinä käytetään pilkkua. __Ohjelma käyttää oletusarvoisesti pakollista sanastokoodia vastaavaa osiota__, mutta tämän voi yliajaa asettamalla `config_section`-komentoriviparametrin (tarpeen esimerkiksi yso-paikkojen tapauksessa, jos haluaa pitää samassa konfiguraatiotiedossa kaikki sanastot).

Ohjelman parametreistä ja konfiguroinnista on lisätietoa [KIWI-sivuilla](https://www.kiwi.fi/pages/viewpage.action?pageId=138085082).

# Finto-skos-to-marc-converter

Converts a SKOS concept from a Finto ontology to MARCXML record in MARC21 format.

Current supported ontologies are YSO (General Finnish ontology), YSO places and SLM.

### Execution and conversion
The program requires Python version 3.4 or higher.
The program can be executed in three ways:
1. All concepts of vocabulary are converted to MARC21 format.
2. All concepts of vocabulary are converted and a file for modification dates is updated.
3. Only modified concepts in an output file.

The first and the most simple way to do conversion is with these command line arguments:
`python3 finto-skos-to-marc.py --vocabulary_code="vocabulary code" --input="file path" --languages="fi" --output="file path" --log_file="file path"`
This creates a file output that has converted records in MARCXML format.

The second way reguires --modification_dates parameter, that is a file path to a record that has the last modified dates of the MARC21 records. 

The third way requires --keep_modified_after parameter in addition to --modification_dates parameter. With this parameter all the concepts that have been modified during or after the date are written to the output file.

It is also possible to pipe the output file to a program. It is not possible to pipe files in multiple languages at simultaneously. When output parameter is used, different language versions are separated by `vocabulary name-language code`. If concepts have references to another vocabularies, their graphs have to be defined with parameters `--endpoint` and `--endpoint_graphs`. References to The Library of Congress subject headings are downloaded and saved for later use, if the `--loc_directory` parameter is defined (make sure that the folder exists and the program has permission to read and write).

See further instructions with --help command.

### Config file
Some of the command line parameters have an equal parameter in the configuration file. The file `config.ini` in the project's folder has a template configuration. `[DEFAULT]` section contains the common properties for all vocabularies and they can be overriden in other sections. __Command line arguments override ALWAYS the values in the configuration file. __Note that not all the values can be set in the command line. When the value is a list, use comma as a separator. __The program uses by default the config section that has same name as --vocabulary_code parameter, but this can overridden by `config_section` command line parameter (Necessary if e.g. YSO places is in the configuration file).

A list of command line and configuration parameters is in a [KIWI web page](https://www.kiwi.fi/pages/viewpage.action?pageId=138085082) (in Finnish only).