# VocBenchissä ylläpidetyn YSOn muuntaminen TBC:ssä käytettyyn kehitystietomalliin.

***VocBenchistä viedyn YSOn jäädyttäminen aiemmin TBC:ssä ylläpidetyn YSOn kehitystietomallia vastaavaksi edellyttää erillistä skriptiä.***

Skriptillä muunnetaan VocBenchissä ylläpidetyn YSOn kehitystietomalli aiemmin TBC:ssä ylläpidetyn YSOn tietomallia vastaavaksi, mutta pitäen VocBenchissä lisätyt datat koskemattomina. Testitapauksena käytettiin Jungin tasalla olevaa JUHOa (raportti ja ohjeet jäljempänä). 

Lisätyötarve: Vaikka mutu-raportti näyttää JUHOa vasten uutta ja vanhaa YSOa vertailtaessa muutoksia, jotka ovat relevantteja ja raportti on testien osalta oikein, on vielä kuitenkin yksi haaste taklattavana. Nyt tiedämme asiantilan asioista, jotka ovat tiedossamme, mutta emme tiedä mitä emme tiedä eli tarkistelua ja varmistelua vielä tarvitaan. Käytännössä pitää löytää keino tutkia ja vertailla dataa niiltä osin, mikä ei päädy raporttiin -> jääkö jotain huomiotta? Onko asioita, joita mutu ei datasta johtuen tunnista?

## Tietomallimuunnosprosessi

YSOn kehitystietomallimuunnoksen (Vocbench -> TBC) suorittava skripti:<br>
_convert_vb_yso_to_tbc_yso.py_

Kesäkuulta 2025 oleva viimeinen TBC:ssä ylläpidetty YSO, jonka pitää olla aina mukana skriptin ajossa (tarvitaan TBC-ajan tietomallin mukailuun):<br>
_old-yso-202506-tbc.ttl_

VocBenchistä viety YSO (simuloi VB-versiosta luotavaa jäädytettyä ysoa mutta ei ole jäädytetty):<br>
_new-yso-202602-vb.ttl_

Jäädytystä simuloiva VB:n dataan (mutta ei tietomalliin) perustuva YSO _mutun_ kanssa käytettäväksi:<br>
_converted-yso.ttl_
(ei oikeasti jäädytetty joten apuluokat vielä mukana)

### Skriptin ajo:

```
python3 ./convert_vb_yso_to_tbc_yso.py --old ./old-yso-202506-tbc.ttl --new ./new-yso-202602-vb.ttl --out converted-yso.ttl
```

### Mututus (testitapaus JUHO)

JUHOn TBC-kehitystiedosto jäädytetyn Jung-YSOn kanssa käytettäväksi:<br>
_juho-to-be-used-with-jung.ttl_

***Ajo***

```
cd Finto-data/tools/vb-to-tbc-yso-conversion-for-mutu

java -jar [mutu folder]/mutu.jar -domainOnt ./juho-to-be-used-with-jung.ttl ../../vocabularies/yso/releases/2024.6.Jung/ysoKehitys.rdf -newYso ./converted-yso.ttl -domainOntUri https://finto.fi/juho/fi/page/ -newYsoUri https://dev.finto.fi/yet_unknown/fi/page/
```

### Lopputulos

***Tuotetut mutu-raportit uudelleennimettynä Excel- ja csv-muodossa:***
- mutu-report.xlsx
- mutu-report.csv

***Tutkitut tapaukset kuvana:***
- cases-checked.png




