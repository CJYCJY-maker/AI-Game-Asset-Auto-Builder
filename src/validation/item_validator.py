"""
装备与物品数据校验模块
使用Pydantic定义严格的物品数据模型
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class ItemRarity(str, Enum):
    """物品稀有度枚举"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class ItemType(str, Enum):
    """物品类型枚举"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST = "quest"


class WeaponType(str, Enum):
    """武器类型枚举"""
    SWORD = "sword"
    GREATSWORD = "greatsword"  # 双手剑
    DAGGER = "dagger"
    STAFF = "staff"
    WAND = "wand"
    BOW = "bow"
    CROSSBOW = "crossbow"
    AXE = "axe"
    MACE = "mace"
    SPEAR = "spear"
    SHIELD = "shield"


class ArmorSlot(str, Enum):
    """防具部位枚举"""
    HEAD = "head"
    CHEST = "chest"
    HANDS = "hands"
    LEGS = "legs"
    FEET = "feet"
    NECK = "neck"
    RING = "ring"
    BACK = "back"


class StatType(str, Enum):
    """属性类型枚举"""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    INTELLIGENCE = "intelligence"
    VITALITY = "vitality"
    AGILITY = "agility"
    LUCK = "luck"
    ATTACK = "attack"
    MAGIC_ATTACK = "magic_attack"
    DEFENSE = "defense"
    MAGIC_DEFENSE = "magic_defense"
    CRITICAL_CHANCE = "critical_chance"
    CRITICAL_DAMAGE = "critical_damage"
    HEALTH = "health"
    MANA = "mana"
    STAMINA = "stamina"


class StatBonus(BaseModel):
    """属性加成模型"""
    stat: StatType = Field(..., description="属性类型")
    value: int = Field(..., description="加成数值")
    is_percentage: bool = Field(default=False, description="是否为百分比加成")


class SpecialEffect(BaseModel):
    """特殊效果模型"""
    name: str = Field(..., min_length=1, max_length=50, description="效果名称")
    description: str = Field(..., min_length=10, max_length=200, description="效果描述")
    trigger_condition: Optional[str] = Field(None, description="触发条件")
    cooldown: Optional[int] = Field(None, ge=0, description="冷却时间（回合）")


class ItemSchema(BaseModel):
    """物品数据模型 - 严格定义所有必填字段"""
    
    # 基本信息
    name: str = Field(..., min_length=1, max_length=100, description="物品名称")
    type: ItemType = Field(..., description="物品类型")
    rarity: ItemRarity = Field(..., description="物品稀有度")
    
    # 类型特定字段
    weapon_type: Optional[WeaponType] = Field(None, description="武器类型（仅武器有效）")
    armor_slot: Optional[ArmorSlot] = Field(None, description="防具部位（仅防具有效）")
    
    # 数值属性
    level_requirement: int = Field(..., ge=1, le=100, description="使用等级要求")
    durability: Optional[int] = Field(None, ge=1, description="耐久度")
    weight: float = Field(..., ge=0.0, description="重量")
    value: int = Field(..., ge=0, description="基础价值（金币）")
    
    # 属性加成
    stat_bonuses: List[StatBonus] = Field(default=[], description="属性加成列表")
    
    # 特殊效果
    special_effects: List[SpecialEffect] = Field(default=[], description="特殊效果列表")
    
    # 描述与背景
    description: str = Field(..., min_length=20, max_length=500, description="物品描述")
    lore: str = Field(..., min_length=50, max_length=1000, description="背景故事")
    flavor_text: Optional[str] = Field(None, max_length=200, description="趣味文本")
    
    # 游戏机制
    is_soulbound: bool = Field(default=False, description="是否灵魂绑定")
    is_tradable: bool = Field(default=True, description="是否可交易")
    is_droppable: bool = Field(default=True, description="是否可掉落")
    stack_size: int = Field(default=1, ge=1, description="堆叠数量")
    
    # 视觉与美术
    visual_prompt: str = Field(..., min_length=50, max_length=500, description="AI绘画提示词")
    
    # 自定义验证器
    @validator('weapon_type')
    def validate_weapon_type(cls, v, values):
        """验证武器类型：仅当物品类型为武器时有效"""
        if v is not None and values.get('type') != ItemType.WEAPON:
            raise ValueError("weapon_type仅对武器类型物品有效")
        return v
    
    @validator('armor_slot')
    def validate_armor_slot(cls, v, values):
        """验证防具部位：仅当物品类型为防具时有效"""
        if v is not None and values.get('type') != ItemType.ARMOR:
            raise ValueError("armor_slot仅对防具类型物品有效")
        return v
    
    @validator('durability')
    def validate_durability(cls, v, values):
        """验证耐久度：仅对武器和防具有效"""
        if v is not None and values.get('type') not in [ItemType.WEAPON, ItemType.ARMOR]:
            raise ValueError("durability仅对武器和防具有效")
        return v
    
    class Config:
        """Pydantic配置"""
        use_enum_values = True
        extra = "forbid"
        validate_assignment = True


def validate_item_data(data: Dict[str, Any]) -> ItemSchema:
    """
    验证物品数据是否符合Schema
    
    Args:
        data: 要验证的数据字典
        
    Returns:
        验证通过的ItemSchema实例
        
    Raises:
        ValueError: 数据验证失败
    """
    try:
        return ItemSchema(**data)
    except Exception as e:
        raise ValueError(f"物品数据验证失败: {str(e)}")


def generate_item_schema_prompt() -> str:
    """
    生成用于系统提示词的物品Schema描述
    
    Returns:
        Schema描述文本
    """
    schema = ItemSchema.schema()
    
    prompt = """你是一个专业的游戏物品设计师。请严格按照以下JSON Schema生成游戏物品数据：

## 物品数据格式要求：
1. 必须输出纯JSON，不要包含任何Markdown标记或解释性文本
2. 所有字段都是必填的，除非特别注明为可选
3. 数值必须在合理范围内（如等级要求1-100，价值非负）

## 字段说明：
"""
    
    for prop_name, prop_info in schema['properties'].items():
        field_type = prop_info.get('type', 'unknown')
        description = prop_info.get('description', '无描述')
        prompt += f"- {prop_name} ({field_type}): {description}\n"
    
    prompt += """
## 枚举值说明：
- type: weapon, armor, accessory, consumable, material, quest
- rarity: common, uncommon, rare, epic, legendary, mythic
- weapon_type: sword, greatsword, dagger, staff, wand, bow, crossbow, axe, mace, spear, shield
- armor_slot: head, chest, hands, legs, feet, neck, ring, back
- stat: strength, dexterity, intelligence, vitality, agility, luck, attack, magic_attack, defense, magic_defense, critical_chance, critical_damage, health, mana, stamina

## 视觉提示词要求：
visual_prompt字段必须是高质量的英文AI绘画提示词，包含：
1. 艺术风格（如masterpiece, best quality）
2. 物品外观详细描述
3. 材质、颜色、光影效果
4. 适合Stable Diffusion的格式

## 示例结构：
{
  "name": "霜之哀伤",
  "type": "weapon",
  "rarity": "legendary",
  "weapon_type": "greatsword",
  ...
}

请严格按照这个格式生成JSON数据。"""
    
    return prompt
