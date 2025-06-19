import os
import asyncio
import asyncpg
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from openai_client import extract_apartment_query
from search_utils import search_apartments

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_SETTINGS = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}

# Setup logger (console + file)
logger = logging.getLogger("telegram_bot")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("apartment_bot.log")

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Initialize Telegram Bot
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Format apartment listing nicely for Telegram
def format_apartment(apartment: dict) -> str:
    return (
        f"<b>📍 Location:</b> {apartment['location']}\n"
        f"<b>🛏️ Rooms:</b> {apartment['rooms']} | <b>Beds:</b> {apartment['beds']}\n"
        f"<b>📐 Area:</b> {apartment['area']:.1f} m² | <b>Floor:</b> {apartment['floor']}\n"
        f"<b>💵 Price:</b> ${round(apartment['price'], 2)} per night\n"
        f"<b>📶 Wi-Fi:</b> {'Yes' if apartment['has_wifi'] else 'No'}\n"
        f"<b>🅿️ Parking:</b> {'Yes' if apartment['has_parking'] else 'No'}\n"
        f"<b>🍽️ Kitchen:</b> {'Yes' if apartment['has_kitchen'] else 'No'}\n\n"
        f"<i>{apartment['description']}</i>"
    )

# Handle /start command
@dp.message(F.text == "/start")
async def handle_start(message: Message):
    await message.answer("👋 Hi! I can help you find an apartment.\n\n"
        "💡 To get the best results, please include in your message:\n"
        "📍 City or location (e.g. Lviv, Kyiv)\n"
        "🛏️ Number of rooms or beds\n"
        "⚙️ Important features (Wi-Fi, kitchen, parking, pool, etc.)\n"
        "🐾 Preferences (pet-friendly, balcony, jacuzzi, near park, etc.)\n\n"
        "📝 Example: 'Looking for an apartment in Lviv with 2 rooms, Wi-Fi, and parking.'"
    )

# Handle user messages
@dp.message(F.text)
async def handle_user_request(message: Message):
    user_query = message.text

    # Step 1: Extract filters from GPT
    result = await extract_apartment_query(user_query)
    logger.info(f"🧠 GPT Function Result:\n{result}")

    if not result:
        await message.answer(
            "❌ I couldn't understand your request.\n\n"
            "💡 To help me find the right apartment, try to include:\n"
            "• City or location (e.g. Lviv, Kyiv)\n"
            "• Number of rooms or beds\n"
            "• Key features (Wi-Fi, kitchen, parking, pool, etc.)\n"
            "• Special preferences (pet-friendly, balcony, jacuzzi, etc.)\n\n"
            "Feel free to write in your own words — I'll do my best to understand!"
                )
        return

    filters = result["arguments"]
    logger.info(f"📥 Filters passed to DB search:\n{filters}")

    try:
        # Step 2: Connect to DB
        conn = await asyncpg.connect(**DB_SETTINGS)

        # Step 3: Search apartments (structured + fallback logic inside)
        apartments = await search_apartments(conn, filters, filters)
        await conn.close()

    except Exception as e:
        logger.exception("❌ Database error occurred")
        await message.answer("⚠️ Something went wrong while accessing the database.")
        return

    # Step 4: Reply to user
    if not apartments:
        logger.warning("🔍 No apartments matched after SQL and vector search")
        await message.answer("🔎 We couldn't find any apartments that match your request.")
        return

    # Step 5: Show result depending on match count
    await message.answer(
    f"🏘️ Found {len(apartments)} apartment(s) that match your request:"
    )

    for apt in apartments:
        text = format_apartment(apt)
        await message.answer(text)

# Start polling
if __name__ == "__main__":
    logger.info("🤖 Bot started")
    asyncio.run(dp.start_polling(bot))