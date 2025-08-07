from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.battle.combat import CombatSystem, MONSTERS
from database.base import async_session
from database.models import Character
from keyboards.battle import battle_keyboard, location_keyboard

router = Router()

@router.message(F.text == "⚔️ Бои")
async def battle_menu(message: Message):
    await message.answer(
        "Выберите локацию для сражений:",
        reply_markup=location_keyboard()
    )

@router.callback_query(F.data.startswith("location_"))
async def select_location(callback: CallbackQuery):
    location = callback.data.split("_")[1]
    
    if location == "forest":
        available_monsters = [m for m in MONSTERS if m["level"] <= 3]
    elif location == "cave":
        available_monsters = [m for m in MONSTERS if 3 <= m["level"] <= 5]
    else:
        available_monsters = [m for m in MONSTERS if m["level"] >= 4]
    
    buttons = [
        [InlineKeyboardButton(
            text=f"{m['name']} (ур. {m['level']})", 
            callback_data=f"monster_{m['name'].lower()}")
        ] for m in available_monsters
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        f"Локация: {location}\nВыберите противника:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("monster_"))
async def start_fight(callback: CallbackQuery):
    monster_name = callback.data.split("_")[1].capitalize()
    
    async with async_session() as session:
        char = await session.get(Character, callback.from_user.id)
        can_fight, message = await CombatSystem.check_cooldown(session, callback.from_user.id)
        
        if not can_fight:
            await callback.answer(message, show_alert=True)
            return
        
        monster = next((m for m in MONSTERS if m["name"].lower() == monster_name.lower()), None)
        if not monster:
            await callback.answer("Монстр не найден", show_alert=True)
            return
        
        result = await CombatSystem.fight(char, monster)
        
        if result["victory"]:
            response = f"🎉 Победа над {monster['name']}!\n\n"
            response += f"Нанесено урона: {result['user_damage']}"
            if result["critical"]:
                response += " (КРИТИЧЕСКИЙ УДАР!)"
            response += f"\nПолучено золота: {monster['gold_reward']}"
            response += f"\nПолучено опыта: {monster['exp_reward']}"
            
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
        
        char.health = result["user_health"]
        session.add(char)
        await session.commit()
        
        await callback.answer("Бой завершен!", show_alert=True)
        await callback.message.edit_text(
            response,
            reply_markup=battle_keyboard()
        )
