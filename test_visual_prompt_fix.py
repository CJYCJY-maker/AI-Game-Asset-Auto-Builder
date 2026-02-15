#!/usr/bin/env python3
"""
测试visual_prompt字段修复效果
使用真实API调用验证visual_prompt是否正确显示
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
from src.validation.validator import validate_monster_data
from src.validation.item_validator import validate_item_data

def test_monster_visual_prompt():
    """测试怪物visual_prompt字段"""
    print("🧟 测试怪物visual_prompt字段...")
    
    api_client = DeepSeekClient()
    
    # 组装Prompt
    prompts = prompt_manager.assemble_full_prompt(
        prompt_type="monster_generator",
        monster_type="goblin",
        level=10,
        element="fire",
        special_request="需要2个技能，带有火焰效果"
    )
    
    try:
        # 调用API（不使用模拟模式）
        response = api_client.generate_content(
            prompt=prompts['user'],
            system_prompt=prompts['system'],
            temperature=0.7,
            mock_mode=False  # 真实API调用
        )
        
        print(f"✅ API响应长度: {len(response)} 字符")
        
        # 提取和验证JSON
        monster_dict = api_client.extract_json_from_response(response)
        
        # 检查是否包含visual_prompt字段
        if 'visual_prompt' in monster_dict:
            visual_prompt = monster_dict['visual_prompt']
            print(f"✅ 怪物数据包含visual_prompt字段")
            print(f"📏 长度: {len(visual_prompt)} 字符")
            print(f"📝 内容预览: {visual_prompt[:100]}...")
            
            # 验证数据
            monster_data = validate_monster_data(monster_dict)
            print(f"🎉 怪物验证通过: {monster_data.name} (等级{monster_data.level})")
            
            # 检查visual_prompt长度是否符合要求
            if 50 <= len(visual_prompt) <= 500:
                print("✅ visual_prompt长度符合要求 (50-500字符)")
            else:
                print(f"⚠️  visual_prompt长度不符合要求: {len(visual_prompt)} 字符")
            
            return True
        else:
            print("❌ 怪物数据不包含visual_prompt字段")
            print(f"📋 可用字段: {list(monster_dict.keys())}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_item_visual_prompt():
    """测试物品visual_prompt字段"""
    print("\n⚔️  测试物品visual_prompt字段...")
    
    api_client = DeepSeekClient()
    
    # 组装Prompt
    prompts = prompt_manager.assemble_full_prompt(
        prompt_type="item_generator",
        item_type="weapon",
        item_name="火焰剑",
        rarity="rare",
        special_request="单手剑，火属性，稀有武器"
    )
    
    try:
        # 调用API（不使用模拟模式）
        response = api_client.generate_content(
            prompt=prompts['user'],
            system_prompt=prompts['system'],
            temperature=0.7,
            mock_mode=False  # 真实API调用
        )
        
        print(f"✅ API响应长度: {len(response)} 字符")
        
        # 提取和验证JSON
        item_dict = api_client.extract_json_from_response(response)
        
        # 检查是否包含visual_prompt字段
        if 'visual_prompt' in item_dict:
            visual_prompt = item_dict['visual_prompt']
            print(f"✅ 物品数据包含visual_prompt字段")
            print(f"📏 长度: {len(visual_prompt)} 字符")
            print(f"📝 内容预览: {visual_prompt[:100]}...")
            
            # 验证数据
            item_data = validate_item_data(item_dict)
            print(f"🎉 物品验证通过: {item_data.name} ({item_data.rarity})")
            
            # 检查visual_prompt长度是否符合要求
            if len(visual_prompt) <= 400:
                print("✅ visual_prompt长度符合要求 (≤400字符)")
            else:
                print(f"⚠️  visual_prompt长度不符合要求: {len(visual_prompt)} > 400 字符")
            
            # 检查是否为英文
            import re
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', visual_prompt)
            if not chinese_chars:
                print("✅ visual_prompt为纯英文")
            else:
                print(f"⚠️  visual_prompt包含中文: {len(chinese_chars)} 个中文字符")
            
            return True
        else:
            print("❌ 物品数据不包含visual_prompt字段")
            print(f"📋 可用字段: {list(item_dict.keys())}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 测试visual_prompt字段修复效果")
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
    tests = [
        ("怪物visual_prompt", test_monster_visual_prompt),
        ("物品visual_prompt", test_item_visual_prompt),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*30}")
            print(f"开始测试: {test_name}")
            print(f"{'='*30}")
            
            success = test_func()
            results.append((test_name, success))
            
            if not success:
                print(f"\n❌ {test_name}测试失败，停止后续测试")
                break
                
        except Exception as e:
            print(f"❌ {test_name}测试异常: {str(e)}")
            results.append((test_name, False))
            break
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    all_passed = True
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！visual_prompt字段修复完成。")
        print("💡 现在Gradio界面应该能正确显示AI绘画提示词了。")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要进一步检查修复。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
