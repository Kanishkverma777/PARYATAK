"""
Places Agent - Specialist for tourist attractions and places to visit.
Uses Overpass/OpenStreetMap API and Tavily search to find places of interest.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.api_clients import search_overpass, search_tavily

class PlacesAgent:
    def __init__(self):
        """Initialize the Places Agent."""
        pass

    def find_places(self, destination: str, duration_days: int) -> dict:
        """
        Find tourist attractions and places to visit in a destination.

        Args:
            destination (str): The destination city/region
            duration_days (int): Number of days for the trip

        Returns:
            dict: Places information or error message
        """
        # Try Overpass API first for structured OpenStreetMap data
        overpass_result = search_overpass(destination, radius=10000)  # 10km radius

        # Also search Tavily for additional information and reviews
        tavily_query = f"top tourist attractions things to do in {destination} for {duration_days} days"
        tavily_result = search_tavily(tavily_query, max_results=5)

        # Check if both failed
        overpass_error = "error" in overpass_result
        tavily_error = "error" in tavily_result

        if overpass_error and tavily_error:
            return {
                "agent": "places",
                "task": f"Find places to visit in {destination} for {duration_days} days",
                "error": f"Both Overpass and Tavily failed. Overpass: {overpass_result.get('error', 'Unknown')}, Tavily: {tavily_result.get('error', 'Unknown')}",
                "success": False
            }

        # Force conversion of USD to INR in the raw search results
        import re
        if not tavily_error and "results" in tavily_result:
            for result in tavily_result["results"]:
                content = result.get("content", "")
                
                def usd_to_inr(match):
                    try:
                        val = float(match.group(1).replace(',', ''))
                        return f"₹{int(val * 83)}"
                    except:
                        return match.group(0)
                        
                content = re.sub(r'\$\s*([\d,]+(?:\.\d+)?)', usd_to_inr, content)
                content = re.sub(r'(?i)usd\s*([\d,]+(?:\.\d+)?)', usd_to_inr, content)
                
                result["content"] = content

        # Return successful result with available data
        return {
            "agent": "places",
            "task": f"Find tourist attractions in {destination}",
            "destination": destination,
            "duration_days": duration_days,
            "overpass_data": overpass_result if not overpass_error else None,
            "tavily_data": tavily_result if not tavily_error else None,
            "success": not (overpass_error and tavily_error)
        }