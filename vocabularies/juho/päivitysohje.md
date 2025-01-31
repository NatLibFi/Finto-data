### Poista ylimääräinen ConceptScheme

Muuta julkaistavassa tiedostossa (juho-skos.ttl) yson määrittelyä siten, että poistat skos:ConceptSchemen. Skosify ei tykkää kahdesta skeemasta. Etsi myöhemmin kohta Skosifyn confiksesta, jossa asian voi muuttaam jottei tarvitse aina tehdä tätä "turhaa" vaihetta. Ilman muutosta hierarkiassa näkyy erikseen yson määrittely

Väärin!
`yso: a owl:Ontology,
        skos:ConceptScheme ;`

Oikein

`yso: a owl:Ontology ;`

### Liitetty yso

2025-01-31 yso-taso on Jung

### Päivitys
- validointi
- puritus
- deprekointi
- skossaus
- lokaali testaus
- julkaisu

