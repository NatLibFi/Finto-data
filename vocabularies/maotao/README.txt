Lisätty finnonto.cfg tiedostoon:

	maometa.kyConcept=maometa:Concept,skos:Concept


	  # TSK lisäys, ei yläkäsitettä jos on jo joku YSO yläkäsite  
	  FILTER NOT EXISTS 
	  { 
	    ?a rdfs:subClassOf+ ?anyYsoParent
	    FILTER (STRSTARTS(STR(?anyYsoParent), "http://www.yso.fi/onto/yso/"))
	  }
