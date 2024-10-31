import requests
import json
import sys

entity_uri = sys.argv[1]
property_uri = sys.argv[2]

entity_id = entity_uri.split("/")[-1]
property_id = property_uri.split("/")[-1]

url = "https://www.wikidata.org/w/api.php"
params = {
    "action": "query",
    "titles": entity_id,
    "prop": "revisions",
    "rvprop": "timestamp|user|comment",
    "rvlimit": "500",
    "format": "json"
}

response = requests.get(url, params=params)
data = response.json()

print('***********')
print(data)
print('***********')
print('***********')
print('***********')

page = next(iter(data["query"]["pages"].values()))
revisions = page.get("revisions", [])

# Täytyy ehdottomasti tarkentaa, että mitä tietoja käyttäjien editoinneista tarvitaan
# ja lisäksi se, miten tietoja halutaan katsella, vaikuttaa alla olevan for-loopin
# printtaamien tietojen esitystapaan

for rev in revisions:
    if property_id in rev.get("comment", ""):
        print(f"User: {rev['user']}, Timestamp: {rev['timestamp']}, Comment: {rev['comment']}")

