from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .models import Base, Market
from sqlalchemy import text
from config.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Добавляем тестовые товары
        session = AsyncSession(conn)
        result = await session.execute(text("SELECT * FROM market"))
        if not result.first():
            session.add_all([
                Market(item_id=1, name="Меч", base_price=50),
                Market(item_id=2, name="Яблоко", base_price=10)
            ])
            await session.commit()
