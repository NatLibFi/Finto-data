#!/bin/sh

INFILES="lvont-defs.ttl lexvo*.rdf"
OUTFILE=lexvo-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS="--namespace http://lexvo.org/id/ -c lexvo.cfg"

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
