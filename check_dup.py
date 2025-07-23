import pandas as pd

df = pd.read_csv("data.csv")

if "id" in df.columns:
    duplicated_ids = df[df["id"].duplicated()]
    print(f"🔍 Found {len(duplicated_ids)} duplicate IDs.")
else:
    print("⚠️ No 'id' column found in data.csv.")
