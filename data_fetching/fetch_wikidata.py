import requests

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

# SPARQL query to count streets and buildings named after women and men
SPARQL_QUERY_GENDER_COUNTS = """
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX bd: <http://www.bigdata.com/rdf#>

SELECT ?genderLabel (COUNT(DISTINCT ?item) AS ?count) WHERE {
  ?item wdt:P31/wdt:P279* ?class .
  VALUES ?superclass { wd:Q83620 wd:Q41176 }  # Streets, buildings, etc.
  ?class wdt:P279* ?superclass .
  ?item wdt:P17 wd:Q212 .
  ?item p:P138 ?statement .
  ?statement ps:P138 ?namedAfter .
  OPTIONAL { ?statement pq:P580 ?startTime . }
  OPTIONAL { ?statement pq:P582 ?endTime . }
  FILTER (
    ( !BOUND(?startTime) || ?startTime <= NOW() ) &&
    ( !BOUND(?endTime) || ?endTime > NOW() )
  )
  ?namedAfter wdt:P21 ?gender .
  VALUES ?gender { wd:Q6581097 wd:Q6581072 }  # Male, Female
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
GROUP BY ?genderLabel
ORDER BY ?genderLabel
"""

def fetch_gender_named_counts():
    """
    Fetch counts of streets and buildings in Ukraine named after women and men from Wikidata.
    
    :return: Dictionary with gender labels as keys and their counts as values.
    """
    headers = {"Accept": "application/json"}
    response = requests.get(WIKIDATA_SPARQL_URL, headers=headers, params={"query": SPARQL_QUERY_GENDER_COUNTS})
    
    if response.status_code == 200:
        results = response.json()["results"]["bindings"]
        counts = {result["genderLabel"]["value"]: int(result["count"]["value"]) for result in results}
        print(counts)
        return counts
    else:
        raise Exception(f"Failed to fetch data from Wikidata: {response.status_code}")
