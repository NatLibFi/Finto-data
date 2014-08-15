OntoRip on ohjelma, joka irrottaa yhdistelmäontologiasta domain-spesifisen
osuuden (ts. poistaa YSOn) ja halutessa myös päivittää YSOn uudempaan ja/tai
sylkee ulos erikoisontologian sisältämän (vanhan) YSO-version.

Oletuksena sylkee ulos Turtlea, tätä voi vaihtaa --format parametrilla.
Tarvittaessa ohjeet saa näin: ./ontorip.py -h

Käyttö esim.

./ontorip.py --old yso-liito.ttl liito.owl >liito-ilman-ysoa.ttl
./ontorip.py --new uusin-yso.owl --format xml liito.owl >liito-uusimmalla-ysolla.owl


Vaatimukset: Python (2.6+) ja python-rdflib (4.x)
