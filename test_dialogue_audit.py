#!/usr/bin/env python3
"""
对话生成模块全盘审计测试脚本
验证Schema、Prompt模板、模拟数据和Gradio参数传递的一致性
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入相关模块
from src.validation.dialogue_validator import DialogueTreeSchema, validate_dialogue_data
from src.prompts.manager import prompt_manager
from src.api.client import DeepSeekClient

def test_schema_definition():
    """测试Schema定义"""
    print("🔍 测试Schema定义...")
    
    # 检查Schema字段
    schema = DialogueTreeSchema.schema()
    required_fields = schema.get('required', [])
    
    print(f"✅ Schema包含 {len(schema['properties'])} 个字段")
    print(f"✅ 必填字段: {required_fields}")
    
    # 验证Schema没有name字段，只有npc_name字段
    properties = schema['properties']
    if 'name' in properties:
        print("❌ Schema错误：包含'name'字段（应为'npc_name'）")
        return False
    if 'npc_name' not in properties:
        print("❌ Schema错误：缺少'npc_name'字段")
        return False
    
    print("✅ Schema字段定义正确")
    return True

def test_prompt_template():
    """测试Prompt模板"""
    print("\n🔍 测试Prompt模板...")
    
    # 获取对话生成提示词
    system_prompt = prompt_manager.get_system_prompt("dialogue_generator")
    
    # 检查提示词是否包含正确的Schema描述
    if "dialogue_id" not in system_prompt:
        print("❌ 提示词缺少'dialogue_id'字段说明")
        return False
    if "npc_name" not in system_prompt:
        print("❌ 提示词缺少'npc_name'字段说明")
        return False
    if "nodes" not in system_prompt:
        print("❌ 提示词缺少'nodes'字段说明")
        return False
    
    print("✅ Prompt模板包含正确的Schema描述")
    
    # 测试组装完整Prompt
    prompts = prompt_manager.assemble_full_prompt(
        prompt_type="dialogue_generator",
        npc_name="测试NPC",
        npc_role="铁匠",
        dialogue_theme="测试对话主题",
        special_request="测试特殊要求"
    )
    
    if 'system' not in prompts or 'user' not in prompts:
        print("❌ 组装Prompt失败：缺少system或user字段")
        return False
    
    print(f"✅ 成功组装Prompt：系统提示词长度={len(prompts['system'])}, 用户提示词长度={len(prompts['user'])}")
    return True

def test_mock_data():
    """测试模拟数据"""
    print("\n🔍 测试模拟数据...")
    
    api_client = DeepSeekClient()
    
    # 生成模拟对话数据
    mock_response = api_client._generate_mock_dialogue_response()
    
    # 提取JSON
    import re
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(json_pattern, mock_response, re.DOTALL)
    
    if not match:
        print("❌ 模拟数据格式错误：未找到JSON代码块")
        return False
    
    json_str = match.group(1).strip()
    json_str = re.sub(r'^```json\s*', '', json_str)
    json_str = re.sub(r'\s*```$', '', json_str)
    
    try:
        mock_data = json.loads(json_str)
        print(f"✅ 模拟数据JSON解析成功，包含 {len(mock_data)} 个字段")
        
        # 验证模拟数据
        dialogue_data = validate_dialogue_data(mock_data)
        print(f"✅ 模拟数据通过Schema验证：{dialogue_data.npc_name} ({dialogue_data.npc_role})")
        
        # 检查节点连接性
        node_ids = {node.node_id for node in dialogue_data.nodes}
        for node in dialogue_data.nodes:
            for option in node.player_options:
                if option.next_node_id not in node_ids and option.next_node_id != "END":
                    print(f"❌ 节点连接错误：{node.node_id} -> {option.next_node_id}")
                    return False
        
        print("✅ 模拟数据节点连接性验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 模拟数据验证失败: {str(e)}")
        return False

def test_gradio_parameters():
    """测试Gradio参数传递"""
    print("\n🔍 测试Gradio参数传递...")
    
    # 从app.py导入generate_dialogue函数
    from app import generate_dialogue
    
    try:
        # 测试调用（使用模拟模式）
        json_output, visual_prompt, status = generate_dialogue(
            npc_name="测试NPC",
            npc_role="铁匠",
            dialogue_theme="测试主题",
            special_request="测试要求",
            use_mock=True
        )
        
        if "✅" in status:
            print(f"✅ Gradio函数调用成功: {status}")
            
            # 验证返回的JSON
            if json_output:
                data = json.loads(json_output)
                if 'dialogue_id' in data and 'npc_name' in data:
                    print(f"✅ 返回JSON格式正确: {data['npc_name']}")
                    return True
                else:
                    print("❌ 返回JSON缺少必要字段")
                    return False
            else:
                print("❌ 未返回JSON数据")
                return False
        else:
            print(f"❌ Gradio函数调用失败: {status}")
            return False
            
    except Exception as e:
        print(f"❌ Gradio参数传递测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始对话生成模块全盘审计")
    print("=" * 50)
    
    tests = [
        ("Schema定义", test_schema_definition),
        ("Prompt模板", test_prompt_template),
        ("模拟数据", test_mock_data),
        ("Gradio参数", test_gradio_parameters),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 审计结果汇总:")
    
    all_passed = True
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！对话生成模块审计完成。")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要修复。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
