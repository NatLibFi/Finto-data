## Fiktiivisen aineiston ontologia KAUNO

### Päivitysprosessi
0. Voit muuntaa RDF-tiedostot yhdenmuotoisiksi helpompaa vertailua varten rapper-työkalulla ("Raptor RDF syntax parsing and serializing utility") komennolla `rapper -i turtle -o turtle $TIEDOSTO > tmp.ttl && mv tmp.ttl $TIEDOSTO`
1. Aja purify.sh
2. Aja Deprekaattori KAUNOlle
3. Siirrä deprekaattorin tuottama tiedosto toskos.sh:n lähtötiedostoksi ja aja se rapper-työkalun läpi
4. Aja toskos.sh

(24.9.2021) Seuraavat toimenpiteet ovat voimassa vain sinne asti kunnes saadaan sanastoylläpitäjältä seuraava kehitystiedosto, johon faceteista puuttuvat käsitteet tulee lisätä skos:memeber-suhteella. Tämän jälkeen nyt mainitut toimenpiteet voi jättää tekemättä, mikäli sanastoylläpitäjä on ohjeistettu lisäämään käsitteet vastaisuudessa myös facetteihin.

5. Aja ./add_concepts_to_facets.py kauno-skos.ttl replace_kauno-skos.ttl_with_this_$(date +%F)_$(date +%R).ttl
6. Tarkista, että `replace_kauno-skos.ttl_with_this_päivämäärä_kellonaika.ttl` on oikeellinen ja sopiva julkaisutiedostoksi
7. Ylikirjoita tiedosto `kauno-skos.ttl` tiedostolla `replace_kauno-skos.ttl_with_this_päivämäärä_kellonaika.ttl`
