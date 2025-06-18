import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Define database connection parameters
DB_SETTINGS = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}

# SQL commands to initialize database: install PGVector and create table
CREATE_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS apartments (
    id SERIAL PRIMARY KEY,
    location TEXT,
    rooms INTEGER,
    price NUMERIC,
    area NUMERIC,
    floor INTEGER,
    beds INTEGER,
    has_wifi BOOLEAN,
    has_parking BOOLEAN,
    has_kitchen BOOLEAN,
    description TEXT,
    embedding VECTOR(1536)
);
"""

async def init_db():
    # Connect to the PostgreSQL database
    conn = await asyncpg.connect(**DB_SETTINGS)
    # Execute the SQL command
    await conn.execute(CREATE_SQL)
    print("✅ Database initialized: extension and apartments table created.")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(init_db())