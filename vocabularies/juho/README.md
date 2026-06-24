JUHO
====

22.4.2024: Käytössä oleva yso-versio on: Ghosha (tämä todnäk ei pidä enää paikkaansa, vaan on Laotse)

## Miten päivitän juhon VocBench-aikakaudella

### Tarvitset seuraavat:

#### Deprekointi
tools/deprecator/run_deprecate-juho-vb.sh
tools/deprecator/configs/JUHO-VB-deprecator-config.txt

#### Skosifiointi
vocabularies/juho/toskos.sh
conf/skosify/juho-vb.cfg
vocabularies/juho/extract-juho.rq

### Prosessi:

0) Finto-data-repon juuressa: `git pull`

1) Deprekointi

Suorittaa deprekoinnin ja palautaa juhon ja yson yhdistelmän GraphDB:hen. Jos deprekoitavaa ei ole, tulosta ei synny ja seuraavan vaiheen skosifioinnissa pitää käyttää deprekoinnin tuottamaa dumppitiedostoa, mutta deprekaattori tulee aina ajaa.

Konfiguraatio: tools/deprecator/configs/JUHO-VB-deprecator-config.txt

Ajetaan kansiossa tools/deprecator:
- muuta polut omaan ajoympärisöösi sopiviksi
- `./run_deprecate-juho-vb.sh`

2) Skosifiointi

Konfiguraatio: conf/skosify/juho-vb.cfg

Jos oli deprekoitavaa, tulee EXTRACTABLE:n arvoksi asettaa deprekoinnin tulostiedosto, jos ei, niin silloin dumppi.
- muuta myös polut omaan ajoympärisöösi sopiviksi ja varmista, että sinulla on Python virtuaaliympäristössäsi asennettuna skosify
- `./toskos.sh`
- Tällä hetkellä on käytössä devin testisanaston (https://dev.finto.fi/juho-vb/) graafi http://www.yso.fi/onto/juho-vb/ ja sanastodatan sisältävä tiedosto ./juho-skos-vb.ttl, mutta tullee muuttumaan, kun pääsemme tuotantoon.






