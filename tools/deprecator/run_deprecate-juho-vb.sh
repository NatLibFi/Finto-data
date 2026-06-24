#!/bin/bash

# Muuta polut mieleisiksesi. Kannattaa suosia absoluuttisia polkuja, vaikka niitä ei esimerkissä käytetäkään ;-)
JUHODIR=~/codes/Finto-data/vocabularies/juho
TTLFILE=$JUHODIR/juho-vb-dump.ttl
TTLFILENEW=$JUHODIR/juho-vb-deprecator-out.ttl
DEPRHOME=~/codes/Finto-data/tools/deprecator
CONF=$DEPRHOME/configs/JUHO-VB-deprecator-config.txt
EMAILOUTPUT=$DEPRHOME/email.txt
LOG=$DEPRHOME/deprecator-juho-vb.log

cd $DEPRHOME
./compile.sh

# Haetaan niin, että GraphDB:n ylimääräiset roskat jäävät pois
curl -L -X POST \
  -H "Accept: text/turtle" \
  -H "Content-Type: application/sparql-query" \
  --data-binary '
CONSTRUCT {
  ?s ?p ?o .
}
WHERE {
  ?s ?p ?o .

  FILTER (
    STRSTARTS(STR(?s), "http://www.yso.fi/onto/juho/")
    ||
    STRSTARTS(STR(?s), "http://www.yso.fi/onto/juho-meta/")
    ||
    STRSTARTS(STR(?s), "http://www.yso.fi/onto/yso-meta/")
    ||
	    STRSTARTS(STR(?s), "http://www.yso.fi/onto/yso-meta/2007-03-02/")    
  )
}
' \
"http://graphdb-dev.finto.fi/repositories/juho-maimonides-2026-06-05-c_main" \
> "$TTLFILE"

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

# Jos onnistui, ladataan takaisin GraphDB:hen.
if [ $status -ge 1 ]; then
  echo "Some concepts have been deprecated"
  ttlsize=$(du -b "$TTLFILENEW" | cut -f 1)
  if [ $ttlsize -ge $minimumsize ]; then
    echo "Loading back to GraphDB"
    curl -L -X PUT -H "Content-Type: text/turtle" --data-binary "@$TTLFILENEW" "https://graphdb-dev.finto.fi/repositories/juho-maimonides-2026-06-05-c_main/rdf-graphs/service?graph=http://www.yso.fi/onto/juho/"
  fi
fi

# Huomaa, että seuraavassa, skosify-vaiheessa käytetään deprekoinnin tulostiedostoa (juho-vb-deprecator-out-a.ttl), 
# mikäli deprekoitavaa oli. Muussa tapauksessa skosifioinnissa tulee käyttää juho-vb-dump.ttl-tiedostoa. 
# Joka tapauksessa, aja deprekaattori aina.