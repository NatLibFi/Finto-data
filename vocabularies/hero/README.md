## Heraldiikan ontologia HERO

Kansallisarkisto tuottaa HEROn päivityksen accdb-tietokantadumppina.
Komentosarja import-hero.sh sisältää tarvittavat komennot tiedoston muuttamiseksi automaattisesti skos-muotoon. Muunnoksen ei pitäisi onnistua jos tietokantadumppi sisältää virheitä, tarkkaile komentosarjan tulostamia ilmoituksia. Komentosarjan ajamiseen tarvitaan seuraavat työkalut:

- access2csv.jar - muuttaa MS Access-tiedoston CSV:ksi
- heroparser.jar - siivoaa CSV:n turtle-muotoon
- NatLibFi/Finto-data/tools/sanitycheck/skos-sanity-check.sh - sanitoi ja validoi turtle-tiedoston rakenteen ja koon ennen julkaisuversion tekemistä
  - rapper - "Raptor RDF syntax parsing and serializing utility" tarvitaan asennettuna sanity-check -työkalun ajamiseen
- NatLibFi/Skosify - muokkaa HEROn julkaisuversion, tämä tulee olla asennettuna `pip install skosify`:lla ja asetettuna PATH-muuttujaan

