import requests
from bs4 import BeautifulSoup
import re
import time
import os

CANTONS = [
    "aargau", "appenzell-ausserrhoden", "appenzell-innerrhoden", "basel-landschaft",
    "basel-stadt", "bern", "fribourg", "geneva", "glarus", "graubuenden", "jura", "lucerne",
    "neuchatel", "nidwalden", "obwalden", "schaffhausen", "schwyz", "solothurn", "st-gallen",
    "thurgau", "ticino", "uri", "valais", "vaud", "zug", "zurich"
]

def collect_canton_ids(canton_short, delay=12, max_pages=50):
    ids = set()
    for pn in range(1, max_pages+1):
        url = f"https://www.immoscout24.ch/en/real-estate/rent/canton-{canton_short}?pn={pn}"
        print(f"[{canton_short}] Fetching page {pn}: {url}")
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            print(f"[{canton_short}] Failed to fetch page {pn}, status code {resp.status_code}")
            break
        soup = BeautifulSoup(resp.text, "html.parser")
        count = 0
        for a in soup.find_all("a", href=True):
            m = re.match(r"/rent/(\d+)", a['href'])
            if m:
                id_ = m.group(1)
                if id_ not in ids:
                    ids.add(id_)
                    count += 1
        print(f"[{canton_short}] Page {pn}: found {count} new ids, total {len(ids)}")
        time.sleep(delay)
    return ids

if __name__ == "__main__":
    os.makedirs("ids", exist_ok=True)
    for canton in CANTONS:
        print(f"\n--- Scraping canton: {canton} ---\n")
        ids = collect_canton_ids(canton_short=canton)
        filename = os.path.join("ids", f"{canton}_ids.txt")
        with open(filename, "w") as f:
            for id_ in sorted(ids):
                f.write(id_ + "\n")
        print(f"[{canton}] Done! Total {len(ids)} unique listing IDs saved to {filename}\n")
