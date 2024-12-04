# NOT IMPLEMENTED FULLY. In a working state, though

import requests

DBPEDIA_SPARQL_URL = "https://dbpedia.org/sparql"

# SPARQL query to fetch Ukrainian gender equality activists
SPARQL_QUERY_ACTIVISTS = """
PREFIX dbc: <http://dbpedia.org/resource/Category:>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT ?activist ?name ?description WHERE {
  ?activist dct:subject dbc:Ukrainian_feminists ;
            foaf:name ?name ;
            dbo:abstract ?description .
  FILTER (lang(?description) = "en" && lang(?name) = "en")
}
LIMIT 10
"""

def fetch_ukrainian_gender_activists():
    """
    Fetches a list of Ukrainian gender equality activists from DBPedia.
    
    :return: List of dictionaries with activist data (name, link, description)
    """
    headers = {
        "Accept": "application/sparql-results+json"
    }
    response = requests.get(DBPEDIA_SPARQL_URL, headers=headers, params={"query": SPARQL_QUERY_ACTIVISTS})
    
    if response.status_code == 200:
        results = response.json()["results"]["bindings"]
        activists = []
        for result in results:
            activist_data = {
                "link": result['activist']['value'],
                "name": result['name']['value'],
                "description": result['description']['value']
            }
            activists.append(activist_data)
        return activists
    else:
        return None
