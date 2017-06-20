#!/bin/sh

sparql \
	--data=../ysa/ysa-skos.ttl \
	--data=../allars/allars-skos.ttl \
	--query=merge-places.rq -q \
	>merged-places-skos.ttl

sparql \
	--data merged-places-skos.ttl \
	--query=rename-places.rq -q \
	>yso-paikat.ttl

./disambiguate.py yso-paikat.ttl >yso-paikat-disambiguated.ttl

./fix-notes.py yso-paikat-disambiguated.ttl >yso-paikat-fixednotes.ttl

# fetch mappings from Wikidata and store them in a sorted NT file, so version control works
rsparql --results NT --service https://query.wikidata.org/sparql --query wikidata-links.rq | sort >wikidata-links.nt

INFILES="yso-paikat-metadata.ttl yso-paikat-fixednotes.ttl wikidata-links.nt"
OUTFILE=yso-paikat-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--no-enrich-mappings"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE

bats test.bats
