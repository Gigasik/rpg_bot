import random
from datetime import datetime, timedelta
from database.models import Character, Monster
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

class CombatSystem:
    @staticmethod
    def calculate_damage(attacker, defender):
        """Рассчитывает урон с учетом силы и брони"""
        base_damage = attacker.strength * 1.5
        armor_reduction = max(0, defender.armor - (attacker.level * 0.5))
        return max(1, int(base_damage - armor_reduction))
    
    @staticmethod
    def calculate_critical():
        """Рассчитывает шанс критического удара (5%)"""
        return random.random() < 0.05
    
    @staticmethod
    async def fight(user_char, monster):
        """Проводит бой между пользователем и монстром"""
        user_damage = CombatSystem.calculate_damage(user_char, monster)
        monster_damage = CombatSystem.calculate_damage(monster, user_char)
        
        critical = CombatSystem.calculate_critical()
        if critical:
            user_damage *= 2
            
        user_char.health -= monster_damage
        monster_health = max(0, monster.health - user_damage)
        
        return {
            "user_damage": user_damage,
            "monster_damage": monster_damage,
            "critical": critical,
            "user_health": max(0, user_char.health),
            "monster_health": monster_health,
            "victory": monster_health <= 0
        }
    
    @staticmethod
    async def check_cooldown(session, user_id):
        """Проверяет, можно ли пользователю сражаться"""
        char = await session.get(Character, user_id)
        if not char:
            return False, "Персонаж не найден"
            
        cooldown = timedelta(minutes=5)
        if char.last_fight and datetime.utcnow() - char.last_fight < cooldown:
            remaining = cooldown - (datetime.utcnow() - char.last_fight)
            return False, f"Подождите {int(remaining.total_seconds() // 60)} минуту(ы)"
            
        return True, ""
    
    @staticmethod
    async def update_experience(session, user_id, exp_gained):
        """Обновляет опыт и уровень персонажа"""
        char = await session.get(Character, user_id)
        if not char:
            return False
            
        new_exp = char.experience + exp_gained
        level_up = False
        new_level = char.level
        
        # Расчет нового уровня
        while new_exp >= CombatSystem.exp_to_level_up(new_level):
            new_level += 1
            level_up = True
            
        # Обновляем данные
        char.level = new_level
        char.experience = new_exp
        char.health = min(100 + (new_level - 1) * 20, 1000)  # Максимальное здоровье растет с уровнем
        char.last_fight = datetime.utcnow()
        
        session.add(char)
        await session.commit()
        
        return level_up
    
    @staticmethod
    def exp_to_level_up(level):
        """Рассчитывает опыт, необходимый для следующего уровня"""
        return 100 * level * 1.5

# Предустановленные монстры
MONSTERS = [
    {"name": "Волк", "level": 1, "health": 30, "strength": 8, "armor": 1, "gold_reward": 5, "exp_reward": 10},
    {"name": "Скелет", "level": 3, "health": 45, "strength": 10, "armor": 2, "gold_reward": 10, "exp_reward": 15},
    {"name": "Гоблин", "level": 2, "health": 25, "strength": 7, "armor": 1, "gold_reward": 3, "exp_reward": 5},
    {"name": "Тролль", "level": 5, "health": 70, "strength": 15, "armor": 4, "gold_reward": 20, "exp_reward": 30}
]
