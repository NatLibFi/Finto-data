#!/bin/sh

INFILES="lvont-defs.ttl lexvo*.rdf"
OUTFILE=lexvo-skos.ttl

SKOSIFYHOME="../../../Skosify/"
LOGFILE=skosify.log
OPTS="--namespace http://lexvo.org/id/ -c lexvo.cfg"

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
