#!/usr/bin/env python3
"""
简单测试对话生成修复效果
使用模拟模式验证Pydantic模型修复
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入相关模块
from src.validation.dialogue_validator import validate_dialogue_data, DialogueTreeSchema

def test_simple_dialogue():
    """测试简单的对话数据"""
    print("💬 测试简单对话数据验证...")
    
    # 创建一个简单的对话数据（模拟AI生成的结构）
    simple_dialogue = {
        "dialogue_id": "test_dialogue_001",
        "npc_name": "测试NPC",
        "npc_description": "一个用于测试的NPC",
        "npc_role": "测试员",
        "nodes": [
            {
                "node_id": "start_1",
                "type": "start",  # AI可能使用type而不是node_type
                "text": "你好，旅行者！",  # AI可能使用text而不是npc_text
                "next_node_id": "choice_1"
            },
            {
                "node_id": "choice_1",
                "type": "player_choice",
                "options": [  # AI可能使用options而不是player_options
                    {
                        "option_text": "你好！",  # AI可能使用option_text而不是text
                        "next_node_id": "end_1"
                    },
                    {
                        "option_text": "再见！",
                        "next_node_id": "end_2"
                    }
                ]
            },
            {
                "node_id": "end_1",
                "type": "end",
                "text": "很高兴见到你！"
            },
            {
                "node_id": "end_2",
                "type": "end",
                "text": "再见！"
            }
        ],
        "start_node_id": "start_1",
        "is_quest_related": False,
        "repeatable": True,
        "version": "1.0.0",
        "author": "测试系统"
    }
    
    try:
        # 验证数据
        dialogue_data = validate_dialogue_data(simple_dialogue)
        print(f"✅ 简单对话验证通过: {dialogue_data.npc_name} ({dialogue_data.npc_role})")
        print(f"📊 节点数量: {len(dialogue_data.nodes)}")
        
        # 检查字段映射是否正确
        for i, node in enumerate(dialogue_data.nodes):
            print(f"  节点 {i+1}: {node.node_id} ({node.node_type})")
            if node.text:
                print(f"    文本: {node.text[:50]}...")
            if node.options:
                print(f"    选项数量: {len(node.options)}")
                for j, option in enumerate(node.options):
                    print(f"      选项 {j+1}: {option.text[:30]}... -> {option.next_node_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 简单对话验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_complex_dialogue():
    """测试更复杂的对话数据"""
    print("\n💬 测试复杂对话数据验证...")
    
    # 创建一个更复杂的对话数据（模拟AI生成的结构）
    complex_dialogue = {
        "dialogue_id": "complex_dialogue_001",
        "npc_name": "神秘的魔女",
        "npc_description": "一位拥有月光般银发与紫罗兰色眼眸的神秘女性",
        "npc_role": "命运揭示者",
        "nodes": [
            {
                "node_id": "start_1",
                "node_type": "start",
                "npc_text": "（魔女并未看你，只是凝视着手中悬浮的水晶球）旅人……你身上缠绕的丝线，比常人更加复杂。",
                "next_node_id": "choice_1"
            },
            {
                "node_id": "choice_1",
                "node_type": "player_choice",
                "player_options": [
                    {
                        "text": "我想知道我的命运",
                        "next_node_id": "response_1"
                    },
                    {
                        "text": "我只是路过",
                        "next_node_id": "end_1"
                    }
                ]
            },
            {
                "node_id": "response_1",
                "node_type": "npc_speech",
                "text": "命运……既是礼物，也是诅咒。你准备好了吗？",
                "next_node_id": "choice_2"
            },
            {
                "node_id": "choice_2",
                "node_type": "player_choice",
                "player_options": [
                    {
                        "text": "是的，我准备好了",
                        "next_node_id": "end_good"
                    },
                    {
                        "text": "不，我还没准备好",
                        "next_node_id": "end_bad"
                    }
                ]
            },
            {
                "node_id": "end_good",
                "node_type": "end",
                "text": "那么，接受你的命运吧……",
                "end_type": "good_end"
            },
            {
                "node_id": "end_bad",
                "node_type": "end",
                "text": "明智的选择……但命运终将找到你。",
                "end_type": "bad_end"
            },
            {
                "node_id": "end_1",
                "node_type": "end",
                "text": "那么，愿命运指引你的道路。"
            }
        ],
        "start_node_id": "start_1",
        "is_quest_related": True,
        "quest_id": "quest_fate_reveal",
        "repeatable": False,
        "version": "1.0.0",
        "author": "神秘系统"
    }
    
    try:
        # 验证数据
        dialogue_data = validate_dialogue_data(complex_dialogue)
        print(f"✅ 复杂对话验证通过: {dialogue_data.npc_name} ({dialogue_data.npc_role})")
        print(f"📊 节点数量: {len(dialogue_data.nodes)}")
        
        # 统计节点类型
        node_types = {}
        for node in dialogue_data.nodes:
            node_type = node.node_type
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print(f"📊 节点类型分布:")
        for node_type, count in node_types.items():
            print(f"  - {node_type}: {count}个")
        
        # 检查结束节点
        end_nodes = [node for node in dialogue_data.nodes if node.node_type == "end"]
        print(f"📊 结束节点:")
        for end_node in end_nodes:
            end_type = getattr(end_node, 'end_type', '未指定')
            print(f"  - {end_node.node_id}: {end_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ 复杂对话验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 测试对话生成修复效果（模拟模式）")
    print("=" * 50)
    
    # 运行简单测试
    simple_success = test_simple_dialogue()
    
    # 运行复杂测试
    complex_success = test_complex_dialogue()
    
    print("\n" + "=" * 50)
    if simple_success and complex_success:
        print("🎉 所有模拟测试通过！对话验证器修复完成。")
        print("💡 现在Pydantic模型应该能正确处理AI生成的各种字段名变体。")
        return 0
    else:
        print("⚠️  模拟测试失败，需要进一步检查修复。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
