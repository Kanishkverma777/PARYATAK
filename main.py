#!/usr/bin/env python3
"""
Main entry point for the Multi-Agent Travel Planning System.
Demonstrates the Supervisor/Worker architecture with all travel agents.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.main_agent import MainAgent
from agents.weather_agent import WeatherAgent
from agents.hotel_agent import HotelAgent
from agents.places_agent import PlacesAgent
from agents.food_agent import FoodAgent
from agents.budget_agent import BudgetAgent
from agents.itinerary_agent import ItineraryAgent

def main():
    """Main function to run the travel planning system."""
    print("🤖 Multi-Agent Travel Planning System")
    print("=" * 50)
    print("Architecture: Supervisor/Worker Pattern")
    print("Main Agent (Supervisor) coordinates:")
    print("  - Weather Agent")
    print("  - Hotel Agent")
    print("  - Places Agent")
    print("  - Food Agent")
    print("  - Budget Agent")
    print("  - Itinerary Agent")
    print("=" * 50)

    # Initialize agents
    print("\n🔧 Initializing agents...")
    main_agent = MainAgent()
    weather_agent = WeatherAgent()
    hotel_agent = HotelAgent()
    places_agent = PlacesAgent()
    food_agent = FoodAgent()
    budget_agent = BudgetAgent()
    itinerary_agent = ItineraryAgent()
    print("✅ All agents initialized!")

    # Get user input
    print("\n📝 Enter your travel request:")
    print('Example: "Plan a 5-day trip to Manali for 2 people under ₹30,000"')
    user_query = input("\n> ").strip()

    if not user_query:
        # Use default example if no input
        user_query = "Plan a 5-day trip to Manali for 2 people under ₹30,000"
        print(f"\nUsing default query: {user_query}")

    print("\n🚀 Starting travel planning workflow...")
    print("-" * 50)

    try:
        # Run the orchestration
        final_plan = main_agent.orchestrate_travel_plan(
            user_query=user_query,
            weather_agent=weather_agent,
            hotel_agent=hotel_agent,
            places_agent=places_agent,
            food_agent=food_agent,
            budget_agent=budget_agent,
            itinerary_agent=itinerary_agent
        )

        print("\n📋 FINAL TRAVEL PLAN")
        print("=" * 50)
        print(final_plan)
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Error during planning: {str(e)}")
        print("Please check your API keys and internet connection.")

if __name__ == "__main__":
    main()