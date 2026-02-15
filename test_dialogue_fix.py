#!/usr/bin/env python3
"""
测试对话生成修复效果
验证AI生成的对话树能够通过Pydantic验证
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入相关模块
from src.api.client import DeepSeekClient
from src.prompts.manager import prompt_manager
from src.validation.dialogue_validator import validate_dialogue_data

def test_dialogue_generation():
    """测试对话生成"""
    print("💬 测试对话生成修复效果...")
    
    api_client = DeepSeekClient()
    
    # 组装Prompt - 生成一个美丽的魔女对话
    prompts = prompt_manager.assemble_full_prompt(
        prompt_type="dialogue_generator",
        npc_name="美丽的魔女",
        npc_role="神秘人",
        dialogue_theme="关于命运与选择的对话",
        special_request="包含3个分支结局：好结局、坏结局、隐藏结局"
    )
    
    try:
        print(f"📝 系统提示词长度: {len(prompts['system'])} 字符")
        print(f"📝 用户提示词长度: {len(prompts['user'])} 字符")
        
        # 调用API（不使用模拟模式）
        response = api_client.generate_content(
            prompt=prompts['user'],
            system_prompt=prompts['system'],
            temperature=0.7,
            mock_mode=False  # 真实API调用
        )
        
        print(f"✅ API响应长度: {len(response)} 字符")
        
        # 提取和验证JSON
        dialogue_dict = api_client.extract_json_from_response(response)
        
        # 验证数据
        dialogue_data = validate_dialogue_data(dialogue_dict)
        print(f"🎉 对话验证通过: {dialogue_data.npc_name} ({dialogue_data.npc_role})")
        
        # 打印对话树信息
        print(f"📊 对话树统计:")
        print(f"  - 节点数量: {len(dialogue_data.nodes)}")
        
        # 统计节点类型
        node_types = {}
        for node in dialogue_data.nodes:
            node_type = node.node_type
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print(f"  - 节点类型分布:")
        for node_type, count in node_types.items():
            print(f"    - {node_type}: {count}个")
        
        # 检查起始节点
        start_node = next((node for node in dialogue_data.nodes if node.node_id == dialogue_data.start_node_id), None)
        if start_node:
            print(f"  - 起始节点: {start_node.node_id} ({start_node.node_type})")
        
        # 检查是否有分支结局
        end_nodes = [node for node in dialogue_data.nodes if node.node_type == "end"]
        if end_nodes:
            print(f"  - 结束节点数量: {len(end_nodes)}")
            for end_node in end_nodes[:3]:  # 显示前3个结束节点
                end_type = getattr(end_node, 'end_type', '未指定')
                print(f"    - {end_node.node_id}: {end_type}")
        
        # 保存示例文件
        output_dir = Path("output/test_dialogues")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"test_dialogue_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dialogue_dict, f, ensure_ascii=False, indent=2)
        
        print(f"💾 对话已保存: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 测试对话生成修复效果")
    print("=" * 50)
    
    print("⚠️  注意：这将进行真实的DeepSeek API调用，需要网络连接和有效的API密钥")
    print("=" * 50)
    
    # 检查API密钥
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 未找到DEEPSEEK_API_KEY，请在.env文件中配置")
        return 1
    
    print(f"✅ 找到API密钥: {api_key[:10]}...")
    
    # 运行测试
    try:
        success = test_dialogue_generation()
        
        if success:
            print("\n" + "=" * 50)
            print("🎉 对话生成测试通过！修复完成。")
            print("💡 现在Gradio界面的对话生成功能应该能正常工作了。")
            return 0
        else:
            print("\n" + "=" * 50)
            print("⚠️  对话生成测试失败，需要进一步检查修复。")
            return 1
            
    except Exception as e:
        print(f"\n❌ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
