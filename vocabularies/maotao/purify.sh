#!/bin/sh

ONTOFILE=maotao.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify.py
MAONTONS=http://www.yso.fi/onto/mao/
TAONTONS=http://www.yso.fi/onto/tao/
PURICHAR=p
MAONTOPURIBASE="${MAONTONS}${PURICHAR}"
TAONTOPURIBASE="${TAONTONS}${PURICHAR}"
MAOCONTEXT=$MAONTOPURIBASE
TAOCONTEXT=$TAONTOPURIBASE
OUTFILE="${ONTOFILE}.new"

$PURIFY -c $MAOCONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT $ONTOFILE $MAONTONS $MAONTOPURIBASE >$OUTFILE
if [ -s $OUTFILE ]; then
  mv $OUTFILE $ONTOFILE
  echo "Done, replaced $ONTOFILE with purified version."
  echo "Remember to load and re-save using TBC to preserve file order!"
fi

$PURIFY -c $TAOCONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT $ONTOFILE $TAONTONS $TAONTOPURIBASE >$OUTFILE
if [ -s $OUTFILE ]; then
  mv $OUTFILE $ONTOFILE
  echo "Done, replaced $ONTOFILE with purified version."
  echo "Remember to load and re-save using TBC to preserve file order!"
fi
