#!/bin/sh

VALOFILE=valo.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify.py
VALONS=http://www.yso.fi/onto/valo/
PURICHAR=p
VALOPURIBASE="${VALONS}${PURICHAR}"
CONTEXT=$VALOPURIBASE
OUTFILE="${VALOFILE}.new"

$PURIFY -c $CONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT $VALOFILE $VALONS $VALOPURIBASE >$OUTFILE
if [ -s $OUTFILE ]; then
  mv $OUTFILE $VALOFILE
  echo "Done, replaced $VALOFILE with purified version."
fi
