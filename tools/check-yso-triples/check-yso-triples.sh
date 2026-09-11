#!/bin/bash

# Pitää varmistaa, että putkitetuissa komennoissa kaikkien osien virheistä tulee virheellinen exit-koodi (esim. curl | jq)
set -o pipefail

COUNTFILE=/srv/Finto-data/tools/check-yso-triples/yso-triple-count.txt
LOG=/srv/Finto-data/tools/check-yso-triples/check-yso-triples.log

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG"
}

count_ttl() {
    rapper -q -i turtle "$1" 2>/dev/null | wc -l
}

graphdb_count() {
    # Hyvä selventää curlauksen argumentteja, jos eivät ole tulleet usein vastaan:
    # f = palauttaa http-virhekoodin, s = silent eli ei näytä "progressiopalkkia", S-flagistä huolimatta näyttää virheet, G = GET-request
    curl -fsSG \
      -H 'Accept: application/sparql-results+json' \
      --data-urlencode 'query=SELECT (COUNT(*) AS ?c) WHERE {
          GRAPH <http://www.yso.fi/onto/yso/> { ?s ?p ?o }
      }' \
      'https://graphdb-dev.finto.fi/repositories/YSO_core' \
    | jq -r '.results.bindings[0].c.value'
}

current=$(graphdb_count)

if [ $? -ne 0 ]; then
    log "VIRHE: GraphDB:n triplemäärän haku epäonnistui"
    exit 1
fi

# PUT
# Jos kutsussa on argumentti, verrataan lähetettävän sanastoätiedoston triplemäärää GraphDB:n YSO-datan nykyiseen määrään.
if [ -n "$1" ]; then
    new=$(count_ttl "$1")

    if [ $((new * 1000)) -lt $((current * 999)) ]; then
        log "VIRHE: PUT estettiin: GraphDB=$current, vertailutiedosto=$new"
        exit 1
    fi

    log "PUT-tarkistus OK: GraphDB=$current, tiedosto=$new"
    exit 0
fi

if [ ! -f "$COUNTFILE" ]; then
    echo "$current" > "$COUNTFILE"
    exit 0
fi

old=$(cat "$COUNTFILE")

# GET
if [ $((current * 1000)) -lt $((old * 999)) ]; then
    log "VIRHE: GET estettiin: edellinen=$old, nykyinen=$current"
    exit 1
fi

log "GET-tarkistus OK: edellinen=$old, nykyinen=$current"

echo "$current" > "$COUNTFILE"
exit 0