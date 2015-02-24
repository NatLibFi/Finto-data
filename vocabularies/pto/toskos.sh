#!/bin/sh

JENAHOME="$HOME/sw/apache-jena"
INFILE="paikkatieto-ei45-eiinspire-puritettu-ylakas-pois.ttl"
MERGEHIER="../../tools/merge-hierarchy/merge-hierarchy.sparql"

$JENAHOME/bin/arq --data=$INFILE --data=yso-paikkatieto.ttl --query=$MERGEHIER --results=NT >pto-hierarchy.nt

INFILES="pto-metadata.ttl pto-hierarchy.nt $INFILE yso-paikkatieto.ttl"
OUTFILE=pto-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-c pto2skos.cfg"

$SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
