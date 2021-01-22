22.1.2021 sanastopäivitys:

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
