"""
Prompt模板引擎
存储预设的系统提示词，与用户输入进行拼接
"""

from typing import Dict, Any, Optional
from src.validation.validator import generate_monster_schema_prompt
from src.validation.item_validator import generate_item_schema_prompt
from src.validation.dialogue_validator import generate_dialogue_schema_prompt


class PromptManager:
    """Prompt模板管理器"""
    
    def __init__(self):
        self.system_prompts = {
            "monster_generator": self._get_monster_generator_prompt(),
            "item_generator": self._get_item_generator_prompt(),
            "dialogue_generator": self._get_dialogue_generator_prompt(),
        }
    
    def _get_monster_generator_prompt(self) -> str:
        """获取怪物生成器系统提示词"""
        schema_prompt = generate_monster_schema_prompt()
        
        return f"""{schema_prompt}

## 游戏数值平衡指南：
1. 属性成长：每级生命值增长约80-120，攻击力增长约8-12
2. 技能设计：每个技能应有独特效果，避免重复
3. 元素相克：合理设计弱点和抵抗，保持战斗平衡
4. 掉落物品：稀有度与怪物难度匹配

## 重要格式约束（必须严格遵守）：
1. drops字段必须是对象数组，绝对不能是字符串数组！
   正确格式示例："drops": [{{"item": "怪物素材", "chance": 0.5, "quantity": "1-2"}}]
   错误格式示例："drops": ["怪物素材", "金币"] （绝对不允许！）
2. skill_list字段必须是对象数组，每个技能必须包含name、type、element、power、cost、description等完整字段
3. weaknesses和resistances字段必须是字符串数组，如["fire", "lightning"]
4. 元素一致性规则：怪物不能弱于自己的元素！
   例如：火属性怪物（element: "fire"）的weaknesses不能包含"fire"
5. visual_prompt字段必须是高质量的英文AI绘画提示词，总长度在50-500字符之间！
   要求：纯英文，包含艺术风格、怪物外观详细描述、材质、颜色、光影效果，适合Stable Diffusion

## 输出要求：
- 只输出JSON对象，不要有任何额外文本
- 确保所有数值在合理范围内
- 技能描述要具体且有游戏感
- 怪物描述要生动形象，体现其特性

现在请根据用户需求生成怪物数据："""
    
    def _get_item_generator_prompt(self) -> str:
        """获取物品生成器系统提示词"""
        schema_prompt = generate_item_schema_prompt()
        
        return f"""{schema_prompt}

## 游戏物品设计指南：
1. 稀有度平衡：传说级物品应有独特背景故事和强大效果
2. 属性设计：根据物品类型和等级合理分配属性加成
3. 特殊效果：高稀有度物品应有独特的主动或被动效果
4. 背景故事：为物品创作有深度的背景故事，增强游戏沉浸感

## 重要格式约束（必须严格遵守）：
1. special_effects字段必须是对象数组，绝对不能是字符串数组！
   正确格式示例："special_effects": [{{"name": "霜冻之触", "description": "攻击有30%概率冻结敌人", "trigger_condition": "on_hit", "cooldown": 0}}]
   错误格式示例："special_effects": ["攻击有30%概率冻结敌人", "击败敌人恢复生命"] （绝对不允许！）
2. stat_bonuses字段必须是对象数组，每个对象必须包含stat、value和is_percentage字段
3. visual_prompt必须是高度精简的英文AI绘画提示词，总长度绝对不允许超过400个字符！
   要求：纯英文，包含艺术风格、外观描述、材质、颜色、光影效果，剔除所有废话和冗余描述

## 输出要求：
- 只输出JSON对象，不要有任何额外文本
- visual_prompt必须严格控制在400字符以内
- 背景故事要丰富且有深度
- 数值设计要平衡且符合游戏设定

现在请根据用户需求生成物品数据："""
    
    def _get_dialogue_generator_prompt(self) -> str:
        """获取对话生成器系统提示词"""
        schema_prompt = generate_dialogue_schema_prompt()
        
        return f"""{schema_prompt}

## NPC对话设计指南：
1. 角色塑造：通过对话体现NPC的性格特点（如暴躁、友善、神秘等）
2. 对话流程：设计自然的对话流程，避免生硬的转折
3. 玩家选择：提供有意义的选项，影响对话走向或游戏进程
4. 条件分支：合理使用条件分支增加对话深度和重玩价值

## 极其重要的格式约束（必须严格遵守）：
1. 玩家选项的文本必须严格使用键名 "text"，绝不能使用 "choice_text" 或 "option_text"！
   正确格式示例："text": "你好，我想了解这个任务"
   错误格式示例："choice_text": "你好，我想了解这个任务" （绝对不允许！）
2. 条件判定 type 必须从已知的列表中选取：quest_complete, item_present, skill_level, reputation, time_of_day, random, always, flag_check
3. 对于 "always" 类型的条件，不需要提供 target 和 value 字段
4. 确保所有必填字段都有值，不要遗漏任何必需字段

## 输出要求：
- 只输出JSON对象，不要有任何额外文本
- 对话树必须逻辑连贯，有明确的开始和结束
- 玩家选项应反映不同的角色扮演选择
- 可以包含幽默、悬念或情感元素增强沉浸感

现在请根据用户需求生成NPC对话树："""
    
    def get_system_prompt(self, prompt_type: str = "monster_generator") -> str:
        """
        获取系统提示词
        
        Args:
            prompt_type: 提示词类型
            
        Returns:
            系统提示词文本
        """
        if prompt_type not in self.system_prompts:
            raise ValueError(f"未知的提示词类型: {prompt_type}")
        
        return self.system_prompts[prompt_type]
    
    def build_user_prompt(self, 
                         monster_type: str = None,
                         level: int = None,
                         element: Optional[str] = None,
                         special_request: Optional[str] = None,
                         item_type: Optional[str] = None,
                         item_name: Optional[str] = None,
                         rarity: Optional[str] = None,
                         npc_name: Optional[str] = None,
                         npc_role: Optional[str] = None,
                         dialogue_theme: Optional[str] = None) -> str:
        """
        构建用户提示词
        
        Args:
            monster_type: 怪物类型
            level: 怪物等级
            element: 元素属性
            special_request: 特殊要求
            item_type: 物品类型
            item_name: 物品名称
            rarity: 物品稀有度
            npc_name: NPC名称
            npc_role: NPC角色
            dialogue_theme: 对话主题
            
        Returns:
            用户提示词文本
        """
        if monster_type:
            prompt = f"请生成一个{level}级的{monster_type}怪物"
            
            if element:
                prompt += f"，元素属性为{element}"
            
            if special_request:
                prompt += f"。特殊要求：{special_request}"
            
            prompt += "。请确保数值平衡且符合游戏设定。"
            return prompt
        
        elif item_type:
            prompt = f"请生成一个{item_type}"
            
            if item_name:
                prompt += f"，名称为{item_name}"
            
            if rarity:
                prompt += f"，稀有度为{rarity}"
            
            if special_request:
                prompt += f"。特殊要求：{special_request}"
            
            prompt += "。请确保设计合理且符合游戏设定。"
            return prompt
        
        elif npc_name or npc_role:
            prompt = f"请生成一个"
            
            if npc_name:
                prompt += f"名为{npc_name}的"
            
            if npc_role:
                prompt += f"{npc_role}"
            else:
                prompt += "NPC"
            
            if dialogue_theme:
                prompt += f"的对话树，主题为：{dialogue_theme}"
            else:
                prompt += "的对话树"
            
            if special_request:
                prompt += f"。特殊要求：{special_request}"
            
            prompt += "。请确保对话逻辑连贯且有深度。"
            return prompt
        
        else:
            raise ValueError("必须提供monster_type、item_type或npc_name/npc_role")
    
    def assemble_full_prompt(self,
                           prompt_type: str = "monster_generator",
                           **kwargs) -> Dict[str, str]:
        """
        组装完整Prompt（系统提示词 + 用户提示词）
        
        Args:
            prompt_type: 提示词类型
            **kwargs: 传递给build_user_prompt的参数
            
        Returns:
            包含system和user的字典
        """
        system_prompt = self.get_system_prompt(prompt_type)
        
        # 根据提示词类型传递不同的参数
        if prompt_type == "monster_generator":
            user_prompt = self.build_user_prompt(
                monster_type=kwargs.get('monster_type'),
                level=kwargs.get('level'),
                element=kwargs.get('element'),
                special_request=kwargs.get('special_request')
            )
        elif prompt_type == "item_generator":
            user_prompt = self.build_user_prompt(
                item_type=kwargs.get('item_type'),
                item_name=kwargs.get('item_name'),
                rarity=kwargs.get('rarity'),
                special_request=kwargs.get('special_request')
            )
        elif prompt_type == "dialogue_generator":
            user_prompt = self.build_user_prompt(
                npc_name=kwargs.get('npc_name'),
                npc_role=kwargs.get('npc_role'),
                dialogue_theme=kwargs.get('dialogue_theme'),
                special_request=kwargs.get('special_request')
            )
        else:
            user_prompt = "请生成相应的游戏数据。"
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }


# 单例实例
prompt_manager = PromptManager()
