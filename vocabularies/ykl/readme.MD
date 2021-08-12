### 22.1.2021 sanastopäivitys:

Tehdyt tekniset työt:
- toskos.sh muokattu niin, että seuraan päivityksen toteuttamisen pitäisi onnistua ajamalla kyseinen skripti
- vääriin taltioituneita owl:Class-määrityksiä korjattiin skosifyllä (ykl.cfg-tiedostossa tehdyillä määrityksillä)
- subClassOf-määritykset, jotka eivät liity skos:Conceptiin

Dataan liittyvät muutokset:
- poistettiin datasta ylimääräisiä välilyöntejä (korjattiin muokatulla toskos.sh-skripillä)
- korjattiin väärin asetettuja rivinvaihtoja (toskos.sh-skriptillä)
- poistettiin ylimääräiset tyhjät rivit (jos yli kaksi tyhjää riviä peräkkäin)
- paikoitellen hiddenLabeleissa esiintyvä '+ )'-merkkijono yhdenmukaistettiin seuraavaksi: '+)'

Ongelmia edelleen:
- joiltain käsitteiltä puuttuu prefLabeleit, vaikka löytyy altLabelit
- tulisi poistaa skofify-ajon jälkeen tulevat ylimääräiset triplet, joissa hklj on subjektin asemassa



### 12.8.2021 sanastopäivitys:

Tehdyt tekniset työt:

-- poistettu turhia TBC:n käyttämiä triplejä

-- ei duplikaatteja

-- ei asiaankuulumattomia orpoja käsitteitä (YKL:ssä voi olla luokkia, jotka on muodostettu toisen luokan tai muotoluokan avulla)

-- ei deprekointeja

-- YKL:n URIn loppuosa itsessään sisältää semantiikkaa ja sillä on tosielämässä vastine, joten tavanomaista URIn purittamista ei pidä tehdä

-- skossattu julkaisutiedosto testattu paikallisessa Fusekissa sekä Skosmoksessa:

- löytyi importoinnin estävä ongelma riviltä 8775 (ykl-skos.ttl) eli: "<http://urn.fi/URN:NBN:fi:au:ykl:00.6>" skos:related ykl:02 .
- edellinen muutettiin käsin muotoon: ykl:00.6 skos:related ykl:02 .
- RDFLib toimii spesifikaation vastaisesti, kun hyväksyy subjektiksi urin lisäksi myös literaalin. Tehty issue RDFLib-projektin repoon (https://github.com/RDFLib/rdflib/issues/1389).

-- luokan ykl:36.09 notaatio oli väärin:
skos:notation "36" -> skos:notation "36.09"

-- luokka 36.09 oli hierarkiassa väärässä kohdassa, korjattiin:
- skos:broader ykl:3 -> skos:broader ykl:36
- luokassa ykl:36 lisätty: skos:narrower ykl:36.09;
- luokassa ykl:3 poistettu: skos:narrower ykl:36.09

-- päivityksessä tarvitut tai muodostetut tiedostot:

- ykl-orig_2021-08-10.ttl
- ykl-2021-08-10-processed.ttl
- ykl-metadata.ttl
- ykl-hklj.ttl
- ykl-skos.ttl


