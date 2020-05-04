#!/bin/sh

INFILES="finaf-metadata.ttl rdaa.rdf rdac.rdf finaf.ttl"
OUTFILE=finaf-skos.ttl

SKOSIFYHOME="../../tools/skosify"
LOGFILE=skosify.log
OPTS="--set-modified --no-mark-top-concepts --no-enrich-mappings --namespace http://urn.fi/URN:NBN:fi:au:finaf:"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
