"""
NPC对话树数据校验模块
使用Pydantic定义严格的对话树数据模型
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, AliasChoices
from enum import Enum


class DialogueNodeType(str, Enum):
    """对话节点类型枚举"""
    START = "start"
    NPC_SPEECH = "npc_speech"
    PLAYER_CHOICE = "player_choice"
    BRANCH = "branch"
    END = "end"
    CONDITIONAL = "conditional"


class ConditionType(str, Enum):
    """条件类型枚举"""
    QUEST_COMPLETE = "quest_complete"
    ITEM_PRESENT = "item_present"
    SKILL_LEVEL = "skill_level"
    REPUTATION = "reputation"
    TIME_OF_DAY = "time_of_day"
    RANDOM = "random"
    ALWAYS = "always"
    FLAG_CHECK = "flag_check"


class Condition(BaseModel):
    """条件模型"""
    type: ConditionType = Field(..., description="条件类型")
    target: Optional[str] = Field(None, description="条件目标（如任务ID、物品名称等）")
    value: Optional[Any] = Field(None, description="条件值")
    operator: str = Field(default=">=", description="比较运算符")
    
    # 注意：对于always类型的条件，target和value可以为None
    # 我们不需要验证器，因为字段已经是Optional的


class DialogueOption(BaseModel):
    """对话选项模型 - 支持AI生成的灵活字段名"""
    text: Optional[str] = Field(None, min_length=1, max_length=200, description="选项文本")
    option_text: Optional[str] = Field(None, min_length=1, max_length=200, description="选项文本（兼容AI生成）")
    next_node_id: str = Field(..., description="下一个节点ID")
    conditions: List[Condition] = Field(default=[], description="显示条件")
    effects: List[Dict[str, Any]] = Field(default=[], description="选择效果")
    
    # 根验证器，处理字段映射
    @validator('text', pre=True, always=True)
    def merge_text_fields(cls, v, values):
        """合并text和option_text字段"""
        # 如果text为空，但option_text有值，使用option_text
        # 注意：在pre=True阶段，values包含原始输入数据
        if v is None and 'option_text' in values and values['option_text'] is not None:
            return values['option_text']
        return v
    
    @validator('option_text', pre=True, always=True)
    def merge_option_text_fields(cls, v, values):
        """合并option_text和text字段"""
        # 如果option_text为空，但text有值，使用text
        if v is None and 'text' in values and values['text'] is not None:
            return values['text']
        return v
    
    @validator('text', always=True)
    def validate_text_final(cls, v, values):
        """最终验证text字段"""
        # 在合并后验证text字段是否有值
        # 如果text为空，检查option_text是否为空
        if v is None:
            # 检查option_text字段
            option_text = values.get('option_text')
            if option_text is None:
                raise ValueError("选项必须提供text或option_text字段")
        return v
    
    class Config:
        """Pydantic配置"""
        use_enum_values = True
        extra = "ignore"  # 允许额外字段
        validate_assignment = True


class DialogueNode(BaseModel):
    """对话节点模型 - 支持AI生成的灵活字段结构"""
    node_id: str = Field(..., min_length=1, max_length=50, description="节点唯一ID")
    node_type: Optional[DialogueNodeType] = Field(None, description="节点类型")
    type: Optional[str] = Field(None, description="节点类型（兼容AI生成的type字段）")
    
    # 支持AI生成的各种字段名
    # NPC对话内容 - 支持多种字段名
    npc_text: Optional[str] = Field(None, min_length=1, max_length=500, description="NPC对话文本")
    text: Optional[str] = Field(None, min_length=1, max_length=500, description="NPC对话文本（兼容AI生成）")
    npc_name: Optional[str] = Field(None, min_length=1, max_length=50, description="NPC名称")
    emotion: Optional[str] = Field(None, description="NPC情绪状态")
    
    # 玩家选项 - 支持多种字段名
    player_options: List[DialogueOption] = Field(default=[], description="玩家选项列表")
    options: List[DialogueOption] = Field(default=[], description="玩家选项列表（兼容AI生成）")
    
    # 节点连接 - 支持多种字段名
    next_node_id: Optional[str] = Field(None, description="下一个节点ID")
    true_next_node_id: Optional[str] = Field(None, description="条件为真时的下一个节点ID")
    false_next_node_id: Optional[str] = Field(None, description="条件为假时的下一个节点ID")
    
    # 条件与效果
    conditions: List[Condition] = Field(default=[], description="节点激活条件")
    condition: Optional[Condition] = Field(None, description="单个条件（兼容AI生成）")
    effects: List[Dict[str, Any]] = Field(default=[], description="节点触发效果")
    
    # 结束类型
    end_type: Optional[str] = Field(None, description="结束类型（如good_end, bad_end）")
    
    # 元数据
    is_branching: bool = Field(default=False, description="是否为分支节点")
    can_repeat: bool = Field(default=True, description="是否可以重复对话")
    priority: int = Field(default=1, ge=1, le=10, description="节点优先级")
    
    # 自定义验证器
    @validator('node_type', pre=True, always=True)
    def merge_node_type_fields(cls, v, values):
        """合并node_type和type字段 - 优先处理type字段"""
        # 首先检查是否有type字段
        type_field = values.get('type')
        if v is None and type_field is not None:
            # 将type字段的值转换为DialogueNodeType枚举
            try:
                return DialogueNodeType(type_field)
            except ValueError:
                # 如果无法转换，尝试一些常见的映射
                type_mapping = {
                    'start': DialogueNodeType.START,
                    'npc_speech': DialogueNodeType.NPC_SPEECH,
                    'player_choice': DialogueNodeType.PLAYER_CHOICE,
                    'branch': DialogueNodeType.BRANCH,
                    'end': DialogueNodeType.END,
                    'conditional': DialogueNodeType.CONDITIONAL
                }
                if type_field in type_mapping:
                    return type_mapping[type_field]
                else:
                    # 如果无法映射，使用默认值
                    return DialogueNodeType.NPC_SPEECH
        return v
    
    @validator('type', pre=True, always=True)
    def merge_type_fields(cls, v, values):
        """合并type和node_type字段"""
        node_type = values.get('node_type')
        if v is None and node_type is not None:
            return str(node_type)  # 转换为字符串
        return v
    
    @validator('text', pre=True, always=True)
    def merge_text_fields(cls, v, values):
        """合并text和npc_text字段"""
        npc_text = values.get('npc_text')
        if v is None and npc_text is not None:
            return npc_text
        return v
    
    @validator('options', pre=True, always=True)
    def merge_options_fields(cls, v, values):
        """合并options和player_options字段"""
        player_options = values.get('player_options')
        if v is None and player_options is not None:
            return player_options
        return v
    
    @validator('npc_text')
    def validate_npc_text(cls, v, values):
        """验证NPC文本：当节点类型为NPC_SPEECH时必须提供"""
        node_type = values.get('node_type')
        if node_type in [DialogueNodeType.NPC_SPEECH, DialogueNodeType.START] and not v:
            # 检查是否有text字段
            if not values.get('text'):
                raise ValueError("NPC_SPEECH和START类型节点必须提供npc_text或text字段")
        return v
    
    @validator('player_options')
    def validate_player_options(cls, v, values):
        """验证玩家选项：当节点类型为PLAYER_CHOICE时必须提供"""
        node_type = values.get('node_type')
        if node_type == DialogueNodeType.PLAYER_CHOICE and not v:
            # 检查是否有options字段
            if not values.get('options'):
                raise ValueError("PLAYER_CHOICE类型节点必须提供player_options或options字段")
        return v
    
    class Config:
        """Pydantic配置"""
        use_enum_values = True
        extra = "ignore"  # 允许额外字段，避免extra_forbidden错误
        validate_assignment = True


class DialogueTreeSchema(BaseModel):
    """对话树数据模型"""
    
    # 基本信息
    dialogue_id: str = Field(..., min_length=1, max_length=50, description="对话树唯一ID")
    npc_name: str = Field(..., min_length=1, max_length=50, description="NPC名称")
    npc_description: str = Field(..., min_length=10, max_length=500, description="NPC描述")
    npc_role: str = Field(..., min_length=1, max_length=50, description="NPC角色（如铁匠、商人等）")
    
    # 对话节点
    nodes: List[DialogueNode] = Field(..., min_items=1, description="对话节点列表")
    start_node_id: str = Field(..., description="起始节点ID")
    
    # 游戏机制
    is_quest_related: bool = Field(default=False, description="是否与任务相关")
    quest_id: Optional[str] = Field(None, description="关联的任务ID")
    repeatable: bool = Field(default=True, description="对话是否可重复")
    
    # 元数据
    version: str = Field(default="1.0.0", description="对话树版本")
    author: Optional[str] = Field(None, description="作者")
    
    # 自定义验证器
    @validator('start_node_id')
    def validate_start_node(cls, v, values):
        """验证起始节点是否存在"""
        if 'nodes' in values:
            node_ids = [node.node_id for node in values['nodes']]
            if v not in node_ids:
                raise ValueError(f"起始节点ID '{v}' 不存在于节点列表中")
        return v
    
    @validator('nodes')
    def validate_node_connections(cls, v):
        """验证节点连接性"""
        node_ids = {node.node_id for node in v}
        
        for node in v:
            for option in node.player_options:
                if option.next_node_id not in node_ids and option.next_node_id != "END":
                    raise ValueError(f"节点 '{node.node_id}' 的选项指向不存在的节点: {option.next_node_id}")
        
        return v
    
    class Config:
        """Pydantic配置"""
        use_enum_values = True
        extra = "ignore"  # 允许额外字段，避免extra_forbidden错误
        validate_assignment = True


def validate_dialogue_data(data: Dict[str, Any]) -> DialogueTreeSchema:
    """
    验证对话数据是否符合Schema
    
    Args:
        data: 要验证的数据字典
        
    Returns:
        验证通过的DialogueTreeSchema实例
        
    Raises:
        ValueError: 数据验证失败
    """
    try:
        # 预处理数据：处理字段名映射
        processed_data = preprocess_dialogue_data(data)
        return DialogueTreeSchema(**processed_data)
    except Exception as e:
        raise ValueError(f"对话数据验证失败: {str(e)}")


def preprocess_dialogue_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    预处理对话数据，处理字段名映射
    
    Args:
        data: 原始数据
        
    Returns:
        预处理后的数据
    """
    # 深拷贝数据以避免修改原始数据
    import copy
    processed = copy.deepcopy(data)
    
    # 处理节点列表
    if 'nodes' in processed:
        for node in processed['nodes']:
            # 处理节点类型字段映射
            if 'type' in node and 'node_type' not in node:
                node['node_type'] = node['type']
            
            # 处理文本字段映射
            if 'text' in node and 'npc_text' not in node:
                node['npc_text'] = node['text']
            elif 'npc_text' in node and 'text' not in node:
                node['text'] = node['npc_text']
            
            # 处理选项字段映射
            if 'options' in node and 'player_options' not in node:
                node['player_options'] = node['options']
            elif 'player_options' in node and 'options' not in node:
                node['options'] = node['player_options']
            
            # 处理选项中的字段映射
            if 'player_options' in node:
                for option in node['player_options']:
                    # 支持多种字段名：choice_text, option_text, text
                    if 'choice_text' in option and 'text' not in option:
                        option['text'] = option['choice_text']
                    elif 'option_text' in option and 'text' not in option:
                        option['text'] = option['option_text']
                    elif 'text' in option:
                        # 确保其他字段也有值
                        if 'choice_text' not in option:
                            option['choice_text'] = option['text']
                        if 'option_text' not in option:
                            option['option_text'] = option['text']
            
            if 'options' in node:
                for option in node['options']:
                    # 支持多种字段名：choice_text, option_text, text
                    if 'choice_text' in option and 'text' not in option:
                        option['text'] = option['choice_text']
                    elif 'option_text' in option and 'text' not in option:
                        option['text'] = option['option_text']
                    elif 'text' in option:
                        # 确保其他字段也有值
                        if 'choice_text' not in option:
                            option['choice_text'] = option['text']
                        if 'option_text' not in option:
                            option['option_text'] = option['text']
    
    return processed


def generate_dialogue_schema_prompt() -> str:
    """
    生成用于系统提示词的对话Schema描述
    
    Returns:
        Schema描述文本
    """
    schema = DialogueTreeSchema.schema()
    
    prompt = """你是一个专业的游戏剧情设计师。请严格按照以下JSON Schema生成NPC对话树数据：

## 对话数据格式要求：
1. 必须输出纯JSON，不要包含任何Markdown标记或解释性文本
2. 对话树必须逻辑连贯，有合理的开始、发展和结束
3. 玩家选项应提供有意义的选择，影响对话走向

## 字段说明：
"""
    
    for prop_name, prop_info in schema['properties'].items():
        field_type = prop_info.get('type', 'unknown')
        description = prop_info.get('description', '无描述')
        prompt += f"- {prop_name} ({field_type}): {description}\n"
    
    prompt += """
## 节点类型说明：
- start: 对话起始节点
- npc_speech: NPC说话节点
- player_choice: 玩家选择节点
- branch: 分支节点
- end: 对话结束节点
- conditional: 条件节点

## 设计指南：
1. 对话应有合理的流程：开始 -> NPC介绍 -> 玩家选择 -> NPC回应 -> 结束
2. 为重要的NPC（如铁匠、商人）设计有深度的对话树
3. 玩家选项应反映角色性格和游戏选择
4. 可以包含条件分支（如根据玩家声望、任务进度等）

## 示例结构：
{
  "dialogue_id": "blacksmith_dialogue",
  "npc_name": "暴躁的矮人铁匠",
  "npc_description": "一个脾气暴躁但手艺精湛的矮人铁匠...",
  "nodes": [...],
  "start_node_id": "start_1"
}

请严格按照这个格式生成JSON数据。"""
    
    return prompt
