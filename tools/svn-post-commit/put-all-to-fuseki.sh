#!/bin/sh

# Configuration
SPUT=./s-put
DATASET=http://localhost:3030/onki-light/data

for voc in ../../vocabularies/* ; do
  echo "-- updating: $voc"
  for file in $voc/*-skos.*; do
    voc=`basename $voc`
    echo "---- file: $file"
    echo $SPUT $DATASET http://www.yso.fi/onto/$voc $file
    $SPUT $DATASET http://www.yso.fi/onto/$voc $file
  done
done
