#!/bin/bash

YEAR="2024"
REPO_PATH="/codes/Finto-data/"
FILE_PATH="vocabularies/yso/yso-skos.ttl"
LAST_DATE="2024-12-31"
FIRST_DATE="2024-01-01"
OUTPUT_LAST="the-last.ttl"
OUTPUT_FIRST="the-first.ttl"
ARQ_PATH="/Softs/SPARQL/apache-jena-4.5.0/bin/arq"
QUERY_FILE="query-for-changed-alt-labels.rq"
COMBINE_SCRIPT="combine_ttl_to_trig.py"
RESULT_FILE="all-altlabels.result"

echo "Fetching the last version of YSO for the $YEAR"
last_commit=$(git -C $REPO_PATH log --since="$FIRST_DATE" --until="$LAST_DATE" --pretty=format:"%H" -- $FILE_PATH | head -n 1)
git -C $REPO_PATH show $last_commit:$FILE_PATH > $OUTPUT_LAST

echo "Fetching the first version of YSO for the $YEAR"
first_commit=$(git -C $REPO_PATH log --since="$FIRST_DATE" --until="$LAST_DATE" --reverse --pretty=format:"%H" -- $FILE_PATH | head -n 1)
git -C $REPO_PATH show $first_commit:$FILE_PATH > $OUTPUT_FIRST


echo "Combining the last and first versions into a single Trig file"
python $COMBINE_SCRIPT

echo "Running SPARQL query to find changed altLabels"
$ARQ_PATH --data combined.trig --query $QUERY_FILE > $RESULT_FILE

echo "Label counts by language for the $YEAR:"
echo "Swedish (sv): $(grep @sv $RESULT_FILE | wc -l)"
echo "Finnish (fi): $(grep @fi $RESULT_FILE | wc -l)"
echo "Northern Sami (se): $(grep @se $RESULT_FILE | wc -l)"
echo "English (en): $(grep @en $RESULT_FILE | wc -l)"
