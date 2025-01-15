# Wikidata-botti

## Taustaa ja tilanne 8. tammikuuta 2025

Wikidata-botin on tarkoitus hakea Wikidatasta YSO ID:hen (P2347) liittyvät tiedot, joita verrataan "vastaaviin" YSOn puolella. Lisäksi botilla luodaan erilaisia raportteja. Toteutus siirtää Wikidatasta RDF-muotoiset tiedot relaatiotietokantaan (sqlite3), josta jo määriteltyjen, mutta myös mahdollisesti uudenlaisten raporttien muodostaminen ja laatiminen on luontevaa ja helppoa. Lisäksi Wikidatan rajapinnasta haetaan kunkin Wikidata-entityn reviisiohistoriasta P2347-propertyn viimeisin muokkaaja, jonka tekemä muokkaus joko hyväksytään mukaan listaukseen tai hyältään. Lopulta botilla on raporttien luomisen lisäksi tarkoitus automaattisesti päivittää sovituin ehdoin ja rajoituksin YSOa mäppäyssuhteiden osalta sekä myös Wikidataa P2347-propertyn osalta.

### ETL
Skripti toteuttaa useista lähteistä tietoa hakevissa sovelluksissa tyypillisesti käytettävää <a href="https://en.wikipedia.org/wiki/Extract,_transform,_load" target="_blank">ETL-mallia</a>.

(_Extract-Transform-Load_). Vaikka tiedonhaku, tiedon muuntaminen ja tietokantaan siirto ei kaikin osin tapahdu peräkkäisinä vaiheina, mukaillaan kuitenkin kyseistä mallia. 

### Mocking
Iteratiivisia työtapoja noudattaen, tämänhetkinen versio botista on testi- ja mocking-toteutus, jolla on tarkoitus ainoastaan hahmottaa Wikidatan ja Finton väliseen tiedonhakuun, kyselyihin, tiedonsiirtoon sekä tietomallien välisiin konversioihin liittyviä parhaita käytöntöjä. Kun mocking-version myötä parhaat toteutustavat ovat selvinneet, aletaan tehdä varsinaista käyttöön tulevaa YSO-bottia ja sen testaamisen jälkeen sitä jälleen parannellaan - iteratiivisissä sykleissä.

Mocking-toteutuksessa on tarkoituksella tehty valinta käyttää mahdollisimman paljon Linuxissa natiivisti olevia komentoja ja työkaluja, jotta oltaisiin vähemmän riippuvaisia esimerkiksi ei-natiivien frameworkien, tulkkien, kielten ja kielten versiomuutoksista. Kansanomaisesti: _botin tulisi toimia kuin junan vessa_. Täysin versiomuutoksista riippumatonta toteutusta ei voida kuitenkaan kehittää (datan muokkausta toteutettu Pythonilla), mutta tavoitteena on kuitenkin teknisesti mahdollisimman linjakas ja yhdenmukainen (joka mocking-versio ei todellakaan vielä ole!) sekä mahdollisimman paljon natiiveja komentoja hyödyntävä toteutetus.

Mocking-versiossa on paljon epäjohdonmukaisuuksia ja oikaisuja sekä jäännöksiä eri työvaiheista, mutta on hyvä muistaa, että sen ei ole tarkoituskaan olla valmis sovellus, vaan testauksen, kokeilun ja tutkimisen väline, jota luonnollisesti seuraa saadun kokemuksen pohjalta laadittava varsinainen botti. Mocking-vaihe on ollut onnistunut. Testitoteutus tekee onnistuneesti seuraavat asiat eli luo raportit seuraaville tapauksille:
1) Linkki deprekoitu Wikidatassa, mutta mäppäys edelleen YSOssa.
2) Mäppäyksen sisältävä käsite deprekoitu ysossa, mutta vastaavaa linkkiä ei deprekoitu Wikidatassa.
3) Wikidatassa on linkki YSOn käsitteeseen, mutta vastaavassa käsitteessä YSOssa ei ole mäppäystä Wikidatan käsitteeseen (tarkistaa että linkin on tehnyt hyväksytty käyttäjä).

Varsinaisen käyttöön otettavan botin tulee ensimmäisessä julkaisuversiossa muodostaa NT-tiedostot kohtien 1 ja 3 pohjalta. Tiedoston avulla tiedot tullaan ajamaan automaattisesti YSOon.

### Tietokanta

**Principio**: _Pyrkimyksenä on toteuttaa selkeästi ja helposti hahmotettava tekninen kokoknaisuus, joka mahdollistaa botin helpon jatkokehittäminen - erillinen "datakerros" mahdollistaa tämän._

Botti käyttää erillistä relaatiotietokantaa, johon tarvittavat oikeaan muotoon muokatut tiedot tallentuvat. Näin toimitaan koska kerättyyn tietoon viittaminen (teknisesti ja loogisesti) on näin jatkossa helpompaa eli botin toimintojen kehittäminen ja uusien raporttien laatiminen on selkeämpää ja sujuvampaa. Useamman tietolähteen (_Wikidatan SPARQL-rajapinta, Wikidatan API_ ja _YSO_) kanssa toimiessa pelkkää, todennäköisesti ylipitkäksi venynyttä ja hankalasti hahmotettavaa skriptiä on hankalampi hallita ja muokata, jos "välissä" ei ole selkeätä datakerrosta. 

Relaatiotietokanta valikoitui käyttöön myös koska esimerkiksi graafitietokantaan luotavasta tietomallista tulisi botin kaltaisen sovelluksen käytön kannalta tarpeettoman monimutkainen ja "väkisin tehdyn tuntuinen". Relaatiotietokanta, on käyttötarkoitus huomioiden suoraviivaisempi käyttää. Graafitietokannan käytön ainut varsinainen etu olisi ollut mahdollisuus vähemmän jäykän ja helpommin muokattavan tietomallin jatkokehittämiseen ilman, että se sekoittaisi sovelluksen toimintaa, mutta botin kokoluokassa myös relaatiotietokannan skeeman muuttaminen on helppoa (todennäköisesti myös tulevaisuudessa).

Lopullisessa toteutuksessa tietokannat versioidaan eli aina uuden ajon alkaessa vanhasta tietokannasta otetaan varmuuskopio ja luodaan kokonaan uusi tietokanta (mocking-toteutus jo olemassa). Tietokannan koko ei tule kasvamaan niin suureksi, että versiointi olisi pitkässä juoksussa kestämätöntä, mutta aiempien tietokantojen säilytysaikaa kannattaa silti pohtia.

**Summa summarum**: _Sen sijaan, että kaikki datan käsittely on skriptissä, on järkevää kattavasti kerätä kaikki tarvittava ja mahdollisesti myös vähemmän tarvittava data harkittuun relaatiotietokannan skeemaan, johon voidaan myöhemmin viitata useilla eri halutuilla tavoilla._

## Pohdintaa

Wikidatassa käytetään paljon tarkenteita (qualifier) ja sen myötä blank nodeja, todennäköisesti ylläpidollisista syistä (vähemmän ureja, pienemmät tietokannat ja parempi skaalautuvuus - maybe). Käytetty reifikaatio-malli, jos sitä sellaisella nimellä halutaan kutsua, on toki tiivis ja älyllisesti stimuloiva, mutta semanttisesti köyhähkö, turhan implisiittinen ja työkaluille haastellinen pääteltävä. Periaatteessa olisi myös mahdollista luoda ihan oma tietomalli, jossa Wikidatan blank nodeilla toteutettu malli rikastetaankin ja eksplikoidaan luomalla tarvittavat uudet tyypit ja niille toteutukset, jolloin ei nää tarvitsisi viitata kokonaisiin predikaatti-objekti-pareihin, vaan qualifierit määrittäisivät sopivan tyyppisiä urillisia resursseja. Näin botin käyttämä tietomalli,olisi eksplisiittisempi, rikkaampi ja helpommin pääteltävissä sekä omat triplettikannan käyttö botin tietokantana olisi perustellumpaa. Lopulta kuitenkin, näin toimiminen tuntuisi turhalta ja tarpeettomalta akateemiselta kikkailulta ja ehkä jopa ajanhukalta. Parempi ratkaisu on elää reifikaatioiden ja blank nodejen kanssa, vaikka se tuo datan koneelliseen lukemiseen tiettyä hankaluutta.

## Mocking-vaiheen jälkeen
1) "Isoon kuvaan" liittyvien teknisten valintojen tekeminen (ja sen suunnitelma mahdollisesti kommentoidaan suoraan koodiin)
2) Skriptissä tarvittavien komentojen ja sovellusten parametrisoinnin ja käyttötapojen sekä kokonaisuuden yhdenmukaistaminen sekä lisäksi nimeämisten yhtenäistäminen esimerkiksi niin, että tiedostonimistä tulee ilmi, liittyykö tiedosto tiedonhakuun, tiedon muokkaamiseen vain tietokantaan lataamiseen tai raportointiin.
3) Datan oikeellisuuden tarkistaminen (tarkistelua tehty jo mocking-vaiheessa).
4) Raportti muokatuista WD-entiteeteistä ja käyttäjistä, jotka ovat tehneet Wikidataan muokkauksia, mutta joihin emme voi automatique luottaa (ehtona YSOn päivittämiselle, rajoitus on jo toteutettu).
5) Toiminto, jolla muodostetaan NT-tiedosto, jonka dataan pohjautuen YSOsta puuttuvat mäppäykset lisätään osaksi YSOA automaattisesti.

## Skriptien toiminnan kuvaus

Dokumentaatio kuvaa kirjoittamishetken mukaista tilaa, ei valmista sovellusta. Esimerkiksi skriptien polut ja tiedostonimet pitää järkevöittää sekä kovakoodatut tiedostonimet ja inputit argumentoida ja/tai siirtää muuttujiin sekä muutenkin tarpeellisissa kohdissa refaktoroida koodia helpommin luettavaksi ja vähemmän toisteiseksi (näitä tarpeita kuvattu jo yllä). Lisäksi kommentointia pitää yhtenäistää ja selkeyttää.

### Skriptin ajo:
```
./6wikidata-bot.sh
```
Ajoon saataa mennä yli tuntikin. Skripti näyttää etenemisen, mutta ei progressiota suhteessa kaikkien vaiheiden valmistumisen määrään. Mittakaavasta: Esimerkiksi Wikidatasta tarkistettavien linkitysten kohdalla tietokantaan tallennettavia käyttäjänimiä on kirjoittamishetekellä 8888 kappaletta, joista jokaiseen liittyvät tiedot on erikseen haettu Wikidatastan rajapinnan kautta ja yhdistetty entityihin, joita käyttäjänimi on kontribuoinut.

(**seuraavat ovat 6wikidata-bot.sh-skriptin sisältämiä vaiheita**)

### Datan haku Wikidatasta
```
$RSPARQL --results NT --service https://query.wikidata.org/sparql --query 6all_as_rdf.rq | sort > 6all_as_rdf.nt
```

Haetaan SPARQL-kyselyllä Wikidatan SPARQL-rajapinnasta kaikki propertyn P2347 "ympärillä" oleva data ja tulostetaan se järjestettyine tripleineen NT-tiedostoon.

### Haettujen tietojen järjestäminen luettavampaan muotoon ja blank nodejen mielekkäämpi esittäminen
```
python ./6flatten_nt.py 6all_as_rdf.nt 6all_as_rdf_coverted_from_nt_and_grouped.ttl
```

Toimitaan otsikon mukaisesti ja tulostetaan lopputulos turtle-tiedostoon myöhempää käyttöä varten ja muutenkin itse datan luettavuudellakin on merkitystä debuggauksen ja muun tarkastelun takia (nt versus turtle). 

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
$RIOT --output=N-TRIPLES 6all_as_rdf_coverted_from_nt_and_grouped.ttl | \
grep "<http://wikiba.se/ontology#rank>" | \
awk '{
    gsub(/[<>]/, "", $1); 
    gsub(/.*#/, "", $3); 
    gsub(/>/, "", $3); 
    print $1, $3
}' | \
while read uri rank; do
    sqlite3 6wikidata.db \
        "INSERT OR REPLACE INTO wd_main (wd_entity_uri, wd_rank) VALUES ('$uri', '$rank');"
done
```

Ranking-tietoja käytetään sen selvittämiseen, onko Wikidatassa oleva P2347 deprekoitu. Tietoa hyödyntämällä voidaan tehdä vertailuja YSOn vastaaviin tietoihin käsitteissä. Tieto tallennetaan tietokannan tauluun _wd_main_.

### Haetaan Wikidatasta päivityksiin liittyvät päivämäärät
```
$ARQ --data=6all_as_rdf_coverted_from_nt_and_grouped.ttl --query=6get_wd_uris_and_dates.rq | \
awk '
{
    gsub(/[|"]/, "");
    gsub(/^ */, "");
    gsub(/ *$/, "");
    if (NF == 2) {  # Varmistetaan, että yksi rivi sisältää tasan kaksi kenttää (uri | date)
        print $1, $2;
    }
}' | while read -r uri date; do
    sqlite3 6wikidata.db "INSERT INTO wd_dates_for_stated_in (wd_entity_uri, date) VALUES ('$uri', '$date');"
done
```

Tarve aikaleimoille on hieman epäselvä, mutta sillä oletukella, että tietoa saatetaan tarvita tulevaisuudessa, tieto on haetaan ja se tallennetaan tietokannan tauluun _wd_dates_for_stated_in_.

### Parsitaan YSOon viittaavat linkit
```
echo "yso-links from wikidata"
$ARQ --data=6all_as_rdf_coverted_from_nt_and_grouped.ttl \
     --query=6get_yso_links_from_wikidata.rq | \
awk '{
    if ($0 !~ /^wd/) next;
    gsub(/wd:/, "http://www.wikidata.org/entity/");
    gsub(/wd:/, "http://www.wikidata.org/entity/");
    gsub(/p:P[0-9]+/, "|");
    gsub(/yso:/, "http://www.yso.fi/onto/yso/p");
    gsub(/\.+$/, "");
    gsub(/ /, "");
    if (NF > 0) print
}' > 6yso_links_from_wikidata_clean.txt
```
Tiedot YSO-linkeistä ovat Wikidata-botin käytön kannalta kaikkein oleellisimpia, koska niihin perustuvat YSOon automaattisesti päivitettävät triplet. Myös muut tiedot ovat myös tärkeitä automaation onnistumisen kannalta, koska käytössä pitää olla myös tiedot muun muassa mahdollisista deprekoinneista, rankingeista ja editoijien käyttäjänimistä yms. 

Selkeyden ja sujuvan tietokantaan siirtämisen vuoksi tieto esitetään listamaisessa muodossa.

### Siiretään Wikidatan YSO-linkkien tiedot tietokannan tauluun wd_yso_links
```
sqlite3 6wikidata.db <<EOF
.mode csv
.separator "|"
.import 6yso_links_from_wikidata_clean.txt wd_yso_links
EOF
```

### Haetaan Wikidata-mäppäykset YSOsta
```
$ARQ --data=$YSO_DEV --query=6get_wikidata_links_from_yso.rq | awk '
{
    if ($0 ~ /^[[:space:]]*@prefix/) next;
    gsub(/yso:/, "http://www.yso.fi/onto/yso/");
    gsub(/ skos:closeMatch /, "|");
    gsub(/[<>]/, "");
    gsub(/[[:space:]]*,[[:space:]]*/, ",");
    gsub(/[[:space:]]*\.[[:space:]]*$/, "");
    gsub(/[[:space:]]*\|[[:space:]]*/, "|");
    gsub(/[[:space:]]+$/, "");
    if (NF > 0) print;
}' > 6wikidata_links_from_yso_clean.txt
```
Wikidatasta haetut tiedot tulostetaan tiedostoon, joka sisältää sekä YSO-käsitteen urin että käsitteen sisältämän mäppäyksen Wikidataan. Lopuksi tiedot siirretään tietokantaan.
```
sqlite3 6wikidata.db <<EOF
.mode csv
.separator "|"
.import 6wikidata_links_from_yso_clean.txt yso_wd_links
EOF
```

### Haetaan YSOn kehitystiedostosta tieto YSO-käsitteiden deprekoinnista
```
$ARQ --data=$YSO_DEV --query=6get_yso_main.rq | \
awk '
    BEGIN {
        yso_prefix = "http://www.yso.fi/onto/yso/"
    }
    {
        gsub(/yso:/, yso_prefix);
        gsub(/ ex:deprecationStatus /, "|");
        gsub(/[.]$/, "");
        if ($0 !~ /^@prefix/) {
            gsub(/"/, "", $3);
            sub(/[ \t]+$/, "", $0)
            if (NF > 0) {
                print $1 "|" $3
            }
        }
    }
' | awk '
    !(/^\|\|/ || /^\|$/) { print }
' > 6yso_main_clean.txt
```

Deprekointitietoja varten luotu tiedosto siistitään ja tiedot tallennetaan tietokantaan, jotta niitä voidaan hyödyntää myöhemmissä raportointien luonnissa, kuten vaikkapa raportissa, joka osoittaa ne ei-deprekoidut YSO-linkit Wikidatassa, jotka viittaavat YSOssa deprekoituun käsitteeseen.

```
sqlite3 6wikidata.db <<EOF
.mode csv
.separator "|"
.import 6yso_main_clean.txt yso_main
EOF
```

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

Kutsuttava skripti vie tiedot tietokannan tauluun _p2347_editors_in_wd_ hyödyntäen jo kertättyä tietoa (taulu: _wd_yso_links_) siitä, mitkä Wikidatan entiteetit sisältävät linkin YSOon. Kyseiset entiteetit syötetään parametrinä Wikidataan kohdistuvalle rajapintakutsulle. 

Tämä on ollut koko projektin hankalin kohta sen takia, että käyttäjätietoja ei löydy Wikidatan sanastodatasta, joten tiedot pitää hakea muita reittejä. Pitkällisen pohdinnan ja erinäisten testailujen päätteeksi päädyttiin loopattuun rajapintakutsuun, jossa entity annetaan kutsulle argumenttia ja jolloin vastaus sisältää käyttäjänimen. 

Vaihtoehtona olisi ollut hakea muutamien päivien välein päivitetty jättikokoinen dumppi koko Wikidatan sisällöstä (sopivaa suppeampaa rajapintakutsua ei ole mahdollista laatia), mutta sen lataaminen, tallentaminen ja parsiminen olisi liian raskas operaatio skriptin skoupissa. Myöskään rajapinnan "pommittaminen" ei ole välttämättä suositeltavaa, mutta toisaalta, sitä tapahtuu harvakseltaan, headerissa on tuotu avoimesti esiin Kansalliskirjasto ja testausnäkökulma sekä ensimmäisen ison YSO-päivityksen jälkeen korjattavien linkkausten määrä kuitenkin pienentyy merkittävästi.

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
```
wd_entity_uri TEXT
date TEXT
```
**wd_yso_links:**
```
wd_entity_uri TEXT
yso_concept_uri TEXT
```
**yso_wd_links:**
```
yso_concept_uri TEXT
wd_entity_uri TEXT
```

**wd_main:**
```
wd_entity_uri TEXT UNIQUE
wd_rank TEXT
```

**yso_main:**
```
yso_concept_uri TEXT UNIQUE
is_deprecated BOOLEAN
```

**p2347_editors_in_wd:**
```
wd_entity_uri TEXT
latest_p2347_editor TEXT
```

