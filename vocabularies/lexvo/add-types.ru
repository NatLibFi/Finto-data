PREFIX lvont: <http://lexvo.org/ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

INSERT {
  ?c a lvont:Language, skos:Concept .
} WHERE {
  ?c lvont:iso6392BCode ?code .
}
