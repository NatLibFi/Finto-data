#!/bin/sh

SKOSIFYCMD="skosify"
TIMESTAMPER="../../tools/timestamper/timestamper.py"
EXPANDURIS="../../tools/expand-note-uris/expand-note-uris.py"

# expand URIs in notes and definitions
$EXPANDURIS slm.ttl >slm-expanded.ttl 2>slm-expanded.log

INFILES="slm-expanded.ttl"
OUTFILE=slm-skos.ttl

LOGFILE=skosify.log
TIMESTAMPFILE=timestamps.tsv
OPTS="--namespace http://urn.fi/URN:NBN:fi:au:slm: -c ./slm.cfg -F turtle"

$SKOSIFYCMD $OPTS $INFILES 2>$LOGFILE | $TIMESTAMPER $TIMESTAMPFILE >$OUTFILE
