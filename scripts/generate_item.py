#!/usr/bin/env python3
"""
独立游戏资产与配置自动构建器 - 物品生成脚本
集成DeepSeek API调用、Pydantic校验和容错重试逻辑

通过Cline调用示例：
python generate_item.py --type weapon --name "霜之哀伤" --rarity legendary --weapon-type greatsword
"""

import os
import sys
import json
import argparse
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.client import DeepSeekClient
from src.prompts.manager import prompt_manager
from src.validation.item_validator import validate_item_data, ItemSchema
from src.fileio.handler import FileHandler


def generate_item_with_retry(
    item_type: str,
    item_name: Optional[str] = None,
    rarity: Optional[str] = None,
    weapon_type: Optional[str] = None,
    armor_slot: Optional[str] = None,
    level_requirement: int = 1,
    special_request: Optional[str] = None,
    max_retries: int = 3
) -> ItemSchema:
    """
    生成物品数据（带重试机制）
    
    Args:
        item_type: 物品类型
        item_name: 物品名称
        rarity: 物品稀有度
        weapon_type: 武器类型
        armor_slot: 防具部位
        level_requirement: 使用等级要求
        special_request: 特殊要求
        max_retries: 最大重试次数
        
    Returns:
        验证通过的物品数据
        
    Raises:
        Exception: 所有重试都失败
    """
    print(f"🔧 开始生成物品: {item_name or item_type} (类型: {item_type}, 稀有度: {rarity or '默认'})")
    
    # 初始化API客户端
    api_client = DeepSeekClient()
    
    # 组装Prompt
    prompts = prompt_manager.assemble_full_prompt(
        prompt_type="item_generator",
        item_type=item_type,
        item_name=item_name,
        rarity=rarity,
        special_request=special_request
    )
    
    print(f"📝 系统提示词已组装 ({len(prompts['system'])} 字符)")
    print(f"💬 用户指令: {prompts['user']}")
    
    # 重试逻辑
    for attempt in range(1, max_retries + 1):
        print(f"\n🔄 尝试第 {attempt}/{max_retries} 次生成...")
        
        try:
            # 调用API
            print("🌐 调用DeepSeek API...")
            response = api_client.generate_content(
                prompt=prompts['user'],
                system_prompt=prompts['system'],
                temperature=0.7
            )
            
            print(f"✅ API响应接收成功 ({len(response)} 字符)")
            
            # 提取JSON
            print("🔍 从响应中提取JSON数据...")
            item_dict = api_client.extract_json_from_response(response)
            
            print(f"📊 提取到JSON数据，包含 {len(item_dict)} 个字段")
            
            # 验证数据
            print("⚙️ 使用Pydantic Schema验证数据...")
            item_data = validate_item_data(item_dict)
            
            print(f"🎉 数据验证通过！物品 '{item_data.name}' 创建成功")
            print(f"   • 类型: {item_data.type}")
            print(f"   • 稀有度: {item_data.rarity}")
            print(f"   • 等级要求: {item_data.level_requirement}")
            print(f"   • 价值: {item_data.value} 金币")
            print(f"   • 属性加成: {len(item_data.stat_bonuses)} 个")
            
            return item_data
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 第 {attempt} 次尝试失败: {error_msg}")
            
            if attempt < max_retries:
                print(f"⏳ 等待2秒后重试...")
                import time
                time.sleep(2)
            else:
                print(f"💥 所有 {max_retries} 次尝试均失败")
                raise Exception(f"生成物品数据失败，已重试{max_retries}次。最后错误: {error_msg}")
    
    # 理论上不会执行到这里
    raise Exception("生成过程异常")


def main():
    """主函数：生成物品配置"""
    parser = argparse.ArgumentParser(
        description="独立游戏资产与配置自动构建器 - 物品生成脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --type weapon --name "霜之哀伤" --rarity legendary --weapon-type greatsword
  %(prog)s --type armor --rarity epic --armor-slot chest --level 30
  %(prog)s --type accessory --rarity rare --name "火焰护符"
        """
    )
    
    parser.add_argument("--type", type=str, required=True, 
                       choices=["weapon", "armor", "accessory", "consumable", "material", "quest"],
                       help="物品类型")
    parser.add_argument("--name", type=str, help="物品名称")
    parser.add_argument("--rarity", type=str, 
                       choices=["common", "uncommon", "rare", "epic", "legendary", "mythic"],
                       help="物品稀有度")
    parser.add_argument("--weapon-type", type=str,
                       choices=["sword", "greatsword", "dagger", "staff", "wand", "bow", 
                               "crossbow", "axe", "mace", "spear", "shield"],
                       help="武器类型（仅武器有效）")
    parser.add_argument("--armor-slot", type=str,
                       choices=["head", "chest", "hands", "legs", "feet", "neck", "ring", "back"],
                       help="防具部位（仅防具有效）")
    parser.add_argument("--level", type=int, default=1, help="使用等级要求 (默认: 1)")
    parser.add_argument("--special-request", type=str, help="特殊要求描述")
    parser.add_argument("--output-dir", type=str, help="输出目录 (默认: ./output/assets/items)")
    parser.add_argument("--max-retries", type=int, default=3, help="最大重试次数 (默认: 3)")
    parser.add_argument("--force", action="store_true", help="强制覆盖已存在的文件")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎮 独立游戏资产与配置自动构建器 - 物品生成器")
    print("=" * 70)
    
    # 初始化文件处理器
    file_handler = FileHandler()
    
    # 检查是否已存在相同文件
    item_name = args.name or f"{args.type}_item"
    existing_file = None
    
    # 简化检查：只检查名称
    output_dir = Path("output/assets/items")
    if output_dir.exists():
        for file in output_dir.glob("*.json"):
            if not file.name.endswith('.meta.json'):
                with open(file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if data.get('name') == item_name:
                            existing_file = str(file)
                            break
                    except:
                        continue
    
    if existing_file and not args.force:
        print(f"⚠️  发现已存在的文件: {existing_file}")
        print("   使用 --force 参数强制覆盖，或调整物品名称")
        return
    
    if existing_file and args.force:
        backup_path = file_handler.backup_existing_file(existing_file)
        print(f"📦 已备份原文件到: {backup_path}")
    
    try:
        # 生成物品数据（带重试机制）
        item_data = generate_item_with_retry(
            item_type=args.type,
            item_name=args.name,
            rarity=args.rarity,
            weapon_type=args.weapon_type,
            armor_slot=args.armor_slot,
            level_requirement=args.level,
            special_request=args.special_request,
            max_retries=args.max_retries
        )
        
        # 保存文件
        print("\n💾 保存物品数据到文件...")
        saved_path = file_handler.save_monster_data(item_data, subdirectory="items")
        
        print("=" * 70)
        print(f"✅ 生成完成！")
        print(f"📁 文件位置: {saved_path}")
        print(f"📊 文件大小: {os.path.getsize(saved_path)} 字节")
        print(f"🕒 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # 显示生成的JSON（前几行）
        print("\n📄 生成的JSON数据预览:")
        print("-" * 50)
        with open(saved_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            preview = json.dumps(data, ensure_ascii=False, indent=2)
            lines = preview.split('\n')
            for i in range(min(20, len(lines))):
                print(lines[i])
            if len(lines) > 20:
                print("... (完整内容请查看文件)")
        print("-" * 50)
        
        # 提取visual_prompt并保存为单独文件
        print("\n🎨 提取AI绘画提示词...")
        visual_prompt = data.get('visual_prompt', '')
        if visual_prompt:
            prompt_filename = Path(saved_path).stem + '.txt'
            prompt_path = Path("output/prompts") / prompt_filename
            prompt_path.parent.mkdir(exist_ok=True)
            
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(visual_prompt)
            
            print(f"✅ 提示词已保存: {prompt_path}")
            print(f"📝 提示词长度: {len(visual_prompt)} 字符")
            print(f"🔤 语言: {'英文' if all(ord(c) < 128 for c in visual_prompt) else '混合'}")
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("💥 生成过程失败")
        print("=" * 70)
        print(f"错误信息: {str(e)}")
        print("\n详细错误:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
