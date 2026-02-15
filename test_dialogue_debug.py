#!/usr/bin/env python3
"""
调试对话验证器问题
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入相关模块
from src.validation.dialogue_validator import DialogueOption

def test_dialogue_option():
    """测试DialogueOption模型"""
    print("🔍 测试DialogueOption模型...")
    
    # 测试1: 只有option_text字段
    print("\n测试1: 只有option_text字段")
    try:
        data = {
            "option_text": "测试选项",
            "next_node_id": "next_1"
        }
        option = DialogueOption(**data)
        print(f"✅ 成功创建: text='{option.text}', option_text='{option.option_text}'")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试2: 只有text字段
    print("\n测试2: 只有text字段")
    try:
        data = {
            "text": "测试选项",
            "next_node_id": "next_1"
        }
        option = DialogueOption(**data)
        print(f"✅ 成功创建: text='{option.text}', option_text='{option.option_text}'")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试3: 两个字段都有
    print("\n测试3: 两个字段都有")
    try:
        data = {
            "text": "文本",
            "option_text": "选项文本",
            "next_node_id": "next_1"
        }
        option = DialogueOption(**data)
        print(f"✅ 成功创建: text='{option.text}', option_text='{option.option_text}'")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 测试4: 两个字段都没有
    print("\n测试4: 两个字段都没有")
    try:
        data = {
            "next_node_id": "next_1"
        }
        option = DialogueOption(**data)
        print(f"✅ 成功创建: text='{option.text}', option_text='{option.option_text}'")
    except Exception as e:
        print(f"❌ 失败: {e}")

def test_validation_order():
    """测试验证器执行顺序"""
    print("\n🔍 测试验证器执行顺序...")
    
    # 查看DialogueOption的验证器
    from pydantic import BaseModel
    import inspect
    
    print("DialogueOption验证器:")
    for name, method in inspect.getmembers(DialogueOption):
        if hasattr(method, '__validator_config__'):
            config = method.__validator_config__
            print(f"  - {name}: field={config['field_name']}, pre={config['pre']}, always={config['always']}")

if __name__ == "__main__":
    test_dialogue_option()
    test_validation_order()
