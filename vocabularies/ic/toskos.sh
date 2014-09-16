#!/bin/sh

INFILES="prefixes.ttl ic-metadata.ttl iconclass*.nt.gz"
OUTFILE=ic-skos.ttl

SKOSIFYHOME="../../tools/skosify"
LOGFILE=skosify.log
OPTS="-f turtle --debug -c iconclass.cfg"

zcat -f $INFILES | $SKOSIFYHOME/skosify.py $OPTS -o ic-unstripped.ttl 2>$LOGFILE
./strip-untyped-concepts.py ic-unstripped.ttl >$OUTFILE
