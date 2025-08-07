from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="⚔️ Бои"), KeyboardButton(text="🛒 Рынок")]
        ],
        resize_keyboard=True
    )
