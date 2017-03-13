#!/bin/sh

sparql \
	--data=../ysa/ysa-skos.ttl \
	--data=../allars/allars-skos.ttl \
	--query=merge-places.rq -q \
	>merged-places-skos.ttl

sparql \
	--data merged-places-skos.ttl \
	--query=rename-places.rq -q \
	>pl.ttl

INFILES="pl.ttl"
OUTFILE=pl-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--no-enrich-mappings"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
