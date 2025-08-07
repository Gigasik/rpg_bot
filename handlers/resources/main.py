from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from services.resources.core import ResourceService, CRAFTING_RECIPES
from database.base import async_session
from keyboards.resources import resources_keyboard, buildings_keyboard, crafting_keyboard

router = Router()

@router.message(F.text == "🌱 Ресурсы")
async def resources_menu(message: Message):
    """Показывает меню ресурсов"""
    await message.answer(
        "Выберите действие:",
        reply_markup=resources_keyboard()
    )

@router.message(F.text == "Собрать ресурсы")
async def collect_resources(message: Message):
    """Собирает доступные ресурсы"""
    async with async_session() as session:
        resources = await ResourceService.collect_resources(session, message.from_user.id)
    
    if not resources:
        await message.answer("Ошибка при сборе ресурсов")
        return
    
    response = "📦 Собранные ресурсы:\n"
    response += f"💰 Золото: {resources['gold']}\n"
    response += f"🌾 Еда: {resources['food']}\n"
    response += f"🪵 Дерево: {resources['wood']}\n"
    response += f"🪨 Камень: {resources['stone']}"
    
    await message.answer(response, reply_markup=resources_keyboard())

@router.message(F.text == "Постройки")
async def buildings_menu(message: Message):
    """Показывает меню построек"""
    await message.answer(
        "Выберите постройку для управления:",
        reply_markup=buildings_keyboard()
    )

@router.callback_query(F.data.startswith("building_"))
async def building_info(callback: CallbackQuery):
    """Показывает информацию о постройке"""
    building_type = callback.data.split("_")[1]
    
    async with async_session() as session:
        resources = await ResourceService.get_user_resources(session, callback.from_user.id)
    
    if not resources:
        await callback.answer("Ошибка при получении данных", show_alert=True)
        return
    
    # Определяем информацию о постройке
    building_info = {
        "gold_mine": {
            "name": "Золотая шахта",
            "level": resources["gold_mine_level"],
            "description": "Добывает золото для покупок и улучшений"
        },
        "farm": {
            "name": "Ферма",
            "level": resources["farm_level"],
            "description": "Производит еду для поддержания здоровья"
        },
        "lumber_mill": {
            "name": "Лесопилка",
            "level": resources["lumber_mill_level"],
            "description": "Производит дерево для строительства"
        },
        "stone_quarry": {
            "name": "Каменоломня",
            "level": resources["stone_quarry_level"],
            "description": "Добывает камень для построек"
        }
    }
    
    building = building_info[building_type]
    
    # Получаем информацию об уровне
    levels = ResourceService.BUILDING_LEVELS[building_type]
    current_level = min(building["level"] - 1, len(levels) - 1)
    level_info = levels[current_level]
    
    # Формируем сообщение
    response = f"🏰 {building['name']} (Уровень {building['level']}/4)\n\n"
    response += f"{building['description']}\n\n"
    response += f"Производство: x{level_info['production_bonus']}\n"
    response += f"Макс. хранилище: {level_info['storage']}\n\n"
    
    if building["level"] < 4:
        next_level = levels[min(building["level"], len(levels) - 1)]
        response += "Следующий уровень:\n"
        if "gold" in next_level["upgrade_cost"]:
            response += f"💰 Золото: {next_level['upgrade_cost']['gold']}\n"
        if "wood" in next_level["upgrade_cost"]:
            response += f"🪵 Дерево: {next_level['upgrade_cost']['wood']}\n"
        if "stone" in next_level["upgrade_cost"]:
            response += f"🪨 Камень: {next_level['upgrade_cost']['stone']}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Улучшить постройку", 
                callback_data=f"upgrade_{building_type}"
            )]
        ])
    else:
        response += "Постройка достигла максимального уровня!"
        keyboard = None
    
    await callback.message.edit_text(response, reply_markup=keyboard)

@router.callback_query(F.data.startswith("upgrade_"))
async def upgrade_building(callback: CallbackQuery):
    """Улучшает постройку"""
    building_type = callback.data.split("_")[1]
    
    async with async_session() as session:
        success, message = await ResourceService.upgrade_building(
            session, 
            callback.from_user.id, 
            building_type
        )
    
    if success:
        await callback.answer("Постройка успешно улучшена!", show_alert=True)
        # Показываем обновленную информацию
        await building_info(callback)
    else:
        await callback.answer(message, show_alert=True)

@router.message(F.text == "Крафт")
async def crafting_menu(message: Message):
    """Показывает меню крафта"""
    await message.answer(
        "Выберите рецепт для крафта:",
        reply_markup=crafting_keyboard()
    )

@router.callback_query(F.data.startswith("craft_"))
async def craft_item(callback: CallbackQuery):
    """Создает предмет через крафт"""
    recipe_index = int(callback.data.split("_")[1])
    
    if recipe_index >= len(CRAFTING_RECIPES):
        await callback.answer("Рецепт не найден", show_alert=True)
        return
    
    recipe = CRAFTING_RECIPES[recipe_index]
    
    async with async_session() as session:
        resources = await ResourceService.get_user_resources(session, callback.from_user.id)
    
    if not resources:
        await callback.answer("Ошибка при получении данных", show_alert=True)
        return
    
    # Проверяем достаточно ли ресурсов
    if (resources["gold"] < recipe["gold_cost"] or
        resources["wood"] < recipe["wood_cost"] or
        resources["stone"] < recipe["stone_cost"] or
        resources["food"] < recipe["food_cost"]):
        await callback.answer("Недостаточно ресурсов для крафта", show_alert=True)
        return
    
    # Проверяем уровень персонажа
    async with async_session() as session:
        char = await session.get(Character, callback.from_user.id)
        if not char or char.level < recipe["required_level"]:
            await callback.answer(f"Требуется уровень {recipe['required_level']}", show_alert=True)
            return
    
    # Выполняем крафт
    async with async_session() as session:
        resource = await session.get(Resource, callback.from_user.id)
        
        resource.gold -= recipe["gold_cost"]
        resource.wood -= recipe["wood_cost"]
        resource.stone -= recipe["stone_cost"]
        resource.food -= recipe["food_cost"]
        
        session.add(resource)
        await session.commit()
    
    await callback.answer(f"Предмет '{recipe['output_item']}' успешно создан!", show_alert=True)
    await crafting_menu(callback.message)
