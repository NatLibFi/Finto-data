#!/bin/sh

PUHOFILE=puho.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify.py
PUHONS=http://www.yso.fi/onto/puho/
PURICHAR=ph
PUHOPURIBASE="${PUHONS}${PURICHAR}"
CONTEXT=$PUHOPURIBASE
OUTFILE="${PUHOFILE}.new"

$PURIFY -c $CONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT $PUHOFILE $PUHONS $PUHOPURIBASE >$OUTFILE
if [ -s $OUTFILE ]; then
  mv $OUTFILE $PUHOFILE
  echo "Done, replaced $PUHOFILE with purified version."
fi
