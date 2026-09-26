"""
Utility functions for API clients used by worker agents.
Each function wraps a specific API call and returns structured data.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_weather(latitude, longitude, days=5):
    """
    Get weather forecast from Open-Meteo API.

    Args:
        latitude (float): Latitude of the location
        longitude (float): Longitude of the location
        days (int): Number of days for forecast (default 5)

    Returns:
        dict: Weather forecast data or error message
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max',
            'timezone': 'auto',
            'forecast_days': days
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Weather API failed: {str(e)}"}

def search_tavily(query, max_results=5):
    """
    Search using Tavily API.

    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return

    Returns:
        dict: Search results or error message
    """
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": os.getenv("TAVILY_API_KEY"),
            "query": query,
            "max_results": max_results,
            "include_answer": True,
            "include_raw_content": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Tavily search failed: {str(e)}"}

def geocode_location(location_name):
    """
    Get coordinates for a location using Nominatim (OpenStreetMap).

    Args:
        location_name (str): Name of the location to geocode

    Returns:
        dict: Latitude and longitude or error message
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': location_name,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'Multi-Agent-Travel-System/1.0'
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return {
                "latitude": float(data[0]["lat"]),
                "longitude": float(data[0]["lon"]),
                "display_name": data[0]["display_name"]
            }
        else:
            return {"error": f"Could not geocode location: {location_name}"}
    except Exception as e:
        return {"error": f"Geocoding failed: {str(e)}"}

def search_overpass(location_name, radius=5000):
    """
    Search for tourist attractions using Overpass API (OpenStreetMap).

    Args:
        location_name (str): Name of the location to search around
        radius (int): Search radius in meters (default 5km)

    Returns:
        dict: Overpass API results or error message
    """
    try:
        # First geocode the location to get coordinates
        geo_result = geocode_location(location_name)
        if "error" in geo_result:
            return geo_result

        lat = geo_result["latitude"]
        lon = geo_result["longitude"]

        # Overpass query for tourism attractions
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["tourism"](around:{radius},{lat},{lon});
          way["tourism"](around:{radius},{lat},{lon});
          relation["tourism"](around:{radius},{lat},{lon});
          node["leisure"="park"](around:{radius},{lat},{lon});
          way["leisure"="park"](around:{radius},{lat},{lon});
          relation["leisure"="park"](around:{radius},{lat},{lon});
          node["historic"](around:{radius},{lat},{lon});
          way["historic"](around:{radius},{lat},{lon});
          relation["historic"](around:{radius},{lat},{lon});
        );
        out center;
        """

        response = requests.post(overpass_url, data=overpass_query)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Overpass search failed: {str(e)}"}

def get_currency_exchange(from_currency, to_currency, amount=1):
    """
    Get currency exchange rate using Frankfurter API.

    Args:
        from_currency (str): Source currency code (e.g., 'USD')
        to_currency (str): Target currency code (e.g., 'EUR')
        amount (float): Amount to convert

    Returns:
        dict: Exchange rate information or error message
    """
    try:
        url = f"https://api.frankfurter.dev/v1/latest"
        params = {
            'from': from_currency,
            'to': to_currency,
            'amount': amount
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Currency exchange failed: {str(e)}"}