## Fiktiivisen aineiston ontologia KAUNO

# Päivitysprosessi
0. Voit muuttaa RDF-tiedostot yhdenmuotoisiksi helpompaa vertailua varten rapper-työkalulla ("Raptor RDF syntax parsing and serializing utility") komennolla `rapper -i turtle -o turtle $TIEDOSTO > tmp.ttl && mv tmp.ttl $TIEDOSTO`
1. Aja purify.sh
2. Aja Deprekaattori KAUNOlle
3. Siirrä deprekaattorin tuottama tiedosto toskos.sh:n lähtötiedostoksi ja aja se rapper-työkalun läpi
4. Aja toskos.sh 
