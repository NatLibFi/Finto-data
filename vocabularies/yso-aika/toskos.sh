#!/bin/sh

INFILES="yso-aika.rdf yso-aika-meta.ttl"
OUTFILE=yso-aika-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="-c ../../conf/skosify/finnonto.cfg"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
