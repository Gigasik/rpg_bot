from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def battle_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_menu")]
        ]
    )

def location_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌲 Лес", callback_data="location_forest")],
            [InlineKeyboardButton(text="🏔️ Пещера", callback_data="location_cave")],
            [InlineKeyboardButton(text="🏜️ Пустошь", callback_data="location_wasteland")]
        ]
    )
