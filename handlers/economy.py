from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.queries import get_market_items, buy_item
from keyboards.market import market_keyboard
from database.base import async_session
from aiogram.exceptions import TelegramBadRequest

router = Router()

@router.message(F.text == "🛒 Рынок")
async def market_handler(message: Message):
    async with async_session() as session:
        items = await get_market_items(session)
    await message.answer(
        "🛒 <b>Рынок</b>\nВыберите товар для покупки:",
        reply_markup=market_keyboard(items),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("buy_"))
async def buy_callback(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    
    async with async_session() as session:
        success = await buy_item(
            session, 
            callback.from_user.id, 
            item_id
        )
    
    if success:
        await callback.answer("✅ Покупка успешна!", show_alert=True)
    else:
        await callback.answer("❌ Недостаточно золота!", show_alert=True)
    
    # Получаем обновленный список товаров
    async with async_session() as session:
        items = await get_market_items(session)
    
    # Проверяем, изменилась ли клавиатура
    try:
        new_markup = market_keyboard(items)
        
        # Если текущая клавиатура существует и отличается от новой
        if callback.message.reply_markup and str(callback.message.reply_markup) != str(new_markup):
            await callback.message.edit_reply_markup(
                reply_markup=new_markup
            )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Клавиатура не изменилась, не нужно обновлять
            pass
        else:
            # Другие ошибки
            await callback.message.answer(
                "🛒 <b>Рынок</b>\nВыберите товар для покупки:",
                reply_markup=market_keyboard(items),
                parse_mode="HTML"
            )
