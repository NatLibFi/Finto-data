#!/bin/bash

CONF=configs/YSO-deprecator-config.txt
INPUT=../../vocabularies/yso/ysoKehitys.rdf
OUTPUT=ysoKehitysDeprecated.rdf
EMAILOUTPUT=email.txt
LOG=deprecator-yso.log

ARGS="$INPUT $CONF $OUTPUT $EMAILOUTPUT"

java -Xmx4G -cp 'lib/*:.' GeneralDeprecator $ARGS 2>&1 | tee $LOG

