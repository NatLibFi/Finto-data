#!/bin/sh

INFILES="finaf-metadata.ttl rdaa.rdf rdac.rdf rdap.rdf rdau.rdf finaf.ttl"
OUTFILE=finaf-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--config finaf.cfg --namespace http://urn.fi/URN:NBN:fi:au:finaf:"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
gzip <$OUTFILE >$OUTFILE.gz
