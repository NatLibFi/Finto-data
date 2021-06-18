TERO
====

Terveyden ja hyvinvoinnin ontologia (Tero) on YSO-pohjainen erikoisontologia, joka on mukana ontologiapilvi KOKOssa. TEROn erikoispiirre on että sen luonnissa yhdistettiin useissa sanastoissa olevia samoja käsitteitä yhdeksi kokoavaksi TERO-käsitteeksi. Näiden käsitteiden alkuperäislähde on näkyvillä käsitteen rdf:type ominaisuuden arvossa. Näiden käsitteiden URIen loppuosat viittaavat myös käsitteen alkuperäislähteeseen.

### TERO-YSO tuplakäsitteiden poisto 2017

TEROsta poistettiin loppuvuonna 2017 sellaiset TERO-käsitteet, jotka oli muodostettu suoraan YSO-käsite kopioimalla. Näille käsitteille luotiin tässä yhteydessä dct:isReplacedBy -triplet, jotka on nyt eriytetty omaan tiedostoonsa tero-yso-replacedby.ttl. Tämä erottelu tehtiin, jotta termieditori ei kadottaisi tietoa näistä suhteista.

### Näin tuotat mutu-raportin ja luot uuden kehitystiedoston

* Mututus

1) Ajamalla skriptin cleanAndFixTero.py toimitetulle lähdetiedostolle (turtle)

-> poistat Termieditorin käyttämät ylimääräiset triplet

-> lisäät määrittelyt:

- terometa.Concept rdfs.subClassOf owl.Class
- terometa.Class rdfs.subClassOf owl.Class
- tero:[xyz] rdf:type terometa.Concept

2) Aja cleanAndFixTero.py-skriptin tuloksena syntyneelle tiedostolle ontorip-skripti (erottelee erikoisontologian siihen liitetystä ysosta ja löytyy Finto-datan tools-kansiosta sekä käyttää toistaiseksi python-versiota 2)

3) Ontoripillä erottamaasi ysoon lisää,

-> yso-meta:Class  a        owl:Class ;
        rdfs:subClassOf  owl:Class .

-> yso-meta:Concept  a      owl:Class ;
        rdfs:comment     "YSO:n indeksoinnissa käytettävä käsiteluokka."@fi ;
        rdfs:subClassOf  yso-meta:Class ;
        skos:note        "YSO:n indeksoinnissa käytettävä käsiteluokka."@fi .

-> yso-meta:GroupConcept
        a                owl:Class ;
        rdfs:subClassOf  yso-meta:Class .

-> korvaa:
- skos:broader -> rdfs:subClassOf 
- skos:Concept -> yso-meta:Concept
- skos:Collection -> yso-meta:GroupConcept

-> tarkista, että
- kaikki tarvittavat prefixit on määritelty ja poista ylimääräiset

4) Ontoripillä erottamassasi erikoisontologiatiedostossa varmista, että seuraavat on määritelty:

-> isothes:ThesaurusArray a rdfs:Class ;
    rdfs:label "Sisarkäsitteiden joukko"@fi .

-> terometa:Class a terometa:Concept ;
    rdfs:subClassOf owl:Class .

5) Aja:
time java -jar mutu.jar -domainOnt [ontoripillä_tuotettu_ja_tarkistettu_erikoisontologia.ttl] ontoripillä_tuotettu_ja_tarkistettu_yso.ttl] -newYso [polku_uusimpaan_jäädytetyn_yson_kehitysversioon]/ysoKehitys.ttl -domainOntUri http://finto.fi/[erikoisontologia]/ -newYsoUri http://dev.finto.fi/yso[uusin_jäädytetty_yso]/

6) Muuta mutun tuottama tiedosto MUTU-results-excel.xml Excel-muotoon (MUTU-results-excel.xlsx)

7) Erikoisontologian kehittäjän avuksi, kerro hänelle) lajitteluehdotus, jolla mahdollistetaan useiden (parhaimmillaan tuhansien) muutosten kerralla tekeminen tai kuittaaminen:
a) Yso-käsitteiden lkm nyt (descending)
b) Linkki erikoisontologian YSO-käsitteeseen
c) Muutostyypin tunnus


* Erikoisontologian kehitystiedoston luominen

1) poista mututusta varten luomastasi ontoripillä_tuotettu_ja_tarkistettu_erikoisontologia.ttl-tiedostosta kaikki yso-triplet, joita ontorip ei saanut poistettua.

2) (koskee mututtamisessa käyttämiäsi tiedostoja) Liitä ontoripillä_tuotettu_ja_tarkistettu_erikoisontologia.ttl-tiedostoon ontoripillä_tuotettu_ja_tarkistettu_yso.ttl-tiedosto käyttäen kopioi ja liitä -toimintoa.

3) Tarkista mahdolliset prefixeihin liittyvät ristiriidat (käytännössä voi olla helpompaa muuttaa prefixejä jo ennen yson liittämistä)

4) Tuo erikoisontologian ja uusimman jäädytetyn yson kehitysversion yhdistävä tiedosto TBC:hen

5) Aseta tarvittaessa TBC:ssä:

-> näytettävien käsitteiden määrä

-> fi sv en -kieliasetukset

-> tarvittavat SKOS-importtaukset

-> käyttöön 'human readable labels'

6) Jos tiedosto näyttää TBC:ssä tarkasteltuna oikeelliselta, erikoisontologian kehitystiedosto on valmis


### Näin generoit sanaston:

1) Korvaa tero.ttl saamallasi uudella erikoisontologiatiedostolla

2) Aja toskos.sh

3) Ajon jälkeen, varmista oikeellisuus tero-skos.ttl-tideostosta eli:
- terometa:Concept-viittaukset kaikissa teron käsitteissä
- git diff

4) Jos kaikki on kunnossa, git commit, git push
