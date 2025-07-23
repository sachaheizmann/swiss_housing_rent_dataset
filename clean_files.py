import os
import pandas as pd
import requests
import time



file_path = "clean_data/basel-landschaft.csv"

numeric_columns = [
    "rooms", "living_space", "price", "avg_travel_time",
    "last_refurbishment", "year_built", "balcony_or_terrace"
]

def clean_file(path):
    df = pd.read_csv(path)

    # Remove rows with only ID and -1 or empty
    def is_invalid(row):
        values = row.drop(labels=["id"])
        return all(val in [-1, "-1", "", None] for val in values)

    df = df[~df.apply(is_invalid, axis=1)]

    counter =0
    # Track manual address fixes
    for _, row in df.iterrows():
        if pd.isna(row["street"]) or row["street"] in ["", "-1"]:
            counter+=1
            print(f"[Missing Address] id={row['id']}" + f"    {counter}")
        if pd.isna(row["city_postal"]) or row["city_postal"] in ["", "-1"]:
            print(f"[Missing City] id={row['id']}")

    # Replace -1 and empty strings in numeric columns with column mean
    int_columns = ["rooms", "last_refurbishment", "year_built", "balcony_or_terrace"]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].replace(-1, pd.NA)
        mean_val = df[col].dropna().mean()

        # Round if it should be int
        if col in int_columns:
            mean_val = round(mean_val)
            df[col] = df[col].fillna(mean_val)
            df[col] = df[col].astype(int)
        else:
            df[col] = df[col].fillna(mean_val)
            df[col] = df[col].astype(float)


    # Geocoding function using geo.admin.ch
    def geocode_address(street, city_postal):
        if pd.isna(street) or pd.isna(city_postal):
            return pd.NA, pd.NA

        query = f"{street}, {city_postal}"
        url = "https://api3.geo.admin.ch/rest/services/api/SearchServer"
        params = {
            "searchText": query,
            "lang": "fr",
            "type": "locations"
        }

        try:
            r = requests.get(url, params=params, timeout=4)
            r.raise_for_status()
            results = r.json().get("results", [])
            if results:
                attrs = results[0]["attrs"]
                return float(attrs["y"]), float(attrs["x"])  # lat, lon
        except:
            pass

        return pd.NA, pd.NA
    # Infer missing 'type'
    def infer_type(row):
        if row["type"] not in ["apartment", "house"]:
            rooms = row["rooms"]
            if rooms <= 3:
                return "apartment"
            elif rooms >= 5:
                return "house"
            else:
                return "apartment"  # fallback
        return row["type"]

    df["type"] = df.apply(infer_type, axis=1)
    # Calculate price per m²
    df["price_per_m2"] = df["price"] / df["living_space"]

    # Fill missing or infinite values with column average
    mean_price_m2 = df["price_per_m2"].dropna().mean()
    print(mean_price_m2)
    df["price_per_m2"] = df["price_per_m2"].fillna(mean_price_m2)

    # Add lat/lon columns by geocoding address
    print("Geocoding rows (this may take a while)...")

    df[["lat", "lon"]] = df.apply(
        lambda row: pd.Series(geocode_address(row["street"], row["city_postal"])),
        axis=1
    )

    # Compute mean per postal code
    postal_means = df.groupby("city_postal")[["lat", "lon"]].transform("mean")

    # Make everything numeric first
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

    # Fill with postal-level mean
    df["lat"] = df["lat"].fillna(postal_means["lat"])
    df["lon"] = df["lon"].fillna(postal_means["lon"])

    # ✅ Final fallback: fill remaining with overall mean
    df["lat"] = df["lat"].fillna(df["lat"].mean())
    df["lon"] = df["lon"].fillna(df["lon"].mean())

    # Round and cast to Int64
    df["lat"] = df["lat"].round().astype("Int64")
    df["lon"] = df["lon"].round().astype("Int64")



    # Optional: slow down if you're doing many rows
    # time.sleep(0.1)  # Add inside the geocode function if needed

    # Drop the 'id' column
    #df = df.drop(columns=["id"])

    # Save back to file
    df.to_csv(path, index=False)

# Run cleaning on all files
exclude = {"aargau.csv", "basel-landschaft.csv"}
folder = "clean_data"

# Run cleaning on all files except excluded
for filename in sorted(os.listdir(folder)):
    if filename.endswith(".csv") and filename not in exclude:
        print(f"Cleaning {filename}...")
        clean_file(os.path.join(folder, filename))