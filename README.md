# Multi-Agent Travel Planning System

## Overview
This is a Supervisor/Worker architecture-based travel planning system that coordinates multiple specialized AI agents to create comprehensive travel plans. The system uses the Groq API (with Llama models) for reasoning and integrates with various travel APIs to gather real-time information.

## System Architecture

### Main Components
1. **Main Agent (Supervisor)** - Orchestrates the workflow, analyzes user requests, delegates tasks to specialist agents, and synthesizes final responses
2. **Specialist Worker Agents** - Each agent handles a specific domain:
   - Weather Agent: Retrieves weather forecasts using Open-Meteo API
   - Hotel Agent: Finds accommodation options using Tavily search API
   - Places Agent: Identifies tourist attractions using Overpass/OpenStreetMap and Tavily APIs
   - Food Agent: Provides restaurant and food recommendations using Tavily search API
   - Budget Agent: Calculates trip budget estimates based on data from other agents
   - Itinerary Agent: Creates day-by-day travel schedules using information from all other agents

### Data Flow
```
User Query → Main Agent (Analysis) → 
[Weather Agent] → 
[Places Agent] → 
[Food Agent] → 
[Hotel Agent] → 
[Budget Agent] → 
[Itinerary Agent] → 
Main Agent (Synthesis) → Final Travel Plan
```

## Features
- **Multi-Agent Coordination**: Supervisor dynamically selects and orders agents based on user request
- **Real-Time Data Integration**: Connects to live APIs for current travel information
- **Comprehensive Planning**: Covers weather, accommodation, attractions, food, budget, and daily itinerary
- **Error Handling**: Graceful degradation when APIs fail or return limited data
- **Token Management**: Truncates large API responses to prevent LLM context overflow
- **Fallback Mechanism**: Uses regex extraction when LLM JSON parsing fails

## Files Structure
```
multi model/
├── main.py                    # Entry point - initializes agents and runs the system
├── agents/
│   ├── main_agent.py          # Supervisor agent - orchestrates workflow
│   ├── weather_agent.py       # Weather information specialist
│   ├── hotel_agent.py         # Accommodation specialist
│   ├── places_agent.py        # Tourist attractions specialist
│   ├── food_agent.py          # Food/restaurant specialist
│   ├── budget_agent.py        # Budget calculation specialist
│   └── itinerary_agent.py     # Day-by-day schedule specialist
├── utils/
│   └── api_clients.py         # Wrapper functions for all external APIs
├── .env                       # Environment variables (API keys)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## How It Works

### 1. User Input Processing
- User provides natural language travel request (e.g., "Plan a 5-day trip to Manali for 2 people under ₹30,000")
- Main Agent extracts: destination, duration, number of people, budget constraints, preferences

### 2. Agent Coordination
- Main Agent decides which specialist agents to call and in what order
- Default execution order: Weather → Places → Food → Hotel → Budget → Itinerary
- Each agent builds upon information from previous agents in the chain

### 3. Specialist Agent Functions
- **Weather Agent**: Gets forecast for destination using Open-Meteo API
- **Places Agent**: Finds attractions using Overpass (OSM) and Tavily APIs
- **Food Agent**: Searches for restaurants and local cuisine using Tavily
- **Hotel Agent**: Finds accommodation options using Tavily
- **Budget Agent**: Calculates costs based on hotel, food, activities data
- **Itinerary Agent**: Creates day-by-day schedule using weather, places, food, budget data

### 4. Response Synthesis
- Main Agent compiles results from all agents
- Sends comprehensive prompt to LLM with all gathered information
- LLM generates formatted travel plan covering:
  - Weather forecast (temperature, precipitation, conditions)
  - Accommodation options (with pricing and highlights)
  - Attractions and activities (with timing and cost estimates)
  - Food and restaurant recommendations
  - Budget breakdown (accommodation, food, activities, miscellaneous)
  - Day-by-day itinerary schedule
  - Practical tips and suggestions

## Setup & Usage

### Prerequisites
- Python 3.7+
- API keys for:
  - Groq (for LLM reasoning)
  - Tavily (for search functionality)
  - (Open-Meteo, Overpass, Nominatim are free and don't require keys)

### Installation
```bash
# Clone or copy this repository
cd multi model

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
# GROQ_API_KEY=your_groq_key_here
# TAVILY_API_KEY=your_tavily_key_here
```

### Running the System
```bash
python main.py
```

Then enter your travel request when prompted, or pipe a query directly:
```bash
echo "Plan a 3-day trip to Goa for 4 people under ₹40,000" | python main.py
```

## Example Outputs
The system generates detailed travel plans including:
- Day-by-day weather forecasts with temperature ranges and precipitation chances
- Hotel options with per-night/total costs and booking tips
- Attraction lists with suggested visit times and entry costs
- Restaurant recommendations with cuisine types and price ranges
- Budget breakdowns showing cost allocation by category
- Hour-by-hour itinerary suggestions for each day
- Packing and preparation tips based on weather and activities

## Customization
- Modify `main_agent.py` to change agent calling order or add new specialist agents
- Update `utils/api_clients.py` to integrate additional travel APIs
- Adjust prompts in agents to change output format or detail level
- Extend `requirements.txt` for additional Python dependencies

## Limitations & Considerations
- Dependent on external API availability and rate limits
- Accuracy depends on underlying API data quality and freshness
- LLM reasoning quality affects agent selection and synthesis
- Budget estimates are approximate and based on available data
- Real-time pricing may vary from actual booking costs

## Future Enhancements
- Add date parsing for actual calendar dates in weather/itinerary display
- Integrate booking APIs for direct reservations
- Add user preference learning over multiple trips
- Support for multi-destination trips
- Language localization for international users
- Interactive map integration for attractions

---
*Built with ❤️ using Claude Code and the Supervisor/Worker AI agent pattern*