import requests

OPENALEX_API_URL = "https://api.openalex.org/works"

def fetch_latest_research_papers(query="gender equality", per_page=15):
    """
    Fetch the latest research papers on gender equality from OpenAlex.

    :param query: Search query for papers.
    :param per_page: Number of papers to fetch.
    :return: A list of dictionaries with detailed paper information.
    """
    url = f"{OPENALEX_API_URL}?search={query}&sort=publication_date:desc&per-page={per_page}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        papers = []
        for item in data.get("results", []):
           
            # Extract top concepts based on score
            concepts = sorted(item.get("concepts", []), key=lambda c: c.get("score", 0), reverse=True)
            top_concepts = [concept.get("display_name", "General") for concept in concepts[:3]]

            paper = {
                "id": item.get("id", "N/A"),
                "title": item.get("display_name", "No Title Available"),
                "authors": ", ".join([auth['author']['display_name'] for auth in item.get("authorships", [])]),
                "publication_date": item.get("publication_date", "N/A"),
                "license": item.get("license", {}).get("url", None),
                "open_access": item.get("open_access", {}).get("is_oa", False),
                "link": item.get("primary_location", {}).get("landing_page_url", "#"),
                "categories": top_concepts
            }
            papers.append(paper)
        return papers
    return []

