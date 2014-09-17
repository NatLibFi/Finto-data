#!/usr/bin/env bash

# $1 domain name
# $2 cobined ontology file
# $3 directory for the configuration files
# $4 directory for outputting the domain and general ontology files

if [ "$#" -ne 4 ]; then
  echo "Illegal number of parameters"
  exit 1
fi

domain=$1
yso=yso-${1}
dir=$4


# Separating the YSO and domain ontology
../../ontorip/ontorip.py --old ${4}/${yso}-ontorip.ttl $2 > ${4}/${domain}-ontorip.ttl

# Making the files TBC combatible
./prote-to-tbc.py ${3}/yso.prop ${4}/${yso}-ontorip.ttl ${4}/${yso}-tbc.ttl
./prote-to-tbc.py ${3}/${domain}.prop ${4}/${domain}-ontorip.ttl ${4}/${domain}-tbc.ttl

# Adding the baseURI definition that TBC requires
line=`grep baseuri ${3}/yso.prop`
baseuri=${line##*=}
./add_baseuri.py  ${4}/${yso}-tbc.ttl $baseuri > ${4}/${yso}.ttl

line=`grep baseuri ${3}/yso.prop`
baseuri=${line##*=}
./add_baseuri.py  ${4}/${domain}-tbc.ttl $baseuri > ${4}/${domain}.ttl


# Removes temp files
rm -f ${4}/${yso}-ontorip.ttl ${4}/${domain}-ontorip.ttl ${4}/${yso}-tbc.ttl ${4}/${domain}-tbc.ttl
