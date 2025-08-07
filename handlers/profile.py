from aiogram import Router, F
from aiogram.types import Message
from database.queries import get_profile
from database.base import async_session

router = Router()

@router.message(F.text == "👤 Профиль")
async def profile_handler(message: Message):
    async with async_session() as session:
        user, char = await get_profile(
            session, 
            message.from_user.id
        )
    
    await message.answer(
        f"🪪 <b>Ваш профиль</b>\n"
        f"Имя: @{user.username}\n"
        f"Уровень: {char.level}\n"
        f"Здоровье: {char.health}\n"
        f"Баланс: {user.balance} золота",
        parse_mode="HTML"
    )
