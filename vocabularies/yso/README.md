Yleinen suomalainen ontologia YSO
=================================

Tässä kansiossa sijaitsevat sekä YSOn tuottamiseen käytetyt ohjelmanpätkät että itse YSOn kehitys ja julkaisuversiot.

### YSOn kehitysversion päivittyminen

Ajantasainen kehitysversio haetaan tasatunnein cronjobilla `dump-yso-to-svn` onki-kk:n Jena SDB-tietokannasta. Mikäli tietokantadumppi ei ole tyhjä tiedosto, samainen cronjob työntää sanaston GitHubiin käyttäen SVN:ää.

### YSOn julkaisuversion päivittyminen

YSOn purittaminen tapahtuu joka yö ajettavalla `update-yso-1-purify` cronjobilla. Kun puritus on valmis ajetaan `update-yso-2-deprecator` cronjob, joka vastaa käsitteiden hautaamisesta eli deprekoinnista. YSO viedään takaisin SDB-tietokantaan sekä vaiheen 1 että 2 päätteeksi. YSOn yöpäivitys viimeistellään ajamalla `update-yso-3-skosify` cronjob, joka valmistelee puritetusta ja deprekoinnit sisältävästä kehitysversiosta uuden julkaisuversion. Uutta julkaisuversiota ei lähetetä GitHubiin, jos yläkäsitteitä on enemmän/vähemmän kuin kolme tai tiedosto on tyhjä.

### YSAn muutosten päivittyminen YSOn kehitysversioon

YSAn muutokset tuodaan SDB-tietokannan YSO-kehitysversioon aina kuukauden ensimmäisenä päivänä. Päivityksestä vastaa `skos-history-ysa-yso-update` cronjob, joka löytyy onki-kk:n kansiosta `/etc/cron.d/`.

### YSOn ajallisesti jäädytetyn kehitysversion julkaisu

Ennen kuin ysoKehitys.rdf siirretään omaan kansioonsa (katso mallia Aristoteles julkaisusta), tulee sisäiseen käyttöön tarkoitetut kehityspropertyt poistaa esimerkiksi oheisella sparql-kyselyllä. Kysely on helpointa ajaa Jenan `sparql`-komentorivityökalulla.

```
PREFIX yso-meta: <http://www.yso.fi/onto/yso-meta/2007-03-02/>
PREFIX yso-translate: <http://www.yso.fi/onto/yso-translate/>
PREFIX yso-update: <http://www.yso.fi/onto/yso-update/>

CONSTRUCT { ?s ?p ?o . } 
WHERE {
  ?s ?p ?o .
  FILTER(!STRSTARTS(STR(?s),STR(yso-update:))) .
  FILTER(!STRSTARTS(STR(?o),STR(yso-update:))) .
  FILTER(!STRSTARTS(STR(?s),STR(yso-translate:))) .
  FILTER(!STRSTARTS(STR(?o),STR(yso-translate:))) .
  FILTER(!STRSTARTS(STR(?p),STR(yso-meta:developmentComment))) .
}
```

### Ratkaisuja yleisiin ongelmatilanteisiin

Kootaan tänne yleisimpiä YSO-niksejä.

#### YSO ei päivity koska yläkäsitteiden lukumäärä on jotain muuta kuin kolme:

YSOn kehitysversioon on todennäköisesti lipsahtanut uusi käsite, jolla ei ole vielä merkattuna yläkäsitettä. Tällöin käsite tulkitaan virheellisesti YSOn uudeksi yläkäsitteeksi ja julkaisu estetään. Tilanne ratkeaa automaattisesti kun virheellinen data on korjattu SDB-tietokantaan TBC:llä.

Jos yläkäsitteiden määrä on nolla, kehitystiedosto on todennäköisesti tyhjä jonkin käsittelyssä tapahtuneen virheen takia. Tällöin oikea ratkaisu on mennä palvelimelle katsomaan miksei päivitysputki toimi oikein. Päivityksessä pyöriteltävät tiedostot löytyvät onki-kk:n kansiosta /data/Finto-data-update/.

#### YSOn julkaisuversion käsitteillä näkyy ylimääräisiä kehitykseen liittyviä propertyjä:

YSOn kehitysversiossa on tällöin otettu todennäköisesti käyttöön uusi property, mutta sitä ei ole muistettu lisätä poistettavien propertyjen joukkoon skosifyn konfiguraatiossa `finnonto.cfg`.

### Ongelmaloki

14.2.2018: YSO ei ollut päivittynyt yöllä sillä ysa/allärs matchien päivitin tuotti jostain syystä lähes tyhjän tiedoston. Cronjobien ajaminen uudestaan ratkaisi ongelman.

9.9.2018: YSO ei ollut päivittynyt yöllä sillä skossauksen yhteydessä tehty asa/allärt matchien päivitin tuotti pelkät namespace prefixit. Cronjobien ajaminen uudestaan ratkaisi ongelman.

