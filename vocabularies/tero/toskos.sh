#!/bin/sh

# temporary file for uniforming the literal serialization of explicitly stated xsd:string datatypes with implicit ones
TEROMODIFIED=tero-modified.ttl
cat tero.ttl | sed -e 's/"^^xsd:string/"/g' > $TEROMODIFIED

INFILES="$TEROMODIFIED tero-meta.ttl tero-metadata.ttl tero-yso-replacedby.ttl ysoKehitysTBC_2026-3_Maimonides.ttl"
OUTFILE=tero-skos.ttl

LOGFILE=skosify.log
#OPTS="-c tero.cfg -l fi -f turtle"
OPTS="-c finnonto.cfg -l fi -f turtle"

# Tero Concepts have been marked as as such in the ontology 
# ./add-tero-types.py $INFILES | skosify $OPTS - -o $OUTFILE 2>$LOGFILE

~/ontology/python3venv/bin/python3 ~/ontology/SKOSIFY/Skosify-master/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE

# remove the temporary file afterwards
rm $TEROMODIFIED
