import asyncpg
import os
import json
from dotenv import load_dotenv

# Load DB config from .env
load_dotenv()

DB_SETTINGS = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}

# Parse stringified JSON arguments (from GPT function_call.arguments)
def parse_function_args(args_str: str) -> dict:
    try:
        return json.loads(args_str)
    except Exception as e:
        print(f"❌ Failed to parse function arguments: {e}")
        return {}

# Build SQL query with optional filters
def build_sql_query(params: dict) -> (str, list):
    sql = "SELECT * FROM apartments WHERE TRUE"
    values = []

    if "location" in params:
        sql += " AND location ILIKE $%d" % (len(values) + 1)
        values.append(f"%{params['location']}%")
    if "rooms" in params:
        sql += " AND rooms = $%d" % (len(values) + 1)
        values.append(params["rooms"])
    if "has_wifi" in params:
        sql += " AND has_wifi = $%d" % (len(values) + 1)
        values.append(params["has_wifi"])
    if "has_parking" in params:
        sql += " AND has_parking = $%d" % (len(values) + 1)
        values.append(params["has_parking"])
    if "has_kitchen" in params:
        sql += " AND has_kitchen = $%d" % (len(values) + 1)
        values.append(params["has_kitchen"])
    if "min_price" in params:
        sql += " AND price >= $%d" % (len(values) + 1)
        values.append(params["min_price"])
    if "max_price" in params:
        sql += " AND price <= $%d" % (len(values) + 1)
        values.append(params["max_price"])

    sql += " ORDER BY price ASC LIMIT 5"
    return sql, values

# Perform actual query and return matching apartments
async def search_apartments(args_str: str) -> list:
    params = parse_function_args(args_str)
    if not params:
        return []

    sql, values = build_sql_query(params)

    try:
        conn = await asyncpg.connect(**DB_SETTINGS)
        rows = await conn.fetch(sql, *values)
        await conn.close()

        # Convert results to list of dicts
        return [dict(row) for row in rows]

    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return []