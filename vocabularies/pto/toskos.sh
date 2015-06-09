#!/bin/sh

JENAHOME="$HOME/ontology/sw/apache-jena"
INFILE="paikkatieto-ei45-eiinspire-puritettu-ylakas-pois.ttl"
MERGEHIER="../../Finto-tools/merge-hierarchy/merge-hierarchy.sparql"

$JENAHOME/bin/arq --data=$INFILE --data=yso-paikkatieto.ttl --query=$MERGEHIER --results=NT >pto-hierarchy.nt

INFILES="pto-metadata.ttl pto-hierarchy.nt $INFILE yso-paikkatieto.ttl"
OUTFILE=pto-skos.ttl

SKOSIFYHOME="../../SKOSIFY/"
LOGFILE=skosify.log
OPTS="-c pto2skos.cfg"

$SKOSIFYHOME/skosify.py $OPTS -o $OUTFILE $INFILES 2>$LOGFILE
