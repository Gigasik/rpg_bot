from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.battle.combat import CombatSystem
from database.base import async_session
from database.models import Character
from database.queries import get_profile, get_or_create_user
from keyboards.battle import battle_keyboard, location_keyboard, battle_result_keyboard
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text == "⚔️ Бои")
async def battle_menu(message: Message):
    """Показывает меню боев"""
    logger.info(f"Пользователь {message.from_user.id} открыл меню боев")
    await message.answer(
        "⚔️ Выберите локацию для сражений:",
        reply_markup=location_keyboard()
    )

@router.callback_query(F.data.startswith("location_"))
async def select_location(callback: CallbackQuery):
    """Выбор локации для боя"""
    location = callback.data.split("_")[1]
    logger.info(f"Пользователь {callback.from_user.id} выбрал локацию: {location}")
    
    # Определяем доступных монстров для локации
    if location == "forest":
        available_monsters = [m for m in MONSTERS if m["level"] <= 3]
    elif location == "cave":
        available_monsters = [m for m in MONSTERS if 3 <= m["level"] <= 5]
    else:  # wasteland
        available_monsters = [m for m in MONSTERS if m["level"] >= 4]
    
    # Создаем клавиатуру с монстрами
    buttons = [
        [InlineKeyboardButton(
            text=f"{m['name']} (ур. {m['level']})", 
            callback_data=f"monster_{m['name'].lower()}")
        ] for m in available_monsters
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        f"🌲 Локация: {location}\nВыберите противника:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("monster_"))
async def start_fight(callback: CallbackQuery):
    """Начало боя с выбранным монстром"""
    monster_name = callback.data.split("_")[1].capitalize()
    logger.info(f"Пользователь {callback.from_user.id} выбрал монстра: {monster_name}")
    
    async with async_session() as session:
        # Получаем персонажа пользователя
        char = await session.get(Character, callback.from_user.id)
        
        # Проверяем кулдаун
        can_fight, message = await CombatSystem.check_cooldown(session, callback.from_user.id)
        if not can_fight:
            logger.warning(f"Кулдаун для пользователя {callback.from_user.id}: {message}")
            await callback.answer(message, show_alert=True)
            return
        
        # Находим монстра
        monster = next((m for m in MONSTERS if m["name"].lower() == monster_name.lower()), None)
        if not monster:
            logger.error(f"Монстр {monster_name} не найден для пользователя {callback.from_user.id}")
            await callback.answer("Монстр не найден", show_alert=True)
            return
        
        logger.info(f"Начало боя: пользователь {callback.from_user.id} vs {monster['name']}")
        
        # Проводим бой
        try:
            result = await CombatSystem.fight(char, monster)
            
            # Формируем сообщение о результате
            if result["victory"]:
                response = f"🎉 Победа над {monster['name']}!\n\n"
                response += f"Нанесено урона: {result['user_damage']}"
                if result["critical"]:
                    response += " (КРИТИЧЕСКИЙ УДАР!)"
                response += f"\nПолучено золота: {monster['gold_reward']}"
                response += f"\nПолучено опыта: {monster['exp_reward']}"
                
                # Обновляем опыт
                level_up = await CombatSystem.update_experience(
                    session, 
                    callback.from_user.id, 
                    monster['exp_reward']
                )
                
                if level_up:
                    response += "\n\n🎉 ПОЗДРАВЛЯЕМ! Вы достигли нового уровня!"
            else:
                response = f"💀 Поражение от {monster['name']}!\n\n"
                response += f"Нанесено урона: {result['user_damage']}\n"
                response += f"Получено урона: {result['monster_damage']}\n"
                response += "Ваше здоровье слишком низкое для продолжения боя."
            
            # Обновляем здоровье персонажа
            char.health = result["user_health"]
            session.add(char)
            await session.commit()
            
            logger.info(f"Бой завершен для пользователя {callback.from_user.id}. Результат: {'победа' if result['victory'] else 'поражение'}")
            await callback.answer("Бой завершен!", show_alert=True)
            await callback.message.edit_text(
                response,
                reply_markup=battle_result_keyboard()
            )
        except Exception as e:
            logger.exception(f"Ошибка при проведении боя для пользователя {callback.from_user.id}")
            await callback.answer(f"Произошла ошибка: {str(e)}", show_alert=True)
            await callback.message.edit_text(
                "⚠️ Произошла ошибка при проведении боя. Попробуйте позже.",
                reply_markup=battle_result_keyboard()
            )

@router.callback_query(F.data == "back_to_battle_menu")
async def back_to_battle_menu(callback: CallbackQuery):
    """Возвращение в меню боев"""
    logger.info(f"Пользователь {callback.from_user.id} вернулся в меню боев")
    await callback.message.edit_text(
        "⚔️ Выберите локацию для сражений:",
        reply_markup=location_keyboard()
    )
