#!/bin/sh

INFILES="aika.rdf aika-meta.ttl"
OUTFILE=aika-skos.ttl


SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--no-enrich-mappings --no-mark-top-concepts --set-modified --namespace http://urn.fi/URN:NBN:fi:au:krono:"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE


