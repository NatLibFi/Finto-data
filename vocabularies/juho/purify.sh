#!/bin/sh

ONTOFILE=juhoKehitys.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify.py
ONTONS=http://www.yso.fi/onto/juho/
PURICHAR=p
ONTOPURIBASE="${ONTONS}${PURICHAR}"
CONTEXT=$ONTOPURIBASE
OUTFILE="${ONTOFILE}.new"

$PURIFY -c $CONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT $ONTOFILE $ONTONS $ONTOPURIBASE >$OUTFILE
if [ -s $OUTFILE ]; then
  mv $OUTFILE $ONTOFILE
  echo "Done, replaced $ONTOFILE with purified version."
  echo "Remember to load and re-save using TBC to preserve file order!"
fi
