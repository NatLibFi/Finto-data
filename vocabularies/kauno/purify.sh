#!/bin/sh

ONTOFILE=kauno.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify-local.py
ONTONS=http://www.yso.fi/onto/kauno/
PURICHAR=p
ONTOPURIBASE="${ONTONS}${PURICHAR}"
PURIMAPPINGS=puri-mappings.tsv
CONTEXT=$ONTOPURIBASE
OUTFILE="${ONTOFILE}.new"

$PURIFY -s $PURICHAR -f $FORMAT -t $FORMAT $ONTOFILE $ONTONS $ONTOPURIBASE $PURIMAPPINGS >$OUTFILE
if [ -s $OUTFILE ]; then
  mv $OUTFILE $ONTOFILE
  sleep 5
  echo "Done, replaced $ONTOFILE with purified version."
fi
