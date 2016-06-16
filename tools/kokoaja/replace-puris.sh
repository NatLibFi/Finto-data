#!/bin/bash

# tälle annetaan parametrina TSV-muotoinen puri-listaus, jonka saa
# puri.onki.fi:stä esim. 
# http://puri.onki.fi/getmappings?context=http://www.yso.fi/onto/muso/p

awk '{print "s|" $1 " |" $2 " |"}' <$1 | while read exp; do perl -pi -e "$exp" kokoUriVastaavuudet.txt; done
