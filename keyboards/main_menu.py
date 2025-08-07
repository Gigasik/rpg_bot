from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚔️ Бои"), KeyboardButton(text="🌱 Ресурсы")],
            [KeyboardButton(text="🛒 Рынок"), KeyboardButton(text="👤 Профиль")]
        ],
        resize_keyboard=True
    )
