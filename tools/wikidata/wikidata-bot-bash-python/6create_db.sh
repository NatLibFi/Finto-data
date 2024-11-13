#!/bin/bash

sqlite3 $1 <<EOF
CREATE TABLE IF NOT EXISTS "wd_dates_for_stated_in" (
    wd_entity_uri TEXT,
    date TEXT
);

CREATE TABLE IF NOT EXISTS "wd_yso_links" (
    wd_entity_uri TEXT,
    yso_concept_uri TEXT
);

CREATE TABLE IF NOT EXISTS "yso_wd_links" (
    yso_concept_uri TEXT,
    wd_entity_uri TEXT
);

CREATE TABLE IF NOT EXISTS "wd_main" (
    wd_entity_uri TEXT UNIQUE,     
    wd_rank TEXT
);

CREATE TABLE IF NOT EXISTS yso_main (
    yso_concept_uri TEXT UNIQUE,
    is_deprecated BOOLEAN
);

CREATE TABLE IF NOT EXISTS p2347_editors_in_wd (
    wd_entity_uri TEXT,
    latest_p2347_editor TEXT
);
EOF

echo "Database and tables created successfully."
