import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up logger for diagnostics
logger = logging.getLogger("openai_client")
logger.setLevel(logging.INFO)

# Avoid duplicate handlers if file is reloaded
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(stream_handler)

# Define function schema for GPT to call
function_definitions = [
    {
        "name": "search_apartments",
        "description": "Search for apartments based on user preferences",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City or district"},
                "rooms": {"type": "integer", "description": "Number of rooms"},
                "beds": {"type": "integer", "description": "Minimum number of beds"},
                "area": {"type": "number", "description": "Minimum area in square meters"},
                "floor": {"type": "integer", "description": "Preferred floor"},
                "price": {"type": "number", "description": "Target price"},
                "min_price": {"type": "number", "description": "Minimum price in USD"},
                "max_price": {"type": "number", "description": "Maximum price in USD"},
                "has_wifi": {"type": "boolean", "description": "Wi-Fi required or not"},
                "has_parking": {"type": "boolean", "description": "Parking required or not"},
                "has_kitchen": {"type": "boolean", "description": "Kitchen required or not"}
            },
            "required": ["location"],
            "additionalProperties": True  # Allow GPT to include non-schema fields like pool, pets
        }
    }
]

# System message to guide GPT behavior
SYSTEM_PROMPT = (
    "You are a function-calling assistant that helps users search for apartments. "
    "Always call the function 'search_apartments' and include all relevant fields. "
    "If the user mentions any extra features like 'pool', 'balcony', 'pets', or others not defined in the schema, "
    "just add them directly as boolean fields, like 'has_pool': true, 'allows_pets': false. "
    "Do NOT use 'extra_fields' or any other nested structure."
)

# Run GPT function extraction
async def extract_apartment_query(user_input: str):
    logger.info(f"📨 User query: {user_input}")

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        functions=function_definitions,
        function_call="auto"  # Let GPT decide if the function should be called
    )

    logger.info("📩 GPT response received")

    choice = response.choices[0]
    if choice.finish_reason == "function_call":
        func_call = choice.message.function_call
        logger.info(f"🧠 Function called: {func_call.name}")
        arguments = json.loads(func_call.arguments)
        logger.info(f"🧾 Extracted arguments: {arguments}")
        return {
            "name": func_call.name,
            "arguments": arguments
        }

    logger.warning("⚠️ GPT did not call any function")
    return None