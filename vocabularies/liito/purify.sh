#!/bin/sh

LIITOFILE=liito.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify.py
MAKETBCCOMP=../../tools/onto-maintenance-tools/tbc-compatibility/make_tbc_compatible.py
LIITONS=http://www.yso.fi/onto/liito/
PURICHAR=p
LIITOPURIBASE="${LIITONS}${PURICHAR}"
CONTEXT=$LIITOPURIBASE
OUTFILE="${LIITOFILE}.new"

$PURIFY -c $CONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT $LIITOFILE $LIITONS $LIITOPURIBASE >$OUTFILE
if [ -s $OUTFILE ]; then
  $MAKETBCCOMP $OUTFILE $LIITONS >$LIITOFILE
  rm $OUTFILE
  echo "Done, replaced $LIITOFILE with purified version."
  echo "Remember to load and re-save using TBC to preserve file order!"
fi
