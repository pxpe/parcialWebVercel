import requests

MAPQUEST_URL = 'https://geocode.maps.co/search?q='

async def get_coords(location: str):
    if len(location) < 4 :
        return None
    
    response = requests.get(MAPQUEST_URL + location)

    if(int(response.status_code / 100) != 2):
        return None
    
    result = response.json()

    lat, lon = result[0]['lat'], result[0]['lon']

    return lat, lon