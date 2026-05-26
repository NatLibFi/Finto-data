# VocBenchissä ylläpidetyn YSOn kehitystietomallin mukaisen YSOn muuntaminen TBC:n vastaavaan.

***Tietomallimuunnoksen toteuttaminen edellyttää siihen tarkoitetun skriptin ajamista VocBenchistä ladatulle YSOlle.***

Skriptille syötetään vanha YSO _(--old)_ eli viimeinen TBC:llä ylläpidetty versio kesäkuulta 2025. Se toimii tietomallina, johon VocBenchistä ladattu YSO _(--new)_ mukautetaan eli käytännössä uudemman YSOn datat talletetaan TBC:ssä käytetyn YSOn tietomalliin ja TBC-version datoja ei siirretä konvertoitavaan tiedostoon _(--out)_. Kaikissa tulevissa ajoissa täytyy käyttää mallina, vanhaa YSOa eli tiedostoa _old-yso-202506-tbc.ttl_.

Skriptin tuottama konvertoitu YSO on testattu Jungin aikaisella erikoiontologia _juhon_ kehitystiedostolla (_juho-to-be-used-with-jung.ttl_) ja [_Jung_-YSOlla](https://raw.githubusercontent.com/NatLibFi/Finto-data/refs/heads/master/vocabularies/yso/releases/2024.6.Jung/ysoKehitys.ttl) sekä konversioskriptin tuottamalla uutta YSOa edustavalla tiedostolla _converted-yso.ttl_. Tämä sen takia, että _Jungin_ ja nykyisen YSOn välillä on riittävästi eroavaikuuksia mutu-raportin tuloksen myötä skriptin tuotoksen oikeellisuuden varmistamiseksi, mutta ei kuitenkaan niin paljoa, että muutosten määrä olisi yliampuva. Muutosriveistä löytyi kaikkia _mutun_ muutostyyppejä edustava rivi, joten skriptin tuotoksen testaaminen oli mahdollista
 
## Tiedostoista

### Konversioskripti:

Ajaa kaiken konversiossa tarvittavan kerralla:<br>
_run-post-update.sh_

Tekee muutamia korjauksia varsinaisen koversion lisäksi (purkkaa kiireen takia):<br>
_post-update.py_

YSOn kehitystietomallimuunnoksen (Vocbench -> TBC) suorittava skripti:<br>
_convert_vb_yso_to_tbc_yso.py_

Kesäkuulta 2025 oleva viimeinen TBC:ssä ylläpidetty YSO, jonka pitää olla AINA mukana skriptin ajossa (tarvitaan TBC-ajan tietomallin mukailuun):<br>
_old-yso-202506-tbc.ttl_

VocBenchistä helmikuussa 2026 ladattu YSO (simuloi mutu-testeissä jäädytetyn YSOn lähdetiedostoa):<br>
_new-yso-202602-vb.ttl_

Jäädytyksen pohjaksi sekä mututtamisen testaamiseen soveltuva konvertoitu ja valmis YSO:<br>
_converted-yso.ttl_
(ei oikeasti jäädytetty eli esim apuluokat vielä mukana)

### Mutu:

Testaamisessa käytetty Jungin aikainen _juhon_ kehitystiedosto:<br>
_juho-to-be-used-with-jung.ttl_ 

Jung-YSO:<br>
_Finto-data/vocabularies/yso/releases/2024.6.Jung/ysoKehitys.rdf_

Mututuksen lopputulos:<br>
_MUTU-results-excel.xml_


## Skriptien ajo:

Aja näin (ajaa kaiken konversioon liittyvän tarvittavan kerralla):
```run-post-update.sh ysoKehitys.rdf```

### Konvertointi YSO(VB)->YSO(TBC)

- Älä koskaan muuta tai korvaa tiedostoa ./_old-yso-202506-tbc.ttl_, koska skripti saa tiedostosta oikean tietomallin.
- Korvaa _./new-yso-202602-vb.ttl_ VB:stä lataamallasi YSOlla.
- Nimeä _converted-yso.ttl_ haluamallasi tavalla mutu-käyttöön sopivaksi.

Skripti tarvitsee Python3:n. Sen käyttämä kirjasto _rdflib_ voidaan ottaa käyttöön ajamalla ```pip install rdflib ```.

```
python3 ./convert_vb_yso_to_tbc_yso.py --old ./old-yso-202506-tbc.ttl --new ./new-yso-202602-vb.ttl --out converted-yso.ttl
```

### Mutu

Huomaa, että _-newYso ./converted-yso.ttl_ on TBC:ssä käytetyn mallin mukaiseksi konvertoitu YSO, jonka loit aiemmin muunniskriptillä.

Sopiva mutu-versio löytyy [täältä](https://github.com/NatLibFi/mutu/releases/tag/v1.1.0) (_mutu v1.1.0_).

```
cd Finto-data/tools/vb-to-tbc-yso-conversion-for-mutu

java -jar [mutu folder]/mutu.jar -domainOnt ./juho-to-be-used-with-jung.ttl ../../vocabularies/yso/releases/2024.6.Jung/ysoKehitys.rdf -newYso ./converted-yso.ttl -domainOntUri https://finto.fi/juho/fi/page/ -newYsoUri https://dev.finto.fi/yet_unknown/fi/page/
```

### Lopputulos

Tuotettu mutu-raportti MUTU-results-excel.xml uudelleennimettynä, Excel- ja csv-muodossa:

- mutu-report.xlsx
- mutu-report.csv

***Tutkitut tapaukset kuvana:***
- cases-checked.png




