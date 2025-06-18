import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define function schema
function_definitions = [
    {
        "name": "search_apartments",
        "description": "Search for apartments based on user preferences",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City or district"},
                "rooms": {"type": "integer", "description": "Number of rooms"},
                "has_wifi": {"type": "boolean", "description": "Wi-Fi needed or not"},
                "has_parking": {"type": "boolean", "description": "Parking needed or not"},
                "has_kitchen": {"type": "boolean", "description": "Kitchen needed or not"},
                "min_price": {"type": "number", "description": "Minimum price in USD"},
                "max_price": {"type": "number", "description": "Maximum price in USD"},
            },
            "required": ["location"]
        }
    }
]

# Core function to get structured search parameters from OpenAI
def extract_apartment_query(user_input: str):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts apartment search preferences from a user's request."},
            {"role": "user", "content": user_input}
        ],
        functions=function_definitions,
        function_call="auto"
    )

    choice = response.choices[0]
    if choice.finish_reason == "function_call":
        func_call = choice.message.function_call
        return {
            "name": func_call.name,
            "arguments": func_call.arguments
        }
    else:
        return None