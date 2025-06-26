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
    output_file = input_file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Cleaned JSON saved to: {output_file}")

    # Export to Excel
    output_excel = 'data/tripadvisor_hotels_data.xlsx'

    rows = []
    for entry in data:
        row = entry.copy()

        # Extract city
        state = entry.get('state', '')

        # Format nearby_hotels
        nearby = entry.get('nearby_hotels', [])
        row['nearby_hotels'] = '\n'.join(nearby)

        # Create descriptive nearby list
        row['nearby_hotels_descriptive'] = '\n'.join([f"{hotel}, {state}" for hotel in nearby])

        rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(rows)

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
    remove_duplicates_from_json('data/texas.json', 'Texas')  # Replace with your actual filename