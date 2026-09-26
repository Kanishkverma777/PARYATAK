"""
Food Agent - Specialist for local food/restaurant/food recommendations.
Uses Tavily search API to find food information.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.api_clients import search_tavily

class FoodAgent:
    def __init__(self):
        """Initialize the Food Agent."""
        pass

    def find_food_recommendations(self, destination: str, duration_days: int) -> dict:
        """
        Find food recommendations and restaurant information for a destination.

        Args:
            destination (str): The destination city/region
            duration_days (int): Number of days for the trip

        Returns:
            dict: Food information or error message
        """
        # Construct search query
        query = f"best food restaurants local specialties eateries (budget, mid-range, upscale) street-food in {destination} for {duration_days} days trip prices strictly in INR (₹)"

        # Search using Tavily
        search_result = search_tavily(query, max_results=8)

        if "error" in search_result:
            return {
                "agent": "food",
                "task": f"Find food recommendations in {destination} for {duration_days} days",
                "error": search_result["error"],
                "success": False
            }

        # Force conversion of USD to INR in the raw search results
        import re
        if "results" in search_result:
            for result in search_result["results"]:
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

        # Return successful result
        return {
            "agent": "food",
            "task": f"Find food and restaurant recommendations in {destination}",
            "destination": destination,
            "duration_days": duration_days,
            "search_results": search_result,
            "success": True
        }