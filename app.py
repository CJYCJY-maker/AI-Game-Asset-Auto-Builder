#!/usr/bin/env python3
"""
独立游戏资产与配置自动构建器 - 可视化管理中心
使用Gradio框架提供Web界面，复用现有核心逻辑
"""

import os
import sys
import json
import subprocess
import gradio as gr
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入现有核心模块
from src.api.client import DeepSeekClient
from src.prompts.manager import prompt_manager
from src.validation.validator import validate_monster_data
from src.validation.item_validator import validate_item_data
from src.validation.dialogue_validator import validate_dialogue_data
from src.fileio.handler import FileHandler

# 全局变量存储生成结果
current_result = {
    "json_output": "",
    "visual_prompt": "",
    "file_path": "",
    "status": "等待生成..."
}

def generate_monster(monster_type, level, element, special_request, use_mock):
    """生成怪物配置（复用现有逻辑）"""
    try:
        api_client = DeepSeekClient()
        
        # 组装Prompt
        prompts = prompt_manager.assemble_full_prompt(
            prompt_type="monster_generator",
            monster_type=monster_type,
            level=int(level),
            element=element if element else None,
            special_request=special_request if special_request else None
        )
        
        # 调用API
        response = api_client.generate_content(
            prompt=prompts['user'],
            system_prompt=prompts['system'],
            temperature=0.7,
            mock_mode=use_mock
        )
        
        # 提取和验证JSON
        monster_dict = api_client.extract_json_from_response(response)
        monster_data = validate_monster_data(monster_dict)
        
        # 保存文件
        file_handler = FileHandler()
        saved_path = file_handler.save_data(monster_data, "monster", subdirectory="monsters")
        
        # 更新全局结果
        current_result["json_output"] = json.dumps(monster_dict, ensure_ascii=False, indent=2)
        current_result["visual_prompt"] = monster_dict.get('visual_prompt', '无visual_prompt字段')
        current_result["file_path"] = saved_path
        current_result["status"] = f"✅ 怪物生成成功: {monster_data.name} (等级{monster_data.level})"
        
        return current_result["json_output"], current_result["visual_prompt"], current_result["status"]
        
    except Exception as e:
        error_msg = f"❌ 怪物生成失败: {str(e)}"
        current_result["status"] = error_msg
        return "", "", error_msg

def generate_item(item_type, item_name, rarity, weapon_type, armor_slot, level_req, special_request, use_mock):
    """生成物品配置（复用现有逻辑）"""
    try:
        api_client = DeepSeekClient()
        
        # 组装Prompt
        prompts = prompt_manager.assemble_full_prompt(
            prompt_type="item_generator",
            item_type=item_type,
            item_name=item_name if item_name else None,
            rarity=rarity if rarity else None,
            special_request=special_request if special_request else None
        )
        
        # 调用API
        response = api_client.generate_content(
            prompt=prompts['user'],
            system_prompt=prompts['system'],
            temperature=0.7,
            mock_mode=use_mock
        )
        
        # 提取和验证JSON
        item_dict = api_client.extract_json_from_response(response)
        item_data = validate_item_data(item_dict)
        
        # 保存文件
        file_handler = FileHandler()
        saved_path = file_handler.save_data(item_data, "item", subdirectory="items")
        
        # 更新全局结果
        current_result["json_output"] = json.dumps(item_dict, ensure_ascii=False, indent=2)
        current_result["visual_prompt"] = item_dict.get('visual_prompt', '无visual_prompt字段')
        current_result["file_path"] = saved_path
        current_result["status"] = f"✅ 物品生成成功: {item_data.name} ({item_data.rarity})"
        
        return current_result["json_output"], current_result["visual_prompt"], current_result["status"]
        
    except Exception as e:
        error_msg = f"❌ 物品生成失败: {str(e)}"
        current_result["status"] = error_msg
        return "", "", error_msg

def generate_dialogue(npc_name, npc_role, dialogue_theme, special_request, use_mock):
    """生成对话配置（复用现有逻辑）"""
    try:
        api_client = DeepSeekClient()
        
        # 组装Prompt
        prompts = prompt_manager.assemble_full_prompt(
            prompt_type="dialogue_generator",
            npc_name=npc_name if npc_name else None,
            npc_role=npc_role if npc_role else None,
            dialogue_theme=dialogue_theme if dialogue_theme else None,
            special_request=special_request if special_request else None
        )
        
        # 调用API
        response = api_client.generate_content(
            prompt=prompts['user'],
            system_prompt=prompts['system'],
            temperature=0.7,
            mock_mode=use_mock
        )
        
        # 提取和验证JSON
        dialogue_dict = api_client.extract_json_from_response(response)
        dialogue_data = validate_dialogue_data(dialogue_dict)
        
        # 保存文件
        file_handler = FileHandler()
        saved_path = file_handler.save_data(dialogue_data, "dialogue", subdirectory="dialogues")
        
        # 更新全局结果
        current_result["json_output"] = json.dumps(dialogue_dict, ensure_ascii=False, indent=2)
        current_result["visual_prompt"] = "对话数据不包含visual_prompt字段"
        current_result["file_path"] = saved_path
        current_result["status"] = f"✅ 对话生成成功: {dialogue_data.npc_name} ({dialogue_data.npc_role})"
        
        return current_result["json_output"], current_result["visual_prompt"], current_result["status"]
        
    except Exception as e:
        error_msg = f"❌ 对话生成失败: {str(e)}"
        current_result["status"] = error_msg
        return "", "", error_msg

def copy_to_clipboard():
    """复制JSON到剪贴板"""
    import pyperclip
    try:
        pyperclip.copy(current_result["json_output"])
        return "✅ 已复制到剪贴板！"
    except:
        # 如果pyperclip不可用，提供备用方案
        return "📋 请手动复制上方JSON内容"

def open_output_folder():
    """打开output文件夹"""
    output_path = Path("output").absolute()
    if os.name == 'nt':  # Windows
        os.startfile(output_path)
    elif os.name == 'posix':  # macOS/Linux
        subprocess.run(['open', str(output_path)] if sys.platform == 'darwin' else ['xdg-open', str(output_path)])
    return f"📁 已打开输出文件夹: {output_path}"

def extract_visual_prompt():
    """提取visual_prompt到单独文件"""
    if not current_result["visual_prompt"] or current_result["visual_prompt"] == "无visual_prompt字段":
        return "⚠️  当前数据不包含visual_prompt字段"
    
    try:
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_filename = f"visual_prompt_{timestamp}.txt"
        prompt_path = Path("output/prompts") / prompt_filename
        prompt_path.parent.mkdir(exist_ok=True)
        
        # 保存提示词
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(current_result["visual_prompt"])
        
        return f"🎨 AI绘画提示词已保存: {prompt_path}"
    except Exception as e:
        return f"❌ 保存失败: {str(e)}"

# 创建Gradio界面
with gr.Blocks(title="独立游戏资产与配置自动构建器 - 可视化管理中心") as demo:
    gr.Markdown("# 🎮 独立游戏资产与配置自动构建器 - 可视化管理中心")
    gr.Markdown("### 基于Gradio的三层架构可视化界面，复用现有核心逻辑")
    
    with gr.Tabs():
        # 怪物生成标签页
        with gr.TabItem("🧟 怪物生成"):
            with gr.Row():
                with gr.Column(scale=1):
                    monster_type = gr.Dropdown(
                        choices=["goblin", "troll", "dragon", "skeleton", "orc", "slime", "beast"],
                        label="怪物类型",
                        value="goblin"
                    )
                    monster_level = gr.Slider(
                        minimum=1, maximum=100, value=10, step=1,
                        label="怪物等级"
                    )
                    monster_element = gr.Dropdown(
                        choices=["fire", "ice", "lightning", "earth", "water", "wind", "none"],
                        label="元素属性",
                        value="none"
                    )
                    monster_special = gr.Textbox(
                        label="特殊要求",
                        placeholder="例如：需要3个技能，带有冰冻效果"
                    )
                    monster_mock = gr.Checkbox(
                        label="使用模拟模式（API失败时自动启用）",
                        value=True
                    )
                    monster_btn = gr.Button("生成怪物配置", variant="primary")
                    
                with gr.Column(scale=2):
                    monster_status = gr.Textbox(
                        label="生成状态",
                        value="等待生成...",
                        interactive=False
                    )
                    monster_json = gr.Code(
                        label="生成的JSON配置",
                        language="json",
                        value="",
                        lines=20
                    )
        
        # 物品生成标签页
        with gr.TabItem("⚔️ 物品生成"):
            with gr.Row():
                with gr.Column(scale=1):
                    item_type = gr.Dropdown(
                        choices=["weapon", "armor", "accessory", "consumable", "material", "quest"],
                        label="物品类型",
                        value="weapon"
                    )
                    item_name = gr.Textbox(
                        label="物品名称",
                        placeholder="例如：霜之哀伤"
                    )
                    item_rarity = gr.Dropdown(
                        choices=["common", "uncommon", "rare", "epic", "legendary", "mythic"],
                        label="物品稀有度",
                        value="rare"
                    )
                    weapon_type = gr.Dropdown(
                        choices=["sword", "greatsword", "dagger", "staff", "wand", "bow", "crossbow", "axe", "mace", "spear", "shield"],
                        label="武器类型（仅武器有效）",
                        value="sword"
                    )
                    armor_slot = gr.Dropdown(
                        choices=["head", "chest", "hands", "legs", "feet", "neck", "ring", "back"],
                        label="防具部位（仅防具有效）",
                        value="chest"
                    )
                    item_level = gr.Slider(
                        minimum=1, maximum=100, value=10, step=1,
                        label="使用等级要求"
                    )
                    item_special = gr.Textbox(
                        label="特殊要求",
                        placeholder="例如：双手剑，冰属性，传说级武器"
                    )
                    item_mock = gr.Checkbox(
                        label="使用模拟模式",
                        value=True
                    )
                    item_btn = gr.Button("生成物品配置", variant="primary")
                    
                with gr.Column(scale=2):
                    item_status = gr.Textbox(
                        label="生成状态",
                        value="等待生成...",
                        interactive=False
                    )
                    item_json = gr.Code(
                        label="生成的JSON配置",
                        language="json",
                        value="",
                        lines=20
                    )
        
        # 对话生成标签页
        with gr.TabItem("💬 对话生成"):
            with gr.Row():
                with gr.Column(scale=1):
                    npc_name = gr.Textbox(
                        label="NPC名称",
                        placeholder="例如：暴躁的矮人铁匠"
                    )
                    npc_role = gr.Dropdown(
                        choices=["铁匠", "商人", "法师", "战士", "村长", "守卫", "旅店老板", "神秘人"],
                        label="NPC角色",
                        value="铁匠"
                    )
                    dialogue_theme = gr.Textbox(
                        label="对话主题",
                        placeholder="例如：买卖武器与闲聊"
                    )
                    dialogue_special = gr.Textbox(
                        label="特殊要求",
                        placeholder="例如：包含买卖对话、武器升级、背景故事分支"
                    )
                    dialogue_mock = gr.Checkbox(
                        label="使用模拟模式",
                        value=True
                    )
                    dialogue_btn = gr.Button("生成对话配置", variant="primary")
                    
                with gr.Column(scale=2):
                    dialogue_status = gr.Textbox(
                        label="生成状态",
                        value="等待生成...",
                        interactive=False
                    )
                    dialogue_json = gr.Code(
                        label="生成的JSON配置",
                        language="json",
                        value="",
                        lines=20
                    )
    
    # 实时监控与工具区域
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 📊 实时监控")
            json_display = gr.Code(
                label="当前JSON源码",
                language="json",
                value="",
                lines=15
            )
            with gr.Row():
                copy_btn = gr.Button("📋 复制到剪贴板")
                extract_btn = gr.Button("🎨 提取AI绘画提示词")
                open_folder_btn = gr.Button("📁 打开输出文件夹")
            
            copy_status = gr.Textbox(
                label="操作状态",
                value="",
                interactive=False
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 🎨 AI绘画提示词预览")
            visual_prompt_display = gr.Code(
                label="Visual Prompt (用于Stable Diffusion)",
                language="markdown",
                value="",
                lines=15
            )
            gr.Markdown("""
            **提示词特征：**
            - ✅ 纯英文，适合Stable Diffusion
            - ✅ 包含艺术风格标签
            - ✅ 详细的外观描述
            - ✅ 材质、颜色、光影效果
            """)
    
    # 绑定事件
    monster_btn.click(
        generate_monster,
        inputs=[monster_type, monster_level, monster_element, monster_special, monster_mock],
        outputs=[monster_json, visual_prompt_display, monster_status]
    ).then(
        lambda x: x,  # 更新JSON显示
        inputs=[monster_json],
        outputs=[json_display]
    )
    
    item_btn.click(
        generate_item,
        inputs=[item_type, item_name, item_rarity, weapon_type, armor_slot, item_level, item_special, item_mock],
        outputs=[item_json, visual_prompt_display, item_status]
    ).then(
        lambda x: x,
        inputs=[item_json],
        outputs=[json_display]
    )
    
    dialogue_btn.click(
        generate_dialogue,
        inputs=[npc_name, npc_role, dialogue_theme, dialogue_special, dialogue_mock],
        outputs=[dialogue_json, visual_prompt_display, dialogue_status]
    ).then(
        lambda x: x,
        inputs=[dialogue_json],
        outputs=[json_display]
    )
    
    copy_btn.click(
        copy_to_clipboard,
        outputs=[copy_status]
    )
    
    extract_btn.click(
        extract_visual_prompt,
        outputs=[copy_status]
    )
    
    open_folder_btn.click(
        open_output_folder,
        outputs=[copy_status]
    )
    
    # 初始化说明
    gr.Markdown("""
    ## 🚀 使用说明
    
    1. **选择生成类型**：在顶部标签页切换怪物、物品或对话生成
    2. **填写参数**：根据需求填写相应的生成参数
    3. **点击生成**：系统将调用现有核心逻辑生成配置
    4. **实时监控**：右侧区域实时显示生成的JSON源码和AI绘画提示词
    5. **工具操作**：使用下方按钮进行复制、提取或打开文件夹操作
    
    ## 🔧 技术架构
    
    - **前端界面**：Gradio Web框架
    - **核心逻辑**：复用现有的Python脚本（import导入）
    - **数据校验**：Pydantic Schema确保100%格式正确率
    - **容错机制**：API失败时自动降级到模拟模式
    - **文件管理**：自动保存到output目录，生成元数据文件
    
    ## 📁 输出目录结构
    
    ```
    output/
    ├── assets/
    │   ├── monsters/      # 怪物配置
    │   ├── items/         # 物品配置
    │   └── dialogues/     # 对话配置
    ├── prompts/           # AI绘画提示词
    └── *.meta.json        # 元数据文件（完整性校验）
    ```
    """)

if __name__ == "__main__":
    # 创建必要的输出目录
    Path("output/prompts").mkdir(parents=True, exist_ok=True)
    
    # 启动Gradio应用
    print("🚀 启动独立游戏资产与配置自动构建器 - 可视化管理中心")
    print("🌐 本地访问地址: http://localhost:7870")
    print("📁 输出目录: output/")
    print("🔄 按Ctrl+C停止服务")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7870,
        share=False,
        show_error=True
    )
