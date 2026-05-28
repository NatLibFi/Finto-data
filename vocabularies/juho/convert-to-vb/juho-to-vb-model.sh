#!/bin/bash
set -euo pipefail
UPDATE='/home/mijuahon/Softs/apache-jena-5.6.0/bin/update'

if [ "$#" -ne 3 ]; then
    echo "Käyttö: $0 <input.ttl> <update.rq> <output.ttl>"
    echo "Esim: ./juho-to-vb-model.sh ../juho.ttl ./remove_asiasanalaji.rq juho-asiasanalaji-removed.ttl"
    echo "Tämä ./remove_asiasanalaji.rq on aina pakollinen"
    exit 1
fi

echo "Poistetaan juho-meta:hasAsiasanalaji"
$UPDATE --data "$1" --update "$2" --dump > "$3"

echo "juho-meta:hasAsiasanalaji poistettu ja päivitetty data tiedostossa $3."

IMPORT_FOR_HASLAHDE=$3
HASLAHDE=./remove_hasLahde.rq
HASLAHDE_REMOVED="./juho-haslahde-removed.ttl"
echo "Poistetaan juho-meta:hasLahde"
$UPDATE --data "$IMPORT_FOR_HASLAHDE" --update "$HASLAHDE" --dump > "$HASLAHDE_REMOVED"

echo "juho-meta:hasLahde poistettu ja päivitetty data tiedostossa $HASLAHDE_REMOVED."
