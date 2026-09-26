"""
Budget Agent - Specialist for calculating/estimating trip budget.
Uses information from other agents to calculate budget estimates.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class BudgetAgent:
    def __init__(self):
        """Initialize the Budget Agent."""
        pass

    def calculate_budget(self, destination: str, num_people: int, duration_days: int,
                        weather_data: dict, hotel_data: dict, places_data: dict, food_data: dict = None) -> dict:
        """
        Calculate trip budget based on information from other agents.

        Args:
            destination (str): The destination city/region
            num_people (int): Number of people traveling
            duration_days (int): Number of days for the trip
            weather_data (dict): Weather information from WeatherAgent
            hotel_data (dict): Hotel information from HotelAgent
            places_data (dict): Places information from PlacesAgent
            food_data (dict, optional): Food information from FoodAgent

        Returns:
            dict: Budget breakdown and total estimate
        """
        # Initialize budget components
        accommodation_cost = 0
        food_cost = 0
        activities_cost = 0
        miscellaneous_cost = 0

        # Extract accommodation costs from hotel data
        if hotel_data.get("success", False) and "search_results" in hotel_data:
            # Try to extract price information from Tavily results
            search_results = hotel_data["search_results"]
            if "results" in search_results:
                # Look for price patterns in the results
                prices_found = []
                for result in search_results["results"]:
                    content = result.get("content", "")
                    # Simple price extraction - look for patterns like ₹X,xxx or $xxx
                    import re
                    price_matches = re.findall(r'[₹$]\s*[\d,]+(?:\.\d+)?', content)
                    for price in price_matches:
                        # Clean and convert to number
                        cleaned = re.sub(r'[^\d]', '', price)
                        if cleaned.isdigit():
                            prices_found.append(int(cleaned))

                # If we found prices, use the median as estimated nightly rate
                if prices_found:
                    prices_found.sort()
                    median_price = prices_found[len(prices_found)//2]
                    # Assume this is per night per room
                    accommodation_cost = median_price * duration_days

        # If we couldn't extract specific prices, use reasonable defaults
        if accommodation_cost == 0:
            # Default budget accommodation: ₹1500 per night
            accommodation_cost = 1500 * duration_days

        # Estimate food costs
        # Default: ₹800 per person per day for meals
        food_cost = 800 * num_people * duration_days

        # Estimate activities/entrance fees
        # Default: ₹500 per person per day for activities
        activities_cost = 500 * num_people * duration_days

        # Miscellaneous (transport within city, souvenirs, etc.)
        # Default: ₹300 per person per day
        miscellaneous_cost = 300 * num_people * duration_days

        # Calculate total
        total_cost = accommodation_cost + food_cost + activities_cost + miscellaneous_cost

        # Create budget breakdown
        budget_breakdown = {
            "accommodation": {
                "cost": accommodation_cost,
                "description": f"Accommodation for {num_people} people for {duration_days} nights"
            },
            "food": {
                "cost": food_cost,
                "description": f"Meals for {num_people} people for {duration_days} days"
            },
            "activities": {
                "cost": activities_cost,
                "description": f"Activities and entrance fees for {num_people} people for {duration_days} days"
            },
            "miscellaneous": {
                "cost": miscellaneous_cost,
                "description": f"Local transport, souvenirs, and other expenses for {num_people} people for {duration_days} days"
            }
        }

        return {
            "agent": "budget",
            "task": f"Calculate budget for {destination} trip for {num_people} people over {duration_days} days",
            "destination": destination,
            "num_people": num_people,
            "duration_days": duration_days,
            "budget_breakdown": budget_breakdown,
            "total_cost": total_cost,
            "currency": "INR",
            "success": True
        }