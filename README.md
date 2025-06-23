# 🏡 Apartment Search Bot

A simple chatbot powered by **Streamlit**, **OpenAI embeddings**, and **PostgreSQL + PGVector** to help users find apartments by describing them in natural language.

---

## 🚀 Features

* 🔍 Search by structured fields: location, rooms, beds, price, etc.
* 🐾 Understands soft constraints like “pet-friendly”, “with a pool”, “no smoking”
* 🧐 Semantic reranking with OpenAI + PGVector
* ⚡️ Chat interface via Streamlit
* 🐿️ Runs locally with Docker (PostgreSQL inside container)

---

## ⚙️ Technologies Used

* Python 3.10+
* [Streamlit](https://streamlit.io/)
* [OpenAI API](https://platform.openai.com/)
* PostgreSQL + [PGVector](https://github.com/pgvector/pgvector)
* AsyncPG
* Docker + Docker Compose

---

## 🧱 Project Structure

```
.
├── db/
│ ├── generated_apartments.json # Apartment dataset
│ ├── init_db.py # Table + PGVector extension creation
│ └── populate_db_from_json.py # Insert apartments and generate embeddings
├── main.py # Streamlit chatbot UI
├── openai_client.py # GPT function-calling extraction logic
├── search_utils.py # SQL + PGVector rerank logic
├── docker-compose.yml # Docker setup for PostgreSQL
├── requirements.txt # Python dependencies
├── .env # Local environment config (not in repo)
├── .env.example # Template environment file
├── .gitignore # Files to ignore in Git
├── apartment_bot.log # Runtime logs
└── README.md # Project overview and setup
```

---

## 🐿️ Getting Started

### 1. Create `.env` file

Create a `.env` file in the project root with the following contents:

```
OPENAI_API_KEY=your_openai_key_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=apartments_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
```

### 2. Start PostgreSQL with Docker

```bash
docker-compose up -d
```

This will launch a local PostgreSQL container with pgvector enabled.

---

### 3. Initialize the Database

Create the `apartments` table and PGVector index:

```bash
python init_db.py
```

---

### 4. Populate the Database

Insert apartment listings from JSON and generate OpenAI embeddings:

```bash
python populate_db_from_json.py
```

---

### 5. Launch the Chatbot

Start the Streamlit app:

```bash
streamlit run main.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 💬 Example Prompts

* `Looking for a pet-friendly apartment in Kyiv with 2 beds`
* `I need a studio in Odesa with a pool and no kitchen`
* `Family-friendly flat in Lviv, no smoking, parking included`
* `Spacious apartment near city center with balcony and Wi-Fi`

---

## 👩‍💼 Author

Oksana Mezentseva
GitHub: [@OksanaMezentseva](https://github.com/OksanaMezentseva)

> A pet project to explore vector search with OpenAI + PGVector + Streamlit for real-world NLP use cases.