import requests
import json
from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY


def pexels_photo(city, state):
    url = "https://api.pexels.com/v1/search"
    params = {
        "per_page": 1,
        "query": city + " " + state,
    }
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(
        url,
        params=params,
        headers=headers,
    )
    content = json.loads(response.content)
    try:
        return {"picture_url": content["photos"][0]["src"]["original"]}
    except (KeyError, IndexError):
        return {"picture_url": None}
    # Create a dictionary for the headers to use in the request
    # Create the URL for the request with the city and state
    # Make the request
    # Parse the JSON response
    # Return a dictionary that contains a `picture_url` key and
    #   one of the URLs for one of the pictures in the response


def get_weather(city, state):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    country_code = "1"
    params = {
        "q": city + "," + state + "," + country_code,
        "appid": OPEN_WEATHER_API_KEY,
    }
    response = requests.get(url, params=params)
    content = json.loads(response.content)
    lat = content[0]["lat"]
    lon = content[0]["lon"]
    new_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPEN_WEATHER_API_KEY,
    }
    new_response = requests.get(new_url, params)
    new_content = json.loads(new_response.content)
    try:
        return {
            "weather": new_content["weather"][0]["description"],
            "temp": new_content["main"]["temp"],
        }
    except (KeyError, IndexError):
        return {"weather": None, "temp": None}
