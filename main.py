import asyncio
import os
from dotenv import load_dotenv
import uvicorn
from src.bot.bot import NotificationBot
from src.webhook.server import app
import threading

# Load environment variables
load_dotenv()

# Initialize the bot
bot = NotificationBot()

# Store bot instance in FastAPI state
app.state.bot = bot

def run_webhook_server():
    """Run the FastAPI webhook server"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT")),
        log_level="info"
    )

async def main():
    # Start the webhook server in a separate thread
    webhook_thread = threading.Thread(target=run_webhook_server)
    webhook_thread.daemon = True
    webhook_thread.start()

    # Start the bot
    async with bot:
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main()) 