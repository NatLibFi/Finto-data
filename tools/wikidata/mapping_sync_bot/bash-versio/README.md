
Jotta saadaan ensin kaikki data Wikidatasta, koska sillä tavoin botin käyttö on sujuvampaa lokaaleilla tiedoilla. Pitää kuitenkin minimoida tietojen katoaminen

JSON: 
/opt/apache-jena-fuseki-4.6.1/bin/s-query --service=https://query.wikidata.org/sparql --query=get_normal_ranked.rq > normal_ranked_results.json

NT: 
/home/mijuahon/from-the-previous-machine/Softs/SPARQL/apache-jena-4.5.0/bin/rsparql --results NT --service https://query.wikidata.org/sparql --query all_as_rdf.rq | sort > all_as_rdf.nt

Conversion: 
~/from-the-previous-machine/Softs/SPARQL/apache-jena-4.5.0/bin/riot --output=turtle all_as_rdf.nt > all_as_rdf_coverted_from_nt.ttl

Ajo:

rsparql --results NT --service https://query.wikidata.org/sparql --query 5all_as_rdf.rq | sort > 5all_as_rdf.nt
python ./flatten_nt.py 5all_as_rdf.nt 5all_as_rdf_coverted_from_nt_and_grouped.ttl
