#!/bin/sh

pdftotext -f 3 -layout OKM*.pdf
./okm-toskos.py OKM*.txt OKM*.csv >okm-tieteenala.ttl

INFILES=okm-tieteenala.ttl
OUTFILE=okm-tieteenala-skos.ttl

SKOSIFYHOME="../../tools/skosify/"
LOGFILE=skosify.log
OPTS=""

$SKOSIFYHOME/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
