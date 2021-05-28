#!/bin/sh

# temporary file for uniforming the literal serialization of explicitly stated xsd:string datatypes with implicit ones
YSOTEROMODIFIED=yso-tero-modified.ttl
cat yso-tero.ttl | sed -e 's/"^^xsd:string/"/g' > $YSOTEROMODIFIED

INFILES="tero-metadata.ttl tero-yso-replacedby.ttl tero.ttl $YSOTEROMODIFIED"
OUTFILE=tero-skos.ttl

LOGFILE=skosify.log
#OPTS="-c tero.cfg -l fi -f turtle"
OPTS="-c ../../conf/skosify/finnonto.cfg -l fi -f turtle"

./add-tero-types.py $INFILES | skosify $OPTS - -o $OUTFILE 2>$LOGFILE

# remove the temporary file afterwards
rm $YSOTEROMODIFIED
