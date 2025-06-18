import asyncio
import asyncpg
import os
import json
from dotenv import load_dotenv
from openai import OpenAI  # new-style client

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database credentials from .env
DB_SETTINGS = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}

# Path to JSON file with apartment data
JSON_PATH = os.path.join(os.path.dirname(__file__), "generated_apartments.json")

async def populate_database():
    # Load apartment data from JSON file
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        apartments = [json.loads(line) for line in f]

    # Connect to PostgreSQL database
    conn = await asyncpg.connect(**DB_SETTINGS)

    for apt in apartments:
        # Generate embedding using the OpenAI client (new API)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=apt["description"]
        )
        embedding = response.data[0].embedding
        embedding = "[" + ",".join([str(x) for x in embedding]) + "]"

        # Insert apartment record into the database
        await conn.execute("""
            INSERT INTO apartments (
                location, rooms, price, area, floor,
                beds, has_wifi, has_parking, has_kitchen,
                description, embedding
            ) VALUES (
                $1, $2, $3, $4, $5,
                $6, $7, $8, $9,
                $10, $11
            )
        """, apt["location"], apt["rooms"], apt["price"], apt["area"], apt["floor"],
             apt["beds"], apt["has_wifi"], apt["has_parking"], apt["has_kitchen"],
             apt["description"], embedding)

    print(f"✅ Successfully inserted {len(apartments)} apartments into the database.")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(populate_database())