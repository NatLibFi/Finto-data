#!/bin/bash
set -euo pipefail
UPDATE='/apache-jena-5.6.0/bin/update'

if [ "$#" -ne 3 ]; then
    echo "Käyttö: $0 <input.ttl> <update.rq> <output.ttl>"
    exit 1
fi

echo "Poistetaan juho-meta:hasAsiasanalaji"
$UPDATE --data "$1" --update "$2" --dump > "$3"

echo "juho-meta:hasAsiasanalaji poistettu ja päivitetty data tiedostossa $3."