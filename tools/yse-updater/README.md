YSEn päivitystyökalut
---------------------

Tässä kansiossa sijaitsevat ehdotusjärjestelmä-prototyypin
pyörittämiseen tarvittavat työkalut.

Skriptien ajaminen vaatii pygithub moduulin, 
joka asennetaan esimerkiksi seuraavalla komennolla:
`pip install pygithub`

#### issues-to-triples.py

Tämä skripti hakee "vastaanotettu"-labelilla varustetut
uusien termien ehdotukset GitHubista. Noudetut issuet muunnetaan
skos-muotoon ja "vastaanotettu"-label otetaan pois. Skripti on
tarkoitettu ajettavan joka öisenä cron-jobina.

Skriptin käyttäminen vaatii GitHub-tunnukset Finto-ehdotus-tilille.
Tunnukset sisältävän tiedoston polku annetaan skriptille syöteparametrinä.

Jos skripti käynnistetään parametrillä debug, ohjelma ei
tee muutoksia Finto-ehdotuksen YSE-repositorion issueisiin.

Ohjelma tuottaa kaksi turtle tiedostoa
* yse-new.ttl, joka sisältää tuoreimman ajon generoidut triplet
* yse-skos.ttl, päivitetty ysen julkaisuversio uusine ehdotuksineen
sekä kaksi lokitiedostoa
* /data/Finto-data-update/vocabularies/yse/yse-closed.log
* /data/Finto-data-update/vocabularies/yse/yse-convert.log

#### check-closed-issues.py

Tämä skripti vastaa suljettujen issueiden käsittelystä YSEssä.

Tätä työtä ei ole tällä hetkellä automatisoitu, sillä työkalu ei suoriudu
kaikista tapauksista itsekseen.
