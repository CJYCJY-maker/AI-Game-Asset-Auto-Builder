# 独立游戏资产与配置自动构建器
## Indie Game Asset & Config Auto-Builder

一个基于LLM与智能代理的本地开发者工具，运行于VS Code工作区内，通过自然语言指令自动化生成游戏项目所需的结构化配置文件（JSON/CSV）及相关素材的提示词文案。

## 🎯 核心特性

- **自然语言交互**：通过Cline扩展接收自然语言指令（如"生成一个带有3种技能的Boss配置文件"）
- **结构化数据生成**：调用DeepSeek API生成严格符合游戏设定的JSON数据
- **自动化文件I/O**：自动创建目录树并写入配置文件，支持增量更新
- **数据容错性**：Pydantic Schema校验，API自动重试机制
- **美术提示词生成**：根据游戏实体属性生成AI绘画标准化Prompt

## 🏗️ 项目结构

```
独立游戏资产与配置自动构建器/
├── src/                    # 源代码目录
│   ├── api/               # API通信模块
│   ├── prompts/           # Prompt模板管理
│   ├── validation/        # 数据校验模块（Pydantic）
│   └── fileio/            # 文件I/O模块
├── scripts/               # 可执行脚本
│   ├── generate_monster.py    # 生成怪物配置
│   ├── generate_item.py       # 生成物品配置
│   └── generate_dialogue.py   # 生成对话树
├── templates/             # 模板文件
│   ├── schemas/          # Pydantic Schema定义
│   └── prompts/          # 系统提示词模板
├── output/               # 生成文件输出目录
│   ├── assets/          # 游戏资产配置
│   │   ├── monsters/    # 怪物配置
│   │   ├── items/       # 物品配置
│   │   └── dialogues/   # 对话配置
│   └── prompts/         # AI绘画提示词
├── config/              # 配置文件
│   └── settings.json    # 项目设置
├── docs/                # 项目文档
│   ├── 项目需求、目标与技术指标.md
│   ├── 软件需求说明书.md
│   └── 概要设计说明书.md
├── .env.example         # 环境变量模板
├── requirements.txt     # Python依赖
└── README.md           # 项目说明
```

## 🚀 快速开始

### 1. 环境配置
```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入您的DeepSeek API密钥
```

### 2. 使用示例
通过Cline执行：
```
# 生成5个史莱姆怪物配置
python scripts/generate_monster.py --count 5 --type slime

# 生成一个Boss配置文件
python scripts/generate_monster.py --name "冰霜巨龙" --level 50 --skills 3
```

### 3. 预期输出
脚本将在`output/assets/monsters/`目录下生成对应的JSON配置文件，格式可直接被Unity、Godot等游戏引擎读取。

## 🔧 技术栈

- **语言**：Python 3.10+
- **数据校验**：Pydantic（确保100%格式正确率）
- **HTTP客户端**：Requests（调用DeepSeek API）
- **配置管理**：python-dotenv
- **命令行界面**：Click
- **终端输出**：Colorama

## 📋 核心工作流

1. **指令接收**：用户通过Cline输入自然语言需求
2. **Prompt组装**：系统提示词 + 用户指令 → 完整Prompt
3. **API调用**：向DeepSeek API发送请求
4. **数据校验**：使用Pydantic Schema验证返回的JSON
5. **文件生成**：校验通过后写入本地文件系统
6. **错误处理**：格式错误时自动重试（最多3次）

## ⚙️ 配置说明

### 环境变量（.env）
```env
DEEPSEEK_API_KEY=your_api_key_here          # DeepSeek API密钥
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_MODEL=deepseek-chat
API_MAX_RETRIES=3                           # API重试次数
```

### 游戏数值配置
可在`.env`中配置基础数值体系，确保生成的数值逻辑一致：
```env
GAME_MAX_LEVEL=100
GAME_BASE_HP=100
GAME_BASE_ATTACK=10
```

## 📄 许可证

MIT License
