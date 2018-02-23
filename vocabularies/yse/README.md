YSE
===

YSE pitää sisällään ehdotusjärjestelmän kautta vastaanotetut käsite-ehdotukset. Ehdotukset päivittyvät päivittäin GitHub-issueista tripleiksi skriptillä `issues-to-triples.py`.

YSEstä poistetaan päivittäin käsite-ehdotuksia, jotka on otettu YSAan samalla URIlla ja prefLabelilla. Käsite-ehdotusten poistosta vastaa skripti `check-closed-issues.py`. Skriptit ajetaan finto-dev-kk -palvelimella.

Lue tarkemmat yksityiskohdat näistä työkaluista [YSE-päivittimen ohjeesta](https://github.com/NatLibFi/Finto-data/tree/master/tools/yse-updater).
