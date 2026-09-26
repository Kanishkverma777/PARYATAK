"""
Itinerary Agent - Specialist for creating day-by-day itinerary.
Uses all collected information (weather, places, food, etc.) to create structured day-by-day schedule.
Does NOT independently research new information.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class ItineraryAgent:
    def __init__(self):
        """Initialize the Itinerary Agent."""
        pass

    def create_itinerary(self, destination: str, duration_days: int,
                        weather_data: dict, places_data: dict,
                        budget_data: dict) -> dict:
        """
        Create day-by-day itinerary based on information from other agents.

        Args:
            destination (str): The destination city/region
            duration_days (int): Number of days for the trip
            weather_data (dict): Weather information from WeatherAgent
            places_data (dict): Places information from PlacesAgent
            budget_data (dict): Budget information from BudgetAgent

        Returns:
            dict: Structured day-by-day itinerary
        """
        # Initialize itinerary structure
        itinerary = {
            "destination": destination,
            "duration_days": duration_days,
            "days": []
        }

        # Extract useful information from the data
        weather_summary = self._extract_weather_summary(weather_data)
        places_summary = self._extract_places_summary(places_data)
        budget_info = budget_data.get("total_cost", "Budget not available") if budget_data.get("success", False) else "Budget not available"

        # Create day-by-day plan
        for day in range(1, duration_days + 1):
            day_plan = {
                "day": day,
                "date": f"Day {day}",  # In a real app, we'd calculate actual dates
                "weather": weather_summary,
                "activities": [],
                "meals": [],
                "notes": ""
            }

            # Distribute places across days (simple approach: divide evenly)
            if places_summary:
                places_per_day = max(1, len(places_summary) // duration_days)
                start_idx = (day - 1) * places_per_day
                end_idx = min(start_idx + places_per_day, len(places_summary))
                day_activities = places_summary[start_idx:end_idx]
                for place in day_activities:
                    day_plan["activities"].append({
                        "name": place.get("name", "Unknown Place"),
                        "type": place.get("type", "attraction"),
                        "description": place.get("description", "")[:100] + "..." if len(place.get("description", "")) > 100 else place.get("description", ""),
                        "suggested_time": self._suggest_time_for_activity(place.get("type", ""))
                    })

            # Add day-specific notes
            notes = []
            if weather_summary and isinstance(weather_summary, dict) and "temperature" in weather_summary:
                notes.append(f"Pack clothing suitable for {weather_summary.get('temperature', 'variable weather')}")
            if budget_info != "Budget not available":
                daily_budget = budget_info / duration_days if isinstance(budget_info, (int, float)) else 0
                notes.append(f"Approximate daily budget: ₹{daily_budget:.0f}")

            day_plan["notes"] = ". ".join(notes) if notes else "Enjoy your day!"

            itinerary["days"].append(day_plan)

        return {
            "agent": "itinerary",
            "task": f"Create {duration_days}-day itinerary for {destination}",
            "destination": destination,
            "duration_days": duration_days,
            "itinerary": itinerary,
            "budget_info": budget_info,
            "success": True
        }

    def _extract_weather_summary(self, weather_data: dict) -> dict:
        """Extract user-friendly weather summary from weather data."""
        if not weather_data.get("success", False):
            return {"summary": "Weather information not available"}

        # Try to extract meaningful weather info
        if "forecast" in weather_data:
            forecast = weather_data["forecast"]
            if isinstance(forecast, list) and len(forecast) > 0:
                # Take first day's forecast as representative
                day_forecast = forecast[0]
                return {
                    "temperature": f"{day_forecast.get('temp_min', 'N/A')}°-{day_forecast.get('temp_max', 'N/A')}°",
                    "conditions": day_forecast.get('weather', [{}])[0].get('description', 'variable'),
                    "precipitation_chance": f"{day_forecast.get('pop', 0)}%"
                }

        # Fallback for Open-Meteo format
        if "daily" in weather_data:
            daily = weather_data["daily"]
            if "temperature_2m_max" in daily and len(daily["temperature_2m_max"]) > 0:
                return {
                    "temperature": f"{daily['temperature_2m_min'][0]}°-{daily['temperature_2m_max'][0]}°",
                    "precipitation": f"{daily['precipitation_probability_max'][0]}% chance"
                }

        return {"summary": "Weather data available"}

    def _extract_places_summary(self, places_data: dict) -> list:
        """Extract places information into a usable format."""
        if not places_data.get("success", False):
            return []

        places = []

        # Handle Tavily results
        if "search_results" in places_data:
            search_results = places_data["search_results"]
            if "results" in search_results:
                for result in search_results["results"][:10]:  # Limit to top 10
                    places.append({
                        "name": result.get("title", "Unknown Place"),
                        "type": "attraction",
                        "description": result.get("content", "")[:200]
                    })

        # Handle Overpass results
        elif "elements" in places_data:
            for element in places_data["elements"][:10]:  # Limit to top 10
                tags = element.get("tags", {})
                places.append({
                    "name": tags.get("name", f"Place {len(places)+1}"),
                    "type": tags.get("tourism", tags.get("leisure", tags.get("historic", "attraction"))),
                    "description": tags.get("description", tags.get("info", "Point of interest"))
                })

        return places

        return places

    def _suggest_time_for_activity(self, place_type: str) -> str:
        """Suggest appropriate time of day for different types of activities."""
        time_suggestions = {
            "park": "Morning or Late Afternoon",
            "museum": "Morning",
            "historical": "Morning",
            "restaurant": "Lunch or Dinner",
            "cafe": "Afternoon",
            "shopping": "Afternoon",
            "temple": "Early Morning",
            "beach": "Morning or Late Afternoon",
            "mountain": "Morning",
            "default": "Flexible timing"
        }

        return time_suggestions.get(place_type.lower(), time_suggestions["default"])