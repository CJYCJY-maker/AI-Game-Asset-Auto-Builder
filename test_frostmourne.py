#!/usr/bin/env python3
"""
测试脚本：生成传说级武器霜之哀伤（强制使用模拟模式）
用于展示完整的物品生成工作流
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
from src.validation.item_validator import validate_item_data
from src.fileio.handler import FileHandler
from datetime import datetime

def main():
    print("=" * 70)
    print("🧪 独立游戏资产与配置自动构建器 - 物品生成工作流测试")
    print("=" * 70)
    
    # 1. 初始化组件
    print("\n1. 🔧 初始化系统组件...")
    api_client = DeepSeekClient()
    
    # 2. 组装Prompt
    print("\n2. 📝 组装Prompt模板...")
    prompts = prompt_manager.assemble_full_prompt(
        prompt_type="item_generator",
        item_type="weapon",
        item_name="霜之哀伤",
        rarity="legendary",
        special_request="双手剑，冰属性，传说级武器"
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
        item_dict = api_client.extract_json_from_response(response)
        print(f"   ✅ JSON提取成功: {len(item_dict)} 个字段")
    except Exception as e:
        print(f"   ❌ JSON提取失败: {str(e)}")
        return
    
    # 5. 验证数据
    print("\n5. ⚙️ 使用Pydantic Schema验证数据...")
    try:
        item_data = validate_item_data(item_dict)
        print(f"   ✅ 数据验证通过！")
        print(f"   • 物品名称: {item_data.name}")
        print(f"   • 物品类型: {item_data.type}")
        print(f"   • 稀有度: {item_data.rarity}")
        print(f"   • 等级要求: {item_data.level_requirement}")
        print(f"   • 武器类型: {item_data.weapon_type}")
        print(f"   • 特殊效果: {len(item_data.special_effects)} 个")
    except Exception as e:
        print(f"   ❌ 数据验证失败: {str(e)}")
        print("\n   🔧 尝试修复数据...")
        
        # 尝试修复常见问题
        if "special_effects" in item_dict and isinstance(item_dict["special_effects"], list):
            print("   • 检查special_effects格式...")
            # 如果special_effects是字符串列表，尝试转换为对象
            if item_dict["special_effects"] and isinstance(item_dict["special_effects"][0], str):
                print("   • 修复: 将字符串格式的特殊效果转换为对象格式")
                # 这里简化处理，实际应该解析字符串
                item_dict["special_effects"] = [
                    {
                        "name": f"效果{i+1}",
                        "description": effect,
                        "trigger_condition": "on_hit",
                        "cooldown": 0
                    }
                    for i, effect in enumerate(item_dict["special_effects"])
                ]
        
        # 检查visual_prompt长度
        if "visual_prompt" in item_dict and len(item_dict["visual_prompt"]) > 500:
            print(f"   • 修复: 截断visual_prompt (原长度: {len(item_dict['visual_prompt'])})")
            item_dict["visual_prompt"] = item_dict["visual_prompt"][:497] + "..."
        
        # 重新验证
        try:
            item_data = validate_item_data(item_dict)
            print(f"   ✅ 修复后验证通过！")
        except Exception as e2:
            print(f"   ❌ 修复后仍然失败: {str(e2)}")
            return
    
    # 6. 保存文件
    print("\n6. 💾 保存物品数据到文件...")
    try:
        file_handler = FileHandler()
        saved_path = file_handler.save_data(item_data, data_type="item", subdirectory="items")
        print(f"   ✅ 文件保存成功: {saved_path}")
        print(f"   • 文件大小: {os.path.getsize(saved_path)} 字节")
        print(f"   • 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"   ❌ 文件保存失败: {str(e)}")
        return
    
    # 7. 显示结果
    print("\n" + "=" * 70)
    print("🎉 测试完成！物品生成工作流验证成功")
    print("=" * 70)
    
    print("\n📄 生成的物品配置文件内容:")
    print("-" * 50)
    with open(saved_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    print("-" * 50)
    
    # 8. 提取visual_prompt
    print("\n🎨 AI绘画提示词提取:")
    visual_prompt = data.get('visual_prompt', '')
    if visual_prompt:
        prompt_filename = Path(saved_path).stem + '.txt'
        prompt_path = Path("output/prompts") / prompt_filename
        prompt_path.parent.mkdir(exist_ok=True)
        
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(visual_prompt)
        
        print(f"   ✅ 提示词已保存: {prompt_path}")
        print(f"   📝 提示词长度: {len(visual_prompt)} 字符")
        print(f"   🔤 语言: {'英文' if all(ord(c) < 128 for c in visual_prompt) else '混合'}")
        
        # 显示提示词预览
        print("\n   📋 提示词预览:")
        print("   " + "-" * 46)
        lines = visual_prompt.split(', ')
        for i in range(min(5, len(lines))):
            print(f"   • {lines[i]}")
        if len(lines) > 5:
            print(f"   • ... 等{len(lines)-5}个标签")
    
    # 9. 验证文件完整性
    print("\n🔍 文件完整性验证:")
    meta_file = saved_path.replace('.json', '.meta.json')
    if os.path.exists(meta_file):
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            print(f"   • 验证状态: {meta.get('validation_status', 'unknown')}")
            print(f"   • 文件哈希: {meta.get('file_hash', '')[:16]}...")
            print(f"   • Schema版本: {meta.get('schema_version', 'unknown')}")
    
    print("\n" + "=" * 70)
    print("✅ 独立游戏资产与配置自动构建器 - 物品生成测试完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
