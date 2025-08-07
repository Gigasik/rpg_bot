from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def battle_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌲 Лес"), KeyboardButton(text="🕸️ Пещера")],
            [KeyboardButton(text="👺 Пустошь"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def location_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌲 Лес", callback_data="location_forest")],
            [InlineKeyboardButton(text="🕸️ Пещера", callback_data="location_cave")],
            [InlineKeyboardButton(text="👺 Пустошь", callback_data="location_wasteland")]
        ]
    )
