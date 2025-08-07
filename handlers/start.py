from aiogram import Router, F
from aiogram.types import Message
from database.queries import get_or_create_user
from keyboards.main_menu import main_menu_keyboard
from database.base import async_session

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    async with async_session() as session:
        await get_or_create_user(
            session, 
            message.from_user.id, 
            message.from_user.username or "player"
        )
    await message.answer(
        "⚔️ Добро пожаловать в RPG-мир!\n"
        "У вас 100 золотых монет. Что будете делать?",
        reply_markup=main_menu_keyboard()
    )
