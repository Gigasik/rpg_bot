from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def resources_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Собрать ресурсы")],
            [KeyboardButton(text="Постройки"), KeyboardButton(text="Крафт")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )

def buildings_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 Золотая шахта", callback_data="building_gold_mine")],
            [InlineKeyboardButton(text="🌾 Ферма", callback_data="building_farm")],
            [InlineKeyboardButton(text="🪵 Лесопилка", callback_data="building_lumber_mill")],
            [InlineKeyboardButton(text="🪨 Каменоломня", callback_data="building_stone_quarry")]
        ]
    )

def crafting_keyboard():
    buttons = []
    for i, recipe in enumerate(CRAFTING_RECIPES):
        buttons.append([
            InlineKeyboardButton(
                text=f"{recipe['name']} (ур. {recipe['required_level']})", 
                callback_data=f"craft_{i}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
