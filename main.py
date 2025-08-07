import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.settings import settings
from database.base import init_db
from handlers import start, profile, economy
from handlers.resources import main as resources_handler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Запуск бота...")
        logger.info("Инициализация базы данных...")
        await init_db()
        
        logger.info("Создание бота...")
        bot = Bot(token=settings.BOT_TOKEN)
        dp = Dispatcher()
        
        logger.info("Регистрация роутеров...")
        dp.include_router(start.router)
        dp.include_router(profile.router)
        dp.include_router(economy.router)
        dp.include_router(resources_handler.router)
        
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("Критическая ошибка при запуске бота")
        raise

if __name__ == "__main__":
    asyncio.run(main())
