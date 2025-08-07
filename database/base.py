from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .models import Base, MarketItem
from config.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Добавляем тестовые товары, используя новую модель MarketItem
        async with AsyncSession(conn) as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT * FROM market_items"))
            if not result.first():
                # Создаем объекты MarketItem напрямую
                from datetime import datetime
                session.add_all([
                    MarketItem(name="Меч", description="Острое оружие", base_price=50, current_price=50, supply=100, demand=50, price_change=0.0, last_update=datetime.utcnow()),
                    MarketItem(name="Щит", description="Защитное снаряжение", base_price=75, current_price=75, supply=100, demand=50, price_change=0.0, last_update=datetime.utcnow())
                ])
                await session.commit()
