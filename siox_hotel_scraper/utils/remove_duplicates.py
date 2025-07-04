import json
import pandas as pd
from openpyxl import load_workbook
import os

from calculate_nearby import calculate_distances

def remove_duplicates_from_json(input_file, sheet_name=None, output_excel=None):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON must contain a list at the top level.")

    original_length = len(data)
    # Remove duplicates while preserving order
    seen = set()
    unique_data = []
    for item in data:
        trip_id = item.get("tripadvisor_id")
    
        if trip_id and trip_id not in seen:
            seen.add(trip_id)
            unique_data.append(item)

    cleaned_length = len(unique_data)

    print(f"Original length: {original_length}")
    print(f"Cleaned length: {cleaned_length}")
    print(f"Duplicates removed: {original_length - cleaned_length}")

    data = calculate_distances(data)

    # Save to output file (or overwrite input)
    # output_file = input_file
    output_file = 'data/processed_texas.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Cleaned JSON saved to: {output_file}")

    # Export to Excel
    output_excel = 'data/tripadvisor_hotels_data.xlsx'

    # Define fixed column order
    fixed_columns = [
        "hotel_name", "hotel_url", "tripadvisor_id", "address", "city", "state", "zip_code",
        "region_rank", "overall_rating", "latitude", "longitude", "total_reviews", "number_of_rooms",
        "Location", "Rooms", "Value", "Cleanliness", "Service", "Sleep Quality",
        "nearby_hotels", "nearby_hotels_descriptive", "reviews"
    ]

    rows = []
    for entry in data:
        row = entry.copy()

        # Extract city
        state = entry.get('state', '')

        for col in fixed_columns:
            if col == "nearby_hotels":
                row[col] = '\n'.join(entry.get("nearby_hotels", []))
            elif col == "nearby_hotels_descriptive":
                state = entry.get("state", "")
                row[col] = '\n'.join([f"{hotel}, {state}" for hotel in entry.get("nearby_hotels", [])])
            elif col == "reviews":
                reviews = entry.get("reviews", [])
                formatted_reviews = []
                for review in reviews:
                    review_text = review.get("text", "").strip().replace("\n", " ")
                    response_text = review.get("mgmt_response", "None")
                    if isinstance(response_text, dict):
                        response_text = response_text.get("text", "").strip().replace("\n", " ")
                    formatted_reviews.append(f"Review: {review_text}\nResponse: {response_text}")
                row[col] = "\n\n".join(formatted_reviews)
            else:
                row[col] = entry.get(col, "")

        rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows, columns=fixed_columns)

    if os.path.exists(output_excel):
        # Load existing workbook and append a new sheet
        with pd.ExcelWriter(output_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        # Create a new workbook with the first sheet
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"✅ Sheet '{sheet_name}' saved to: {output_excel}")

# Example usage:
if __name__ == "__main__":
    remove_duplicates_from_json('data/texas2.json', 'Texas')  # Replace with your actual filename