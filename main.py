import os
import asyncpg
import logging
import streamlit as st
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from openai_client import extract_apartment_query
from search_utils import search_apartments

# Allow nested async loops (required for Streamlit + asyncpg)
nest_asyncio.apply()

# Load environment variables from .env
load_dotenv()

# Set up logger
logger = logging.getLogger("streamlit_bot")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Database connection settings
DB_SETTINGS = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}

# Format apartment info as markdown string
def format_apartment(apartment: dict) -> str:
    return (
        f"📍 **Location:** {apartment['location']}\n"
        f"🛏️ **Rooms:** {apartment['rooms']} | **Beds:** {apartment['beds']}\n"
        f"📐 **Area:** {apartment['area']:.1f} m² | **Floor:** {apartment['floor']}\n"
        f"💵 **Price:** ${round(apartment['price'], 2)} per night\n"
        f"📶 **Wi-Fi:** {'Yes' if apartment['has_wifi'] else 'No'}\n"
        f"🅿️ **Parking:** {'Yes' if apartment['has_parking'] else 'No'}\n"
        f"🍽️ **Kitchen:** {'Yes' if apartment['has_kitchen'] else 'No'}\n\n"
        f"_{apartment['description']}_"
    )

# Async helper to run search
async def handle_apartment_search(filters: dict) -> list:
    conn = await asyncpg.connect(**DB_SETTINGS)
    try:
        apartments = await search_apartments(conn, filters, filters)
    finally:
        await conn.close()
    return apartments

# Streamlit app setup
st.set_page_config(page_title="Apartment Finder Bot")
st.title("🏠 Apartment Search Assistant")

# Initialize session state if needed
if "chat" not in st.session_state:
    st.session_state.chat = []
if "trigger_search" not in st.session_state:
    st.session_state.trigger_search = False
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "search_result" not in st.session_state:
    st.session_state.search_result = None

# Input field for chat
user_input = st.chat_input("Describe the apartment you're looking for...")

# Handle new user message
if user_input:
    st.session_state.user_input = user_input
    st.session_state.chat.append(("user", user_input))
    st.session_state.trigger_search = True
    st.session_state.search_result = None  # Reset result cache

# Run search only once per input
if st.session_state.trigger_search and st.session_state.search_result is None:
    st.session_state.trigger_search = False
    query = st.session_state.user_input

    with st.spinner("🤖 Processing your request..."):
        result = asyncio.run(extract_apartment_query(query))

    logger.info(f"GPT Result: {result}")

    if not result:
        assistant_msg = (
            "❌ I couldn't understand your request.\n"
            "Please try to include:\n"
            "- City or location (e.g., Lviv, Kyiv)\n"
            "- Number of rooms or beds\n"
            "- Desired amenities (Wi-Fi, kitchen, parking, pets, etc.)"
        )
        st.session_state.chat.append(("assistant", assistant_msg))
    else:
        filters = result["arguments"]
        logger.info(f"Filters passed to DB search: {filters}")

        try:
            apartments = asyncio.run(handle_apartment_search(filters))
            if not apartments:
                st.session_state.chat.append(("assistant", "🔍 No apartments matched your request."))
            else:
                st.session_state.chat.append(("assistant", f"🏘️ Found {len(apartments)} apartment(s) matching your request:"))
                for apt in apartments:
                    text = format_apartment(apt)
                    st.session_state.chat.append(("assistant", text))
        except Exception as e:
            logger.exception("❌ Database error")
            st.session_state.chat.append(("assistant", "⚠️ An error occurred while accessing the database."))

    st.session_state.search_result = True  # Prevent re-run

# Display full chat history (only once)
for role, msg in st.session_state.chat:
    if role in {"user", "assistant"}:
        st.chat_message(role).markdown(msg)