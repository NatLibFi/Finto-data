Lisätty 2013-06-26. Otettu ONKI3:sta mesh/mesh.rdf. Ei ollut saatavilla
download-nappulan kautta joten piti puljata tämä suoraan SeCon SVN:stä.

Koska mesh.rdf ei sisältänyt skos:narrower-suhteita, ajettiin se vielä
kertaalleen skosifyn läpi:
./skosify.py mesh.rdf -o mesh-skos.ttl
