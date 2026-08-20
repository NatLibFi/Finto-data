EKSO – Eduskunnan kirjaston ontologia julkaisu paketin kuvaus

HUOM!! 
Tämän julkaisun erottaa muista kaksiportainen temaattinen ryhmittely. Tämän takia julkaisussa käytettystä YSOsta on poistettu temaattiset ryhmät. Lisäksi Skosifiointi ei rakenna oikein temaattisten ryhmien skos:member suhteita ja tästä syystä ne on jouduttu korjaamaan manuaalisesti skosifioituun versioon!!!


Työ tiedosto:
1 ekso-meta.ttl - TBC työtiedoston metadata määrittelyt
2 ekso.ttl - TBC työtiedosto
3 ysoKehitys-2025.2-Kant.ttl - TBC YSO

Julkaisu tiedostot:
1 toSkos.sh - skripti julkaisun tekemiseksi
1 ekso_julkaisu.ttl - Skosifioitava julkaisu versio josta on karsittu poistettavat käsitteet.
2 ekso-meta_publish.ttl - Julkaisuun liittyvä metadata
3 ysoKehitys-2025.2-Kant_thematicGroupsRemoved.ttl - Julkaisussa käytetty YSO josta on poistettu Temaattiset Ryhmät
4 ekso-skos.ttl - Skosifioitu julkaisu versio
5 ekso-skos-thematic-groups-corrected.ttl - Korjattu julkaistava versio 


	
Lisätty finnonto.cfg tiedostoon:

eksometa=http://www.yso.fi/onto/ekso-meta/

eksometa.Concept=eksometa:Concept,skos:Concept
eksometa.Hierarchy=skos:Concept,eksometa:Hierarchy

# EKSO properties
eksometa.source=
eksometa.dt=
eksometa.date= 
eksometa.status=
eksometa.cu=
eksometa.type=



SKOSMOS - configuraatio (!käytetty testauksessa!)

:ekso a skosmos:Vocabulary, void:Dataset ;
	dc:title "EKSO – Eduskunnan kirjaston ontologia"@fi,
		"EKSO – Riksdagsbibliotekets ontologi"@sv,
		"EKSO – The Library of Parliament's ontology"@en ;
	dc:subject :cat_general ;
	void:uriSpace "http://www.yso.fi/onto/ekso/";
	skosmos:language "fi", "sv", "en";
	skosmos:defaultLanguage "fi";
	skosmos:useModifiedDate "true";
	skosmos:shortName "EKSO";
	skosmos:marcSourceCode "ekso";
#	skosmos:feedbackRecipient "somename@eduskunta.fi";
	skosmos:indexShowClass <http://www.yso.fi/onto/ekso-meta/Concept>;
	skosmos:indexShowClass <http://www.yso.fi/onto/ekso-meta/Hierarchy>;
	skosmos:groupClass isothes:ConceptGroup ;
	skosmos:arrayClass isothes:ThesaurusArray ;
	skosmos:showTopConcepts "true" ;
#	void:dataDump <http://api.finto.fi/download/maotao/maotao-skos.ttl> ;
#	void:dataDump <http://api.finto.fi/download/maotao/maotao-skos.rdf> ;
#	void:sparqlEndpoint <http://api.finto.fi/sparql> ;

	void:sparqlEndpoint <http://localhost:3030/skosmos/sparql> ;
	skosmos:sparqlGraph <http://www.yso.fi/onto/ekso/> ;
	skosmos:mainConceptScheme <http://www.yso.fi/onto/ekso/> .
