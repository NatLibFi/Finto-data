#!/bin/sh

JENAHOME="$HOME/sw/apache-jena"
INFILE="juho.ttl"
YSOFILE="yso-juho.ttl"
HIERFILE="juho-hierarchy.nt"
MERGEHIER="../../tools/merge-hierarchy/merge-hierarchy.sparql"

$JENAHOME/bin/arq --data=$INFILE --data=$YSOFILE --query=$MERGEHIER --results=NT >$HIERFILE

INFILES="juho-metadata.ttl $HIERFILE $INFILE $YSOFILE"
OUTFILE=juho-skos.ttl

SKOSIFYHOME="../../tools/skosify"
CONFFILE=$SKOSIFYHOME/finnonto.cfg
LOGFILE=skosify.log
OPTS="-l fi -f turtle"

$SKOSIFYHOME/skosify.py $OPTS -c $CONFFILE -o $OUTFILE $INFILES 2>$LOGFILE
