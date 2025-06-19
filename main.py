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

# Set up logging
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

# Format apartment details into readable message
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

# Async helper for running search
async def handle_apartment_search(filters: dict) -> list:
    conn = await asyncpg.connect(**DB_SETTINGS)
    try:
        apartments = await search_apartments(conn, filters, filters)
    finally:
        await conn.close()
    return apartments

# Streamlit page configuration
st.set_page_config(page_title="Apartment Finder Bot")
st.title("🏠 Apartment Search Assistant")

# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = []

if "trigger_search" not in st.session_state:
    st.session_state.trigger_search = False

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Chat input field
user_input = st.chat_input("Describe the apartment you're looking for...")

# If user submits input, store and trigger search
if user_input:
    st.session_state.user_input = user_input
    st.session_state.trigger_search = True

# Process search if triggered
if st.session_state.trigger_search:
    st.session_state.trigger_search = False
    query = st.session_state.user_input
    st.session_state.chat.append(("user", query))
    st.chat_message("user").markdown(query)

    # Step 1: Extract apartment filters
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
        st.chat_message("assistant").markdown(assistant_msg)
    else:
        filters = result["arguments"]
        logger.info(f"Filters passed to DB search: {filters}")

        try:
            apartments = asyncio.run(handle_apartment_search(filters))
        except Exception as e:
            logger.exception("❌ Database error")
            assistant_msg = "⚠️ An error occurred while accessing the database."
            st.session_state.chat.append(("assistant", assistant_msg))
            st.chat_message("assistant").markdown(assistant_msg)
            apartments = []

        if not apartments:
            no_result_msg = "🔍 No apartments matched your request."
            st.session_state.chat.append(("assistant", no_result_msg))
            st.chat_message("assistant").markdown(no_result_msg)
        else:
            found_msg = f"🏘️ Found {len(apartments)} apartment(s) matching your request:"
            st.session_state.chat.append(("assistant", found_msg))
            st.chat_message("assistant").markdown(found_msg)

            for apt in apartments:
                text = format_apartment(apt)
                st.session_state.chat.append(("assistant", text))
                st.chat_message("assistant").markdown(text)

# Display full chat history
for role, msg in st.session_state.chat:
    if role in {"user", "assistant"}:
        st.chat_message(role).markdown(msg)