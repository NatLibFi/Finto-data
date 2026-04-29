#!/bin/bash

# Aja komento sh create-release-version.sh Nimi
# (Anna nimi esim. muodossa Aristoteles)

# Tämä komentosarja tekee yson jäädytetyn version työvaiheet.
# Tarkista lopputulos ennen versionhallintaan tallennusta!
# joelitak 2026.04.29

# Tarkistetaan, että käyttäjä on antanut nimen parametrina

set -e

if [ $# -ne 1 ]; then
    echo "Käyttö: $0 Nimi"
    exit 1
fi

NIMI_PARAM="$1"

echo "Luodaan kansiorakenne..."

V=$(date +%Y)
K=$(date +%m | sed 's/^0//')
P=$(date +%d | sed 's/^0//')

Nimi=${NIMI_PARAM}
NIMI_UPPER=$(echo "$NIMI_PARAM" | tr '[:lower:]' '[:upper:]')
NIMI_LOWER=$(echo "$NIMI_PARAM" | tr '[:upper:]' '[:lower:]')

DIR=releases/${V}.${K}.${Nimi}
mkdir $DIR
cp ysoKehitys.rdf $DIR/.
cp yso-skos.ttl $DIR/.
cp ../yso-paikat/yso-paikat-vb-dump.rdf $DIR/yso-paikat.rdf
cp ../yso-paikat/yso-paikat-skos.ttl $DIR/.
cd $DIR

cat <<EOF > README.md
Tämä on Yleisen Suomalaisen Ontologian (YSO) julkaisu ${V}.${K}.${Nimi}. Nämä tiedostot kuvastavat YSOn tilaa ${P}. ${K}. ${V}. YSO-${Nimi} on erityisesti erikoisontologioiden kehittäjille suunnattu versio YSOsta. Tiedostot ysoKehitys.ttl ja ysoKehitys.rdf on optimoitu VocBench-editointityökalulla tapahtuvaa ontologiatyötä ajatellen. Nämä poikkeavat tietomalliltaan joiltain osin YSOn Fintosta löytyvästä julkaisuversiosta. YSOn kielimallien opettamiseen käytetty versio yso-combined sisältää yhdistelmän YSOn ja YSO-paikkojen julkaisuversioista. YSOn ${Nimi}-versio on sisällöltään "jäädytetty", eli siihen ei päivitetä YSOn julkaisuversiossa näkyviä jatkuvia muutoksia. Versio sisältää YSOn viimeisimmät sisällölliset uudistukset.
EOF

echo "Muodostetaan julkaisutiedostot..."

riot -formatted turtle yso-paikat.rdf > yso-paikat.ttl
riot -formatted turtle ysoKehitys.rdf > ysoKehitys.ttl
riot -out rdfxml-abbrev yso-skos.ttl yso-paikat-skos.ttl  > yso-combined.rdf
riot -formatted turtle yso-skos.ttl yso-paikat-skos.ttl  > yso-combined.ttl

echo -e "\nYSOn jäädytetty versio on luotu. Tarkista vielä tiedostot ennenkuin lisäät muutokset versionhallintaan. Voit lisätä vielä Skosmoksen config.ttl-tiedostoon seuraavan tietueen:\n"
cat <<EOF
:yso${Nimi} a skosmos:Vocabulary, void:Dataset ;
    dc:title "YSO - Yleinen suomalainen ontologia, ${Nimi}-versio"@fi,
        "ALLFO - Allmän finländsk ontologi, ${Nimi} version"@sv,
        "YSO - General Finnish ontology, ${Nimi} version"@en ;
    skosmos:shortName "${NIMI_UPPER}"@fi, "${NIMI_UPPER}"@sv, "${NIMI_UPPER}"@se, "${NIMI_UPPER}"@en;
    dc:subject :cat_general ;
    void:uriSpace "http://www.yso.fi/onto/yso/";
    skosmos:language "fi", "sv", "en", "se";
    skosmos:defaultLanguage "fi";
    skosmos:showTopConcepts "true";
    skosmos:groupClass isothes:ConceptGroup ;
    skosmos:arrayClass isothes:ThesaurusArray ;
    skosmos:showChangeList "true" ;
        skosmos:showPropertyInSearch skos:note ;
    skosmos:useModifiedDate "true";
    skosmos:usePlugin "finna" ;
    void:dataDump <https://dev.finto.fi/download/yso/releases/${V}.${K}.${Nimi}/yso-skos.ttl> ;
    void:dataDump <https://dev.finto.fi/download/yso/releases/${V}.${K}.${Nimi}/ysoKehitys.rdf> ;
    void:sparqlEndpoint <http://api.dev.finto.fi/sparql> ;
    skosmos:sparqlGraph <http://www.yso.fi/onto/yso-${NIMI_LOWER}/> ;
    skosmos:mainConceptScheme <http://www.yso.fi/onto/yso/> .

EOF
