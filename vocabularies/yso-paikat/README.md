## Ohjeistus YSO-paikkojen PNR-koordinaattitietojen ekstrahointiin:

Hae API-avain Maanmittauslaitoksen rajapintaan. Ohjeet sivulla https://www.maanmittauslaitos.fi/rajapinnat/api-avaimen-ohje.

Aloita lataamalla tarvittava .gkpg-tiedosto paikkatyyppeineen esim. QGIS-ohjelmalla (pelkät koordinaattitiedot ilman paikkatyyppitietoja on saatu aiemmin osoitteesta http://www.nic.funet.fi/index/geodata/mml/paikannimet/)

### Avaa QGIS -ohjelma (saatavilla HY:n Software Centeristä)

1) Selain / Browser -valikkoikkunasta "WFS / OGC API - Features"
2) Uusi yhteys / New connection -> avaa ikkunan "Luo uusi WFS-yhteys" / "Create a new WFS Connection"
3) Autentikointi / Authentication -> Yksinkertainen todennus / Basic -> Käyttäjänimen kohdalle API-avain
4) URL: https://avoin-paikkatieto.maanmittauslaitos.fi/geographic-names/features/v1/
5) Sivun koko / Page size: 1000
6) Selain / Browser -valikkoikkunan kohdan "WFS / OGC API - Features" alta tuplaklikkaa PlaceName
7) Tasot / Layers -ikkunassa PlaceName -> "Export..." > "Save features as"
8) Valitse tallennusikkunasta Tiedostomuoto: GeoPackage ja anna tiedostonimi
9) Valitse vietävät kentät ja niiden vientivalinnat / Select fields to export and their export options: poista kenttävalinnoista muut kuin placeId ja placeType

Huom. koordinaattitiedot on tallennettu oheisessa
Maanmittauslaitoksen .gpkg-tiedostossa ESPG:3067 - ETRS89 / TM35FIN(E,N) -muodossa,
nämä täytyy muuntaa WGS84-koordinaattitason mukaisiksi koordinaattipisteiksi.
Tämä tapahtuu esimerkiksi QGIS-ohjelmalla seuraavasti:

1) Avaa Database -> Database Manager
2) GeoPackage -> New Connection
3) Valitse lataamasi .gpkg-tiedosto
4) Avaa edellinen GeoPackage-näkymästä
5) Valitse "Export to File..."
6) Aseta "Source SRID"-arvoksi 3067
7) Aseta "Target SRID"-arvoksi 4326
8) Tallenna WGS84-koordinaattitasoon muutettu .gpkg-tiedosto haluamaasi paikkaan.

Voit nyt sulkea edellisen yhteyden ja avata WGS84-muotoisen tiedoston.
Varmista, että QGIS-ohjelmassa sinulla on auki ja valittuna WGS84-muotoinen kerros
Layers-paneelista (jos tämä ei ole näkyvissä, saat sen näkyviin valitsemalla
View -> Panels -> Layers).
Ohjelman tulisi piirtää Suomen muotoinen kartta koordinaattipisteistä.

### Seuraavaksi tavoitteena on ekstrahoida vain haluamamme tiedot haluamassamme muodossa.
Tämä tapahtuu seuraavasti:

1) Valitse WGS84-muotoinen kerros
2) Edit -> Select -> Select All Features
3) Valitse "Open Field Calculator" Attributes Toolbar -työkaluvalikosta
4) Varmista, että avautuvassa ikkunassa valittuja featureita on 800000+ kohdassa
"Only update * selected features"
5) Aseta ruksi edelliseen kohtaan ja kohtaan "Create a new field"
6) "Output field name" -> WGS84_E
7) "Output field type" -> Decimal number (real)
8) Kohtaan "Expression" syötä seuraava lauseke: round($x, 5)
9) Preview-kohdasta näet, minkälaisen arvon järjestelmä on laskemassa valitulle featurelle.
10) Paina "OK". Tässä menee hetki, sillä järjestelmä luo kaikille featureille uuden sarakkeen,
jossa on viiden desimaalin tarkkuudella määritetty itäinen WGS84-koordinaatti.
11) Toista edelliset kohdat käyttäen arvoja "WGS84_N" ja round($y, 5) luodaksesi
pohjoisen WGS84-koordinaattisarakkeen.

### Lopuksi haluamme tallentaa .csv-tiedostoon tarvitsemamme arvot. Tämä tapahtuu seuraavasti:

1) Paina oikealla painikkeella WGS84-muotoista kerrosta -> Export -> Save Features As..
2) Format: Comma Separated Value [CSV]
3) Valitse vain kentät "placeID", "placeType", "WGS84_N", "WGS84_E"
4) Voit ottaa pois valinnan "Add saved file to map"
5) Valittuasi tiedostonimen voit painaa "OK"-painiketta. Järjestelmä luo halutut tiedot sisältävän
.csv-tiedoston.
6) Voit nyt sulkea QGIS-ohjelmiston.

Voit nyt avata Microsoft Excelissä tai muussa vastaavassa taulukko-ohjelmistossa .csv-tiedoston.
Huom! Tiedosto sisältää duplikaatteja. Tämä johtuu siitä, että alkuperäisessä datassa on merkitty
joillekin paikoille useita nimiä. Esim. paikkaID 10001222 (Porinlahti, Pihlavanlahti). Toisaalta
myös on havaittavaa, että paikkaID-arvoissa on reikiä, esim. 10001223.
Voit poistaa duplikaatit tiedostosta, esimerkiksi Excelissä tämän voi tehdä seuraavasti:

1) Valitse sarake, jonka otsikko on paikkaID
2) Data -> Remove Duplicates
3) Valitse "Expand the selection"
4) "Remove Duplicates...". Järjestelmä poistaa duplikaattiarvot.
5) Voit tämän jälkeen tallentaa tämän duplikaatteja sisältämättömän taulukon.

### Seuraavaksi voit vielä normalisoida kaikki arvot viiteen desimaaliin seuraavasti (ensimmäinen vaihe oli typistänyt päättyvät nollat):

1) Valitse edellinen taulukko ja sieltä B- ja C-sarakkeet (WGS84_N, WGS84_E) ja paina oikeaa nappia
2) Valitse "Format Cells" avautuva ikkunasta
3) Valitse Category: Number ja aseta sieltä "Decimal places" arvoon 5
4) Paina "OK"-painiketta
5) Tallenna taulukko nyt

Nyt sinulla on valmis, kaikki PNR:n paikat/niiden koordinaatit sisältävä normalisoitu taulukko.
Jos myöhemmin on tarvetta, voi taulukkoon ottaa myös muita sarakkeita.
Huom! Moni skripti odottaa sarakkeiden olevan järjestyksessä 'placeID', 'placeType', 'WGS84_N', 'WGS84_E'.
Huom2! Suurinta osaa PNR:n paikoista ei ole käytetty YSO-paikoissa. Tämä on otettu huomioon automaattisessa komentosarjassa (alla lyhyt kuvaus).


Jokaisella sanaston julkaisukerralla tehtävää (sisältyy toskos.sh-komentosarjaan):

### Edellisestä taulukosta voidaan ottaa vain käytetyt arvot seuraavasti (nopeuttaa skosify-ohjelman ajoa):

1) Haetaan käytetyt paikkaID:t seuraavasti ja tallennetaan ne tiedostoon:
grep -oP "(?<=rdf:resource=\"http://paikkatiedot.fi/so/1000772/).*(?=\")" /srv/Finto-data/vocabularies/yso-paikat/yso-paikat-vb-dump.rdf | sort -u > yso-paikat-usedPNRs.txt
2) extractUsedPNRs.py --input $duplikaatiton_ja_normalisoitu_edellisen_vaiheen_taulukko.csv --selector yso-paikat-usedPNRs.txt > yso-paikat-pnr.ttl

Kohta 2) tuottaa Skosify-ohjelmalle vain sanastossa käytetyille PNR-paikoille sijaintitiedot turtle-muodossa.
