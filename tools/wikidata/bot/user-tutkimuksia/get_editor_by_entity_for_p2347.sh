#!/bin/bash

if [ -z "$1" ]; then
    echo "Käyttö: $0 <Wikidata-entiteetin URL>"
    exit 1
fi

entity_url="$1"
entity_id="${entity_url##*/}"

property_id="P2347"

response=$(curl -s "https://www.wikidata.org/w/api.php?action=query&titles=$entity_id&prop=revisions&rvprop=user|timestamp|comment&rvlimit=max&format=json")

# Etsitään viimeisin käyttäjä, joka editoi P2347-propertyn arvoja
last_user=$(echo "$response" | jq -r --arg property "$property_id" \
    '.query.pages[].revisions[] | select(.comment | test("\\[\\[Property:" + $property + "\\]\\]|" + $property)) | .user' | head -n 1)

if [ -n "$last_user" ]; then
    echo "Viimeisin käyttäjä, joka on editoinut propertyä $property_id entiteetille $entity_id oli: $last_user"
else
    echo "Ei editointeja annetulle propertylle $property_id koskien entiteettiä $entity_id."
fi

# Seuraava vaihe on sen tutkiminen aiemmin sparkkelilla kertätystä datasta, että onko tämän
# skriptin tulos oikein.
# Jos tulos on oikein, muutetaan outputia raportointia ja yso-automaatiota varten sopipaksi
# Esimerkkiajo:
# ./get_editor_by_entity_for_p2347.sh https://www.wikidata.org/wiki/Q314613


