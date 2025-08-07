from .models import User, Character, MarketItem as Market
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def get_or_create_user(session: AsyncSession, user_id: int, username: str):
    user = await session.get(User, user_id)
    if not user:
        user = User(user_id=user_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    # Проверяем существование персонажа ПЕРЕД добавлением
    char = await session.get(Character, user_id)
    if not char:
        # Явно устанавливаем все значения по умолчанию
        char = Character(
            user_id=user_id,
            level=1,
            health=100,
            strength=10,
            armor=5,
            experience=0,
            gold=100
        )
        session.add(char)
        await session.commit()
    
    # Проверяем, что все поля персонажа инициализированы
    if char.strength is None:
        char.strength = 10
        session.add(char)
        await session.commit()
    
    if char.armor is None:
        char.armor = 5
        session.add(char)
        await session.commit()
    
    return user

async def get_profile(session: AsyncSession, user_id: int):
    user = await session.get(User, user_id)
    char = await session.get(Character, user_id)
    
    # Если персонаж существует, но некоторые поля None, исправляем
    if char and char.strength is None:
        char.strength = 10
        char.armor = 5
        session.add(char)
        await session.commit()
    
    return user, char

async def get_market_items(session: AsyncSession):
    result = await session.execute(select(Market))
    return result.scalars().all()

async def buy_item(session: AsyncSession, user_id: int, item_id: int):
    user = await session.get(User, user_id)
    item = await session.get(Market, item_id)
    
    if not user or not item:
        return False
    
    if user.balance < item.base_price:
        return False
    
    user.balance -= item.base_price
    await session.commit()
    return True
