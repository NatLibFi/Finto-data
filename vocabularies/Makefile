# Convert all */*-skos.ttl files to RDF/XML

all: $(patsubst %.ttl,%.rdf,$(wildcard */*-skos.ttl))

%-skos.rdf: %-skos.ttl
	rapper -i turtle -o rdfxml-abbrev $^ >$@ || rm $@
