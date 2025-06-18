import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from openai_client import extract_apartment_query
from search_utils import search_apartments

# Load environment variables from .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize Telegram Bot
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Format apartment listing nicely for Telegram
def format_apartment(apartment: dict) -> str:
    return (
        f"<b>📍 Location:</b> {apartment['location']}\n"
        f"<b>🛏️ Rooms:</b> {apartment['rooms']} | <b>Beds:</b> {apartment['beds']}\n"
        f"<b>📐 Area:</b> {apartment['area']} m² | <b>Floor:</b> {apartment['floor']}\n"
        f"<b>💵 Price:</b> ${round(apartment['price'], 2)} per night\n"
        f"<b>📶 Wi-Fi:</b> {'Yes' if apartment['has_wifi'] else 'No'}\n"
        f"<b>🅿️ Parking:</b> {'Yes' if apartment['has_parking'] else 'No'}\n"
        f"<b>🍽️ Kitchen:</b> {'Yes' if apartment['has_kitchen'] else 'No'}\n\n"
        f"<i>{apartment['description']}</i>"
    )

# Handle /start command
@dp.message(F.text == "/start")
async def handle_start(message: Message):
    await message.answer("👋 Hi! Just tell me what kind of apartment you're looking for, and I'll try to find it for you.")

# Handle user messages with natural language queries
@dp.message(F.text)
async def handle_user_request(message: Message):
    user_query = message.text

    # Step 1: Extract structured parameters using GPT
    result = extract_apartment_query(user_query)

    if not result:
        await message.answer("❌ Sorry, I couldn't understand your request.")
        return

    # Step 2: Run search in PostgreSQL
    apartments = await search_apartments(result["arguments"])

    # Step 3: Reply to user with search results
    if not apartments:
        await message.answer("🔎 No apartments matched your request.")
        return

    await message.answer(f"✅ Found {len(apartments)} matching apartments:")

    for apt in apartments:
        text = format_apartment(apt)
        await message.answer(text)

# Run the bot
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))