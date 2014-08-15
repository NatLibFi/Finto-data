Scripts:

rdflib-finto-sparql.py
term-in-onto.py
xml-parsers/extract-terms-from-oph.py
xml-parsers/extract-terms-from-oksa.py


** Usage of rdflib-finto-sparql.py **

./rdflib-finto-sparql.py <file-for-output>

Lemmatizes the Finnish prefLabels in JUPO and lists the lemmas and URIs in a csv file.
File form:
lemma,URI,URI


** Usage of term-in-onto.py **

./term-in-onto.py --lemmafile <file-containing-lemmas-and-URIs> <termfile>

Tests how many of the terms in termfile are found in JUPO either unmodified or lemmatized
Prints the files to system-out

** Usage of xml-parsers **

./extract-terms-from-oph.py <xml-term-file>
./extract-terms-from-oksa.py <xml-term-file>

Extracts the terms from an xml file and prints them to system-out
