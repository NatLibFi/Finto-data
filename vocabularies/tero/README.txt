tero.rdf otettu ONKI3 svn:stä, versiotiedot:
Last Changed Author: jwtuomin
Last Changed Rev: 26664
Last Changed Date: 2013-11-27 16:13:23 +0200 (Wed, 27 Nov 2013)

Editoitu sen verran, että vaihdettu ConceptSchemen URI kaikkialla:
http://www.yso.fi/onto/tero/conceptscheme -> http://www.yso.fi/onto/tero/

Alkuperäisessä tero.rdf:ssä on käytetty skosext:broaderGeneric ja
broaderPartitive -suhteita. Ne on muunnettu normaaleiksi
skos:broader/narrower ja skosext:partOf-suhteiksi käyttäen Skosifyn
konfiguraatiotiedostossa määriteltyjä muunnoksia.
