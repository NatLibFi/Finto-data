#!/bin/bash

DB=$1

if [ -z "$DB" ] || [ ! -f "$DB" ]; then
    echo "Virhe: Tietokantaa $DB ei löydy"
    exit 1
fi

TIMESTAMP=$(date +"%Y-%m-%d-%H-%M")
BACKUP_FILE="${DB}-${TIMESTAMP}.gz"

gzip -c "$DB" > "$BACKUP_FILE"

if [ -f "$BACKUP_FILE" ] && gzip -t "$BACKUP_FILE" > /dev/null 2>&1; then
    echo "Tietokanta pakattu tiedostoon $BACKUP_FILE"
    rm "$DB"
    echo "Tietokanta $DB poistettiin"
else
    echo "Virhe: Pakkaus epäonnistui"
    exit 1
fi
