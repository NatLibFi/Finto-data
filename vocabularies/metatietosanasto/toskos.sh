#!/bin/sh

INFILES="metatietosanasto.rdf"
OUTFILE=metatietosanasto-skos.ttl

SKOSIFYHOME="../../../Skosify/skosify/"
LOGFILE=skosify.log
OPTS="-c metatietosanasto.cfg -f turtle --update-query @supergroup-to-member.rq"

$SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
