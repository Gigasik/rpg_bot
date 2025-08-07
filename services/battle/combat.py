import random
from datetime import datetime, timedelta
import logging
from database.models import Character, Monster
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class CombatSystem:
    @staticmethod
    def get_attribute(obj, attr_name, default=None):
        """Получает атрибут из объекта или ключ из словаря"""
        if hasattr(obj, attr_name):
            return getattr(obj, attr_name, default)
        elif isinstance(obj, dict):
            return obj.get(attr_name, default)
        return default

    @staticmethod
    def calculate_damage(attacker, defender):
        """Рассчитывает урон с учетом силы и брони"""
        logger.debug(f"Расчет урона: атакующий={attacker}, защищающийся={defender}")
        
        # Получаем силу атакующего
        attacker_strength = CombatSystem.get_attribute(attacker, 'strength', 10)
        
        # Получаем броню защищающегося
        defender_armor = CombatSystem.get_attribute(defender, 'armor', 5)
        
        # Получаем уровень атакующего
        attacker_level = CombatSystem.get_attribute(attacker, 'level', 1)
        
        base_damage = attacker_strength * 1.5
        armor_reduction = max(0, defender_armor - (attacker_level * 0.5))
        damage = max(1, int(base_damage - armor_reduction))
        
        logger.debug(f"Базовый урон: {base_damage}, броня: {defender_armor}, итоговый урон: {damage}")
        return damage
    
    @staticmethod
    def calculate_critical():
        """Рассчитывает шанс критического удара (5%)"""
        is_critical = random.random() < 0.05
        logger.debug(f"Расчет критического удара: {'КРИТ!' if is_critical else 'обычный удар'}")
        return is_critical
    
    @staticmethod
    async def fight(user_char, monster):
        """Проводит бой между пользователем и монстром"""
        logger.info(f"Начало боя: пользователь (здоровье={user_char.health}) vs {monster['name']} (здоровье={monster['health']})")
        
        # Убедимся, что у пользователя есть все необходимые атрибуты
        if user_char.strength is None:
            logger.warning("strength пользователя None, устанавливаем значение по умолчанию 10")
            user_char.strength = 10
        if user_char.armor is None:
            logger.warning("armor пользователя None, устанавливаем значение по умолчанию 5")
            user_char.armor = 5
            
        user_damage = CombatSystem.calculate_damage(user_char, monster)
        monster_damage = CombatSystem.calculate_damage(monster, user_char)
        
        critical = CombatSystem.calculate_critical()
        if critical:
            user_damage *= 2
            logger.info(f"КРИТИЧЕСКИЙ УДАР! Урон увеличен до {user_damage}")
            
        user_char.health -= monster_damage
        monster_health = max(0, monster['health'] - user_damage)
        
        result = {
            "user_damage": user_damage,
            "monster_damage": monster_damage,
            "critical": critical,
            "user_health": max(0, user_char.health),
            "monster_health": monster_health,
            "victory": monster_health <= 0
        }
        
        logger.info(f"Результат боя: {result}")
        return result
    
    @staticmethod
    async def check_cooldown(session, user_id):
        """Проверяет, можно ли пользователю сражаться"""
        logger.debug(f"Проверка кулдауна для пользователя {user_id}")
        char = await session.get(Character, user_id)
        if not char:
            logger.error(f"Персонаж не найден для пользователя {user_id}")
            return False, "Персонаж не найден"
            
        # Исправляем значения, если они None
        if char.last_fight is None:
            logger.warning(f"last_fight для пользователя {user_id} None, устанавливаем текущее время")
            char.last_fight = datetime.utcnow()
            session.add(char)
            await session.commit()
            
        cooldown = timedelta(minutes=5)
        if char.last_fight and datetime.utcnow() - char.last_fight < cooldown:
            remaining = cooldown - (datetime.utcnow() - char.last_fight)
            minutes = int(remaining.total_seconds() // 60)
            seconds = int(remaining.total_seconds() % 60)
            logger.info(f"Кулдаун активен для пользователя {user_id}. Осталось: {minutes}м {seconds}с")
            return False, f"Подождите {minutes} минуту(ы) {seconds} секунд(ы)"
            
        logger.info(f"Кулдаун прошел для пользователя {user_id}")
        return True, ""
    
    @staticmethod
    async def update_experience(session, user_id, exp_gained):
        """Обновляет опыт и уровень персонажа"""
        logger.info(f"Обновление опыта для пользователя {user_id}: +{exp_gained} опыта")
        char = await session.get(Character, user_id)
        if not char:
            logger.error(f"Персонаж не найден для обновления опыта (user_id={user_id})")
            return False
            
        # Инициализируем недостающие поля, если они None
        if char.experience is None:
            logger.warning(f"experience пользователя {user_id} None, устанавливаем 0")
            char.experience = 0
        if char.level is None:
            logger.warning(f"level пользователя {user_id} None, устанавливаем 1")
            char.level = 1
        if char.health is None:
            logger.warning(f"health пользователя {user_id} None, устанавливаем 100")
            char.health = 100
            
        new_exp = char.experience + exp_gained
        level_up = False
        new_level = char.level
        
        # Расчет нового уровня
        while new_exp >= CombatSystem.exp_to_level_up(new_level):
            new_level += 1
            level_up = True
            logger.info(f"Пользователь {user_id} достиг уровня {new_level}!")
            
        # Обновляем данные
        char.level = new_level
        char.experience = new_exp
        char.health = min(100 + (new_level - 1) * 20, 1000)  # Максимальное здоровье растет с уровнем
        char.last_fight = datetime.utcnow()
        
        session.add(char)
        await session.commit()
        
        if level_up:
            logger.info(f"Пользователь {user_id} повысил уровень до {new_level}!")
        
        return level_up
    
    @staticmethod
    def exp_to_level_up(level):
        """Рассчитывает опыт, необходимый для следующего уровня"""
        exp_needed = int(100 * level * 1.5)
        logger.debug(f"Опыт для уровня {level+1}: {exp_needed}")
        return exp_needed

# Предустановленные монстры
MONSTERS = [
    {"name": "Волк", "level": 1, "health": 30, "strength": 8, "armor": 1, "gold_reward": 5, "exp_reward": 10},
    {"name": "Скелет", "level": 3, "health": 45, "strength": 10, "armor": 2, "gold_reward": 10, "exp_reward": 15},
    {"name": "Гоблин", "level": 2, "health": 25, "strength": 7, "armor": 1, "gold_reward": 3, "exp_reward": 5},
    {"name": "Тролль", "level": 5, "health": 70, "strength": 15, "armor": 4, "gold_reward": 20, "exp_reward": 30}
]
