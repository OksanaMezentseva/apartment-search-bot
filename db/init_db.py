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
CREATE_EXTENSION_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;
"""

CREATE_TABLE_SQL = """
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

CREATE_INDEX_SQL = """
-- Drop old index if exists (optional cleanup)
DROP INDEX IF EXISTS idx_embedding_cosine;

-- Create new vector index if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'idx_embedding_cosine'
    ) THEN
        CREATE INDEX idx_embedding_cosine
        ON apartments USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    END IF;
END$$;
"""

async def init_db():
    conn = None

    # Retry loop for database connection
    for i in range(10):
        try:
            conn = await asyncpg.connect(**DB_SETTINGS)
            print(f"✅ Connected to DB (attempt {i+1})")
            break
        except Exception as e:
            print(f"❌ DB not ready (attempt {i+1}): {e}")
            await asyncio.sleep(2)
    else:
        raise RuntimeError("❌ Could not connect to database after 10 attempts")

    # Create extension
    await conn.execute(CREATE_EXTENSION_SQL)

    # Create table if not exists
    await conn.execute(CREATE_TABLE_SQL)

    # Create index if not exists
    await conn.execute(CREATE_INDEX_SQL)

    await conn.close()
    print("✅ Database initialized: extension, table, and index")

if __name__ == "__main__":
    asyncio.run(init_db())