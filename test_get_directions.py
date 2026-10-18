

import openrouteservice
from geopy.geocoders import Nominatim
import json
import os
import requests

def get_location_coordinates(user_location):
    geolocator = Nominatim(user_agent="IKU_hack_accesibility_app")
    coordinates = geolocator.geocode(user_location)
    print(coordinates)
    return coordinates[1]

def get_directions(start_coordinates, end_coordinates):
    client = openrouteservice.Client(key='eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjA1NTBkYmI0MTlkZjRhYjY5MzYzMTNjZDc4YTBlYjYyIiwiaCI6Im11cm11cjY0In0=') # Specify your personal API key
    routes = client.directions(start_coordinates, end_coordinates, profile='cycling-regular', optimize_waypoints=True)
    print(routes)
    return routes

#def get_directions(start_coordinates, destination_coordinates):
    url = (
        "https://api.openrouteservice.org/v2/"
        "directions/driving-car"
    )

    params = {
        "api_key": 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjA1NTBkYmI0MTlkZjRhYjY5MzYzMTNjZDc4YTBlYjYyIiwiaCI6Im11cm11cjY0In0=',
        "start": f"{start_coordinates[0]},{start_coordinates[1]}",
        "end": f"{destination_coordinates[0]},{destination_coordinates[1]}"
    }


def get_directions(start_coordinates, end_coordinates):

    start_coordinates = (start_coordinates[1], start_coordinates[0])
    end_coordinates = (end_coordinates[1], end_coordinates[0])

    url = "https://api.heigit.org/openrouteservice/v2/directions/driving-car"

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



def main():

    # Rest of your existing function here
    user_destination = "Imperial College London"
    start_location = "Kings College London"
    start_coordinates = get_location_coordinates(user_destination)
    end_coordinates = get_location_coordinates(start_location)
    route = get_directions(start_coordinates, end_coordinates)
    print(route)





if __name__ == '__main__':
    main()
    



