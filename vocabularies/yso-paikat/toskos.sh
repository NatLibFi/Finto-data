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

INFILES="yso-paikat-metadata.ttl yso-paikat-disambiguated.ttl"
OUTFILE=yso-paikat-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--no-enrich-mappings"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE

bats test.bats
