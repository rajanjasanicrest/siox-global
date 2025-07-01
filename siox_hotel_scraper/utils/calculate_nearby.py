import math
import json

# Radius of Earth in miles
EARTH_RADIUS_MI = 3958.8

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance in miles between two coordinates."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return EARTH_RADIUS_MI * c

def calculate_distances(data):

    if not isinstance(data, list):
        raise ValueError("JSON must contain a list at the top level.")
    
    for hotel1_idx in range(len(data)):
        if 'nearby_hotels' not in data[hotel1_idx]:
            data[hotel1_idx]['nearby_hotels'] = []

        hotel1_data = data[hotel1_idx]
        lat1, lon1 = hotel1_data.get('latitude'), hotel1_data.get('longitude')

        if lat1 is None or lon1 is None:
            continue

        for hotel2_idx in range(hotel1_idx + 1, len(data)):
            if 'nearby_hotels' not in data[hotel2_idx]:
                    data[hotel2_idx]['nearby_hotels'] = []

            hotel2_data = data[hotel2_idx]
            lat2, lon2 = hotel2_data.get('latitude'), hotel2_data.get('longitude')

            if lat2 is None or lon2 is None:
                continue

            distance = haversine_distance(lat1, lon1, lat2, lon2)

            if distance <= 2.0:
                hotel1_name = hotel1_data.get('hotel_name', '')
                hotel2_name = hotel2_data.get('hotel_name', '')

                if hotel2_name and hotel2_name not in hotel1_data['nearby_hotels']:
                    data[hotel1_idx]['nearby_hotels'].append(hotel2_name)
                if hotel1_name and hotel1_name not in hotel2_data['nearby_hotels']:
                    data[hotel2_idx]['nearby_hotels'].append(hotel1_name)

    print(f"✅ Calculated and Saved Nearby Hotels")
    return data

# Example usage
if __name__ == "__main__":
    nearby_hotels = calculate_distances('georgia.json', 'test.json')  # Replace with your actual filename