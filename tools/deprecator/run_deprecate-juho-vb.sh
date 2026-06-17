#!/bin/bash

JUHODIR=~/codes/Finto-data/vocabularies/juho
TTLFILE=$JUHODIR/juho-vb-dump.ttl
TTLFILENEW=$JUHODIR/juho-vb-deprecator-out.ttl
DEPRHOME=~/codes/Finto-data/tools/deprecator
CONF=$DEPRHOME/configs/JUHO-VB-deprecator-config.txt
EMAILOUTPUT=$DEPRHOME/email.txt
LOG=$DEPRHOME/deprecator-juho-vb.log

cd $DEPRHOME
./compile.sh

# dump from GraphDB to Turtle file
curl -L -X GET   --header 'Accept: text/turtle'   'http://graphdb-dev.finto.fi/repositories/juho-maimonides-2026-06-05-c_main/statements?infer=false' > $TTLFILE

minimumsize=10000000
ttlsize=$(du -b "$TTLFILE" | cut -f 1)
# if successful, deprecate
if [ $ttlsize -ge $minimumsize ]; then
  java -Xmx4G -cp 'lib/*:.' GeneralDeprecator $TTLFILE $CONF $TTLFILENEW $EMAILOUTPUT
  status=$?
  echo "exit status: $status"
  if [ $status -eq 2 ]; then
    echo "sending e-mail"
    # mail -t <$EMAILOUTPUT
  fi
fi

#Deprecator can break VocBench imports - dirty fix:
# sed -i 's|file:///tmp/addFromLocalFile|file:/tmp/addFromLocalFile|g' $TTLFILENEW

# If successful, load back to GraphDB
if [ $status -ge 1 ]; then
  echo "Some concepts have been deprecated"
  ttlsize=$(du -b "$TTLFILENEW" | cut -f 1)
  if [ $ttlsize -ge $minimumsize ]; then
    echo "Loading back to GraphDB"
    curl -L -X PUT -H "Content-Type: text/turtle" --data-binary "@$TTLFILENEW" "https://graphdb-dev.finto.fi/repositories/juho-maimonides-2026-06-05-c_main/rdf-graphs/service?graph=http://www.yso.fi/onto/juho/"
  fi
fi
