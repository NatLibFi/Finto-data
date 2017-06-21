#!/bin/bash

CONF=configs/JUHO-deprecator-config.txt
INPUT=../../vocabularies/juho/juho.ttl
OUTPUT=juhoDeprecated.ttl
EMAILOUTPUT=email.txt
LOG=deprecator.log

ARGS="$INPUT $CONF $OUTPUT $EMAILOUTPUT"

java -Xmx4G -cp 'lib/*:.' GeneralDeprecator $ARGS 2>&1 | tee $LOG

