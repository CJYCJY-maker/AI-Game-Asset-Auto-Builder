#!/usr/bin/env python3
"""
独立游戏资产与配置自动构建器 - 怪物生成脚本
集成DeepSeek API调用、Pydantic校验和容错重试逻辑

通过Cline调用示例：
python generate_monster.py --type troll --name "雪山巨魔" --level 15 --element ice --skills 3
"""

import os
import sys
import json
import argparse
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.client import DeepSeekClient
from src.prompts.manager import prompt_manager
from src.validation.validator import validate_monster_data, MonsterSchema
from src.fileio.handler import file_handler


def generate_monster_with_retry(
    monster_type: str,
    level: int,
    element: Optional[str] = None,
    monster_name: Optional[str] = None,
    skills: int = 2,
    max_retries: int = 3
) -> MonsterSchema:
    """
    生成怪物数据（带重试机制）
    
    Args:
        monster_type: 怪物类型
        level: 等级
        element: 元素属性
        monster_name: 怪物名称
        skills: 技能数量
        max_retries: 最大重试次数
        
    Returns:
        验证通过的怪物数据
        
    Raises:
        Exception: 所有重试都失败
    """
    print(f"🔧 开始生成怪物: {monster_name or monster_type} (等级{level}, 元素{element or '无'})")
    
    # 初始化API客户端
    api_client = DeepSeekClient()
    
    # 组装Prompt
    prompts = prompt_manager.assemble_full_prompt(
        prompt_type="monster_generator",
        monster_type=monster_type,
        level=level,
        element=element,
        special_request=f"需要{skills}个技能，名称为{monster_name}" if monster_name else f"需要{skills}个技能"
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
            monster_dict = api_client.extract_json_from_response(response)
            
            print(f"📊 提取到JSON数据，包含 {len(monster_dict)} 个字段")
            
            # 验证数据
            print("⚙️ 使用Pydantic Schema验证数据...")
            monster_data = validate_monster_data(monster_dict)
            
            print(f"🎉 数据验证通过！怪物 '{monster_data.name}' 创建成功")
            print(f"   • 类型: {monster_data.type}")
            print(f"   • 元素: {monster_data.element}")
            print(f"   • 等级: {monster_data.level}")
            print(f"   • 生命值: {monster_data.health}")
            print(f"   • 技能数: {monster_data.skills}")
            
            return monster_data
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 第 {attempt} 次尝试失败: {error_msg}")
            
            if attempt < max_retries:
                print(f"⏳ 等待2秒后重试...")
                import time
                time.sleep(2)
            else:
                print(f"💥 所有 {max_retries} 次尝试均失败")
                raise Exception(f"生成怪物数据失败，已重试{max_retries}次。最后错误: {error_msg}")
    
    # 理论上不会执行到这里
    raise Exception("生成过程异常")


def main():
    """主函数：生成怪物配置"""
    parser = argparse.ArgumentParser(
        description="独立游戏资产与配置自动构建器 - 怪物生成脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --type troll --name "雪山巨魔" --level 15 --element ice --skills 3
  %(prog)s --type dragon --level 30 --element fire --skills 4
  %(prog)s --type slime --level 5 --skills 2
        """
    )
    
    parser.add_argument("--type", type=str, required=True, help="怪物类型 (如: troll, dragon, slime)")
    parser.add_argument("--name", type=str, help="怪物名称 (如未提供则使用类型)")
    parser.add_argument("--level", type=int, default=10, help="怪物等级 (默认: 10)")
    parser.add_argument("--element", type=str, choices=[
        "fire", "water", "ice", "earth", "wind", "lightning", "light", "dark", "none"
    ], help="元素属性")
    parser.add_argument("--skills", type=int, default=2, help="技能数量 (默认: 2)")
    parser.add_argument("--output-dir", type=str, help="输出目录 (默认: ./output/assets/monsters)")
    parser.add_argument("--max-retries", type=int, default=3, help="最大重试次数 (默认: 3)")
    parser.add_argument("--force", action="store_true", help="强制覆盖已存在的文件")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎮 独立游戏资产与配置自动构建器 - 怪物生成器")
    print("=" * 60)
    
    # 检查是否已存在相同文件
    monster_name = args.name or args.type
    existing_file = file_handler.check_existing_file(monster_name, args.level)
    
    if existing_file and not args.force:
        print(f"⚠️  发现已存在的文件: {existing_file}")
        print("   使用 --force 参数强制覆盖，或调整怪物名称/等级")
        return
    
    if existing_file and args.force:
        backup_path = file_handler.backup_existing_file(existing_file)
        print(f"📦 已备份原文件到: {backup_path}")
    
    try:
        # 生成怪物数据（带重试机制）
        monster_data = generate_monster_with_retry(
            monster_type=args.type,
            level=args.level,
            element=args.element,
            monster_name=args.name,
            skills=args.skills,
            max_retries=args.max_retries
        )
        
        # 保存文件
        print("\n💾 保存怪物数据到文件...")
        saved_path = file_handler.save_monster_data(monster_data)
        
        print("=" * 60)
        print(f"✅ 生成完成！")
        print(f"📁 文件位置: {saved_path}")
        print(f"📊 文件大小: {os.path.getsize(saved_path)} 字节")
        print(f"🕒 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 显示生成的JSON（前几行）
        print("\n📄 生成的JSON数据预览:")
        print("-" * 40)
        with open(saved_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            preview = json.dumps(data, ensure_ascii=False, indent=2)
            lines = preview.split('\n')
            for i in range(min(15, len(lines))):
                print(lines[i])
            if len(lines) > 15:
                print("... (完整内容请查看文件)")
        print("-" * 40)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("💥 生成过程失败")
        print("=" * 60)
        print(f"错误信息: {str(e)}")
        print("\n详细错误:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
