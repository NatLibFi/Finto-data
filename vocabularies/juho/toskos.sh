#!/bin/sh

set -e

# Vaihda tähän oma Python3-virtuaaliympäristösi, jossa on asennettuna skosify.
# Mikäli se puuttuu, asenna se pip:illä käyttäen komentoa:
# pip install skosify
. ~/codes/venvs/forthree/bin/activate

# Tämä vaihe eli yson irrottaminen (periaatteessa) edellyttää, että olet ensin ajanut skriptin juho-vb-deprecator.sh (löytyy toolseista), joka tuottaa tiedoston juho-vb-deprecator-out.ttl.
# arq on Apache Jena -työkalu, muuta sen käynnistys työskentely-ympäristössäsi käyttämäsi tavan mukaiseksi.
# Huomaa, että juho-vb-deprecator-out.ttl on käytettävissä vain jos deprekointivaiheessa oli deprekoitava. Mikäli deprekoitavaa ei ollut,
# tulee arq:n syötetiedostoksi määritellä juho-vb-dump.ttl.
EXTRACTABLE="juho-vb-deprecator-out.ttl" # tai juho-vb-dump.ttl
arq --data $EXTRACTABLE --query extract-juho.rq > juho-irrotettu.ttl

INFILES="juho-metadata.ttl juho-singular.ttl juho-irrotettu.ttl ../yso/releases/2026.3.Maimonides/yso-skos.ttl"
OUTFILE="./juho-skos-vb.ttl"
TMPFILE="./juho-skos-vb-tmp.ttl"

SKOSIFYCMD=skosify
LOGFILE=skosify.log
OPTS="-l fi"

echo "Ajetaan skosify konfiksella juho-vb.cfg..."
$SKOSIFYCMD $OPTS -c ../../conf/skosify/juho-vb.cfg -o $OUTFILE $INFILES 2>$LOGFILE
