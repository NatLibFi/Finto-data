import requests
import csv

username = "YSObot"

url = "https://www.wikidata.org/w/api.php"
params = {
    "action": "query",
    "list": "usercontribs",
    "ucuser": username,
    "uclimit": "5000",
    "ucnamespace": "0",
    "format": "json"
}

contributions = []
while True:
    response = requests.get(url, params=params)
    data = response.json()
    contributions.extend(data.get("query", {}).get("usercontribs", []))
    if "continue" in data:
        params["uccontinue"] = data["continue"]["uccontinue"]
    else:
        break

with open("user_contributions.csv", mode="w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Wikidata URI", "Change Made", "Date"])

    for contrib in contributions:
        comment = contrib.get("comment", "")
        title = contrib.get("title", "")
        timestamp = contrib.get("timestamp", "")

        # Mieti vielä csv-tiedoston muotoa siitä näkökulmasta, että minkälainen lopulinen käyttö tulee olemaan
        if "P2347" in comment or "YSO ID" in comment:
            wikidata_uri = f"https://www.wikidata.org/wiki/{title}"
            csv_writer.writerow([wikidata_uri, comment, timestamp])

print("user_contributions.csv luotu")

