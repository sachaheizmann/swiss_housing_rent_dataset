import os
import pandas as pd

folder = "clean_data"
output_file = "data.csv"


# Gather all valid files
files = sorted([
    os.path.join(folder, f)
    for f in os.listdir(folder)
    if f.endswith(".csv")
])

merged_df = None

for i, file in enumerate(files):
    if i == 0:
        # First file: read with header
        merged_df = pd.read_csv(file)
    else:
        # Skip header for all other files
        df = pd.read_csv(file, header=0)
        merged_df = pd.concat([merged_df, df], ignore_index=True)

# Save to final CSV
merged_df.to_csv(output_file, index=False)

print(f"✅ Merged {len(files)} files into {output_file} with {len(merged_df)} rows.")
