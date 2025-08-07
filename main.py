import asyncio
from aiogram import Bot, Dispatcher
from config.settings import settings
from database.base import init_db
from handlers import start, profile, economy

async def main():
    await init_db()
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(economy.router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
