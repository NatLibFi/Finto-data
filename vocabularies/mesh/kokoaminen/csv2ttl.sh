#! /bin/bash


if [ $# -eq 0 ]; then
  echo "Usage: csv2ttl file.csv"
  exit
fi

# parameters
csvfile=$1
tmpfile=./tmp.csv

cp $csvfile $tmpfile
dos2unix $tmpfile

sed -E 's|^([^\t]+)\t(.*)$|<http://www.yso.fi/onto/mesh/\2> <http://www.w3.org/2004/02/skos/core#altLabel> \"\1\"@se .|' $tmpfile > altlabels.ttl
rm $tmpfile
