import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, text, text, text
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем модели
from database.models import Base

# Получаем URL базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./rpg_bot.db")

# Конфигурация
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
