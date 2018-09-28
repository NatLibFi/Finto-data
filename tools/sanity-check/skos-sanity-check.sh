#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "This script checks that the given SKOS file exists and contains at least the given number of triples and concepts."
    echo "If the check is succesful, the script exits normally (exit status 0)."
    echo "If the check fails, an e-mail is sent to the given address and the script exits with an error status."
    echo
    echo "Usage: $0 <skos-file> <min-triples> <min-concepts> <email>"
    echo
    exit 1
fi

skosfile=$1
mintriples=$2
minconcepts=$3
email=$4

state="OK"

if [ ! -f $skosfile ]; then
    state="Tiedostoa ei ole olemassa"
elif [ ! -s $skosfile ]; then
    state="Tiedosto on tyhjä"
else
    ext=${skosfile##*.}
    
    rappercmd="rapper -q"
    rapperflags=""
    if [ $ext = "ttl" ]; then
        rapperflags="-i turtle"
    elif [ $ext = "nt" ]; then
        rappercmd="cat"
    fi
    
    # check the number of triples
    triples=`$rappercmd $rapperflags $skosfile | wc -l`
    if [ $triples -lt $mintriples ]; then
        state="Liian vähän triplejä: löytyi $triples, kun pitäisi olla vähintään $mintriples"
    fi

    # check the number of concepts
    typepat=" <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#Concept>"
    concepts=`$rappercmd $rapperflags $skosfile | grep -c -F "$typepat"`
    if [ $concepts -lt $minconcepts ]; then
        state="Liian vähän käsitteitä: löytyi $concepts, kun pitäisi olla vähintään $minconcepts"
    fi
        
fi

if [ "$state" != "OK" ]; then
    echo -e "Ongelma tiedostossa $skosfile:\n$state.\n\nPäivitys keskeytetty." \
     | mail -s "Ongelma tiedostossa $skosfile" $email
    exit 1
fi
