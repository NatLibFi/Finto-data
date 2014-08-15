#!/bin/sh

INFILES="prefixes.ttl iconclass*.nt"
OUTFILE=ic-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="-f turtle --debug -c iconclass.cfg"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o ic-unstripped.ttl 2>$LOGFILE
./strip-untyped-concepts.py ic-unstripped.ttl >$OUTFILE
