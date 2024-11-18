#!/bin/bash

RSPARQL=/Softs/SPARQL/apache-jena-4.5.0/bin/rsparql
RIOT=/Softs/SPARQL/apache-jena-4.5.0/bin/riot
ARQ=/Softs/SPARQL/apache-jena-4.5.0/bin/arq
DB=6wikidata.db
YSO_DEV=/home/mijuahon/codes/Finto-data/vocabularies/yso/ysoKehitys.rdf

echo "Fetching data from Wikidata"
$RSPARQL --results NT --service https://query.wikidata.org/sparql --query 6all_as_rdf.rq | sort > 6all_as_rdf.nt

./6dots.sh 5
python ./6flatten_nt.py 6all_as_rdf.nt 6all_as_rdf_coverted_from_nt_and_grouped.ttl

./6dots.sh 5
echo "Backing up and deleting the previous db"
./6backup-and-delete-db.sh $DB

./6dots.sh 5
echo "Creating the database"
./6create_db.sh $DB

./6dots.sh 5
echo "(Rankings in wd_main) Read the Wikidata source data and parse the entities and rankings and finally update the db)"
$RIOT --output=N-TRIPLES 6all_as_rdf_coverted_from_nt_and_grouped.ttl | grep "<http://wikiba.se/ontology#rank>" | awk '{gsub(/[<>]/, "", $1); gsub(/.*#/, "", $3); gsub(/>/, "", $3); print $1, $3}' | while read uri rank; do     sqlite3 6wikidata.db "INSERT OR REPLACE INTO wd_main (wd_entity_uri, wd_rank) VALUES ('$uri', '$rank');"; done

./6dots.sh 5
echo "The dates on the Wikidata side"
$ARQ --data=6all_as_rdf_coverted_from_nt_and_grouped.ttl --query=6get_wd_uris_and_dates.rq | sed 's/[|"]//g; s/^ *//; s/ *$//' | while read -r uri date; do sqlite3 6wikidata.db "INSERT INTO wd_dates_for_stated_in (wd_entity_uri, date) VALUES ('$uri', '$date');"; done

./6dots.sh 5
echo "yso-links from wikidata"
$ARQ --data=6all_as_rdf_coverted_from_nt_and_grouped.ttl --query=6get_yso_links_from_wikidata.rq | sed 's/wd:/http:\/\/www.wikidata.org\/entity\//g' | sed 's/yso:/http:\/\/www.yso.fi\/onto\/yso\/p/g' | awk -F 'p:P2347' '{
    gsub(/[<>[:space:]]+/, "", $1);
    entity = $1;
    split($2, yso_concepts, ",");
    for (i in yso_concepts) {
        gsub(/[<>[:space:]]+/, "", yso_concepts[i]);
        print entity "|" yso_concepts[i]
    }
}' > 6yso_links_from_wikidata.txt

./6dots.sh 3
sed 's/\.$//' 6yso_links_from_wikidata.txt > 6yso_links_from_wikidata_clean.txt

./6dots.sh 3
sqlite3 6wikidata.db <<EOF
.mode csv
.separator "|"
.import 6yso_links_from_wikidata_clean.txt wd_yso_links
EOF

./6dots.sh 3
echo "wikidata mapping from yso"
$ARQ --data=$YSO_DEV --query=6get_wikidata_links_from_yso.rq | sed 's/yso:/http:\/\/www.yso.fi\/onto\/yso\//g' | sed 's/ skos:closeMatch /|/g' | sed 's/[<>]//g' | awk -F '|' '{ 
    gsub(/[[:space:]]+$/, "", $1);    # Trailing spaces pois 
    yso_uri = $1;                     # YSO-uri-talteen
    split($2, objects, ",");          # Pilkkuerottelu
    for (i in objects) {
        gsub(/[[:space:]]+$/, "", objects[i]);    # Trailing spaces pois
        print yso_uri "|" objects[i] ".";         # Printataan tulos oikeassa formaatissa
    }
}' > 6wikidata_links_from_yso.txt

sed 's/|[[:space:]]*/|/g; s/[[:space:]]*\.\.$//; s/[[:space:]]*$//' 6wikidata_links_from_yso.txt > 6wikidata_links_from_yso_clean.txt

sqlite3 6wikidata.db <<EOF
.mode csv
.separator "|"
.import 6wikidata_links_from_yso_clean.txt yso_wd_links
EOF

./6dots.sh 3
echo "yso_main / deprecation status"
$ARQ --data=$YSO_DEV --query=6get_yso_main.rq | sed 's/yso:/http:\/\/www.yso.fi\/onto\/yso\//g; s/ ex:deprecationStatus /|/g; s/[.]$//' | awk 'NF {gsub(/"/, "", $3); gsub(/[ \t]+$/, "", $0); print $1 "|" $3}' > 6yso_main.txt

sed '/^@prefix/d' 6yso_main.txt > 6yso_main_clean.txt

sqlite3 6wikidata.db <<EOF
.mode csv
.separator "|"
.import 6yso_main_clean.txt yso_main
EOF

./6dots.sh 3
echo "On deprekoitu Wikidatassa mutta ei YSOssa"
echo "Luodaan raportti"
sqlite3 6wikidata.db "SELECT w.wd_entity_uri, y.yso_concept_uri
FROM wd_main w
JOIN wd_yso_links l ON w.wd_entity_uri = l.wd_entity_uri
JOIN yso_main y ON l.yso_concept_uri = y.yso_concept_uri
WHERE w.wd_rank = 'DeprecatedRank'
  AND y.is_deprecated = 'false';" | awk -F'|' '{print "<a href=\"" $1 "\" target=\"_blank\">" $1 "</a> -> <a href=\"" $2 "\" target=\"_blank\">" $2 "</a><br>"}' > 6deprecated_in_wikidata_but_not_in_yso.html 

./6dots.sh 3
echo "On deprekoitu YSOssa mutta ei Wikidatassa"
echo "Luodaan raportti"
sqlite3 6wikidata.db "SELECT y.yso_concept_uri, w.wd_entity_uri
FROM yso_main y
JOIN yso_wd_links l ON y.yso_concept_uri = l.yso_concept_uri
JOIN wd_main w ON l.wd_entity_uri = w.wd_entity_uri
WHERE y.is_deprecated = 'true'
  AND (w.wd_rank != 'DeprecatedRank' OR w.wd_rank IS NULL);" | awk -F'|' '{print "<a href=\"" $1 "\" target=\"_blank\">" $1 "</a> -> <a href=\"" $2 "\" target=\"_blank\">" $2 "</a><br>"}' > 6deprecated_in_yso_but_not_in_wikidata.html

./6dots.sh 5
echo "Getting the usernames that have been editing P2347"
./6get_p2347_editors_in_db.sh $DB

./6dots.sh 3
echo "On Wikidatassa mutta ei ysossa (luotettavien käyttäjien toteuttamana)"
echo "Luodaan raportti"
sqlite3 6wikidata.db "
SELECT w.wd_entity_uri, y.yso_concept_uri
FROM wd_yso_links l
JOIN wd_main w ON l.wd_entity_uri = w.wd_entity_uri
JOIN yso_main y ON l.yso_concept_uri = y.yso_concept_uri
JOIN p2347_editors_in_wd p ON p.wd_entity_uri = w.wd_entity_uri
WHERE w.wd_rank != 'DeprecatedRank'
  AND y.is_deprecated = 'false'
  AND NOT EXISTS (
      SELECT 1 
      FROM yso_wd_links yl 
      WHERE yl.yso_concept_uri = y.yso_concept_uri 
        AND yl.wd_entity_uri = w.wd_entity_uri
  )
  AND p.latest_p2347_editor IN ('YSObot', 'Saarik', 'Tpalonen', 'Tuomas_Palonen', 'Nikotapiopartanen', 'Osmasuominen');
" | awk -F'|' '{print "<a href=\"" $1 "\" target=\"_blank\">" $1 "</a> -> <a href=\"" $2 "\" target=\"_blank\">" $2 "</a><br>"}' > 6yso_link_in_wd_but_not_wd_link_in_yso.html

./6dots.sh 3
echo "On Wikidatassa mutta ei ysossa (luotettavien käyttäjien toteuttamana) -> NT-tiedosto"
echo "Luodaan NT-tiedosto"
sqlite3 6wikidata.db "
SELECT w.wd_entity_uri, y.yso_concept_uri
FROM wd_yso_links l
JOIN wd_main w ON l.wd_entity_uri = w.wd_entity_uri
JOIN yso_main y ON l.yso_concept_uri = y.yso_concept_uri
JOIN p2347_editors_in_wd p ON p.wd_entity_uri = w.wd_entity_uri
WHERE w.wd_rank != 'DeprecatedRank'
  AND y.is_deprecated = 'false'
  AND NOT EXISTS (
      SELECT 1 
      FROM yso_wd_links yl 
      WHERE yl.yso_concept_uri = y.yso_concept_uri 
        AND yl.wd_entity_uri = w.wd_entity_uri
  )
  AND p.latest_p2347_editor IN ('YSObot', 'Saarik', 'Tpalonen', 'Tuomas_Palonen', 'Nikotapiopartanen', 'Osmasuominen');
" | awk -F'|' '{print "<"$2">" " <http://www.w3.org/2004/02/skos/core#closeMatch> " "<"$1"> ."}' > 6yso_link_in_wd_but_not_wd_link_in_yso.nt

