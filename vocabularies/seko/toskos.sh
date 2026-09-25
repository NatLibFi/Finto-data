#!/bin/sh

python fetch-asteri.py "" >seko.mrcx 2>fetch-asteri.log
python oai-pmh-to-skos.py http://urn.fi/urn:nbn:fi:au:seko: seko <seko.mrcx >seko.ttl 2>convert.log

INFILES="seko-metadata.ttl seko.ttl seko-decoded.ttl"
OUTFILE=seko-skos.ttl

SKOSIFYCMD="skosify"
CONFFILE="../../conf/skosify/finnonto.cfg"
LOGFILE=skosify.log

/usr/local/virtualenvs/skosify/bin/python3 unidecode-hidden-labels.py seko.ttl>seko-decoded.ttl
$SKOSIFYCMD -c $CONFFILE $INFILES -o $OUTFILE 2>$LOGFILE
rm seko-decoded.ttl
rm seko.mrcx
