TERO
====

Terveyden ja hyvinvoinnin ontologia (Tero) on YSO-pohjainen erikoisontologia, joka on mukana ontologiapilvi KOKOssa. TEROn erikoispiirre on että sen luonnissa yhdistettiin useissa sanastoissa olevia samoja käsitteitä yhdeksi kokoavaksi TERO-käsitteeksi. Näiden käsitteiden alkuperäislähde on näkyvillä käsitteen rdf:type ominaisuuden arvossa. Näiden käsitteiden URIen loppuosat viittaavat myös käsitteen alkuperäislähteeseen.

### TERO-YSO tuplakäsitteiden poisto 2017

TEROsta poistettiin loppuvuonna 2017 sellaiset TERO-käsitteet, jotka oli muodostettu suoraan YSO-käsite kopioimalla. Näille käsitteille luotiin tässä yhteydessä dct:isReplacedBy -triplet, jotka on nyt eriytetty omaan tiedostoonsa tero-yso-replacedby.ttl. Tämä erottelu tehtiin, jotta termieditori ei kadottaisi tietoa näistä suhteista.
