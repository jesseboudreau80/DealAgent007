
from serpapi import GoogleSearch
from typing import List

def search_disaster_history(location: str, serp_api_key: str) -> List[str]:
    params = {
        "engine": "google",
        "q": f"{location} flood history OR storm damage OR natural disasters site:.gov OR site:weather.com",
        "api_key": serp_api_key,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    links = []

    for result in results.get("organic_results", []):
        links.append(result.get("link", ""))

    return links[:5]  # return top 5 relevant links
