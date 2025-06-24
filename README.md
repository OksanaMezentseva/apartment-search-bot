# 🏡 Apartment Search Bot

A simple chatbot powered by **Streamlit**, **OpenAI embeddings**, and **PostgreSQL + PGVector**, helping users find apartments by describing them in natural language.

---

## 🚀 Features

* 🔍 Search by structured fields: location, rooms, beds, price, etc.
* 🐾 Understands soft constraints like “pet-friendly”, “with a pool”, “no smoking”
* 🧐 Semantic reranking using OpenAI embeddings + PGVector
* 💬 Chat interface built with Streamlit
* 🐳 Fully containerized with Docker (app + PostgreSQL)

---

## ⚙️ Tech Stack

* Python 3.10+
* [Streamlit](https://streamlit.io/)
* [OpenAI API](https://platform.openai.com/)
* PostgreSQL + [PGVector](https://github.com/pgvector/pgvector)
* AsyncPG (async database access)
* Docker + Docker Compose

---

## 🧱 Project Structure

```
.
├── db/
│   ├── generated_apartments.json     # Apartment dataset
│   ├── init_db.py                    # Table creation and PGVector extension
│   └── populate_db_from_json.py      # Insert apartments and generate embeddings
├── main.py                           # Streamlit chatbot UI
├── openai_client.py                  # GPT function-calling extraction logic
├── search_utils.py                   # SQL + PGVector rerank logic
├── entrypoint.sh                     # App bootstrap script
├── Dockerfile                        # Docker app image build file
├── docker-compose.yml                # Multi-service container setup (app + DB)
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables (local only)
├── .env.example                      # Template for .env file
├── .gitignore                        # Files ignored by Git
├── .dockerignore                     # Files ignored during Docker build
└── README.md                         # This file
```

---

## 🐳 Getting Started (with Docker)

### 1. Create your `.env` file

Copy the example:

```bash
cp .env.example .env
```

Edit `.env` and fill in your actual OpenAI key:

```env
OPENAI_API_KEY=your_openai_key_here
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=apartments_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
```

---

### 2. Launch everything with Docker

```bash
docker-compose up --build
```

This will:

* Build the image for the Streamlit app
* Start a PostgreSQL container with PGVector
* Initialize the DB (create tables and insert sample data)
* Start Streamlit at `http://localhost:8501`

📅 No manual database setup required.

---

### 3. Interact with the chatbot

Visit: [http://localhost:8501](http://localhost:8501)

Try prompts like:

* `Looking for a pet-friendly apartment in Kyiv with 2 beds`
* `I need a studio in Odesa with a pool and no kitchen`
* `Family-friendly flat in Lviv, no smoking, parking included`

---

## 💬 FAQ

**Q: How does the vector search work?**
A: Textual apartment descriptions are embedded via OpenAI’s API. Incoming user queries are embedded and matched using PGVector (cosine similarity).

**Q: Will it recreate the DB every time?**
A: No — the app creates a `.db-initialized` file on first successful run. On restart, it skips DB setup.

---

## 👩‍💼 Author

**Oksana Mezentseva**
GitHub: [@OksanaMezentseva](https://github.com/OksanaMezentseva)

> A pet project to explore vector search, NLP, and real-world chat UX using OpenAI + PGVector + Docker + Streamlit.
