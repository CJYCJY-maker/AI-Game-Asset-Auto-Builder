#!/usr/bin/env python3
"""
测试脚本：生成冰属性雪山巨魔（强制使用模拟模式）
用于展示完整的工作流和验证机制
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.client import DeepSeekClient
from src.prompts.manager import prompt_manager
from src.validation.validator import validate_monster_data
from src.fileio.handler import file_handler
from datetime import datetime

def main():
    print("=" * 70)
    print("🧪 独立游戏资产与配置自动构建器 - 完整工作流测试")
    print("=" * 70)
    
    # 1. 初始化组件
    print("\n1. 🔧 初始化系统组件...")
    api_client = DeepSeekClient()
    
    # 2. 组装Prompt
    print("\n2. 📝 组装Prompt模板...")
    prompts = prompt_manager.assemble_full_prompt(
        prompt_type="monster_generator",
        monster_type="troll",
        level=15,
        element="ice",
        special_request="需要3个技能，名称为雪山巨魔"
    )
    
    print(f"   • 系统提示词长度: {len(prompts['system'])} 字符")
    print(f"   • 用户指令: {prompts['user']}")
    
    # 3. 调用API（强制使用模拟模式）
    print("\n3. 🌐 调用DeepSeek API（模拟模式）...")
    response = api_client.generate_content(
        prompt=prompts['user'],
        system_prompt=prompts['system'],
        temperature=0.7,
        mock_mode=True  # 强制使用模拟模式
    )
    
    print(f"   ✅ 收到API响应: {len(response)} 字符")
    
    # 4. 提取JSON
    print("\n4. 🔍 从响应中提取JSON数据...")
    try:
        monster_dict = api_client.extract_json_from_response(response)
        print(f"   ✅ JSON提取成功: {len(monster_dict)} 个字段")
    except Exception as e:
        print(f"   ❌ JSON提取失败: {str(e)}")
        return
    
    # 5. 验证数据
    print("\n5. ⚙️ 使用Pydantic Schema验证数据...")
    try:
        monster_data = validate_monster_data(monster_dict)
        print(f"   ✅ 数据验证通过！")
        print(f"   • 怪物名称: {monster_data.name}")
        print(f"   • 元素属性: {monster_data.element}")
        print(f"   • 等级: {monster_data.level}")
        print(f"   • 生命值: {monster_data.health}")
        print(f"   • 技能数: {monster_data.skills}")
    except Exception as e:
        print(f"   ❌ 数据验证失败: {str(e)}")
        print("\n   🔧 尝试修复数据...")
        
        # 尝试修复常见问题
        if "resistances" in monster_dict and "ice" in monster_dict["resistances"]:
            print("   • 修复: 移除怪物对自己元素的抵抗")
            monster_dict["resistances"] = [r for r in monster_dict["resistances"] if r != "ice"]
        
        # 重新验证
        try:
            monster_data = validate_monster_data(monster_dict)
            print(f"   ✅ 修复后验证通过！")
        except Exception as e2:
            print(f"   ❌ 修复后仍然失败: {str(e2)}")
            return
    
    # 6. 保存文件
    print("\n6. 💾 保存怪物数据到文件...")
    try:
        saved_path = file_handler.save_monster_data(monster_data)
        print(f"   ✅ 文件保存成功: {saved_path}")
        print(f"   • 文件大小: {os.path.getsize(saved_path)} 字节")
        print(f"   • 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"   ❌ 文件保存失败: {str(e)}")
        return
    
    # 7. 显示结果
    print("\n" + "=" * 70)
    print("🎉 测试完成！完整工作流验证成功")
    print("=" * 70)
    
    print("\n📄 生成的怪物配置文件内容:")
    print("-" * 50)
    with open(saved_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    print("-" * 50)
    
    # 8. 验证文件完整性
    print("\n🔍 文件完整性验证:")
    meta_file = saved_path.replace('.json', '.meta.json')
    if os.path.exists(meta_file):
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            print(f"   • 验证状态: {meta.get('validation_status', 'unknown')}")
            print(f"   • 文件哈希: {meta.get('file_hash', '')[:16]}...")
            print(f"   • Schema版本: {meta.get('schema_version', 'unknown')}")
    
    print("\n" + "=" * 70)
    print("✅ 独立游戏资产与配置自动构建器 - 工作流测试完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
