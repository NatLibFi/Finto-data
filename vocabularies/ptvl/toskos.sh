#!/bin/sh

./ptvl-from-docs.py

DATAFILES="palveluluokat.ttl kohderyhmat.ttl elamantilanteet.ttl tuottajatyypit.ttl toteutustavat.ttl"
INFILES="ptvl-metadata.ttl $DATAFILES"
OUTFILE=ptvl-skos.ttl

for datafile in $DATAFILES; do
	csvfile=`basename $datafile .ttl`.csv
	echo $csvfile
	./ptvl-to-skos.py $csvfile >$datafile
done

SKOSIFYHOME="../../../Skosify/"
LOGFILE=skosify.log
OPTS="--set-modified"

$SKOSIFYHOME/skosify/skosify.py $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
