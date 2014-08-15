This script will split an ontology in RDF/XML or Turtle format into two
separate files:
 - the schema (*-meta + DC, SKOS etc) into *-meta.ttl in Turtle syntax
 - the actual ontology classes and data into *-data.nt in N-Triple syntax

Usage e.g.
./split-onto.py ysoKehitys.ttl

will produce:

ysoKehitys-meta.ttl
ysoKehitys-data.nt
