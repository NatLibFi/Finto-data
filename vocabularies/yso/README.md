Yleinen suomalainen ontologia YSO
=================================

Tässä kansiossa sijaitsevat sekä YSOn tuottamiseen käytetyt ohjelmanpätkät että itse YSOn kehitys ja julkaisuversiot.

### YSOn kehitysversion päivittyminen

Ajantasainen kehitysversio haetaan tasatunnein cronjobilla `dump-yso-to-svn` onki-kk:n Jena SDB-tietokannasta. Mikäli tietokantadumppi ei ole tyhjä tiedosto, samainen cronjob työntää sanaston GitHubiin käyttäen SVN:ää.

### YSOn julkaisuversion päivittyminen

YSOn purittaminen tapahtuu joka yö ajettavalla `update-yso-1-purify` cronjobilla. Kun puritus on valmis ajetaan `update-yso-2-deprecator` cronjob, joka vastaa käsitteiden hautaamisesta eli deprekoinnista. YSO viedään takaisin SDB-tietokantaan sekä vaiheen 1 että 2 päätteeksi. YSOn yöpäivitys viimeistellään ajamalla `update-yso-3-skosify` cronjob, joka valmistelee puritetusta ja deprekoinnit sisältävästä kehitysversiosta uuden julkaisuversion. Uutta julkaisuversiota ei lähetetä GitHubiin, jos yläkäsitteitä on enemmän kuin kolme tai tiedosto on tyhjä.

### YSAn muutosten päivittyminen YSOn kehitysversioon

YSAn muutokset tuodaan SDB-tietokannan YSO-kehitysversioon aina kuukauden ensimmäisenä päivänä. Päivityksestä vastaa `skos-history-ysa-yso-update` cronjob, joka löytyy onki-kk:n kansiosta `/etc/cron.d/`.  
