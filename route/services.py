import requests
import pandas as pd
from geopy.distance import geodesic
from decouple import config

ROUTE_API_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
GEOCODE_API_URL = "https://api.openrouteservice.org/geocode/search"
API_KEY = config("API_KEY")
FUEL_PRICES_FILE = "fuel-prices-for-be-assessment.csv"
METERS_TO_MILES = 1609.34
MAX_RANGE = 500
MILES_PER_GALLON = 10

def geocode_location(location):
    """Convert a location name into coordinates using OpenRouteService."""
    response = requests.get(GEOCODE_API_URL, params={
        "api_key": API_KEY,
        "text": location,
    })
    if response.status_code != 200:
        raise Exception("Failed to fetch geocode data")
    features = response.json().get("features", [])
    if not features:
        raise Exception(f"No results found for location: {location}")
    coordinates = features[0]["geometry"]["coordinates"]
    return coordinates

def get_routes(start_coords, finish_coords):
    """Fetch multiple routes between start and finish locations."""
    response = requests.get(ROUTE_API_URL, params={
        "api_key": API_KEY,
        "start": f"{start_coords[0]},{start_coords[1]}",
        "end": f"{finish_coords[0]},{finish_coords[1]}",
        "alternatives": True,
    })
    if response.status_code != 200:
        raise Exception("Failed to fetch route data")
    return response.json()

def get_route_info(start, finish):
    """Fetch the route and calculate fuel stops."""
    try:
        start_coords = geocode_location(start)
        finish_coords = geocode_location(finish)

        # Fetch multiple routes
        routes = get_routes(start_coords, finish_coords)

        # Evaluate each route
        best_route = None
        min_cost = float('inf')
        fuel_prices = pd.read_csv(FUEL_PRICES_FILE)

        for route in routes['features']:
            # Extract route distance
            distance_meters = route['properties']['segments'][0]['distance']
            distance_miles = distance_meters / METERS_TO_MILES

            # Calculate fuel cost using the greedy algorithm
            total_cost, fuel_stops = calculate_fuel_cost(distance_miles, route, fuel_prices)

            # Update the best route
            if total_cost < min_cost:
                min_cost = total_cost
                best_route = {
                    "route": route,
                    "total_cost": total_cost,
                    "distance_miles": distance_miles,
                    "fuel_stops": fuel_stops,
                }

        return best_route
    except Exception as e:
        return {"error": str(e), "status": 500}

def calculate_fuel_cost(distance, route, fuel_prices):
    """
    Calculate the total fuel cost for a given route using a greedy algorithm.
    Args:
        distance: Total distance of the route in miles.
        route: Route geometry containing coordinates.
        fuel_prices: DataFrame of fuel prices with coordinates.

    Returns:
        Total cost of fuel for the route and the list of fuel stops.
    """
    coordinates = route['geometry']['coordinates']
    total_cost = 0
    fuel_stops = []

    current_distance = 0
    current_index = 0

    while current_distance < distance:
        # Determine the range of coordinates within the max range
        end_index = min(len(coordinates) - 1, int((current_distance + MAX_RANGE) * len(coordinates) / distance))
        segment_coords = coordinates[current_index:end_index + 1]
        current_index = end_index

        # Find the cheapest fuel station within range
        cheapest_station = find_cheapest_station(segment_coords, fuel_prices)
        if not cheapest_station:
            raise Exception("No fuel stations available within range")

        # Calculate fuel cost for this segment
        segment_distance = min(MAX_RANGE, distance - current_distance)
        gallons_for_segment = segment_distance / MILES_PER_GALLON
        total_cost += gallons_for_segment * cheapest_station["price"]

        # Add the station to the fuel stops
        fuel_stops.append(cheapest_station)

        # Move to the next segment
        current_distance += MAX_RANGE

    return total_cost, fuel_stops


def fetch_coordinates(address):
    """Fetch longitude and latitude for a given address."""
    response = requests.get(GEOCODE_API_URL, params={"api_key": API_KEY, "text": address})
    if response.status_code == 200:
        features = response.json().get("features", [])
        if features:
            coords = features[0]["geometry"]["coordinates"]
            return coords[0], coords[1]
    return None, None

def find_cheapest_station(segment_coords, fuel_prices):
    """
    Find the cheapest fuel station within a range of coordinates.
    Args:
        segment_coords: List of coordinates (longitude, latitude) in the segment.
        fuel_prices: DataFrame of fuel prices.

    Returns:
        The cheapest station within the range or None.
    """
    cheapest_station = None
    min_price = float('inf')

    for _, station in fuel_prices.iterrows():
        address = f"{station['Address']}, {station['City']}, {station['State']}"
        
        # Fetch coordinates for the station
        longitude, latitude = fetch_coordinates(address)
        if longitude is None or latitude is None:
            continue

        station_coords = (latitude, longitude)

        # Check if the station is near any coordinate in the segment
        for coord in segment_coords:
            if geodesic((coord[1], coord[0]), station_coords).miles <= MAX_RANGE:
                if station["Retail Price"] < min_price:
                    min_price = station["Retail Price"]
                    cheapest_station = {
                        "name": station["Truckstop Name"],
                        "price": station["Retail Price"],
                        "location": [latitude, longitude]
                    }

    return cheapest_station
