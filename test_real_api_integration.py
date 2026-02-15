#!/usr/bin/env python3
"""
真实API联调测试脚本
测试优化后的提示词是否能够生成符合Schema的数据
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
from src.fileio.handler import FileHandler

def test_monster_generation():
    """测试怪物生成"""
    print("🧟 测试怪物生成（龙）...")
    
    api_client = DeepSeekClient()
    
    # 组装Prompt
    prompts = prompt_manager.assemble_full_prompt(
        prompt_type="monster_generator",
        monster_type="dragon",
        level=25,
        element="fire",
        special_request="需要3个技能，带有火焰效果和飞行能力"
    )
    
    print(f"📝 系统提示词长度: {len(prompts['system'])} 字符")
    print(f"📝 用户提示词长度: {len(prompts['user'])} 字符")
    
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
        
        # 验证数据
        monster_data = validate_monster_data(monster_dict)
        
        print(f"🎉 怪物生成成功: {monster_data.name} (等级{monster_data.level}, {monster_data.element})")
        
        # 检查关键字段格式
        if 'drops' in monster_dict:
            drops = monster_dict['drops']
            if drops and isinstance(drops, list):
                first_drop = drops[0]
                if isinstance(first_drop, dict) and 'item' in first_drop:
                    print("✅ drops字段格式正确（对象数组）")
                else:
                    print("⚠️  drops字段格式可能有问题")
        
        # 保存文件
        file_handler = FileHandler()
        saved_path = file_handler.save_data(monster_data, "monster", subdirectory="monsters")
        print(f"💾 文件已保存: {saved_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 怪物生成失败: {str(e)}")
        return False

def test_item_generation():
    """测试物品生成"""
    print("\n⚔️  测试物品生成（传说级武器）...")
    
    api_client = DeepSeekClient()
    
    # 组装Prompt
    prompts = prompt_manager.assemble_full_prompt(
        prompt_type="item_generator",
        item_type="weapon",
        item_name="龙息之刃",
        rarity="legendary",
        special_request="双手剑，火属性，传说级武器，带有龙族特效"
    )
    
    print(f"📝 系统提示词长度: {len(prompts['system'])} 字符")
    print(f"📝 用户提示词长度: {len(prompts['user'])} 字符")
    
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
        
        # 验证数据
        item_data = validate_item_data(item_dict)
        
        print(f"🎉 物品生成成功: {item_data.name} ({item_data.rarity} {item_data.weapon_type})")
        
        # 检查关键字段格式
        if 'special_effects' in item_dict:
            effects = item_dict['special_effects']
            if effects and isinstance(effects, list):
                first_effect = effects[0]
                if isinstance(first_effect, dict) and 'name' in first_effect:
                    print("✅ special_effects字段格式正确（对象数组）")
                else:
                    print("⚠️  special_effects字段格式可能有问题")
        
        # 检查visual_prompt长度
        if 'visual_prompt' in item_dict:
            vp_length = len(item_dict['visual_prompt'])
            print(f"🎨 visual_prompt长度: {vp_length} 字符")
            if vp_length <= 400:
                print("✅ visual_prompt长度符合要求（≤400字符）")
            else:
                print(f"⚠️  visual_prompt过长: {vp_length} > 400 字符")
        
        # 保存文件
        file_handler = FileHandler()
        saved_path = file_handler.save_data(item_data, "item", subdirectory="items")
        print(f"💾 文件已保存: {saved_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 物品生成失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始真实API联调测试")
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
        ("怪物生成", test_monster_generation),
        ("物品生成", test_item_generation),
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
        print("\n🎉 所有测试通过！API联调测试完成。")
        print("💡 提示：如果遇到网络超时，请检查网络连接或API密钥配置")
        return 0
    else:
        print("\n⚠️  部分测试失败，需要检查提示词优化或网络连接。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
