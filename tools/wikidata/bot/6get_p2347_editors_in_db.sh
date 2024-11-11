#!/bin/bash

DB="wikidata_bot.db"
SOURCE_TABLE="wd_yso_links"
TARGET_TABLE="p2347_editors_in_wd"
DELAY=0.5

sqlite3 "$DB" <<EOF
DROP TABLE IF EXISTS $TARGET_TABLE;
CREATE TABLE $TARGET_TABLE (
    wd_entity_uri TEXT,
    latest_p2347_editor TEXT
);
EOF

echo "## Kerätään Wikidata-entityiden URIt tietokannasta"
uris=$(sqlite3 "$DB" "SELECT wd_entity_uri FROM $SOURCE_TABLE;")

for wd_entity_uri in $uris; do
    echo "# Wikidata uri $wd_entity_uri haettu tietokannasta"
    entity_id="${wd_entity_uri##*/}"
    rvcontinue=""
    latest_editor=""

    echo "## Haetaan käyttäjänimi (P2347) Wikidatasta"
    while [ -z "$latest_editor" ]; do
        if [ -z "$rvcontinue" ]; then
            response=$(curl -s -H "User-Agent: Finnish-National-Library-Finto-Team-Wikibot-testing" \
                "https://www.wikidata.org/w/api.php?action=query&titles=$entity_id&prop=revisions&rvprop=user|timestamp|comment&rvlimit=500&rvdir=older&format=json")
        else
            response=$(curl -s -H "User-Agent: Finnish-National-Library-Finto-Team-Wikibot-testing" \
                "https://www.wikidata.org/w/api.php?action=query&titles=$entity_id&prop=revisions&rvprop=user|timestamp|comment&rvlimit=500&rvdir=older&format=json&rvcontinue=$rvcontinue")
        fi

        if echo "$response" | jq -e '.query.pages[].revisions' >/dev/null 2>&1; then
            latest_editor=$(echo "$response" | jq -r \
                --arg property "P2347" \
                '.query.pages[].revisions[]? | select(.comment | test("\\[\\[Property:" + $property + "\\]\\]|" + $property)) | .user' | head -n 1)
        else
            echo "API response missing or malformed for entity $entity_id"
            echo "Raw API response: $response"
            latest_editor="None"
            break
        fi

        rvcontinue=$(echo "$response" | jq -r '.continue.rvcontinue // empty' 2>/dev/null)
        if [ -z "$rvcontinue" ] && [ -z "$latest_editor" ]; then
            latest_editor="None"
            echo "# Ei löydetty P2347-editoijaa entitylle $entity_id"
            break
        fi

        sleep $DELAY
    done

    if [ "$latest_editor" != "None" ]; then
        sqlite3 "$DB" <<EOF
INSERT INTO $TARGET_TABLE (wd_entity_uri, latest_p2347_editor) VALUES ('$wd_entity_uri', '$latest_editor');
EOF
        echo "# Käyttäjänimi $latest_editor tallennettu tietokantaan"
    fi
done
