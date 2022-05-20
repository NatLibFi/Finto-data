#!/bin/sh

SKOSIFYCMD="skosify"
TIMESTAMPER="./metatietosanasto-timestamper.py"
EXPANDURIS="../../tools/expand-note-uris/expand-note-uris.py"

# expand URIs in notes and definitions
$EXPANDURIS metatietosanasto.rdf >metatietosanasto-expanded.ttl 2>metatietosanasto-expanded.log

INFILES="metatietosanasto-meta.ttl metatietosanasto-expanded.ttl"
OUTFILE=metatietosanasto-skos.ttl

LOGFILE=skosify.log
TIMESTAMPFILE=timestamps.tsv
OPTS="-c metatietosanasto.cfg -f turtle -F turtle --update-query @supergroup-to-member-and-fix-types.rq --post-update-query @prepare-for-publishing.rq"

$SKOSIFYCMD $OPTS $INFILES 2>$LOGFILE |$TIMESTAMPER $TIMESTAMPFILE >$OUTFILE
