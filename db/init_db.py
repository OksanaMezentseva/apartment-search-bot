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

# SQL commands to initialize database
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

DROP INDEX IF EXISTS idx_embedding_cosine;
CREATE INDEX idx_embedding_cosine
ON apartments USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
"""

async def init_db():
    # Connect to the PostgreSQL database
    conn = await asyncpg.connect(**DB_SETTINGS)
    # Execute the SQL initialization
    await conn.execute(CREATE_SQL)
    print("✅ Database initialized: extension, table, and vector index created.")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(init_db())