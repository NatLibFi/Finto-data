#!/bin/sh

PAIKATFILE=yso-paikat-vb-dump.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify-local.py
PAIKATNS=http://www.yso.fi/onto/yso/
PURICHAR=p
PAIKATPURIBASE="${PAIKATNS}${PURICHAR}"
PURIFILE=puri-mappings.tsv
OUTFILE="${PAIKATFILE}.new"


# '-C auto' parameter is not a documented feature of purify.py - it is needed for setting the yso-paikat puri number range of 100000+
$PURIFY -s $PURICHAR -f $FORMAT -t $FORMAT -C auto $PAIKATFILE $PAIKATNS $PAIKATPURIBASE $PURIFILE >$OUTFILE

sed -i 's/:p508722/:places/g' $OUTFILE # Prevent purify from changing the conceptScheme

if [ -s $OUTFILE ]; then
  mv -f $OUTFILE $PAIKATFILE
  echo "Done, replaced $PAIKATFILE with purified version."
fi
