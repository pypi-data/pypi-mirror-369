import requests
from bs4 import BeautifulSoup
from difflib import get_close_matches

def view_cultures(keyword):
    url = "https://culturovaultignicion.pythonanywhere.com/view"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    for card in soup.select(".card"):
        title = card.select_one(".title").get_text(strip=True)
        desc = card.select_one(".description").get_text(strip=True)
        if keyword.lower() in title.lower() or keyword.lower() in desc.lower():
            items.append((title, desc))

    if not items:
        print("No direct match found, searching similar...")
        all_titles = [card.select_one(".title").get_text(strip=True) for card in soup.select(".card")]
        matches = get_close_matches(keyword, all_titles, n=5, cutoff=0.4)
        for m in matches:
            print(f"🔍 Similar: {m}")
    else:
        for title, desc in items:
            print(f"🎭 {title}: {desc}")
