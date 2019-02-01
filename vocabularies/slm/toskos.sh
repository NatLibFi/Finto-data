#!/bin/sh

INFILES="slm.ttl"
OUTFILE=slm-skos.ttl

SKOSIFYHOME="../../../Skosify"
TIMESTAMPER="../../tools/timestamper/timestamper.py"
LOGFILE=skosify.log
TIMESTAMPFILE=timestamps.tsv
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:mts: -c ./slm.cfg -F turtle"

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES 2>$LOGFILE | $TIMESTAMPER $TIMESTAMPFILE >$OUTFILE
