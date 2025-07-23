# Swiss Housing Rent Dataset

contains raw, cleaned, and merged housing rent data for properties in Switzerland.

---

## 📁 `/data/`

Contains the **original unmodified `.csv` files** for each Swiss canton.  
Each file includes rows with the following columns:

- `id`: unique listing ID
- `street`: street name
- `city_postal`: postal code and city
- `rooms`: number of rooms
- `living_space`: in m²
- `price`: in CHF
- `avg_travel_time`: average time (in minutes) to supermarket, pharmacy, school, and public transport
- `type`: `apartment` or `house`
- `last_refurbishment`: year of last renovation
- `year_built`: original construction year
- `balcony_or_terrace`: 1 if present, 0 otherwise

Some rows may contain `-1` or empty strings for missing data.

---

## 📁 `/clean_data/`

Contains the **cleaned version** of each `.csv` from `/data/`, with:

- Rows with only `id` and no useful info removed
- Missing numeric values (`-1` or `""`) replaced by column averages
- Missing `type` values inferred based on `rooms` appartement if <=4 rooms else house
- Missing addresses printed for manual inspection 
- New column: `price_per_m2` calculated as `price / living_space`
- Geocoded columns: `lat` and `lon` using Swiss geo.admin API
- Missing coordinates filled with postal or global averages by canton

---

## 📄 `data.csv`

A **single merged file** combining all cleaned canton files, with:

---
