#!/bin/sh

# step 1: remove manually unwanted extra triples from the rawfile (e.g., <file://...)

# step 2: set $RAWFILE to be the file processed in step 1

RAWFILE="ykl.ttl"
PROCESSEDFILE="ykl-processed.ttl"

SKOSIFYCMD="skosify"

# remove (excess) whitespaces before, between (in long quoted literals) and after in literals
cat $RAWFILE | sed 's/[ ]\+/ /g' | sed 's/  //g' | sed -r 's/ \+[)]/\+\)/g' | sed -r 's/([0-9]) \+([^ ][^0-9])/\1\+\2/g' | sed 's/ *$//' | sed 's/^ *//' > $PROCESSEDFILE

INFILES="ykl-metadata.ttl $PROCESSEDFILE ykl-hklj.ttl"
OUTFILE=ykl-skos.ttl

LOGFILE=skosify.log
OPTS="-c ykl.cfg --namespace http://urn.fi/URN:NBN:fi:au:ykl: --mark-top-concepts"

$SKOSIFYCMD $OPTS $INFILES -o $OUTFILE 2>$LOGFILE
