#!/bin/sh

INFILES="lexvo-metadata.ttl lvont-defs.ttl lexvo*.rdf"
OUTFILE=lexvo-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS="--namespace http://lexvo.org/id/ -c lexvo.cfg"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
