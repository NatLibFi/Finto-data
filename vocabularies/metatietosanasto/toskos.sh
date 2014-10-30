#!/bin/sh

INFILES="metatietosanasto.ttl rdam.ttl"
OUTFILE=metatietosanasto-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-c metatietosanasto.cfg -f turtle"

$SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
