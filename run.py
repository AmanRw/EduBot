import asyncio
import os
import sys
from aiohttp import web
from src.bot import bot, dp

# --- Dummy Web Server to satisfy Cloud Port Checks ---
async def health_check(request):
    return web.Response(text="Bot is alive!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Cloud platforms provide the PORT variable
    # We MUST bind to 0.0.0.0, not localhost
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"✅ Dummy server started on port {port}")

# --- Main Application Loop ---
async def main():
    # 1. Start the dummy server first
    await start_dummy_server()
    
    # 2. Then start the bot
    print("🚀 Starting Bot Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("EduBot stopped")