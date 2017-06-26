
Muutettu finnonto.cfg tiedostoon:


oikometa=http://www.yso.fi/onto/oiko-meta/
oikometa.Concept=oikometa:Concept,skos:Concept
oikometa.Hierarchy=oikometa:Hierarchy,skos:Concept
oikometa.deprecatedLabel=oikometa.deprecatedLabel
skos.editorialNote=


Muutettu SKOSMOS vocabularies.ttl

:oiko a skosmos:Vocabulary, void:Dataset ;
	dc:title "OIKO - Oikeushallinnon ontologia"@fi ;
	void:uriSpace "http://www.yso.fi/onto/oiko/";
	skosmos:language "fi";
	skosmos:defaultLanguage "fi";
	skosmos:shortName "OIKO";
	skosmos:arrayClass isothes:ThesaurusArray ;
	skosmos:showTopConcepts "true";
	skosmos:indexShowClass <http://www.yso.fi/onto/oiko-meta/Concept>, isothes:ThesaurusArray ;
        skosmos:hasMultiLingualProperty <http://www.yso.fi/onto/oiko-meta/deprecatedLabel> ;
	skosmos:sparqlGraph <http://www.yso.fi/onto/oiko/> ;
	skosmos:mainConceptScheme <http://www.yso.fi/onto/oiko/> .
