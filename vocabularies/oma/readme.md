OMA - Mediataiteen ontologia on YSO-pohjainen ja kolmikielinen (suomi, ruotsi, englanti) mediataiteen erikoisontologia. Aikaisemmin OMA tunnettiin nimellä Mehi.

OMA-ontologian toteutuksesta on vastannut Mediakulttuuriyhdistys M-cult ry osana Suomen Mediataideverkoston MEHI – Mediataiteen historia Suomessa -hanketta vuosina 2021-2022. Finto vastaa ontologian teknisistä julkaisutöistä.

OMAn pohjalla on YSOn jäädytetty kehitysversio Epikuros, joka liitetään toskos-skriptiä ajettaessa mukaan julkaisuversioon.

Tämä hakemisto sisältää seuraavat tiedostot:

- mehi.ttl (alkuperäinen/kehitysversio)
- oma-skos.ttl (julkaisuversio)
- toskos.sh (tällä generoidaan oma-skos.ttl)
- skosify.log (toskos.sh-skriptin lokitiedosto)

Päivitysprosessi lyhyesti:

- validoi saamasi kehitystiedoston oikeellisuus (mehi.ttl)
- aja purify
- aja General Deprecator
- aja toskos.sh
- git diff .
- commitoi ja pushaa muuttuneet tiedostot
