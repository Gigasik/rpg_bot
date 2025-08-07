from datetime import datetime, timedelta
from database.models import Resource, Building, Character
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class ResourceService:
    # Коэффициенты производства ресурсов
    PRODUCTION_RATES = {
        "gold": 10,    # золото в час
        "wood": 8,     # дерево в час
        "stone": 6,    # камень в час
        "food": 12     # еда в час
    }
    
    # Уровни построек и их эффекты
    BUILDING_LEVELS = {
        "gold_mine": [
            {"production_bonus": 1.0, "storage": 100, "upgrade_cost": {"gold": 50, "wood": 20}},
            {"production_bonus": 1.2, "storage": 150, "upgrade_cost": {"gold": 100, "wood": 40}},
            {"production_bonus": 1.5, "storage": 200, "upgrade_cost": {"gold": 200, "wood": 80}},
            {"production_bonus": 2.0, "storage": 300, "upgrade_cost": {"gold": 400, "wood": 160}}
        ],
        "farm": [
            {"production_bonus": 1.0, "storage": 100, "upgrade_cost": {"gold": 30, "wood": 10}},
            {"production_bonus": 1.2, "storage": 150, "upgrade_cost": {"gold": 60, "wood": 20}},
            {"production_bonus": 1.5, "storage": 200, "upgrade_cost": {"gold": 120, "wood": 40}},
            {"production_bonus": 2.0, "storage": 300, "upgrade_cost": {"gold": 240, "wood": 80}}
        ],
        "lumber_mill": [
            {"production_bonus": 1.0, "storage": 100, "upgrade_cost": {"gold": 40, "stone": 20}},
            {"production_bonus": 1.2, "storage": 150, "upgrade_cost": {"gold": 80, "stone": 40}},
            {"production_bonus": 1.5, "storage": 200, "upgrade_cost": {"gold": 160, "stone": 80}},
            {"production_bonus": 2.0, "storage": 300, "upgrade_cost": {"gold": 320, "stone": 160}}
        ],
        "stone_quarry": [
            {"production_bonus": 1.0, "storage": 100, "upgrade_cost": {"gold": 50, "wood": 30}},
            {"production_bonus": 1.2, "storage": 150, "upgrade_cost": {"gold": 100, "wood": 60}},
            {"production_bonus": 1.5, "storage": 200, "upgrade_cost": {"gold": 200, "wood": 120}},
            {"production_bonus": 2.0, "storage": 300, "upgrade_cost": {"gold": 400, "wood": 240}}
        ]
    }
    
    @staticmethod
    async def get_user_resources(session, user_id):
        """Получает ресурсы пользователя с учетом накопления"""
        resource = await session.get(Resource, user_id)
        building = await session.get(Building, user_id)
        character = await session.get(Character, user_id)
        
        if not resource or not building or not character:
            return None
            
        # Вычисляем накопленные ресурсы
        now = datetime.utcnow()
        elapsed = (now - building.last_collection).total_seconds() / 3600  # часы
        
        # Получаем уровень построек
        gold_mine_level = min(building.gold_mine_level - 1, len(ResourceService.BUILDING_LEVELS["gold_mine"]) - 1)
        farm_level = min(building.farm_level - 1, len(ResourceService.BUILDING_LEVELS["farm"]) - 1)
        lumber_mill_level = min(building.lumber_mill_level - 1, len(ResourceService.BUILDING_LEVELS["lumber_mill"]) - 1)
        stone_quarry_level = min(building.stone_quarry_level - 1, len(ResourceService.BUILDING_LEVELS["stone_quarry"]) - 1)
        
        # Коэффициенты производства
        gold_bonus = ResourceService.BUILDING_LEVELS["gold_mine"][gold_mine_level]["production_bonus"]
        food_bonus = ResourceService.BUILDING_LEVELS["farm"][farm_level]["production_bonus"]
        wood_bonus = ResourceService.BUILDING_LEVELS["lumber_mill"][lumber_mill_level]["production_bonus"]
        stone_bonus = ResourceService.BUILDING_LEVELS["stone_quarry"][stone_quarry_level]["production_bonus"]
        
        # Вычисляем новые значения
        new_gold = min(
            ResourceService.BUILDING_LEVELS["gold_mine"][gold_mine_level]["storage"],
            resource.gold + int(ResourceService.PRODUCTION_RATES["gold"] * gold_bonus * elapsed)
        )
        new_food = min(
            ResourceService.BUILDING_LEVELS["farm"][farm_level]["storage"],
            resource.food + int(ResourceService.PRODUCTION_RATES["food"] * food_bonus * elapsed)
        )
        new_wood = min(
            ResourceService.BUILDING_LEVELS["lumber_mill"][lumber_mill_level]["storage"],
            resource.wood + int(ResourceService.PRODUCTION_RATES["wood"] * wood_bonus * elapsed)
        )
        new_stone = min(
            ResourceService.BUILDING_LEVELS["stone_quarry"][stone_quarry_level]["storage"],
            resource.stone + int(ResourceService.PRODUCTION_RATES["stone"] * stone_bonus * elapsed)
        )
        
        # Обновляем время последней коллекции
        building.last_collection = now
        
        return {
            "gold": new_gold,
            "food": new_food,
            "wood": new_wood,
            "stone": new_stone,
            "gold_mine_level": building.gold_mine_level,
            "farm_level": building.farm_level,
            "lumber_mill_level": building.lumber_mill_level,
            "stone_quarry_level": building.stone_quarry_level
        }
    
    @staticmethod
    async def collect_resources(session, user_id):
        """Собирает ресурсы и возвращает их количество"""
        resources = await ResourceService.get_user_resources(session, user_id)
        
        if not resources:
            return None
            
        # Обновляем ресурсы в базе
        resource = await session.get(Resource, user_id)
        building = await session.get(Building, user_id)
        
        resource.gold = resources["gold"]
        resource.food = resources["food"]
        resource.wood = resources["wood"]
        resource.stone = resources["stone"]
        building.last_collection = datetime.utcnow()
        
        session.add(resource)
        session.add(building)
        await session.commit()
        
        return resources
    
    @staticmethod
    async def upgrade_building(session, user_id, building_type):
        """Улучшает постройку"""
        building = await session.get(Building, user_id)
        resource = await session.get(Resource, user_id)
        character = await session.get(Character, user_id)
        
        if not building or not resource or not character:
            return False, "Ошибка данных"
            
        # Определяем текущий уровень постройки
        current_level = 0
        if building_type == "gold_mine":
            current_level = building.gold_mine_level
        elif building_type == "farm":
            current_level = building.farm_level
        elif building_type == "lumber_mill":
            current_level = building.lumber_mill_level
        elif building_type == "stone_quarry":
            current_level = building.stone_quarry_level
            
        # Проверяем, можно ли улучшить
        if current_level >= 4:
            return False, "Постройка достигла максимального уровня"
            
        # Получаем стоимость улучшения
        levels = ResourceService.BUILDING_LEVELS[building_type]
        if current_level >= len(levels):
            return False, "Ошибка уровня постройки"
            
        cost = levels[current_level]["upgrade_cost"]
        
        # Проверяем достаточно ли ресурсов
        if (resource.gold < cost.get("gold", 0) or
            resource.wood < cost.get("wood", 0) or
            resource.stone < cost.get("stone", 0)):
            return False, "Недостаточно ресурсов для улучшения"
            
        # Проверяем уровень персонажа
        required_level = 1 + (current_level // 2)
        if character.level < required_level:
            return False, f"Требуется уровень {required_level} для улучшения"
            
        # Списываем ресурсы
        resource.gold -= cost.get("gold", 0)
        resource.wood -= cost.get("wood", 0)
        resource.stone -= cost.get("stone", 0)
        
        # Увеличиваем уровень постройки
        if building_type == "gold_mine":
            building.gold_mine_level += 1
        elif building_type == "farm":
            building.farm_level += 1
        elif building_type == "lumber_mill":
            building.lumber_mill_level += 1
        elif building_type == "stone_quarry":
            building.stone_quarry_level += 1
            
        building.last_upgrade = datetime.utcnow()
        
        session.add(resource)
        session.add(building)
        await session.commit()
        
        return True, f"Постройка '{building_type}' улучшена до уровня {current_level + 1}!"

# Предустановленные рецепты крафта
CRAFTING_RECIPES = [
    {
        "name": "Деревянный меч",
        "output_item": "Меч",
        "output_quantity": 1,
        "gold_cost": 0,
        "wood_cost": 10,
        "stone_cost": 0,
        "food_cost": 0,
        "required_level": 1
    },
    {
        "name": "Каменный топор",
        "output_item": "Топор",
        "output_quantity": 1,
        "gold_cost": 0,
        "wood_cost": 5,
        "stone_cost": 10,
        "food_cost": 0,
        "required_level": 2
    },
    {
        "name": "Хлеб",
        "output_item": "Хлеб",
        "output_quantity": 5,
        "gold_cost": 0,
        "wood_cost": 0,
        "stone_cost": 0,
        "food_cost": 10,
        "required_level": 1
    }
]
