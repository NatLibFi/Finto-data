#!/bin/sh

SKOSIFY=../../tools/skosify/skosify.py

if [ ! -f paikka.xml ]; then
  unzip -o paikat.zip
fi

./paikkatyyppi-toskos.py >paikkatyyppi.ttl
./metadata-toskos.py >metadata.ttl
./paikka-toskos.py >paikka.ttl
$SKOSIFY --no-mark-top-concepts paikkatyyppi.ttl metadata.ttl paikka.ttl -o paikka-skos.ttl 2>skosify.log
