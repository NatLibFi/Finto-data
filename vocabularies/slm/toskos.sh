#!/bin/sh

INFILES="slm.ttl"
OUTFILE=slm-skos.ttl

SKOSIFYCMD="skosify"
TIMESTAMPER="../../tools/timestamper/timestamper.py"
LOGFILE=skosify.log
TIMESTAMPFILE=timestamps.tsv
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:slm: -c ./slm.cfg -F turtle"

$SKOSIFYCMD $OPTS $INFILES 2>$LOGFILE | $TIMESTAMPER $TIMESTAMPFILE >$OUTFILE
