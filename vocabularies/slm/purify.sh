#!/bin/sh

ONTOFILE=slm-purify.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify-local.py
ONTONS=http://urn.fi/URN:NBN:fi:au:slm:
PURICHAR=s
ONTOPURIBASE="${ONTONS}${PURICHAR}"
PURIFILE=puri-mappings.tsv
OUTFILE="${ONTOFILE}.new"

$PURIFY -s $PURICHAR -f $FORMAT -t $FORMAT $ONTOFILE $ONTONS $ONTOPURIBASE $PURIFILE >$OUTFILE
if [ -s $OUTFILE ]; then
  mv $OUTFILE $ONTOFILE
  echo "Done, replaced $ONTOFILE with purified version."
  echo "Remember to load and re-save using TBC to preserve file order!"
fi
