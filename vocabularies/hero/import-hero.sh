#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <HERO_file.accdb>"
    exit 1
fi

HEROFILE=$1
HEROCSV=${HEROFILE/accdb/csv}
SANCHECK="../../tools/sanity-check/skos-sanity-check.sh"

java -jar access2csv.jar $HEROFILE
java -jar heroparser.jar $HEROCSV

rapper -i turtle -o turtle hero.ttl > hero-rapper.ttl
mv hero-rapper.ttl hero.ttl

if $SANCHECK hero.ttl 85000 0 ''; then
  ./toskos.sh
  rm $HEROCSV
fi
