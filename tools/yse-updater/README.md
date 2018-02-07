YSEn päivitystyökalut
---------------------

Tässä kansiossa sijaitsevat ehdotusjärjestelmä-prototyypin
pyörittämiseen tarvittavat työkalut.

#### issues-to-triples.py

Tämä skripti hakee "vastaanotettu"-labelilla varustetut
uusien termien ehdotukset GitHubista. Noudetut issuet muunnetaan
skos-muotoon ja "vastaanotettu"-label otetaan pois. Skripti on
tarkoitettu ajettavan joka öisenä cron-jobina.

Skriptin käyttäminen vaatii GitHub-tunnukset Finto-ehdotus-tilille.
Tunnukset sisältävän tiedoston polku annetaan skriptille syöteparametrinä.

Jos skripti käynnistetään parametrillä debug, ohjelma ei
tee muutoksia Finto-ehdotuksen YSE-repositorion issueisiin.

Ohjelma tuottaa kaksi tiedostoa
* yse-new.ttl, joka sisältää tuoreimman ajon generoidut triplet
* yse-skos.ttl, päivitetty ysen julkaisuversio uusine ehdotuksineen

#### check-closed-issues.py

Tämä skripti vastaa suljettujen issueiden käsittelystä YSEssä.

Tätä työtä ei ole tällä hetkellä automatisoitu, sillä työkalu ei suoriudu
kaikista tapauksista itsekseen.
