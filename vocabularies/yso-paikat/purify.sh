#!/bin/sh

PAIKATFILE=yso-paikat-purify.ttl
FORMAT=turtle

PURIFY=../../tools/purify/purify.py
PAIKATNS=http://www.yso.fi/onto/yso/
PURICHAR=p
PAIKATPURIBASE="${PAIKATNS}${PURICHAR}"
CONTEXT=$PAIKATPURIBASE
OUTFILE="${PAIKATFILE}.new"

# Saving the current YSO maxcounter from puri.onki.fi, as we are about to use YSO-paikat counter range
COUNTER=$(curl -s -H "Pragma: no-cache" "http://puri.onki.fi/getcounter?purins=http%3A%2F%2Fwww.yso.fi%2Fonto%2Fyso%2Fp")

if [ $COUNTER -lt 100000 ]; then

  # '-C auto' parameter is not a documented feature of purify.py - it is needed for setting the yso-paikat puri number range of 100000+
  $PURIFY -c $CONTEXT -s $PURICHAR -f $FORMAT -t $FORMAT -C auto $PAIKATFILE $PAIKATNS $PAIKATPURIBASE >$OUTFILE
  sed -i 's/:p508540/:places/g' $OUTFILE # Prevent purify from changing the conceptScheme

  if [ -s $OUTFILE ]; then
    mv $OUTFILE $PAIKATFILE
    echo "Done, replaced $PAIKATFILE with purified version."
  fi

  #Setting the old maxcounter back not to mess with YSOs puri counter
  curl "http://puri.onki.fi/setcounter?purins=http%3A%2F%2Fwww.yso.fi%2Fonto%2Fyso%2Fp&counter=$COUNTER"

  else
    echo "puri.onki.fi counter not in the excepted range for YSO-puris ( < 100000)"
    echo -e "puri.onki.fi counter not in the excepted range for YSO-puris ( < 100000)" | mail -s "Ongelma YSO-paikoissa" joeli.takala@helsinki.fi
fi
