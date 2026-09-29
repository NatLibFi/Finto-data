# Kuinka päivitän FinMeshin

Tarvitset python3-ajoympäristön, rdflib-kirjaston ja useita muita kirjastoja, jotka näet `build_mesh_skos_autodiscover.py`-skriptin alusta. Lisäksi tarvitset edellisen julkaisutiedoston, josta skripti oppii tarvittavan tietomallin ja FinMeshin ylläpidolta saamasi tiedoston. 

Skripti tuottaa julkaisutiedoston, jonka voit muuttaa julkaisussa käytettäväksi tiedostoksi eli mesh-skos.ttl:ksi. Tiedosto esimerkkitapauksessa oli `mesh-skos-20260929-150415.ttl`. Luotua tiedostoa käytetään myös seuraavan ajon *--compare*-parametrissa tietomallin tarjoavana tiedostona.

Skripti ei tarvitse muita tiedostoja kuin alla olevasta esimerkkiajosta käy ilmi. *REQUIRED_SOURCE_FILES*-tuplen sisältämät tiedostot se etsii *KIB*:n sivulta ja lataa ZIP-paketin verkosta muistiin. Lisäksi skripti lataa verkosta *NLM*:n saman vuoden desc[VUOSI].gz-XML:n, josta saadan muun muassa päivämäärät (ovat lisäys edellisiin päivityksiin verrattuna).

Ainoastaan skeeman metatietoja voit joutua päivittämään käsin tilaajalta saamiesi ohjeiden mukaisesti.

## Ajo

### Virtuaaliympäristön aktivointi

    . [polku/python3:n/virtuaaliympäristökansioon]/bin/activate

### Skriptin ajo

    python3 ./build_mesh_skos_autodiscover.py \
    --year 2026 \
    --master MASTER_2026_valmis_20260617_Fintoon.txt \
    --compare mesh-skos-new.ttl \
    --out-dir /tmp/mesh-test

### Virtuaaliympäristön deaktivointi

    . [polku/python3:n/virtuaaliympäristökansioon]/bin/deactivate

Skripti on tehty kokonaan Copilotilla, mutta sen toimivuus on testattu vertaamalla sen tuotosta aiemmin saman sanastonversion (2026) muulla tavoin onnistuneesti luotuun julkaisutiedostoon. Skriptin tarkoitus on helpottaa, nopeuttaa ja suoraviivaistaa aiemmin melko hankalaksi osoittautunutta päivitystä. 

