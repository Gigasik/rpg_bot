from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def battle_keyboard():
    """Основная клавиатура для меню боев (reply-клавиатура)"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌲 Лес"), KeyboardButton(text="🕸️ Пещера")],
            [KeyboardButton(text="👺 Пустошь"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def location_keyboard():
    """Inline-клавиатура для выбора локации"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌲 Лес", callback_data="location_forest")],
            [InlineKeyboardButton(text="🕸️ Пещера", callback_data="location_cave")],
            [InlineKeyboardButton(text="👺 Пустошь", callback_data="location_wasteland")]
        ]
    )

def battle_result_keyboard():
    """Inline-клавиатура для результатов боя"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌲 Лес", callback_data="location_forest")],
            [InlineKeyboardButton(text="🕸️ Пещера", callback_data="location_cave")],
            [InlineKeyboardButton(text="👺 Пустошь", callback_data="location_wasteland")],
            [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_battle_menu")]
        ]
    )
