#!/bin/sh

ONTOFILE=kauno.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify.py
ONTONS=http://www.yso.fi/onto/kauno/
PURICHAR=p
ONTOPURIBASE="${ONTONS}${PURICHAR}"
CONTEXT=$ONTOPURIBASE
OUTFILE="${ONTOFILE}.new"

$PURIFY -c $CONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT $ONTOFILE $ONTONS $ONTOPURIBASE >$OUTFILE
if [ -s $OUTFILE ]; then
  mv $OUTFILE $ONTOFILE
  sleep 5
  wget -O puri-history.log http://puri.onki.fi/getmappings?context=$CONTEXT 2> /dev/null
  echo "Done, replaced $ONTOFILE with purified version."
fi
