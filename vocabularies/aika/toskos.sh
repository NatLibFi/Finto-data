#!/bin/sh

INFILES="aika.rdf"
OUTFILE=aika-skos.ttl


SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--no-enrich-mappings --set-modified --namespace http://www.yso.fi/onto/aika/"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE

#Uudenmalliselle YSO-paikoille ei ole testejä. Vielä.
#bats test.bats
