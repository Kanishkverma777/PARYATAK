"""
Weather Agent - Specialist for weather information retrieval.
Uses Open-Meteo API to get weather forecasts.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.api_clients import get_weather, geocode_location

class WeatherAgent:
    def __init__(self):
        """Initialize the Weather Agent."""
        pass

    def get_weather_info(self, destination: str, duration_days: int = 5) -> dict:
        """
        Get weather forecast for a destination.

        Args:
            destination (str): The destination city/region
            duration_days (int): Number of days for forecast

        Returns:
            dict: Weather information or error message
        """
        # First, geocode the destination to get coordinates
        geo_result = geocode_location(destination)

        if "error" in geo_result:
            return {
                "agent": "weather",
                "task": f"Get weather for {destination}",
                "error": geo_result["error"],
                "success": False
            }

        # Get weather using the coordinates
        weather_result = get_weather(
            latitude=geo_result["latitude"],
            longitude=geo_result["longitude"],
            days=duration_days
        )

        if "error" in weather_result:
            return {
                "agent": "weather",
                "task": f"Get weather for {destination}",
                "error": weather_result["error"],
                "success": False,
                "coordinates": {
                    "latitude": geo_result["latitude"],
                    "longitude": geo_result["longitude"]
                }
            }

        # Return successful result
        return {
            "agent": "weather",
            "task": f"Get {duration_days}-day weather forecast for {destination}",
            "destination": destination,
            "coordinates": {
                "latitude": geo_result["latitude"],
                "longitude": geo_result["longitude"]
            },
            "weather_data": weather_result,
            "success": True
        }