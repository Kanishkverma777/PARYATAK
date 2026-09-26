"""
Main Agent (Supervisor/Manager) for the Multi-Agent Travel Planning System.
Responsible for orchestrating the workflow by deciding which worker agent to call next
and passing information between them.
"""

import os
import re
import json
from groq import Groq
from typing import Dict, Any, List

class MainAgent:
    def __init__(self):
        """Initialize the Main Agent with Groq client."""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-120b"
        self.conversation_history = []

    def add_to_history(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def get_completion(self, prompt: str, system_message: str = None) -> str:
        """
        Get a completion from the Groq API.

        Args:
            prompt (str): The user prompt
            system_message (str): Optional system message

        Returns:
            str: The model's response
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        # Add conversation history
        messages.extend(self.conversation_history)

        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "messages": messages,
            "model": self.model,
            "temperature": 0.5,
            "max_tokens": 4096,
            "response_format": {"type": "json_object"}
        }

        try:
            chat_completion = self.client.chat.completions.create(**kwargs)
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"{{\"error\": \"Error getting completion from Groq: {str(e)}\"}}"

    def orchestrate_travel_plan(self, user_query: str, weather_agent, hotel_agent, places_agent, budget_agent=None, itinerary_agent=None, food_agent=None) -> str:
        """
        Main orchestration method that coordinates the workflow between agents.
        """
        # Reset conversation history for new request
        self.conversation_history = []

        # Step 1: Analyze the user query to extract key information
        system_msg = """You are a travel planning supervisor. Your role is to:
        1. Understand the user's travel request
        2. Extract key details: destination, duration, number of people, budget constraints
        3. Decide which worker agents to call and in what order (based on the user's request and available agents)
        4. Provide clear, specific instructions to each worker agent
        5. Synthesize information from workers to determine next steps
        6. Determine when the planning process is complete

        You do NOT perform actual travel research yourself - you only delegate to specialists.
        You can call any of these agents: weather_agent, hotel_agent, places_agent, food_agent, budget_agent, itinerary_agent.
        
        CRITICAL: YOU MUST ALWAYS RESPOND IN STRICT, VALID JSON FORMAT. NO MARKDOWN, NO PREAMBLE, NO EXTRA TEXT."""

        analysis_prompt = f"""
        Analyze this travel request: "{user_query}"

        Extract the following information:
        - Destination (city/region)
        - Duration (number of days)
        - Number of people
        - Budget constraints (if mentioned)
        - Any other specific preferences

        Based on the user's request and the available agents, decide which worker agents to call and in what order.
        You can call any combination of these agents: weather, hotel, places, food, budget, itinerary.

        Return your analysis in JSON format with EXACTLY these keys:
        - destination: string (the travel destination)
        - duration_days: integer (number of days)
        - num_people: integer (number of travelers)
        - budget: string or null (budget constraint if mentioned)
        - preferences: list of strings (any other preferences)
        - needed_agents: list of strings (subset of ["weather", "hotel", "places", "food", "budget", "itinerary"] in the order they should be called)
        """

        # Try multiple times to get valid JSON
        max_attempts = 3
        for attempt in range(max_attempts):
            analysis_result = self.get_completion(analysis_prompt, system_msg)

            # Try to parse the JSON response
            try:
                # Extract JSON from the response (handle cases where model adds extra text)
                json_match = re.search(r'\{.*\}', analysis_result, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())

                    # Validate that we got expected agent names (any combination of the agents is acceptable)
                    needed_agents = analysis.get("needed_agents", [])
                    acceptable_agents = ["weather", "hotel", "places", "food", "budget", "itinerary"]

                    # Check if all needed agents are acceptable
                    if not all(agent in acceptable_agents for agent in needed_agents):
                        print(f"⚠️  Attempt {attempt+1}: Got unexpected agents {needed_agents}, filtering to acceptable ones")
                        # Filter out any unacceptable agents
                        analysis["needed_agents"] = [agent for agent in needed_agents if agent in acceptable_agents]

                    # Ensure we have all required fields and they are valid integers
                    required_fields = ["destination", "duration_days", "num_people"]
                    if all(field in analysis and analysis[field] is not None for field in required_fields):
                        # Ensure integers
                        try:
                            analysis["duration_days"] = int(analysis["duration_days"])
                            analysis["num_people"] = int(analysis["num_people"])
                            # Store the analysis for use throughout the workflow
                            self.analysis = analysis
                            break
                        except (ValueError, TypeError):
                            print(f"⚠️  Attempt {attempt+1}: Required fields are not valid integers, retrying...")
                            if attempt == max_attempts - 1:
                                analysis = self._create_fallback_analysis(user_query)
                                self.analysis = analysis
                    else:
                        print(f"⚠️  Attempt {attempt+1}: Missing required fields or null values, retrying...")
                        if attempt == max_attempts - 1:
                            # Last attempt, use fallback
                            analysis = self._create_fallback_analysis(user_query)
                            self.analysis = analysis
                else:
                    print(f"⚠️  Attempt {attempt+1}: No JSON found in response, retrying...")
                    if attempt == max_attempts - 1:
                        # Last attempt, use fallback
                        analysis = self._create_fallback_analysis(user_query)
                        self.analysis = analysis
            except json.JSONDecodeError as e:
                print(f"⚠️  Attempt {attempt+1}: JSON decode error: {e}, retrying...")
                if attempt == max_attempts - 1:
                    # Last attempt, use fallback
                    analysis = self._create_fallback_analysis(user_query)
                    self.analysis = analysis
            except Exception as e:
                print(f"⚠️  Attempt {attempt+1}: Unexpected error: {e}, retrying...")
                if attempt == max_attempts - 1:
                    # Last attempt, use fallback
                    analysis = self._create_fallback_analysis(user_query)
                    self.analysis = analysis

        # Step 2: Execute the workflow by calling agents in sequence
        workflow_results = {}

        # Define the order of agent execution based on what agents were provided
        # Default order: weather -> places -> hotel -> food -> budget -> itinerary
        # This allows each agent to build upon information from previous ones
        agent_order = self.analysis.get("needed_agents", ["weather", "places", "hotel", "food", "budget", "itinerary"])

        for agent_name in agent_order:
            if agent_name == "weather" and weather_agent is not None:
                # Get weather information
                weather_result = weather_agent.get_weather_info(
                    self.analysis['destination'],
                    self.analysis['duration_days']
                )
                workflow_results["weather"] = weather_result

                # Inform main agent about the result
                self.add_to_history("assistant", f"Weather agent returned: {str(weather_result)[:200]}...")

            elif agent_name == "places" and places_agent is not None:
                # Get places/attractions information
                places_result = places_agent.find_places(
                    self.analysis['destination'],
                    self.analysis['duration_days']
                )
                workflow_results["places"] = places_result

                # Inform main agent about the result
                self.add_to_history("assistant", f"Places agent returned: {str(places_result)[:200]}...")

            elif agent_name == "hotel" and hotel_agent is not None:
                # Get hotel information
                hotel_result = hotel_agent.find_hotels(
                    self.analysis['destination'],
                    self.analysis['num_people'],
                    self.analysis['duration_days']
                )
                workflow_results["hotel"] = hotel_result

                # Inform main agent about the result
                self.add_to_history("assistant", f"Hotel agent returned: {str(hotel_result)[:200]}...")

            elif agent_name == "budget" and budget_agent is not None:
                # Calculate budget based on information from other agents
                budget_result = budget_agent.calculate_budget(
                    self.analysis['destination'],
                    self.analysis['num_people'],
                    self.analysis['duration_days'],
                    workflow_results.get("weather", {}),
                    workflow_results.get("hotel", {}),
                    workflow_results.get("places", {}),
                    workflow_results.get("food", {})
                )
                workflow_results["budget"] = budget_result

                # Inform main agent about the result
                self.add_to_history("assistant", f"Budget agent returned: {str(budget_result)[:200]}...")

            elif agent_name == "itinerary" and itinerary_agent is not None:
                # Create itinerary based on information from other agents
                itinerary_result = itinerary_agent.create_itinerary(
                    self.analysis['destination'],
                    self.analysis['duration_days'],
                    workflow_results.get("weather", {}),
                    workflow_results.get("places", {}),
                    workflow_results.get("budget", {})
                )
                workflow_results["itinerary"] = itinerary_result

                # Inform main agent about the result
                self.add_to_history("assistant", f"Itinerary agent returned: {str(itinerary_result)[:200]}...")

            elif agent_name == "food" and food_agent is not None:
                # Get food information
                food_result = food_agent.find_food_recommendations(
                    self.analysis['destination'],
                    self.analysis['duration_days']
                )
                workflow_results["food"] = food_result

                # Inform main agent about the result
                self.add_to_history("assistant", f"Food agent returned: {str(food_result)[:200]}...")

        # Step 3: Synthesize results and create final response
        # Truncate workflow results to avoid token limits
        def truncate_for_prompt(data, max_length=500):
            if not data or data == 'Not available':
                return data
            str_data = str(data)
            if len(str_data) <= max_length:
                return str_data
            return str_data[:max_length] + "... [truncated]"

        synthesis_prompt = f"""
        Based on the user's original request: "{user_query}"

        And the information gathered from specialist agents:
        - Weather: {truncate_for_prompt(workflow_results.get('weather', 'Not available'), 1000)}
        - Hotels: {truncate_for_prompt(workflow_results.get('hotel', 'Not available'), 2000)}
        - Places: {truncate_for_prompt(workflow_results.get('places', 'Not available'), 2000)}
        - Food: {truncate_for_prompt(workflow_results.get('food', 'Not available'), 2000)}
        - Budget: {truncate_for_prompt(workflow_results.get('budget', 'Not available'), 1000)}
        - Itinerary: {truncate_for_prompt(workflow_results.get('itinerary', 'Not available'), 2500)}

        Create a comprehensive travel plan summary. YOU MUST RESPOND ONLY WITH VALID JSON.
        
        CRITICAL INSTRUCTIONS:
        1. Keep descriptions detailed but concise.
        2. DO NOT exceed your output limit.
        3. Display all prices strictly in INR (₹). Convert any USD or foreign currency to INR (assume 1 USD ≈ 83 INR).
        4. Do NOT include any star ratings, numerical ratings, or review scores (e.g., remove "4★", "4.5/5", "3-star") for ANY hotels or places. Focus ONLY on amenities and descriptions.

        Use exactly this schema:
        {{
            "overview": "Short summary.",
            "weather": {{"summary": "...", "details": "..."}},
            "budget": {{"total": "₹...", "breakdown": {{"hotels": "₹...", "food": "₹..."}}}},
            "hotels": [
                {{"name": "...", "description": "...", "price": "₹..."}}
            ],
            "food": [
                {{"name": "...", "description": "...", "price": "₹..."}}
            ],
            "places": [
                {{"name": "...", "description": "...", "highlight": "..."}}
            ],
            "itinerary": [
                {{"day": 1, "title": "...", "activities": ["...", "..."]}}
            ]
        }}
        """

        final_response = self.get_completion(synthesis_prompt, system_msg)
        return final_response

    def _create_fallback_analysis(self, user_query: str) -> Dict[str, Any]:
        """
        Create a fallback analysis when the LLM fails to produce valid JSON.
        Uses simple regex extraction for common patterns.
        """
        # Simple fallback - extract destination and basic info
        destination = "Manali"  # default
        duration_days = 5       # default
        num_people = 2          # default
        budget = None

        # Try to extract destination (look for "to [destination]" or "in [destination]")
        destination_match = re.search(r'(?:to|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', user_query, re.IGNORECASE)
        if destination_match:
            destination = destination_match.group(1)

        # Try to extract duration (look for "\d+-day" or "\d+ day")
        duration_match = re.search(r'(\d+)\s*-?\s*day', user_query, re.IGNORECASE)
        if duration_match:
            duration_days = int(duration_match.group(1))

        # Try to extract number of people (look for "\d+ people" or "\d+ person")
        people_match = re.search(r'(\d+)\s*(?:people|persons?)', user_query, re.IGNORECASE)
        if people_match:
            num_people = int(people_match.group(1))

        # Try to extract budget (look for "under ₹\d+" or "budget of ₹\d+")
        budget_match = re.search(r'(?:under|budget\s+of\s+)?₹?(\d+(?:,\d+)*)', user_query, re.IGNORECASE)
        if budget_match:
            budget = f"₹{budget_match.group(1)}"

        return {
            "destination": destination,
            "duration_days": duration_days,
            "num_people": num_people,
            "budget": budget,
            "preferences": [],
            "needed_agents": ["weather", "places", "hotel", "budget", "itinerary"]
        }