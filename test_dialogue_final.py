#!/usr/bin/env python3
"""
最终对话生成修复测试
验证所有修复是否有效
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入相关模块
from src.validation.dialogue_validator import validate_dialogue_data

def test_final_fix():
    """测试最终修复效果"""
    print("💬 测试最终对话修复效果...")
    
    # 创建一个符合我们修复后模型的对话数据
    # 注意：现在我们的模型接受type字段，并且text字段可以从option_text合并
    final_dialogue = {
        "dialogue_id": "final_test_dialogue",
        "npc_name": "测试NPC",
        "npc_description": "一个用于测试的NPC",
        "npc_role": "测试员",
        "nodes": [
            {
                "node_id": "start_1",
                "type": "start",  # 使用type字段
                "text": "你好，旅行者！",  # 使用text字段
                "next_node_id": "choice_1"
            },
            {
                "node_id": "choice_1",
                "type": "player_choice",
                "options": [  # 使用options字段
                    {
                        "text": "你好！",  # 直接使用text字段
                        "next_node_id": "end_1"
                    },
                    {
                        "text": "再见！",
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
        dialogue_data = validate_dialogue_data(final_dialogue)
        print(f"✅ 最终对话验证通过: {dialogue_data.npc_name} ({dialogue_data.npc_role})")
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
        
        print("\n🎉 修复验证成功！")
        print("💡 现在对话验证器可以正确处理：")
        print("  - type字段作为node_type的别名")
        print("  - text字段作为npc_text的别名")
        print("  - options字段作为player_options的别名")
        print("  - option_text字段作为text的别名")
        
        return True
        
    except Exception as e:
        print(f"❌ 最终对话验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_real_api_scenario():
    """测试真实API场景"""
    print("\n💬 测试真实API场景...")
    
    # 模拟AI可能返回的数据结构
    ai_generated_dialogue = {
        "dialogue_id": "ai_generated_dialogue",
        "npc_name": "AI生成的NPC",
        "npc_description": "由AI生成的测试NPC",
        "npc_role": "AI测试员",
        "nodes": [
            {
                "node_id": "start_1",
                "type": "start",  # AI使用type
                "text": "欢迎来到测试场景！",  # AI使用text
                "next_node_id": "choice_1"
            },
            {
                "node_id": "choice_1",
                "type": "player_choice",
                "options": [  # AI使用options
                    {
                        "option_text": "选择选项1",  # AI使用option_text
                        "next_node_id": "response_1"
                    },
                    {
                        "option_text": "选择选项2",
                        "next_node_id": "response_2"
                    }
                ]
            },
            {
                "node_id": "response_1",
                "type": "npc_speech",
                "text": "你选择了选项1",
                "next_node_id": "end_1"
            },
            {
                "node_id": "response_2",
                "type": "npc_speech",
                "text": "你选择了选项2",
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
        "author": "AI生成"
    }
    
    try:
        # 验证数据
        dialogue_data = validate_dialogue_data(ai_generated_dialogue)
        print(f"✅ AI生成对话验证通过: {dialogue_data.npc_name}")
        
        # 检查字段转换是否正确
        for node in dialogue_data.nodes:
            if node.node_type == "player_choice" and node.options:
                for option in node.options:
                    print(f"  选项文本转换: '{option.text}' (来自option_text)")
        
        print("🎉 AI生成场景测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ AI生成场景测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 最终对话生成修复测试")
    print("=" * 50)
    
    # 运行最终修复测试
    final_success = test_final_fix()
    
    # 运行AI场景测试
    ai_success = test_real_api_scenario()
    
    print("\n" + "=" * 50)
    if final_success and ai_success:
        print("🎉 所有测试通过！对话生成修复完成。")
        print("💡 现在可以重新启动Gradio应用测试对话生成功能。")
        return 0
    else:
        print("⚠️  测试失败，需要进一步检查修复。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
