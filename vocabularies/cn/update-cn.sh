#!/bin/sh

CNLOGFILE=cn.log

./convert-cn-to-skos.py >cn.ttl 2>$CNLOGFILE
