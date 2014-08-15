This script splits all of the English and Swedish labels to separate properties.

* Example: *

Original:
yso:p123 skos:prefLabel "kissa"@fi ;
         skos:prefLabel "cat"@en ;
         skos:altLabel "pussycat"@sv.

Split:
yso:p123 skos:prefLabel "kissa"@fi ;
         skos:prefLabel_EN "cat"@en ;
         skos:altLabel_SV "pussycat"@sv.


The new properties have an URI <orig>_<lang> and have both rdf:Property and rdf:AnnotationProperty as type.


Usage e.g.
./split-languages.py ysoKehitys.ttl ysoKehitys-langsplit.ttl

