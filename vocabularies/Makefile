# Convert all */*-skos.ttl files to RDF/XML

# python command that uses the virtual environment for finto-skos-to-marc converter
FINTO_SKOS_TO_MARC_PYTHON = /usr/local/virtualenvs/finto-skos-to-marc/bin/python3

all: $(patsubst %.ttl,%.rdf,$(wildcard */*-skos.ttl)) finaf/finaf-skos.rdf yso/yso-fin.mrcx yso/yso-swe.mrcx aika/yso-aika-fin.mrcx aika/yso-aika-swe.mrcx yso-paikat/yso-paikat-fin.mrcx yso-paikat/yso-paikat-swe.mrcx slm/slm-fin.mrcx slm/slm-swe.mrcx

%-skos.rdf: %-skos.ttl
	rapper -i turtle -o rdfxml-abbrev $^ >$@ || rm $@

finaf/finaf-skos.ttl: $(shell find finaf/finaf-skos/ -type f | sort)
	PYTHONIOENCODING=utf-8 python3 ../tools/split-join-turtle/join-turtle.py $^ >$@

yso/yso-fin.mrcx: yso/yso-skos.ttl
	$(FINTO_SKOS_TO_MARC_PYTHON) ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --input=$^ --languages="fi" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="yso/modified-yso-fi.pkl" 2>yso/yso-fin.log
	
yso/yso-swe.mrcx: yso/yso-skos.ttl
	$(FINTO_SKOS_TO_MARC_PYTHON) ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --input=$^ --languages="sv" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="yso/modified-yso-sv.pkl" 2>yso/yso-swe.log

aika/yso-aika-fin.mrcx: aika/aika-skos.ttl
	$(FINTO_SKOS_TO_MARC_PYTHON) ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --config_section="yso-aika" --input=$^ --languages="fi" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc"

aika/yso-aika-swe.mrcx: aika/aika-skos.ttl
	$(FINTO_SKOS_TO_MARC_PYTHON) ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --config_section="yso-aika" --input=$^ --languages="sv" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc"

yso-paikat/yso-paikat-fin.mrcx: yso-paikat/yso-paikat-skos.ttl
	$(FINTO_SKOS_TO_MARC_PYTHON) ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --config_section="yso-paikat" --input=$^ --languages="fi" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="yso-paikat/modified-yso-paikat-fi.pkl" 2>yso-paikat/yso-paikat-fin.log

yso-paikat/yso-paikat-swe.mrcx: yso-paikat/yso-paikat-skos.ttl
	$(FINTO_SKOS_TO_MARC_PYTHON) ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="yso" --config_section="yso-paikat" --input=$^ --languages="sv" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="yso-paikat/modified-yso-paikat-sv.pkl" 2>yso-paikat/yso-paikat-swe.log

slm/slm-fin.mrcx: slm/slm-skos.ttl
	$(FINTO_SKOS_TO_MARC_PYTHON) ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="slm" --input=$^ --languages="fi" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="slm/modified-slm-fi.pkl" 2>slm/slm-fin.log

slm/slm-swe.mrcx: slm/slm-skos.ttl
	$(FINTO_SKOS_TO_MARC_PYTHON) ../tools/finto-skos-to-marc/finto-skos-to-marc.py --vocabulary_code="slm" --input=$^ --languages="sv" --output=$@ --config="../tools/finto-skos-to-marc/config.ini" --loc_directory="/var/cache/loc" --modification_dates="slm/modified-slm-sv.pkl" 2>slm/slm-swe.log
