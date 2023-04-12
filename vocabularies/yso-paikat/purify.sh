#!/bin/sh

PAIKATFILE=yso-paikat-vb-dump.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify.py
PAIKATNS=http://www.yso.fi/onto/yso/
PURICHAR=p
PAIKATPURIBASE="${PAIKATNS}${PURICHAR}"
CONTEXT=http://www.yso.fi/onto/yso-paikat/
OUTFILE="${PAIKATFILE}.new"


# '-C auto' parameter is not a documented feature of purify.py - it is needed for setting the yso-paikat puri number range of 100000+
$PURIFY -c $CONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT -C auto $PAIKATFILE $PAIKATNS $PAIKATPURIBASE >$OUTFILE

sed -i 's/:p508722/:places/g' $OUTFILE # Prevent purify from changing the conceptScheme

if [ -s $OUTFILE ]; then
  mv -f $OUTFILE $PAIKATFILE
  echo "Done, replaced $PAIKATFILE with purified version."
fi
