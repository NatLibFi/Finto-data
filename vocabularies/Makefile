# Convert all */*-skos.ttl files to RDF/XML

all: $(patsubst %.ttl,%.rdf,$(wildcard */*-skos.ttl)) yso/yso-fin.mrcx

%-skos.rdf: %-skos.ttl
	rapper -i turtle -o rdfxml-abbrev $^ >$@ || rm $@

yso/yso-fin.mrcx: yso/yso-skos.ttl
	python ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --input=$^ --languages="fi" --output=$@ --log_file="yso/yso-fin.log" --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="yso/modified-yso-fi.pkl"
	
