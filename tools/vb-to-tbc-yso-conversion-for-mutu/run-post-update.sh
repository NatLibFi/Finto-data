#!/usr/bin/env bash
set -euo pipefail

# ./run-post-update.sh ./[new yso] converted-yso.rdf


OLD_FILE="old-yso-202506-tbc.ttl"
NEW_FILE="$1"
OUT_FILE="ysoKehitysTempTBC.rdf"
FINAL_OUTPUT="ysoKehitysTBC.rdf"

echo "Muunnetaan VB-versio TBC:n tietomallin mukaiseksi"
python3 "./convert_vb_yso_to_tbc_yso.py" --old "$OLD_FILE" --new "$NEW_FILE" --out "$OUT_FILE"

echo "Ajetaan jälkikorjaukset"
python3 "./post-update.py" --input "$OUT_FILE" --output "$FINAL_OUTPUT"

echo "Luotiin tiedosto ysoKehitysTBC.rdf"
