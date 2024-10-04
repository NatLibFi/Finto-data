
Jotta saadaan ensin kaikki data Wikidatasta, koska sillä tavoin botin käyttö on sujuvampaa lokaaleilla tiedoilla. Pitää kuitenkin minimoida tietojen katoaminen

JSON: 
/opt/apache-jena-fuseki-4.6.1/bin/s-query --service=https://query.wikidata.org/sparql --query=get_normal_ranked.rq > normal_ranked_results.json

NT: 
/home/mijuahon/from-the-previous-machine/Softs/SPARQL/apache-jena-4.5.0/bin/rsparql --results NT --service https://query.wikidata.org/sparql --query all_as_rdf.rq | sort > all_as_rdf.nt

Conversion: 
~/from-the-previous-machine/Softs/SPARQL/apache-jena-4.5.0/bin/riot --output=turtle all_as_rdf.nt > all_as_rdf_coverted_from_nt.ttl

Prepare data for yso comparsion:
python ./prepare_data_for_comparsion.py 5all_as_rdf_coverted_from_nt_and_grouped.ttl ready-for-yso-comparsions.ttl

Ajo:

1
rsparql --results NT --service https://query.wikidata.org/sparql --query 5all_as_rdf.rq | sort > 5all_as_rdf.nt

2
python ./flatten_nt.py 5all_as_rdf.nt 5all_as_rdf_coverted_from_nt_and_grouped.ttl

3 (Tämä vaihe on mahdollisesti tarpeeton, tarkentuu hieman myöhemmin)
python ./prepare_data_for_comparsion.py 5all_as_rdf_coverted_from_nt_and_grouped.ttl ready-for-yso-comparsions.ttl
