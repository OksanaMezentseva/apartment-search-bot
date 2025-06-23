#!/bin/bash

# Initialize DB only once
if [ ! -f "/.db-initialized" ]; then
  echo "📦 Initializing database..."
  python db/init_db.py
  python db/populate_db_from_json.py
  touch /.db-initialized
else
  echo "✅ Database already initialized. Skipping DB setup."
fi

# Run Streamlit app
streamlit run main.py --server.port=8501 --server.address=0.0.0.0