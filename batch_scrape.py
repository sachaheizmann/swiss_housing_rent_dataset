import os
import csv
import time
import traceback
from extract_features import extract_listing_features  # <-- Adjust this if needed

CANTONS = [
    "aargau", "appenzell-ausserrhoden", "appenzell-innerrhoden", "basel-landschaft",
    "basel-stadt", "bern", "fribourg", "geneva", "glarus", "graubuenden", "jura", "lucerne",
    "neuchatel", "nidwalden", "obwalden", "schaffhausen", "schwyz", "solothurn", "st-gallen",
    "thurgau", "ticino", "uri", "valais", "vaud", "zug", "zurich"
]

FIELDNAMES = [
    "id", "street", "city_postal", "rooms", "living_space", "price",
    "avg_travel_time", "type", "last_refurbishment", "year_built", "balcony_or_terrace"
]
IDS_FOLDER = "ids"
DATA_FOLDER = "data"
WAIT = 2  # seconds between requests
ERROR_LOG = "scrape_errors.log"

def get_scraped_ids(csv_path):
    ids = set()
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ids.add(str(row["id"]))
    return ids

def save_row_to_csv(row, csv_path):
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, "a", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def log_error(canton, id_, error_text):
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{canton}] {id_}: {error_text}\n")

def process_canton(canton):
    print(f"\n=== Processing canton: {canton} ===")
    ids_path = os.path.join(IDS_FOLDER, f"{canton}_ids.txt")
    csv_path = os.path.join(DATA_FOLDER, f"{canton}.csv")
    scraped_ids = get_scraped_ids(csv_path)
    if not os.path.isfile(ids_path):
        print(f"[{canton}] Skipping, no ID file found.")
        return

    with open(ids_path, "r") as f:
        all_ids = [line.strip() for line in f if line.strip()]
    to_scrape = [id_ for id_ in all_ids if id_ not in scraped_ids]
    total = len(to_scrape)
    if total == 0:
        print(f"[{canton}] All listings already scraped!")
        return

    for idx, id_ in enumerate(to_scrape, 1):
        url = f"https://www.immoscout24.ch/rent/{id_}"
        print(f"  Scraping {canton} {idx}/{total}: {url}")
        try:
            data = extract_listing_features(url)
            save_row_to_csv(data, csv_path)
            print(f"    ...saved")
        except Exception as e:
            log_error(canton, id_, traceback.format_exc())
            print(f"    ERROR on {id_}, skipping.")
        print(f"    Sleeping {WAIT} seconds before next request...")
        time.sleep(WAIT)

if __name__ == "__main__":
    os.makedirs(DATA_FOLDER, exist_ok=True)
    for canton in CANTONS:
        process_canton(canton)
    print("\nDone! Check your data folder for new CSVs.")
