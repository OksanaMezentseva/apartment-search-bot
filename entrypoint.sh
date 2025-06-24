#!/bin/bash

INIT_FLAG="/app/.db-initialized"

# Initialize DB only once — but only if scripts succeed
if [ ! -f "$INIT_FLAG" ]; then
  echo "📦 Initializing database..."
  echo "⏳ Waiting for DB to be ready..."
  sleep 5

  # Run init_db and populate — and exit on failure
  if python db/init_db.py && python db/populate_db_from_json.py; then
    echo "✅ DB initialized"
    touch "$INIT_FLAG"
  else
    echo "❌ DB setup failed. Will retry next time."
    exit 1
  fi
else
  echo "✅ Database already initialized. Skipping DB setup."
fi

# Run Streamlit app
streamlit run main.py --server.port=8501 --server.address=0.0.0.0