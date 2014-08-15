#!/bin/sh

# Configuration
SPUT=tools/svn-post-commit/s-put
SECRET=tools/svn-post-commit/secret
WARMUP=tools/svn-post-commit/warmup-cache.py
DATASET=http://localhost:3030/onki-light/data

CHANGED=$(svn log -r HEAD -v -q | grep '/vocabularies/.*/.*-skos\.'| cut -d / -f 4|sort|uniq)
need_refresh=false
for voc in $CHANGED; do
  echo "-- updating: $voc"
  for file in vocabularies/$voc/*-skos.*; do
    echo "---- file: $file"
    echo $SPUT $DATASET http://www.yso.fi/onto/$voc $file
    $SPUT $DATASET http://www.yso.fi/onto/$voc $file
    need_refresh=true
  done
done

if $need_refresh; then
  echo "-- purging Varnish cache..."
  varnishadm -T :6082 -S $SECRET "ban.url /"
  
  echo "-- warming up cache..."
  python $WARMUP
else
  echo "-- no datasets changed, no need to reset Varnish cache"
fi

