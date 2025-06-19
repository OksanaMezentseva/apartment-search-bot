# 🏡 Telegram Apartment Search Bot

This is a Telegram bot that helps users find apartments based on structured filters (location, price, rooms, etc.) or unstructured text descriptions. The bot supports both SQL-based filtering and semantic reranking using OpenAI embeddings and PGVector.

## 🚀 Features

* 🔍 Search apartments by location, price, rooms, beds, etc.
* ✅ Filter by amenities: Wi-Fi, kitchen, parking, balcony, jacuzzi, pet-friendly
* 🧠 Semantic search using OpenAI embeddings + PGVector
* 📦 PostgreSQL database with vector support
* 🤖 Telegram interface using `aiogram`
* 🐳 Dockerized for easy deployment

## ⚙️ Technologies

* Python 3.10+
* [OpenAI API](https://platform.openai.com/)
* PostgreSQL + PGVector
* AsyncPG
* aiogram
* Docker + Docker Compose

## 🧱 Project Structure

```
.
├── main.py                  # Telegram bot logic
├── search_utils.py          # SQL builder + PGVector rerank logic
├── openai_client.py         # OpenAI client setup
├── init_db.py               # Table creation and extension setup
├── populate_db_from_json.py # Insert apartments into DB from JSON
├── create_index.py          # Create PGVector index
├── docker-compose.yml
├── requirements.txt
├── .env                     # API keys and DB config
└── README.md
```

## 🐳 Getting Started

### 1. Create `.env`

```
OPENAI_API_KEY=...
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=apartments
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
BOT_TOKEN=your_telegram_bot_token
```

### 2. Start with Docker

```bash
docker-compose up --build
```

### 3. Initialize the database

```bash
python init_db.py
```

### 4. Populate with apartments

```bash
python populate_db_from_json.py
```

### 5. Run the bot

```bash
python main.py
```

## 📨 Example Queries

* `Apartment in Lviv with 2 rooms and a balcony`
* `Pet-friendly studio in Kyiv with a jacuzzi`
* `Flat near city center with parking and Wi-Fi`


## 📢 Author

👩‍💻 [Oksana Mezentseva](https://github.com/OksanaMezentseva)

> This is a pet project to explore PGVector, OpenAI API, and building helpful Telegram bots.
