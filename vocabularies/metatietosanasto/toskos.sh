#!/bin/sh

INFILES=metatietosanasto.ttl
OUTFILE=metatietosanasto-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-c metatietosanasto.cfg -f turtle"

./publish-mts.py $INFILES | $SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE 2>$LOGFILE
