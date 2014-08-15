#!/bin/bash

if [ -z "$1" ]
 then
  echo -e "Usage: ./remove-mutu.sh <ontology_namespace> <ontology_with_mutu> <output_file>\n   removes all triples related to MUTU updates"
  exit 1
fi

# MUTU namespaces
mututempns="http://www.yso.fi/onto/mutu-temp/"
mutuns="http://www.yso.fi/onto/mutu/"

# Paths of the scripts and current folder
sdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
dir="$( pwd )"

ns=$1
inputfile=$2
outputfile=$3

temp1=${dir}"/temp1.ttl"
temp2=${dir}"/temp2.ttl"


# Removing the namespaces
$sdir/remove-ns.py $mutuns $inputfile $temp1
$sdir/remove-ns.py $mututempns $temp1 $temp2


# Making the file tbc compatible
$sdir/../tbc-compatibility/make_tbc_compatible.py $temp2 $ns > $outputfile

# Removing the temp files
rm -f $temp1
rm -f $temp2
