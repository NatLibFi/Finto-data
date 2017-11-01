#!/bin/sh

JENABIN="/data/apache-jena/bin"

$JENABIN/update --data=metatietosanasto.rdf --update=fix-types.rq --dump >metatietosanasto.nt

INFILES="metatietosanasto-meta.ttl metatietosanasto.nt"
OUTFILE=metatietosanasto-skos.ttl

SKOSIFYHOME="../../../Skosify/skosify/"
LOGFILE=skosify.log
OPTS="-c metatietosanasto.cfg -f turtle --update-query @supergroup-to-member.rq"

$SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
