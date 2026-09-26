import streamlit as st
import sys
import os
import json
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.main_agent import MainAgent
from agents.weather_agent import WeatherAgent
from agents.hotel_agent import HotelAgent
from agents.places_agent import PlacesAgent
from agents.food_agent import FoodAgent
from agents.budget_agent import BudgetAgent
from agents.itinerary_agent import ItineraryAgent

# Set page config
st.set_page_config(page_title="पर्यटक | Pryatak", page_icon="🌍", layout="wide")

# Custom CSS for Anti-slop frontend styling
st.markdown("""
<style>
    /* Reset Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Base typography & color */
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Geist', sans-serif !important;
    }
    
    /* Layout & Styling */
    .stApp {
        background-color: #fafafa;
        color: #111111;
    }
    
    /* Typography Overrides */
    h1 {
        font-size: 4.5rem !important;
        font-weight: 500 !important;
        letter-spacing: -0.04em !important;
        line-height: 1 !important;
        color: #111;
        margin-bottom: 0.5rem !important;
    }
    
    h2, h3 {
        font-weight: 500 !important;
        letter-spacing: -0.02em !important;
        color: #111;
    }
    
    p {
        font-size: 1.125rem !important;
        line-height: 1.5 !important;
        color: #555;
    }
    
    /* Button Styling (Clean, sharp, no default radius) */
    .stButton > button {
        background-color: #111111;
        color: #ffffff;
        border: none;
        border-radius: 0px !important;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 1rem;
        letter-spacing: 0.02em;
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.2s;
        width: auto !important;
        box-shadow: none !important;
    }
    
    .stButton > button:hover {
        background-color: #333333;
        transform: translateY(-1px);
        color: #ffffff !important;
        border: none !important;
    }
    
    .stButton > button:active {
        transform: scale(0.99);
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        border-radius: 0px !important;
        border: 1px solid #e5e5e5 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem;
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #111111 !important;
        box-shadow: none !important;
    }
    
    /* Markdown container for output */
    .output-container {
        padding: 2rem;
        background: #ffffff;
        border: 1px solid #e5e5e5;
        margin-top: 2rem;
    }
    
    /* Remove standard padding top */
    .block-container {
        padding-top: 4rem !important;
        max-width: 1400px;
    }
    
    /* Clean dividers */
    hr {
        border-top: 1px solid #e5e5e5 !important;
        margin: 3rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize agents only once using session state
if "agents_initialized" not in st.session_state:
    try:
        st.session_state.main_agent = MainAgent()
        st.session_state.weather_agent = WeatherAgent()
        st.session_state.hotel_agent = HotelAgent()
        st.session_state.places_agent = PlacesAgent()
        st.session_state.food_agent = FoodAgent()
        st.session_state.budget_agent = BudgetAgent()
        st.session_state.itinerary_agent = ItineraryAgent()
        st.session_state.agents_initialized = True
    except Exception as e:
        st.error(f"Failed to initialize agents. Make sure API keys are configured properly in .env.\\nError: {e}")

# Asymmetric Split Layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("<h1>पर्यटक</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.5rem; font-weight: 300; margin-top:-0.5rem; margin-bottom: 2rem; color:#555;'>Pryatak. Multi-agent travel orchestration.</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='max-width: 50ch; margin-bottom: 2.5rem; font-size: 1rem;'>Coordinate weather, hotels, destinations, and dining through an ensemble of specialized AI agents. Enter your parameters to generate a complete itinerary.</p>", unsafe_allow_html=True)
    
    user_query = st.text_input(
        label="Travel Request",
        placeholder="Plan a 5-day trip to Manali for 2 people under ₹30,000",
        label_visibility="collapsed"
    )
    
    submit_btn = st.button("Generate itinerary")

with col2:
    # A real photographic placeholder for the "minimalist / editorial" design read
    st.markdown("""
    <div style="height: 100%; min-height: 450px; overflow: hidden; background: #e5e5e5;">
        <img src="https://picsum.photos/seed/himalayas-travel/800/1000" style="width: 100%; height: 100%; object-fit: cover; filter: grayscale(80%) contrast(1.1); mix-blend-mode: multiply; opacity: 0.9;" alt="Travel landscape">
    </div>
    """, unsafe_allow_html=True)

if submit_btn and user_query:
    st.markdown("<hr>", unsafe_allow_html=True)
    with st.spinner("Orchestrating agents..."):
        if "agents_initialized" in st.session_state:
            try:
                final_plan_raw = st.session_state.main_agent.orchestrate_travel_plan(
                    user_query=user_query,
                    weather_agent=st.session_state.weather_agent,
                    hotel_agent=st.session_state.hotel_agent,
                    places_agent=st.session_state.places_agent,
                    budget_agent=st.session_state.budget_agent,
                    itinerary_agent=st.session_state.itinerary_agent,
                    food_agent=st.session_state.food_agent
                )
                
                # Replace em-dashes or en-dashes from final plan if any (taste-skill rule)
                final_plan_raw = final_plan_raw.replace("—", "-").replace("–", "-")
                
                # Robustly extract JSON by finding the first '{' and last '}'
                json_str = final_plan_raw
                start_idx = final_plan_raw.find('{')
                end_idx = final_plan_raw.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = final_plan_raw[start_idx:end_idx+1]
                
                try:
                    plan_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    # Sometimes LLMs use python comments or invalid trailing commas, let's try a strict clean
                    # If it fails here, the outer try/except will catch it
                    raise e
                
                st.markdown(f"""
                <div class="output-container" style="padding-bottom: 0;">
                    <h3 style="margin-top:0; margin-bottom:0.5rem; font-size: 1.5rem;">{plan_data.get('overview', 'Travel Itinerary')}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Interactive UI
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["Itinerary", "Hotels", "Places", "Food", "Budget & Weather"])
                
                with tab1:
                    st.markdown("<br>", unsafe_allow_html=True)
                    for day in plan_data.get("itinerary", []):
                        with st.expander(f"Day {day.get('day')}: {day.get('title')}", expanded=True):
                            for activity in day.get("activities", []):
                                st.markdown(f"- {activity}")
                
                with tab2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### 🏨 Accommodation")
                    for hotel in plan_data.get("hotels", []):
                        st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #eaeaea; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
                                <h4 style="margin: 0; font-size: 1.1rem; color: #111;">{hotel.get('name')}</h4>
                                <span style="font-weight: 600; color: #2e7d32; background: #e8f5e9; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.9rem;">{hotel.get('price')}</span>
                            </div>
                            <p style="margin: 0; color: #555; line-height: 1.5;">{hotel.get('description')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with tab3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    for place in plan_data.get("places", []):
                        st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #eaeaea; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                            <h4 style="margin: 0 0 0.5rem 0; font-size: 1.1rem; color: #111;">{place.get('name')}</h4>
                            <p style="margin: 0 0 0.5rem 0; color: #6366f1; font-weight: 500; font-size: 0.95rem;">Highlight: {place.get('highlight')}</p>
                            <p style="margin: 0; color: #555; line-height: 1.5;">{place.get('description')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with tab4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("#### 🍽️ Food & Dining")
                    for food in plan_data.get("food", []):
                        st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #eaeaea; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
                                <h4 style="margin: 0; font-size: 1.1rem; color: #111;">{food.get('name')}</h4>
                                <span style="font-weight: 600; color: #b45309; background: #fef3c7; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.9rem;">{food.get('price')}</span>
                            </div>
                            <p style="margin: 0; color: #555; line-height: 1.5;">{food.get('description')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with tab5:
                    st.markdown("<br>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("#### 💰 Budget")
                        st.metric("Estimated Total", plan_data.get("budget", {}).get("total", "N/A"))
                        st.markdown("**Breakdown:**")
                        for k, v in plan_data.get("budget", {}).get("breakdown", {}).items():
                            st.markdown(f"- {k.title()}: {v}")
                    with c2:
                        st.markdown("#### 🌦️ Weather")
                        st.markdown(f"**{plan_data.get('weather', {}).get('summary', '')}**")
                        st.markdown(f"*{plan_data.get('weather', {}).get('details', '')}*")
                # Debug removed per user request
                
            except json.JSONDecodeError:
                # Fallback gracefully if the agent outputs beautiful Markdown instead of strict JSON
                st.markdown(final_plan_raw)
            except Exception as e:
                st.error(f"Error during planning: {str(e)}")
                st.info("Please check your API keys and internet connection.")
        else:
            st.error("Agents failed to initialize. Please check your environment variables.")
