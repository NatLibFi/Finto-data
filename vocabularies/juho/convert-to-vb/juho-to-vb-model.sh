#!/bin/bash
set -euo pipefail
UPDATE='apache-jena-5.6.0/bin/update'

if [ "$#" -ne 3 ]; then
    echo "Käyttö: $0 <input.ttl> <update.rq> <output.ttl>"
    echo "Esim: ./juho-to-vb-model.sh ../juho.ttl ./remove_asiasanalaji.rq juho-asiasanalaji-removed.ttl"
    echo "Tämä ./remove_asiasanalaji.rq on aina pakollinen"
    exit 1
fi

# ../juho.ttl
ORIG_VOC="$1"
# ./remove_asiasanalaji.rq
THE_FIRST_SCRIPT="$2"
# ./juho-asiasanalaji-removed.ttl
ASIASANALAJI_REMOVED="$3"
echo "Poistetaan juho-meta:hasAsiasanalaji"
$UPDATE --data "$ORIG_VOC" --update "$THE_FIRST_SCRIPT" --dump > "$ASIASANALAJI_REMOVED"
echo "juho-meta:hasAsiasanalaji poistettu ja päivitetty data tiedostossa $ASIASANALAJI_REMOVED."

IMPORT_FOR_HASLAHDE=$ASIASANALAJI_REMOVED
HASLAHDE_RQ="./remove_hasLahde.rq"
HASLAHDE_REMOVED="./juho-haslahde-removed.ttl"
echo "Poistetaan juho-meta:hasLahde"
$UPDATE --data "$IMPORT_FOR_HASLAHDE" --update "$HASLAHDE_RQ" --dump > "$HASLAHDE_REMOVED"
echo "juho-meta:hasLahde poistettu ja päivitetty data tiedostossa $HASLAHDE_REMOVED."

IMPORT_FOR_HAS_PAIVITETTY=$HASLAHDE_REMOVED
HASPAIVITETTY_RQ='./copy_hasPaivitetty_to_skos_editorial_note_and_remove_hasPaivitetty.rq'
HASPAIVITETTY_REMOVED_AND_COPIED_TO_NOTE='./juho-hasPaivitetty-removed-and-note-added.ttl'
echo "Poistetaan juho-meta:hasPaivitetty ja kopioidaan arvot editorialNoteihin"
$UPDATE --data "$IMPORT_FOR_HAS_PAIVITETTY" --update "$HASPAIVITETTY_RQ" --dump > "$HASPAIVITETTY_REMOVED_AND_COPIED_TO_NOTE"
echo "Juho-meta:hasPaivitetty poistettu ja arvot kopioitu editorialNoteihin $HASPAIVITETTY_REMOVED_AND_COPIED_TO_NOTE."
