#!/bin/sh

DATADIR=/srv/Finto-data

dir=$DATADIR/vocabularies/kassu
file=kassu-skos.new.ttl

cd $dir

wget -O "$file" 'http://onki.fi/fi/browser/downloadfile/kassu?o=http%3A%2F%2Fwww.yso.fi%2Fonto%2Fkassu&f=kassu%2Fkassu-skos.ttl' >$dir/wget.out 2>$dir/wget.err

SANITYCHECK=/srv/Finto-data/tools/sanity-check/skos-sanity-check.sh
if $SANITYCHECK $dir/$file 1000000 100000 finto-kehitys-botit-aaaaayvdicfloosw2xeqkvlmry@kansalliskirjasto.slack.com; then
    git pull
    mv "$file" kassu-skos.ttl
    git commit -m "automaattipäivitys: kassu" kassu-skos.ttl
    git push
fi
