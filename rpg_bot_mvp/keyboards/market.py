from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def market_keyboard(items):
    buttons = [
        [InlineKeyboardButton(
            text=f"{item.name} | {item.base_price} золота", 
            callback_data=f"buy_{item.item_id}"
        )] for item in items
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
