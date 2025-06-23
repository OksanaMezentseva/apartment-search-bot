from typing import List, Tuple
import asyncpg
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import numpy as np
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up logging (console + file)
logger = logging.getLogger("apartment_search")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("apartment_bot.log")
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Fields that can be used in SQL filters
SQL_FIELDS = {
    "location", "rooms", "beds", "area", "floor",
    "price", "has_wifi", "has_parking", "has_kitchen",
    "min_price", "max_price"
}

# Patterns to reject incompatible apartments based on text
NEGATION_PATTERNS = {
    "allows_pets": [
        "no pets",
        "pets are not allowed",
        "not pet-friendly",
        "pets prohibited"
    ],
    "has_pool": [
        "no pool",
        "pool not available"
    ],
    "allows_smoking": [
        "no smoking",
        "smoking not allowed",
        "non-smoking",
        "smoke-free"
    ],
    "allows_parties": [
        "no parties",
        "parties not allowed",
        "no alcohol"
    ],
    "allows_children": [
        "no children",
        "children not allowed",
        "not suitable for children",
        "no kids"
    ]
}

# Build SQL query and parameters based on filters
def build_sql_query(filters: dict) -> Tuple[str, list]:
    sql = "SELECT * FROM apartments WHERE TRUE"
    values = []

    # Location filter
    if "location" in filters:
        sql += f" AND location ILIKE ${len(values) + 1}"
        values.append(f"%{filters['location']}%")

    # Numeric filters
    for field in ["rooms", "beds", "area", "floor", "price", "min_price", "max_price"]:
        if field in filters:
            operator = ">=" if field == "min_price" else "<=" if field in {"max_price", "price"} else "="
            column = field if field not in ["min_price", "max_price"] else "price"
            sql += f" AND {column} {operator} ${len(values) + 1}"
            values.append(filters[field])

    # Boolean filters
    for field in ["has_wifi", "has_parking", "has_kitchen"]:
        if field in filters:
            sql += f" AND {field} IS {'TRUE' if filters[field] else 'FALSE'}"

    sql += " ORDER BY price ASC LIMIT 20"
    return sql, values

# Separate SQL filters from additional semantic properties
def split_filters(filters: dict) -> Tuple[dict, List[str]]:
    sql_filters = {}
    extra_keys = []
    for key, value in filters.items():
        if key in SQL_FIELDS:
            sql_filters[key] = value
        else:
            extra_keys.append(key)
    return sql_filters, extra_keys

# Build text representation of filters for embedding query
def filters_to_embedding_text(filters: dict) -> str:
    parts = []

    # Include numeric values
    for field in ["beds", "rooms", "floor"]:
        if field in filters:
            parts.append(f"{filters[field]} {field}")

    # Boolean handling
    for key, value in filters.items():
        if key in {"beds", "rooms", "floor"}:
            continue

        readable = key.replace("has_", "").replace("allows_", "").replace("_", " ")

        if key.startswith("has_"):
            if value:
                parts.append(f"has {readable}")
            else:
                parts.append(f"no {readable}")

        elif key.startswith("allows_"):
            if value:
                if readable in {"pets", "children", "kids"}:
                    parts.append(f"{readable}-friendly")
                else:
                    parts.append(f"{readable} allowed")
            else:
                parts.append(f"{readable} not allowed")

    return ", ".join(parts)

# Rerank apartments using cosine similarity (embedding-based)
def rerank_by_vector_similarity(apartments: List[asyncpg.Record], query_vector: list, top_k: int = 3) -> List[asyncpg.Record]:
    scored = []
    for apt in apartments:
        emb = apt["embedding"]
        if isinstance(emb, str):
            emb = json.loads(emb)
        vec = np.array(emb, dtype=np.float32)
        similarity = float(np.dot(query_vector, vec))
        scored.append((similarity, apt))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [apt for _, apt in scored[:top_k]]

# Post-filter apartments to remove logically incompatible results
def reject_if_negated(apartment, filters) -> bool:
    desc = apartment["description"].lower()

    for key, patterns in NEGATION_PATTERNS.items():
        if filters.get(key) is True:
            for p in patterns:
                if p in desc:
                    return True
    return False

# Main apartment search function: SQL filtering + PGVector rerank
async def search_apartments(conn: asyncpg.Connection, filters: dict, query_text: str) -> List[asyncpg.Record]:
    # Separate SQL and semantic filters
    sql_filters, extra_keys = split_filters(filters)

    # Build SQL query
    sql_query, sql_values = build_sql_query(sql_filters)
    logger.info(f"📄 SQL Query: {sql_query}")
    logger.info(f"📦 SQL Params: {sql_values}")

    # Execute SQL query
    filtered_results = await conn.fetch(sql_query, *sql_values)
    logger.info(f"🔢 SQL returned {len(filtered_results)} result(s)")

    # Convert filters into text input for embedding
    embedding_input = filters_to_embedding_text(filters)
    logger.info(f"🧠 Embedding input text: {embedding_input}")

    # Get embedding vector from OpenAI
    response = client.embeddings.create(
        input=embedding_input,
        model="text-embedding-3-small"
    )
    query_vector = response.data[0].embedding

    # Rerank SQL results using PGVector similarity
    top_results = rerank_by_vector_similarity(filtered_results, query_vector, top_k=10)

    # Apply post-filter to reject logically incompatible results
    filtered_top_results = [apt for apt in top_results if not reject_if_negated(apt, filters)]

    logger.info(f"🏁 Returning top-{len(filtered_top_results)} after post-filtering")
    return filtered_top_results[:3]  # Limit to top N