# Kokoelmien kuvailun aihealueet (Kokoelmakartta) -asennusmuistio

Tässä dokumentissa ei kuvata sanastoa, vaan sen ensijulkaisun vaiheet viitetiedoksi teknisille henkilöille eli tämä on asennusmuistio.

## Julkaisukansio:

_Finto-data/vocabularies/kkaa_

## Validointi
```riot --validate kkaa-skos.ttl```

_10:49:00 ERROR riot            :: [line: 82, col: 61] Bad character in IRI (space): <http://urn.fi/URN:NBN:fi:au:ykl:56[space]...>_

- Korjattu, nyt ok

## Config.ttl:

```
:kkaa a skosmos:Vocabulary, void:Dataset ;
    dc:title "Topics for Collection Description (Collection Map)"@en,
        "Kokoelmien kuvailun aihealueet (Kokoelmakartta)"@fi,
        "Kompkarta områden"@sv ;
        skosmos:shortName "KKAA" ;
        dct:subject :cat_general ;
        void:uriSpace "http://urn.fi/URN:NBN:fi:au:kkaa:";
    	skosmos:language "fi", "sv", "en";
        skosmos:defaultLanguage "fi";
        skosmos:useModifiedDate "true";
        skosmos:showChangeList "false";
    	skosmos:showTopConcepts "true";
        skosmos:sortByNotation "lexical" ;
        skosmos:searchByNotation true ;
        skosmos:sortByNotation "lexical" ;
        skosmos:alphabeticalListQualifier skos:notation ;
        skosmos:fullAlphabeticalIndex "true";
        skosmos:defaultSidebarView "hierarchy";
        #skosmos:feedbackRecipient "xyz@helsinki.fi";
        void:dataDump <https://dev.finto.fi/download/kkaa/kkaa-skos.ttl> ;
        void:dataDump <https://dev.finto.fi/download/kkaa/kkaa-skos.rdf> ;
        void:sparqlEndpoint <http://api.finto.fi/sparql> ; 
        skosmos:sparqlGraph <http://urn.fi/URN:NBN:fi:au:kkaa:> ;
        skosmos:mainConceptScheme <http://urn.fi/URN:NBN:fi:au:kkaa:> .   
```

_riot --validate /Finto-data/conf/dev.finto.fi/config.ttl_

ok

    foaf:homepage <https://web.archive.org/web/20120107015151/>,
        <https://varastokirjasto.fi/kokoelmakartta/> .

-->

    foaf:homepage <https://www.kiwi.fi/display/Finto/KKAA+-Kokoelmien+kuvailun+aihealueet> .