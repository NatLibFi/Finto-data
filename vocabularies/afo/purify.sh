#!/bin/sh

AFOFILE=afoKehitys.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify.py
AFONS=http://www.yso.fi/onto/afo/
PURICHAR=p
AFOPURIBASE="${AFONS}${PURICHAR}"
CONTEXT=$AFOPURIBASE
OUTFILE="${AFOFILE}.new"

$PURIFY -c $CONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT $AFOFILE $AFONS $AFOPURIBASE >$OUTFILE
if [ -s $OUTFILE ]; then
  mv $OUTFILE $AFOFILE
  echo "Done, replaced $AFOFILE with purified version."
fi
