"""
Hotel Agent - Specialist for hotel/accommodation information retrieval.
Uses Tavily search API to find accommodation options.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.api_clients import search_tavily

class HotelAgent:
    def __init__(self):
        """Initialize the Hotel Agent."""
        pass

    def find_hotels(self, destination: str, num_people: int, duration_days: int) -> dict:
        """
        Find hotel/accommodation options for a destination.

        Args:
            destination (str): The destination city/region
            num_people (int): Number of people traveling
            duration_days (int): Number of days staying

        Returns:
            dict: Hotel information or error message
        """
        # Construct search query
        query = f"best hotels in {destination} for {num_people} people {duration_days} nights stay prices strictly in INR (₹)"

        # Search using Tavily
        search_result = search_tavily(query, max_results=8)

        if "error" in search_result:
            return {
                "agent": "hotel",
                "task": f"Find hotels in {destination} for {num_people} people, {duration_days} days",
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
            "agent": "hotel",
            "task": f"Find accommodation options in {destination}",
            "destination": destination,
            "num_people": num_people,
            "duration_days": duration_days,
            "search_results": search_result,
            "success": True
        }