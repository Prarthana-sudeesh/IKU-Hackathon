import openrouteservice
from geopy.geocoders import Nominatim
import json
from os import path
import requests
from dotenv import load_dotenv

def get_location_coordinates(user_location):
    geolocator = Nominatim(user_agent="IKU_hack_accesibility_app")
    coordinates = geolocator.geocode(user_location)
    print(coordinates)
    return coordinates[1]

def get_directions(start_coordinates, end_coordinates):

    load_dotenv()
    api_key = os.getenv("ORS_API_KEY")

    start_coordinates = (start_coordinates[1], start_coordinates[0])
    end_coordinates = (end_coordinates[1], end_coordinates[0])

    url = "https://api.heigit.org/openrouteservice/v2/directions/wheelchair"

    headers = {
        "Authorization": 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjA1NTBkYmI0MTlkZjRhYjY5MzYzMTNjZDc4YTBlYjYyIiwiaCI6Im11cm11cjY0In0=',
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    payload = {
        "coordinates": [
            list(start_coordinates),
            list(end_coordinates)
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    with open("response_test.json", "w") as file:
        json.dump(response.json(), file, indent=4)

    return response.json()


def get_route(start_location, destination, output_file=None):
    """
    Get a route between two named places.

    Returns the route as a Python dictionary.
    Optionally saves the result to a JSON file.
    """
    start_coordinates = get_location_coordinates(start_location)
    end_coordinates = get_location_coordinates(destination)

    route = get_directions(start_coordinates, end_coordinates)
    return route






