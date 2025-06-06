#! /bin/bash

RDA_version=5.4.3
OUTPUTFILE=deprecated.txt
ZIPFILE=v$RDA_version.zip
TMP_FOLDER=RDA-Vocabularies-$RDA_version


echo -e "\nLadataan RDA $RDA_version ...\n"
wget https://github.com/RDARegistry/RDA-Vocabularies/archive/$ZIPFILE
unzip -q $ZIPFILE
echo -e "\nValmis. Etsitään deprekoidut resurssit...\n"
grep -h '<http://metadataregistry.org/uri/profile/regap/status> <http://metadataregistry.org/uri/RegStatus/1008>' $TMP_FOLDER/nt/Elements/*.nt | awk '{print $1}' > $OUTPUTFILE
rm -rf $ZIPFILE $TMP_FOLDER/


elementCount=$(wc -l $OUTPUTFILE | awk '{print $1}')
echo "Deprekoituja resursseja löytyi $elementCount kpl. Lista tulostettu $OUTPUTFILE"

python list-deprecated.py metatietosanasto-skos.ttl $OUTPUTFILE

