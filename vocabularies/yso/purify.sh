#!/bin/sh

YSOFILE=ysoKehitys-purify.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify.py
YSONS=http://www.yso.fi/onto/yso/
PURICHAR=p
YSOPURIBASE="${YSONS}${PURICHAR}"
CONTEXT=$YSOPURIBASE
OUTFILE="${YSOFILE}.new"

$PURIFY -c $CONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT $YSOFILE $YSONS $YSOPURIBASE >$OUTFILE
if [ -s $OUTFILE ]; then
  mv $OUTFILE $YSOFILE
  echo "Done, replaced $YSOFILE with purified version."
  echo "Remember to load and re-save using TBC to preserve file order!"
fi
