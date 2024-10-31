### Curlaaminen ja sen jälkeen greppailu yms on mahdollista
curl "https://www.wikidata.org/w/api.php?action=query&titles=Q50000&prop=revisions&rvprop=timestamp|user|comment&rvlimit=500&format=json"

### Kauniimpaa ja hallitumpaa lienee kuitenkin tehdä temppu pythonilla
python get_entity_and_property_metadata.py http://www.wikidata.org/entity/Q1380395 https://www.wikidata.org/wiki/Property:P2347
