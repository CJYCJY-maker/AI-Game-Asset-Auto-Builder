#!/usr/bin/env python3
"""
测试对话数据预处理
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入相关模块
from src.validation.dialogue_validator import preprocess_dialogue_data, validate_dialogue_data

def test_preprocess():
    """测试数据预处理"""
    print("🔍 测试对话数据预处理...")
    
    # 测试1: AI生成的数据结构
    print("\n测试1: AI生成的数据结构")
    ai_data = {
        "dialogue_id": "test_dialogue",
        "npc_name": "测试NPC",
        "npc_description": "测试描述",
        "npc_role": "测试员",
        "nodes": [
            {
                "node_id": "start_1",
                "type": "start",
                "text": "你好！",
                "next_node_id": "choice_1"
            },
            {
                "node_id": "choice_1",
                "type": "player_choice",
                "options": [
                    {
                        "option_text": "选项1",
                        "next_node_id": "end_1"
                    },
                    {
                        "option_text": "选项2",
                        "next_node_id": "end_2"
                    }
                ]
            },
            {
                "node_id": "end_1",
                "type": "end",
                "text": "结束1"
            },
            {
                "node_id": "end_2",
                "type": "end",
                "text": "结束2"
            }
        ],
        "start_node_id": "start_1"
    }
    
    try:
        processed = preprocess_dialogue_data(ai_data)
        print("✅ 预处理成功")
        
        # 检查预处理结果
        for i, node in enumerate(processed['nodes']):
            print(f"  节点 {i+1}: {node['node_id']}")
            if 'node_type' in node:
                print(f"    节点类型: {node['node_type']} (来自type: {node.get('type')})")
            if 'npc_text' in node:
                print(f"    NPC文本: {node['npc_text'][:30]}...")
            if 'player_options' in node:
                print(f"    玩家选项数量: {len(node['player_options'])}")
                for j, option in enumerate(node['player_options']):
                    print(f"      选项 {j+1}: text='{option.get('text')}', option_text='{option.get('option_text')}'")
        
        # 验证数据
        validated = validate_dialogue_data(ai_data)
        print(f"✅ 验证成功: {validated.npc_name} ({validated.npc_role})")
        print(f"📊 节点数量: {len(validated.nodes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 预处理或验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation():
    """测试完整验证流程"""
    print("\n🔍 测试完整验证流程...")
    
    # 测试数据
    test_data = {
        "dialogue_id": "complete_test",
        "npc_name": "完整的NPC",
        "npc_description": "一个完整的测试NPC描述",
        "npc_role": "测试角色",
        "nodes": [
            {
                "node_id": "start_1",
                "type": "start",
                "text": "欢迎来到测试场景！",
                "next_node_id": "choice_1"
            },
            {
                "node_id": "choice_1",
                "type": "player_choice",
                "options": [
                    {
                        "option_text": "选择第一个选项",
                        "next_node_id": "response_1"
                    },
                    {
                        "option_text": "选择第二个选项",
                        "next_node_id": "response_2"
                    }
                ]
            },
            {
                "node_id": "response_1",
                "type": "npc_speech",
                "text": "你选择了第一个选项",
                "next_node_id": "end_1"
            },
            {
                "node_id": "response_2",
                "type": "npc_speech",
                "text": "你选择了第二个选项",
                "next_node_id": "end_2"
            },
            {
                "node_id": "end_1",
                "type": "end",
                "text": "游戏结束1"
            },
            {
                "node_id": "end_2",
                "type": "end",
                "text": "游戏结束2"
            }
        ],
        "start_node_id": "start_1",
        "is_quest_related": False,
        "repeatable": True,
        "version": "1.0.0",
        "author": "测试系统"
    }
    
    try:
        validated = validate_dialogue_data(test_data)
        print(f"✅ 完整验证成功: {validated.npc_name}")
        print(f"📊 对话ID: {validated.dialogue_id}")
        print(f"📊 版本: {validated.version}")
        
        # 检查节点类型
        for node in validated.nodes:
            print(f"  节点 {node.node_id}: {node.node_type}")
            if node.text:
                print(f"    文本: {node.text[:40]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整验证失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_preprocess()
    success2 = test_validation()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 所有测试通过！对话数据预处理和验证功能正常。")
        print("💡 现在可以重新启动Gradio应用测试对话生成功能。")
    else:
        print("⚠️  测试失败，需要进一步检查修复。")
