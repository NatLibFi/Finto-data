#!/bin/sh

JENAHOME="/opt/apache-jena"
INFILE="keko-skos.orig.ttl"
HIERFILE="keko-hierarchy.nt"
MERGEHIER="../../tools/merge-hierarchy/merge-hierarchy-skos.sparql"

$JENAHOME/bin/arq --data=$INFILE --query=$MERGEHIER --results=NT >$HIERFILE

INFILES="$HIERFILE $INFILE"
OUTFILE=keko-skos.ttl

$JENAHOME/bin/rdfcat -out ttl $INFILES >$OUTFILE
