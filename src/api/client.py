"""
DeepSeek API客户端模块
封装API请求、鉴权、重试逻辑
"""

import os
import time
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_API_MODEL", "deepseek-chat")
        self.max_retries = int(os.getenv("API_MAX_RETRIES", 3))
        self.retry_delay = int(os.getenv("API_RETRY_DELAY", 2))
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY未设置，请在.env文件中配置")
    
    def generate_content(self, prompt: str, system_prompt: str = None, 
                        temperature: float = 0.7, mock_mode: bool = False) -> str:
        """
        调用DeepSeek API生成内容（支持模拟模式）
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 生成温度
            mock_mode: 是否使用模拟模式（用于测试）
            
        Returns:
            API返回的文本内容
        """
        # 模拟模式：返回预定义的测试数据
        if mock_mode:
            print("🔧 使用模拟模式生成测试数据")
            return self._generate_mock_response(prompt, system_prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "IndieGameAssetBuilder/1.0"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 8192,  # 增加token限制以支持复杂的对话树
            "stream": False
        }
        
        # 配置请求参数（处理代理问题）
        session = requests.Session()
        
        # 尝试从环境变量获取代理设置
        http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
        
        proxies = {}
        if http_proxy:
            proxies['http'] = http_proxy
        if https_proxy:
            proxies['https'] = https_proxy
        
        # 重试逻辑
        for attempt in range(self.max_retries):
            try:
                print(f"🌐 尝试连接API (尝试 {attempt + 1}/{self.max_retries})...")
                
                response = session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=120,  # 延长超时时间到120秒，给对话生成留出充足时间
                    proxies=proxies if proxies else None,
                    verify=True  # SSL验证
                )
                
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                print(f"✅ API请求成功，收到 {len(content)} 字符响应")
                return content
                
            except requests.exceptions.SSLError as e:
                print(f"⚠️  SSL错误: {str(e)}")
                if attempt == self.max_retries - 1:
                    print("🔧 切换到模拟模式继续...")
                    return self._generate_mock_response(prompt, system_prompt)
                time.sleep(self.retry_delay)
                
            except requests.exceptions.ProxyError as e:
                print(f"⚠️  代理错误: {str(e)}")
                if attempt == self.max_retries - 1:
                    print("🔧 切换到模拟模式继续...")
                    return self._generate_mock_response(prompt, system_prompt)
                time.sleep(self.retry_delay)
                
            except requests.exceptions.Timeout as e:
                print(f"⏳ DeepSeek正在全力思考复杂的对话分支，耗时较长，请耐心等待...")
                if attempt == self.max_retries - 1:
                    print("🔧 所有重试失败，切换到模拟模式...")
                    return self._generate_mock_response(prompt, system_prompt)
                
                print(f"⏳ {self.retry_delay}秒后重试...")
                time.sleep(self.retry_delay)
                
            except requests.exceptions.RequestException as e:
                error_msg = str(e)
                print(f"⚠️  请求错误: {error_msg}")
                
                if attempt == self.max_retries - 1:
                    print("🔧 所有重试失败，切换到模拟模式...")
                    return self._generate_mock_response(prompt, system_prompt)
                
                print(f"⏳ {self.retry_delay}秒后重试...")
                time.sleep(self.retry_delay)
        
        # 如果所有重试都失败，返回模拟数据
        return self._generate_mock_response(prompt, system_prompt)
    
    def extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        从API响应中提取JSON数据
        
        Args:
            response: API返回的文本
            
        Returns:
            解析后的JSON字典
        """
        import re
        
        # 调试：打印原始响应前500字符
        print(f"🔍 原始API响应 ({len(response)} 字符):")
        print(f"   {response[:500]}..." if len(response) > 500 else f"   {response}")
        
        # 尝试查找JSON代码块
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            print(f"🔍 从代码块中提取JSON ({len(json_str)} 字符)")
        else:
            # 如果没有代码块，尝试直接解析整个响应
            json_str = response
            print(f"🔍 直接解析响应文本 ({len(json_str)} 字符)")
        
        # 清理JSON字符串
        json_str = json_str.strip()
        
        # 移除可能的Markdown标记
        json_str = re.sub(r'^```json\s*', '', json_str)
        json_str = re.sub(r'\s*```$', '', json_str)
        
        # 调试：打印清理后的JSON字符串
        print(f"🔍 清理后的JSON字符串 ({len(json_str)} 字符):")
        print(f"   {json_str[:300]}..." if len(json_str) > 300 else f"   {json_str}")
        
        try:
            data = json.loads(json_str)
            print(f"✅ JSON解析成功，包含 {len(data)} 个字段")
            print(f"🔍 解析后的字段: {list(data.keys())}")
            return data
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {str(e)}")
            print(f"📄 原始文本前200字符: {json_str[:200]}...")
            
            # 尝试修复常见的JSON问题
            try:
                # 尝试修复单引号问题
                json_str_fixed = json_str.replace("'", '"')
                data = json.loads(json_str_fixed)
                print("✅ 通过修复单引号成功解析JSON")
                return data
            except:
                pass
            
            # 尝试修复未闭合的字符串
            try:
                json_str_fixed = self._fix_unterminated_strings(json_str)
                data = json.loads(json_str_fixed)
                print("✅ 通过修复未闭合字符串成功解析JSON")
                return data
            except:
                pass
            
            # 尝试修复常见的JSON格式问题
            try:
                json_str_fixed = self._fix_common_json_issues(json_str)
                data = json.loads(json_str_fixed)
                print("✅ 通过修复常见JSON问题成功解析JSON")
                return data
            except:
                pass
            
            # 如果无法修复，抛出详细错误
            raise ValueError(f"无法从响应中提取有效的JSON。错误位置: 第{e.lineno}行第{e.colno}列。内容: {json_str[max(0, e.pos-50):e.pos+50]}")
    
    def _fix_unterminated_strings(self, json_str: str) -> str:
        """修复未闭合的字符串"""
        import re
        
        # 查找未闭合的双引号字符串
        # 匹配模式：双引号开始，但没有对应的结束双引号
        lines = json_str.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # 统计双引号数量
            quote_count = line.count('"')
            
            # 如果双引号数量是奇数，可能有问题
            if quote_count % 2 == 1:
                # 检查是否在字符串值中
                if ': "' in line or '= "' in line or '["' in line or '{' in line:
                    # 在行末添加闭合双引号
                    line = line.rstrip() + '"'
                    print(f"🔧 修复第{i+1}行未闭合字符串")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_common_json_issues(self, json_str: str) -> str:
        """修复常见的JSON格式问题"""
        import re
        
        # 1. 修复未转义的控制字符
        json_str = re.sub(r'[\x00-\x1f\x7f]', ' ', json_str)
        
        # 2. 修复未闭合的数组或对象
        # 统计大括号和中括号
        brace_count = json_str.count('{') - json_str.count('}')
        bracket_count = json_str.count('[') - json_str.count(']')
        
        # 添加缺失的闭合符号
        if brace_count > 0:
            json_str += '}' * brace_count
            print(f"🔧 添加{brace_count}个缺失的闭合大括号")
        
        if bracket_count > 0:
            json_str += ']' * bracket_count
            print(f"🔧 添加{bracket_count}个缺失的闭合中括号")
        
        # 3. 修复末尾的逗号
        json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
        
        # 4. 修复True/False/null（Python风格）
        json_str = re.sub(r':\s*True\b', ': true', json_str)
        json_str = re.sub(r':\s*False\b', ': false', json_str)
        json_str = re.sub(r':\s*None\b', ': null', json_str)
        
        return json_str
    
    def _generate_mock_response(self, prompt: str, system_prompt: str = None) -> str:
        """
        生成模拟响应（用于测试或网络故障时）
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            
        Returns:
            模拟的API响应
        """
        # 判断生成类型
        if "weapon" in prompt.lower() or "剑" in prompt or "霜之哀伤" in prompt:
            print("🎭 生成模拟数据（传说级武器：霜之哀伤）...")
            return self._generate_mock_weapon_response()
        elif "troll" in prompt.lower() or "巨魔" in prompt:
            print("🎭 生成模拟数据（冰属性雪山巨魔）...")
            mock_data = {
                "name": "雪山巨魔",
                "type": "troll",
                "element": "ice",
                "level": 15,
                "health": 1800,
                "attack": 120,
                "defense": 90,
                "magic_attack": 150,
                "magic_defense": 110,
                "speed": 45,
                "skills": 3,
                "skill_list": [
                    {
                        "name": "寒冰重击",
                        "type": "physical",
                        "element": "ice",
                        "power": 85,
                        "cost": 20,
                        "description": "用覆盖寒冰的巨拳猛击敌人，有概率造成冰冻效果",
                        "effect": "freeze_chance",
                        "duration": 2,
                        "target": "single"
                    },
                    {
                        "name": "暴风雪领域",
                        "type": "magic",
                        "element": "ice",
                        "power": 60,
                        "cost": 35,
                        "description": "召唤暴风雪覆盖战场，对所有敌人造成持续冰属性伤害",
                        "effect": "aoe_damage",
                        "duration": 3,
                        "target": "all"
                    },
                    {
                        "name": "冰甲护体",
                        "type": "buff",
                        "element": "ice",
                        "power": 0,
                        "cost": 25,
                        "description": "用寒冰覆盖身体，大幅提升防御力和冰属性抗性",
                        "effect": "defense_up",
                        "duration": 4,
                        "target": "self"
                    }
                ],
                "weaknesses": ["fire", "lightning"],
                "resistances": ["water"],  # 移除ice，因为怪物不能抵抗自己的元素
                "drops": [
                    {
                        "item": "巨魔獠牙",
                        "chance": 0.8,
                        "quantity": "2-4"
                    },
                    {
                        "item": "寒冰核心",
                        "chance": 0.4,
                        "quantity": "1"
                    },
                    {
                        "item": "雪山毛皮",
                        "chance": 0.6,
                        "quantity": "1-2"
                    }
                ],
                "experience": 850,
                "gold": 320,
                "description": "生活在极寒雪山深处的古老巨魔变种，皮肤如冰岩般坚硬，能够操控暴风雪的力量。性格孤僻但领地意识极强，会攻击任何闯入其领域的生物。",
                "ai_behavior": "defensive",
                "spawn_areas": ["frozen_peak", "ice_cave", "snowy_mountains"],
                "rarity": "rare"
            }
        elif "对话" in prompt or "dialogue" in prompt.lower() or "npc" in prompt.lower():
            print("🎭 生成对话模拟数据...")
            return self._generate_mock_dialogue_response()
        else:
            print("🎭 生成通用模拟数据...")
            # 通用模拟数据
            mock_data = {
                "name": "测试怪物",
                "type": "generic",
                "element": "none",
                "level": 10,
                "health": 1000,
                "attack": 80,
                "defense": 60,
                "magic_attack": 100,
                "magic_defense": 70,
                "speed": 50,
                "skills": 2,
                "skill_list": [
                    {
                        "name": "普通攻击",
                        "type": "physical",
                        "element": "none",
                        "power": 50,
                        "cost": 0,
                        "description": "基本的物理攻击",
                        "target": "single"
                    },
                    {
                        "name": "防御姿态",
                        "type": "buff",
                        "element": "none",
                        "power": 0,
                        "cost": 15,
                        "description": "提升自身防御力",
                        "effect": "defense_up",
                        "duration": 3,
                        "target": "self"
                    }
                ],
                "weaknesses": [],
                "resistances": [],
                "drops": [
                    {
                        "item": "怪物素材",
                        "chance": 0.5,
                        "quantity": "1-2"
                    }
                ],
                "experience": 500,
                "gold": 150,
                "description": "一个用于测试的普通怪物",
                "ai_behavior": "aggressive",
                "spawn_areas": ["test_area"],
                "rarity": "common"
            }
        
        # 将模拟数据包装成API响应格式
        mock_response = f"""```json
{json.dumps(mock_data, ensure_ascii=False, indent=2)}
```"""
        
        print(f"✅ 模拟数据生成完成 ({len(mock_response)} 字符)")
        return mock_response
    
    def _generate_mock_dialogue_response(self) -> str:
        """生成对话模拟数据"""
        mock_data = {
            "dialogue_id": "blacksmith_dialogue_001",
            "npc_name": "暴躁的矮人铁匠",
            "npc_description": "一个脾气暴躁但手艺精湛的矮人铁匠，脸上总是挂着不满的表情，但如果你能赢得他的信任，他会为你打造最好的武器。",
            "npc_role": "铁匠",
            "nodes": [
                {
                    "node_id": "start_1",
                    "node_type": "start",
                    "npc_text": "哼！又是谁打扰我工作？想要什么快说，我的时间很宝贵！",
                    "npc_name": "暴躁的矮人铁匠",
                    "emotion": "angry",
                    "player_options": [
                        {
                            "text": "我想看看你这里有什么武器",
                            "next_node_id": "weapons_1",
                            "effects": [{"type": "reputation", "value": 5}]
                        },
                        {
                            "text": "听说你是这里最好的铁匠，我想请你打造一件武器",
                            "next_node_id": "craft_1",
                            "conditions": [{"type": "reputation", "target": "blacksmith", "value": 20, "operator": ">="}]
                        },
                        {
                            "text": "没什么，只是路过打个招呼",
                            "next_node_id": "end_1"
                        }
                    ],
                    "is_branching": True,
                    "priority": 1
                },
                {
                    "node_id": "weapons_1",
                    "node_type": "npc_speech",
                    "npc_text": "哼！算你识货。我这里确实有几件不错的作品，但价格可不便宜！",
                    "npc_name": "暴躁的矮人铁匠",
                    "emotion": "neutral",
                    "player_options": [
                        {
                            "text": "让我看看你的商品",
                            "next_node_id": "shop_1"
                        },
                        {
                            "text": "太贵了，我还是走吧",
                            "next_node_id": "end_1"
                        }
                    ],
                    "priority": 2
                },
                {
                    "node_id": "craft_1",
                    "node_type": "npc_speech",
                    "npc_text": "哦？看来你听说过我的名声。好吧，说说你想要什么样的武器。",
                    "npc_name": "暴躁的矮人铁匠",
                    "emotion": "interested",
                    "player_options": [
                        {
                            "text": "我想要一把锋利的单手剑",
                            "next_node_id": "craft_details"
                        },
                        {
                            "text": "我需要一把坚固的盾牌",
                            "next_node_id": "craft_details"
                        },
                        {
                            "text": "我还没想好，下次再说",
                            "next_node_id": "end_1"
                        }
                    ],
                    "priority": 2
                },
                {
                    "node_id": "craft_details",
                    "node_type": "npc_speech",
                    "npc_text": "好的，我需要一些时间来打造。三天后来取，准备好金币！",
                    "npc_name": "暴躁的矮人铁匠",
                    "emotion": "businesslike",
                    "player_options": [
                        {
                            "text": "好的，我会准时来取",
                            "next_node_id": "end_1"
                        },
                        {
                            "text": "太久了，我等不了",
                            "next_node_id": "end_1"
                        }
                    ],
                    "priority": 3
                },
                {
                    "node_id": "shop_1",
                    "node_type": "player_choice",
                    "npc_text": "选好了吗？别浪费我的时间！",
                    "npc_name": "暴躁的矮人铁匠",
                    "emotion": "impatient",
                    "player_options": [
                        {
                            "text": "我要这把铁剑（50金币）",
                            "next_node_id": "purchase_complete",
                            "effects": [{"type": "transaction", "item": "iron_sword", "price": 50}]
                        },
                        {
                            "text": "这把钢盾看起来不错（80金币）",
                            "next_node_id": "purchase_complete",
                            "effects": [{"type": "transaction", "item": "steel_shield", "price": 80}]
                        },
                        {
                            "text": "太贵了，我买不起",
                            "next_node_id": "end_1"
                        }
                    ],
                    "priority": 3
                },
                {
                    "node_id": "purchase_complete",
                    "node_type": "npc_speech",
                    "npc_text": "成交！这是你的物品，好好使用它！",
                    "npc_name": "暴躁的矮人铁匠",
                    "emotion": "satisfied",
                    "player_options": [
                        {
                            "text": "谢谢！",
                            "next_node_id": "end_1"
                        }
                    ],
                    "priority": 4
                },
                {
                    "node_id": "end_1",
                    "node_type": "end",
                    "npc_text": "哼！下次想好了再来！",
                    "npc_name": "暴躁的矮人铁匠",
                    "emotion": "dismissive",
                    "priority": 10
                }
            ],
            "start_node_id": "start_1",
            "is_quest_related": False,
            "repeatable": True,
            "version": "1.0.0",
            "author": "系统生成"
        }
        
        # 将模拟数据包装成API响应格式
        mock_response = f"""```json
{json.dumps(mock_data, ensure_ascii=False, indent=2)}
```"""
        
        print(f"✅ 对话模拟数据生成完成 ({len(mock_response)} 字符)")
        return mock_response
    
    def _generate_mock_weapon_response(self) -> str:
        """生成传说级武器模拟数据"""
        mock_data = {
            "name": "霜之哀伤",
            "type": "weapon",
            "rarity": "legendary",
            "weapon_type": "greatsword",
            "level_requirement": 60,
            "durability": 1000,
            "weight": 25.5,
            "value": 50000,
            "stat_bonuses": [
                {
                    "stat": "strength",
                    "value": 50,
                    "is_percentage": False
                },
                {
                    "stat": "attack",
                    "value": 200,
                    "is_percentage": False
                },
                {
                    "stat": "critical_chance",
                    "value": 15,
                    "is_percentage": True
                },
                {
                    "stat": "critical_damage",
                    "value": 50,
                    "is_percentage": True
                }
            ],
            "special_effects": [
                {
                    "name": "霜冻之触",
                    "description": "攻击有30%概率冻结敌人2回合，冻结期间敌人无法行动且受到额外冰属性伤害",
                    "trigger_condition": "on_hit",
                    "cooldown": 0
                },
                {
                    "name": "灵魂收割",
                    "description": "击败敌人时恢复10%最大生命值，并永久增加1点攻击力（最多100层）",
                    "trigger_condition": "on_kill",
                    "cooldown": 0
                },
                {
                    "name": "亡者军团",
                    "description": "主动技能：召唤3个被击败敌人的灵魂为你战斗，持续5回合（冷却10回合）",
                    "trigger_condition": "active",
                    "cooldown": 10
                }
            ],
            "description": "传说中的诅咒之剑，由巫妖王亲手锻造。剑身散发着刺骨的寒气，剑刃上凝结着永不融化的冰霜。据说此剑会吞噬持有者的灵魂，但同时也赋予其无可匹敌的力量。",
            "lore": "在远古的冰封王座之战中，巫妖王耐奥祖用千年寒冰和无数英雄的灵魂锻造了这把诅咒之剑。剑成之日，天地变色，北境永冬。历代持有者皆成为剑的奴隶，他们的灵魂被囚禁于剑中，化为无尽的怨灵军团。唯有意志最坚定者，方能驾驭其力而不被反噬。",
            "flavor_text": "「霜之哀伤，饥渴难耐。」——剑身上的古老铭文",
            "is_soulbound": True,
            "is_tradable": False,
            "is_droppable": False,
            "stack_size": 1,
            "visual_prompt": "masterpiece, best quality, ultra detailed, 8k, fantasy weapon, legendary greatsword, frostmourne, icy blue blade, intricate runes engraved on the blade, glowing blue aura, frozen mist surrounding the sword, sharp crystalline edges, dark metal hilt wrapped in ancient leather, skull-shaped pommel with glowing blue eyes, ice spikes along the blade, ethereal souls trapped within the ice, dramatic lighting, dark fantasy atmosphere, cinematic composition, trending on artstation"
        }
        
        # 将模拟数据包装成API响应格式
        mock_response = f"""```json
{json.dumps(mock_data, ensure_ascii=False, indent=2)}
```"""
        
        print(f"✅ 武器模拟数据生成完成 ({len(mock_response)} 字符)")
        return mock_response
