"""
数据校验模块 - 使用Pydantic定义严格的数据模型
确保DeepSeek返回的数据格式100%正确
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class ElementType(str, Enum):
    """元素类型枚举"""
    FIRE = "fire"
    WATER = "water"
    ICE = "ice"
    EARTH = "earth"
    WIND = "wind"
    LIGHTNING = "lightning"
    LIGHT = "light"
    DARK = "dark"
    NONE = "none"


class SkillType(str, Enum):
    """技能类型枚举"""
    PHYSICAL = "physical"
    MAGIC = "magic"
    BUFF = "buff"
    DEBUFF = "debuff"
    HEAL = "heal"
    SUMMON = "summon"


class DropItem(BaseModel):
    """掉落物品模型"""
    item: str = Field(..., description="物品名称")
    chance: float = Field(..., ge=0.0, le=1.0, description="掉落概率(0-1)")
    quantity: str = Field(..., description="数量范围，如'1-3'或'1'")


class Skill(BaseModel):
    """技能模型"""
    name: str = Field(..., min_length=1, max_length=50, description="技能名称")
    type: SkillType = Field(..., description="技能类型")
    element: ElementType = Field(default=ElementType.NONE, description="元素属性")
    power: int = Field(..., ge=0, description="技能威力")
    cost: int = Field(default=0, ge=0, description="消耗(MP/能量)")
    description: str = Field(..., min_length=5, max_length=200, description="技能描述")
    
    # 可选字段
    effect: Optional[str] = Field(None, description="效果类型(如attack_up)")
    duration: Optional[int] = Field(None, ge=1, description="持续回合数")
    target: Optional[str] = Field("single", description="目标类型(single/all/self)")


class MonsterSchema(BaseModel):
    """怪物数据模型 - 严格定义所有必填字段"""
    
    # 基本信息
    name: str = Field(..., min_length=1, max_length=50, description="怪物名称")
    type: str = Field(..., min_length=1, max_length=30, description="怪物类型")
    element: ElementType = Field(..., description="元素属性")
    level: int = Field(..., ge=1, le=100, description="等级(1-100)")
    
    # 基础属性
    health: int = Field(..., ge=1, description="生命值")
    attack: int = Field(..., ge=0, description="攻击力")
    defense: int = Field(..., ge=0, description="防御力")
    magic_attack: int = Field(..., ge=0, description="魔法攻击力")
    magic_defense: int = Field(..., ge=0, description="魔法防御力")
    speed: int = Field(..., ge=0, description="速度")
    
    # 技能系统
    skills: int = Field(..., ge=0, description="技能数量")
    skill_list: List[Skill] = Field(..., min_items=0, description="技能列表")
    
    # 元素相克
    weaknesses: List[ElementType] = Field(default=[], description="弱点元素")
    resistances: List[ElementType] = Field(default=[], description="抵抗元素")
    
    # 掉落系统
    drops: List[DropItem] = Field(default=[], description="掉落物品列表")
    
    # 战斗奖励
    experience: int = Field(..., ge=0, description="经验值")
    gold: int = Field(..., ge=0, description="金币奖励")
    
    # 描述与行为
    description: str = Field(..., min_length=10, max_length=500, description="怪物描述")
    ai_behavior: str = Field(default="aggressive", description="AI行为模式")
    spawn_areas: List[str] = Field(default=[], description="出现区域")
    rarity: str = Field(default="common", description="稀有度")
    
    # 视觉与美术
    visual_prompt: str = Field(..., min_length=50, max_length=500, description="AI绘画提示词")
    
    # 自定义验证器
    @validator('skill_list')
    def validate_skill_count(cls, v, values):
        """验证技能数量与技能列表长度一致"""
        if 'skills' in values and len(v) != values['skills']:
            raise ValueError(f"技能数量({values['skills']})与技能列表长度({len(v)})不匹配")
        return v
    
    @validator('weaknesses')
    def validate_weaknesses_consistency(cls, v, values):
        """验证弱点一致性：怪物不能弱于自己的元素"""
        if 'element' in values and values['element'] in v:
            raise ValueError(f"怪物不能弱于自己的元素: {values['element']}")
        return v
    
    @validator('resistances')
    def validate_resistances_consistency(cls, v, values):
        """验证抵抗一致性：怪物可以抵抗自己的元素，但不能弱于自己的元素"""
        # 注意：这里允许怪物抵抗自己的元素，这是合理的游戏设计
        # 例如：火属性怪物可以抵抗火元素伤害
        return v
    
    class Config:
        """Pydantic配置"""
        use_enum_values = True  # 使用枚举值而不是枚举对象
        extra = "forbid"  # 禁止额外字段
        validate_assignment = True  # 赋值时验证


def validate_monster_data(data: Dict[str, Any]) -> MonsterSchema:
    """
    验证怪物数据是否符合Schema
    
    Args:
        data: 要验证的数据字典
        
    Returns:
        验证通过的MonsterSchema实例
        
    Raises:
        ValueError: 数据验证失败
    """
    try:
        return MonsterSchema(**data)
    except Exception as e:
        raise ValueError(f"怪物数据验证失败: {str(e)}")


def generate_monster_schema_prompt() -> str:
    """
    生成用于系统提示词的Schema描述
    
    Returns:
        Schema描述文本
    """
    schema = MonsterSchema.schema()
    
    prompt = """你是一个专业的游戏数值策划师。请严格按照以下JSON Schema生成怪物数据：

## 怪物数据格式要求：
1. 必须输出纯JSON，不要包含任何Markdown标记或解释性文本
2. 所有字段都是必填的，除非特别注明为可选
3. 数值必须在合理范围内（如等级1-100，概率0-1）

## 字段说明：
"""
    
    for prop_name, prop_info in schema['properties'].items():
        field_type = prop_info.get('type', 'unknown')
        description = prop_info.get('description', '无描述')
        prompt += f"- {prop_name} ({field_type}): {description}\n"
    
    prompt += """
## 枚举值说明：
- element: fire, water, ice, earth, wind, lightning, light, dark, none
- skill.type: physical, magic, buff, debuff, heal, summon

## 视觉提示词要求：
visual_prompt字段必须是高质量的英文AI绘画提示词，包含：
1. 艺术风格（如masterpiece, best quality）
2. 怪物外观详细描述
3. 材质、颜色、光影效果
4. 适合Stable Diffusion的格式

## 示例结构：
{
  "name": "火焰哥布林",
  "type": "goblin",
  "element": "fire",
  "level": 5,
  "health": 500,
  "visual_prompt": "masterpiece, best quality, a fearsome fire goblin with red skin, sharp claws, burning eyes...",
  ...
}

请严格按照这个格式生成JSON数据。"""
    
    return prompt
