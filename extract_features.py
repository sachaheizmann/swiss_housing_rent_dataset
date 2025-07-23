import requests
from bs4 import BeautifulSoup
import re

def extract_listing_features(url):
    headers = {
        "Authorization": "Bearer ecaaeaef-9be4-4ab2-80ba-445acf62fd01",
        "Content-Type": "application/json"
    }
    data = {
        "zone": "imoscount",
        "url": url,
        "format": "raw"
    }

    response = requests.post(
        "https://api.brightdata.com/request",
        json=data,
        headers=headers
    )

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    id_match = re.search(r'/rent/(\d+)', url)
    listing_id = id_match.group(1) if id_match else url

    # Address
    street, city = "", ""
    address_block = soup.find("address", class_="AddressDetails_address_i3koO")
    if address_block:
        parts = address_block.find_all("span")
        if len(parts) >= 2:
            street = parts[0].text.strip()
            city = parts[1].text.strip()

    # Rooms
    rooms = -1
    rooms_div = soup.find("div", class_="SpotlightAttributesNumberOfRooms_item_I09kX")
    if rooms_div:
        value_div = rooms_div.find("div", class_="SpotlightAttributesNumberOfRooms_value_TUMrd")
        if value_div:
            try:
                rooms = float(value_div.text.strip().replace(",", "."))
            except:
                rooms = -1

    # Living space
    space = -1
    space_div = soup.find("div", class_="SpotlightAttributesUsableSpace_item_ryKPW")
    if space_div:
        value_div = space_div.find("div", class_="SpotlightAttributesUsableSpace_value_cpfrh")
        if value_div:
            try:
                space = float(value_div.get_text(strip=True).split("m")[0].replace(",", "."))
            except:
                space = -1

    # Price
    price = -1
    price_div = soup.find("div", class_="SpotlightAttributesPrice_item_iVKUf")
    if price_div:
        value_div = price_div.find("div", class_="SpotlightAttributesPrice_value_TqKGz")
        if value_div:
            raw_price = value_div.get_text(strip=True)
            digits = re.findall(r'\d+', raw_price.replace("'", "").replace(",", ""))
            try:
                price = int(''.join(digits)) if digits else -1
            except:
                price = -1

    # Average travel time
    avg_travel_time = -1
    travel_times = []
    travel_ul = soup.find("ul", class_="TravelTime_travelTimeList_ZpU5h")
    if travel_ul:
        items = travel_ul.find_all("li", class_="TravelTime_travelTimePoiData_GN7yR")
        for li in items:
            time_span = li.find("span", class_="TravelTime_travelTimeListTime_SUflX")
            if time_span:
                try:
                    text = time_span.text.strip()
                    minutes = int(''.join(filter(str.isdigit, text)))
                    travel_times.append(minutes)
                except:
                    continue
    if travel_times:
        avg_travel_time = round(sum(travel_times) / len(travel_times), 2)

    # Core attributes
    type_ = ""
    refurb = -1
    year_built = -1
    core_attrs = soup.find("div", class_="CoreAttributes_coreAttributes_e2NAm")
    if core_attrs:
        dts = core_attrs.find_all("dt")
        dds = core_attrs.find_all("dd")
        for dt, dd in zip(dts, dds):
            label = dt.get_text(strip=True)
            value = dd.get_text(strip=True)
            if label == "Type:":
                type_ = value
            elif label == "Last refurbishment:":
                try:
                    refurb = int(value)
                except:
                    refurb = -1
            elif label == "Year built:":
                try:
                    year_built = int(value)
                except:
                    year_built = -1

    # Balcony/Terrace
    balcony = terrace = 0
    features_ul = soup.find("ul", class_="FeaturesFurnishings_list_S54KV")
    if features_ul:
        for li in features_ul.find_all("li"):
            p = li.find("p")
            if p:
                text = p.text.lower()
                if "balcony" in text:
                    balcony = 1
                if "terrace" in text:
                    terrace = 1

    return {
        "id": listing_id,
        "street": street,
        "city_postal": city,
        "rooms": rooms,
        "living_space": space,
        "price": price,
        "avg_travel_time": avg_travel_time,
        "type": type_,
        "last_refurbishment": refurb,
        "year_built": year_built,
        "balcony_or_terrace": balcony | terrace
    }

# Example usage:
if __name__ == "__main__":
    url = "https://www.immoscout24.ch/rent/4002278896"
    data = extract_listing_features(url)
    print(data)
