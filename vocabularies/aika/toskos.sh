#!/bin/sh

INFILES="aika.rdf aika-meta.ttl"
OUTFILE=aika-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="-c ../../conf/skosify/finnonto.cfg"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
