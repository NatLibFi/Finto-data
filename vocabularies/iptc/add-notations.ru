PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

INSERT {
  ?c skos:notation ?n .
} WHERE {
  ?c a skos:Concept .
  # extract local name from concept URI
  BIND(REPLACE(STR(?c), '^.*/', '') AS ?n)
}
