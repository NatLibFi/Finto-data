# Wikidata-botti

## Yleistä

Wikidata-botin tarkoitus on hakea Wikidatasta YSO ID:hen (P2347) liittyvät tiedot, joita verrataan "vastaaviin" YSOn puolella. Lisäksi botilla luodaan erilaisia raportteja. Toteutus siirtää Wikidatasta RDF-muotoiset tiedot relaatiotietokantaan (sqlite3), josta raporttien muodostaminen ja vaikka uusienkin laatiminen on luontevaa ja helppoa. Lisäksi Wikidatan rajapinnasta haetaan kunkin Wikidata-entityn reviisiohistoriasta P2347-propertyn viimeisin muokkaaja, jonka tekemä muokkaus joko hyväksytään mukaan listaukseen tai hyältään.

## Toistaiseksi muodostetaan seuraavanlaiset raportit:

1) Linkki deprekoitu Wikidatassa, mutta mäppäys edelleen YSOssa.
2) Mäppäyksen sisältävä käsite deprekoitu ysossa, mutta vastaavaa linkkiä ei deprekoitu Wikidatassa.
3) Wikidatassa on linkki YSOn käsitteeseen, mutta vastaavassa käsitteessä YSOssa ei ole mäppäystä Wikidatan käsitteeseen (tarkistaa että linkin on tehnyt hyväksytty käyttäjä).

## Tulossa
1) Datan oikeellisuuden tarkistaminen.
2) Raportti muokatuista WD-entiteeteistä ja käyttäjistä, jotka ovat tehneet Wikidataan muokkauksia, mutta joihin emme voi automatique luottaa.
3) Kohdan 3 mukaisesti muodostetaan NT-tiedosto, jonka avulla YSOsta puuttuvat mäppäykset lisätään osaksi YSOA automaattisesti.
4) Koodin siistiminen.

## Skriptien toiminnan kuvaus

Dokumentaatio kuvaa kirjoittamishetken mukaista tilaa, ei valmista sovellusta. Esimerkiksi skriptien polut ja tiedostonimet pitää järkevöittää sekä kovakoodatut tiedostonimet ja inputit argumentoida ja/tai siirtää muuttujiin sekä muutenkin tarpeellisissa kohdissa refaktoroida koodia helpommin luettavaksi ja vähemmän toisteiseksi. Lisäksi kommentointia pitää yhtenäistää ja selkeyttää.

### Skriptin ajo:
```
./6wikidata-bot.sh
```
Ensimmäisen automatisoidun YSOon lisäyksen jälkeen ajo nopeutunee merkittävästi, koska eroavaisuudet Wikidatan ja YSOn välillä ovat vähentyneet huomattavasti, mutta ensimmäiseen ajoon saataa mennä yli tuntikin. Skripti näyttää etenemisen, mutta ei progressiota suhtessa kaikkien vaiheiden valmistumisen määrään. Mittakaavasta: Esimerkiksi Wikidatasta tarkistettavien linkitysten kohdalla tietokantaan tallennettavia käyttäjänimiä on kirjoittamishetekellä 8888 kappaletta, joista jokainen on erikseen haettu Wikidatasta.


### Datan haku Wikidatasta
```
$RSPARQL --results NT --service https://query.wikidata.org/sparql --query 6all_as_rdf.rq | sort > 6all_as_rdf.nt
```

Haetaan SPARQL-kyselyllä Wikidatan SPARQL-rajapinnasta kaikki propertyn P2347 "ympärillä" oleva data ja tulostetaan se järjestettyine tripleineen NT-tiedostoon.

### Haettujen tietojen järjestäminen luettavampaan muotoon ja blank nodejen parempi esittäminen
```
python ./6flatten_nt.py 6all_as_rdf.nt 6all_as_rdf_coverted_from_nt_and_grouped.ttl
```

Toimitaan otsikon mukaisesti ja tulostetaan lopputulos turtle-tiedostoon myöhempää käyttöä varten.

### Luodaan aiemmasta tietokannasta aikaleimattu varmuuskopio ja poistetaan tietokanta
```
./6backup-and-delete-db.sh $DB
```

### Luodaan uusi tyhjä tietokanta
```
./6create_db.sh $DB
```

### Parsitaan Wikidatasta haetuista tiedoista ranking-tiedot
```
$RIOT --output=N-TRIPLES 6all_as_rdf_coverted_from_nt_and_grouped.ttl | grep "<http://wikiba.se/ontology#rank>" | awk '{gsub(/[<>]/, "", $1); gsub(/.*#/, "", $3); gsub(/>/, "", $3); print $1, $3}' | while read uri rank; do     sqlite3 6wikidata.db "INSERT OR REPLACE INTO wd_main (wd_entity_uri, wd_rank) VALUES ('$uri', '$rank');"; done
```

Ranking-tietoja käytetään sen selvittämiseen, onko Wikidatassa oleva P2347 deprekoitu. Tietoa hyödyntämällä voidaan tehdä vertailuja YSOn vastaaviin tietoihin käsitteissä. Tieto tallennetaan tietokannan tauluun wd_main.

### Parsitaan aikaleima per Wikidata-entity
```
$ARQ --data=6all_as_rdf_coverted_from_nt_and_grouped.ttl --query=6get_wd_uris_and_dates.rq | sed 's/[|"]//g; s/^ *//; s/ *$//' | while read -r uri date; do sqlite3 6wikidata.db "INSERT INTO wd_dates_for_stated_in (wd_entity_uri, date) VALUES ('$uri', '$date');"; done
```

Tarve aikaleimoille on hieman epäselvä, mutta sillä oletukella, että tietoa saatetaan tarvita tulevaisuudessa, tieto on haettu ja se tallennetaan tietokannan tauluun wd_dates_for_stated_in.

### Parsitaan YSOon viittaavat linkit
```
$ARQ --data=6all_as_rdf_coverted_from_nt_and_grouped.ttl --query=6get_yso_links_from_wikidata.rq | sed 's/wd:/http:\/\/www.wikidata.org\/entity\//g' | sed 's/yso:/http:\/\/www.yso.fi\/onto\/yso\/p/g' | awk -F 'p:P2347' '{
    gsub(/[<>[:space:]]+/, "", $1);
    entity = $1;
    split($2, yso_concepts, ",");
    for (i in yso_concepts) {
        gsub(/[<>[:space:]]+/, "", yso_concepts[i]);
        print entity "|" yso_concepts[i]
    }
}' > 6yso_links_from_wikidata.txt
```

Tiedot YSO-linkeistä ovat Wikidata-botin käytön kannalta kaikkein oleellisimpia, koska niihin perustuvat YSOon automaattisesti päivitettävät triplet, vaikkakin pitkälti muut tiedot ovat myös tärkeitä automaation onnistumisen kannalta, koska käytössä pitää olla myös tiedot muun muassa mahdollisista deprekoinneista, rankingeista ja editoijien käyttäjänimistä yms. 

Selkeyden ja tietokantaan siirtämisen vuoksi tieto esitetään listamaisessa muodossa.

### Muokataan Wikidatan YSO-linkit sisältävä tiedosto helpommin tietokantaan siirrettävään muotoon
```
sed 's/\.$//' 6yso_links_from_wikidata.txt > 6yso_links_from_wikidata_clean.txt
```

### Siiretään Wikidatan YSO-linkkien tiedot tietokannan tauluun wd_yso_links
```
sqlite3 6wikidata.db <<EOF
.mode csv
.separator "|"
.import 6yso_links_from_wikidata_clean.txt wd_yso_links
EOF
```

### Haetaan YSOsta Wikidata-mäppäykset
```
$ARQ --data=$YSO_DEV --query=6get_wikidata_links_from_yso.rq | sed 's/yso:/http:\/\/www.yso.fi\/onto\/yso\//g' | sed 's/ skos:closeMatch /|/g' | sed 's/[<>]//g' | awk -F '|' '{ 
    gsub(/[[:space:]]+$/, "", $1);    # Trailing spaces pois 
    yso_uri = $1;                     # YSO-uri-talteen
    split($2, objects, ",");          # Pilkkuerottelu
    for (i in objects) {
        gsub(/[[:space:]]+$/, "", objects[i]);    # Trailing spaces pois
        print yso_uri "|" objects[i] ".";         # Printataan tulos oikeassa formaatissa
    }
}' > 6wikidata_links_from_yso.txt
```

(Siistitään YSOsta Wikidata-mäppäykset sisältävä tiedosto käyttöönsä sopivammaksi ja siirretään tiedot tietokantaan)

```
sed 's/|[[:space:]]*/|/g; s/[[:space:]]*\.\.$//; s/[[:space:]]*$//' 6wikidata_links_from_yso.txt > 6wikidata_links_from_yso_clean.txt
```
```
sqlite3 6wikidata.db <<EOF
.mode csv
.separator "|"
.import 6wikidata_links_from_yso_clean.txt yso_wd_links
EOF
```

Wikidatasta haetut tiedot tulostetaan tiedostoon, joka sisältää sekä YSO-käsitteen urin että käsitteen sisältämän mäppäyksen Wikidataan. Sen jälkeen tiedostoa siivotaan, jotta sen tietokantaan importoiminen mahdollistuu ja lopuksi tiedot siirretään tietokantaan.

### Haetaan YSOn kehitystiedostosta tieto YSO-käsitteiden deprekoinnista
```
$ARQ --data=$YSO_DEV --query=6get_yso_main.rq | sed 's/yso:/http:\/\/www.yso.fi\/onto\/yso\//g; s/ ex:deprecationStatus /|/g; s/[.]$//' | awk 'NF {gsub(/"/, "", $3); gsub(/[ \t]+$/, "", $0); print $1 "|" $3}' > 6yso_main.txt
```
```
sed '/^@prefix/d' 6yso_main.txt > 6yso_main_clean.txt
```
```
sqlite3 6wikidata.db <<EOF
.mode csv
.separator "|"
.import 6yso_main_clean.txt yso_main
EOF
```

Deprekointitietoja varten luotu tiedosto siistitään ja tiedot tallennetaan tietokantaan, jotta niitä voidaan hyödyntää myöhemmissä raportointien luonnissa, kuten vaikkapa raportissa, joka osoittaa ne ei-deprekoidut YSO-linkit Wikidatassa, jotka viittaavat YSOssa deprekoituun käsitteeseen.

### HTML-raportti: Wikidatassa deprekoitu linkki yhä mäppäyksenä YSOssa
```
sqlite3 6wikidata.db "SELECT w.wd_entity_uri, y.yso_concept_uri
FROM wd_main w
JOIN wd_yso_links l ON w.wd_entity_uri = l.wd_entity_uri
JOIN yso_main y ON l.yso_concept_uri = y.yso_concept_uri
WHERE w.wd_rank = 'DeprecatedRank'
  AND y.is_deprecated = 'false';" | awk -F'|' '{print "<a href=\"" $1 "\" target=\"_blank\">" $1 "</a> -> <a href=\"" $2 "\" target=\"_blank\">" $2 "</a><br>"}' > 6deprecated_in_wikidata_but_not_in_yso.html 
```

### HTML-raportti: On deprekoitu YSOssa mutta ei Wikidatassa
```
sqlite3 6wikidata.db "SELECT y.yso_concept_uri, w.wd_entity_uri
FROM yso_main y
JOIN yso_wd_links l ON y.yso_concept_uri = l.yso_concept_uri
JOIN wd_main w ON l.wd_entity_uri = w.wd_entity_uri
WHERE y.is_deprecated = 'true'
  AND (w.wd_rank != 'DeprecatedRank' OR w.wd_rank IS NULL);" | awk -F'|' '{print "<a href=\"" $1 "\" target=\"_blank\">" $1 "</a> -> <a href=\"" $2 "\" target=\"_blank\">" $2 "</a><br>"}' > 6deprecated_in_yso_but_not_in_wikidata.html
```

### Haetaan niiden Wikidata-käyttäjien käyttäjänimet, jotka ovat muokanneet P2347-propertyä
```
./6get_p2347_editors_in_db.sh $DB
```

Wikidatasta haetut käyttäjänimet per Wikidata-entiteetti mahdollistavat sen, että voidaan karsia YSOon lisättävistä Wikidata-mäppäyksistä (tripleistä) pois sellaiset tapaukset, joihin liityy käyttäjänimi, joka ei ole luotettava. Toisaalta tietokantahaulla voidaan esimerkiksi listata vähemmän luotettavien käyttäjien käyttäjänimet ja heidän kohde-entiteettien urit. 

Kutsuttava skripti vie tiedot tietokannan tauluun p2347_editors_in_wd hyödyntäen jo kertättyä tietoa (taulu: wd_yso_links) siitä, mitkä Wikidatan entiteetit sisältävät linkin YSOon. Kyseiset entiteetit syötetään parametrinä Wikidataan kohdistuvalle rajapintakutsulle. 

Tämä on ollut koko projektin hankalin kohta sen takia, että käyttäjätietoja ei löydy Wikidatan sanastodatasta, jolloin tiedot pitää saada muita reittejä. Pitkällisen pohdinnan ja erinäisten testailujen päätteeksi päädyttiin loopattuun rajapintakutsuun, jossa entity annetaan kutsulle argumenttia ja jolloin vastaus sisältää käyttäjänimen. 

Vaihtoehtona olisi ollut hakea muutamien päivien välein päivitetty jättikokoinen dumppi koko Wikidatan sisällöstä (sopivaa suppeampaa rajapinta ei ole mahdollista laatia), mutta sen lataaminen, tallentaminen ja parsiminen olisi liian raskas operaatio skriptin skoupissa. Myöskään rajapinnan "pommittaminen" ei ole välttämättä suositeltavaa, mutta toisaalta, sitä tapahtuu harvakseltaan, headerissa on tuotu avoimesti ilmi Kansalliskirjasto ja testausnäkökulma sekä ensimmäisen ison YSO-päivityksen jälkeen korjattavien linkkausten määrä kuitenkin pienentyy merkittävästi.

### HTML-raportti: YSO-linkki Wikidatassa mutta ei WD-linkkiä YSOssa
```
sqlite3 6wikidata.db "
SELECT w.wd_entity_uri, y.yso_concept_uri
FROM wd_yso_links l
JOIN wd_main w ON l.wd_entity_uri = w.wd_entity_uri
JOIN yso_main y ON l.yso_concept_uri = y.yso_concept_uri
JOIN p2347_editors_in_wd p ON p.wd_entity_uri = w.wd_entity_uri
WHERE w.wd_rank != 'DeprecatedRank'
  AND y.is_deprecated = 'false'
  AND NOT EXISTS (
      SELECT 1 
      FROM yso_wd_links yl 
      WHERE yl.yso_concept_uri = y.yso_concept_uri 
        AND yl.wd_entity_uri = w.wd_entity_uri
  )
  AND p.latest_p2347_editor IN ('YSObot', 'Saarik', 'Tpalonen', 'Tuomas_Palonen', 'Nikotapiopartanen', 'Osmasuominen');
" | awk -F'|' '{print "<a href=\"" $1 "\" target=\"_blank\">" $1 "</a> -> <a href=\"" $2 "\" target=\"_blank\">" $2 "</a><br>"}' > 6yso_link_in_wd_but_not_wd_link_in_yso.html
```

Haetaan tietokannasta tieto niistä Wikidatan YSO-linkeistä, joissa viimeisin editoija on hyväksyttyjen joukossa ja joilta puuttuu vastine YSOsta sekä muodostetaan ehdot täyttävistä tripleistä lista html-raportin muodossa.

### Tietokannan skeema

**wd_dates_for_stated_in:**
    _wd_entity_uri TEXT
    date TEXT_

**wd_yso_links:**
    _wd_entity_uri TEXT
    yso_concept_uri TEXT_

**yso_wd_links:**
    _yso_concept_uri TEXT
    wd_entity_uri TEXT_

**wd_main:**
    _wd_entity_uri TEXT UNIQUE
    wd_rank TEXT_

**yso_main:**
    _yso_concept_uri TEXT UNIQUE
    is_deprecated BOOLEAN_

**p2347_editors_in_wd:**
    _wd_entity_uri TEXT
    latest_p2347_editor TEXT_

