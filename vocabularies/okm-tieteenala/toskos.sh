#!/bin/sh

# Disabled this line in favour of storing the txt file in git / joelitak 2025-01-21
# pdftotext -f 3 -layout OKM*.pdf
./okm-toskos.py OKM*.txt OKM*.csv >okm-tieteenala.ttl

INFILES="okm-tieteenala.ttl okm-tieteenala-metadata.ttl"
OUTFILE=okm-tieteenala-skos.ttl

SKOSIFYCMD="skosify"
LOGFILE=skosify.log
OPTS=""

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
