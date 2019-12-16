# Convert all */*-skos.ttl files to RDF/XML

all: $(patsubst %.ttl,%.rdf,$(wildcard */*-skos.ttl)) yso/yso-fin.mrcx yso/yso-swe.mrcx yso-paikat/yso-paikat-fin.mrcx yso-paikat/yso-paikat-swe.mrcx slm/slm-fin.mrcx slm/slm-swe.mrcx

%-skos.rdf: %-skos.ttl
	rapper -i turtle -o rdfxml-abbrev $^ >$@ || rm $@

yso/yso-fin.mrcx: yso/yso-skos.ttl
	python ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --input=$^ --languages="fi" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="yso/modified-yso-fi.pkl" 2>yso/yso-fin.log
	
yso/yso-swe.mrcx: yso/yso-skos.ttl
	python ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --input=$^ --languages="sv" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="yso/modified-yso-sv.pkl" 2>yso/yso-swe.log

yso-paikat/yso-paikat-fin.mrcx: yso-paikat/yso-paikat-skos.ttl
	python ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --config_section="yso-paikat" --input=$^ --languages="fi" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="yso-paikat/modified-yso-paikat-fi.pkl" 2>yso-paikat/yso-paikat-fin.log

yso-paikat/yso-paikat-swe.mrcx: yso-paikat/yso-paikat-skos.ttl
	python ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --config_section="yso-paikat" --input=$^ --languages="sv" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="yso-paikat/modified-yso-paikat-sv.pkl" 2>yso-paikat/yso-paikat-swe.log

slm/slm-fin.mrcx: slm/slm-skos.ttl
	python ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="slm" --input=$^ --languages="fi" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="slm/modified-slm-fi.pkl" 2>slm/slm-fin.log

slm/slm-swe.mrcx: slm/slm-skos.ttl
	python ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="slm" --input=$^ --languages="sv" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="slm/modified-slm-sv.pkl" 2>slm/slm-swe.log
