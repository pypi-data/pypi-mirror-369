# AutoTerminal - 智能终端工具

AutoTerminal 是一个基于大语言模型的智能终端工具，可以将自然语言转换为终端命令，提高工作效率。

## 功能特点

- 🧠 基于LLM的智能命令生成
- 🔐 安全的命令执行机制（需要用户确认）
- ⚙️ 灵活的配置管理
- 🌍 中文支持
- 🔄 支持多种LLM模型

## 安装

### 方法1：使用uv（开发模式）
确保已安装 `uv` 工具，然后运行：

```bash
uv sync
```

### 方法2：使用pip安装到用户目录（推荐给最终用户）
```bash
pip install --user .
```

安装后可以直接使用 `at` 命令：

```bash
at "查看当前目录"
```

### 卸载
```bash
pip uninstall autoterminal
```

### 全局安装（需要管理员权限）
```bash
sudo pip install .
```

## 配置

首次运行时，程序会引导您完成配置：

1. API密钥
2. Base URL
3. 模型名称

配置信息会保存在 `config.json` 文件中。

## 使用方法

### 方法1：使用uv run
```bash
uv run python autoterminal/main.py "查看当前目录下的所有文件"
```

### 方法2：安装后使用at命令
```bash
uv pip install -e .
at "查看当前目录下的所有文件"
```

程序会生成终端命令并显示提示，用户按回车后程序会直接执行该命令。

## 示例

```
$ at "列出当前目录下的所有文件"
$ ls -a
Press Enter to execute...
.  ..  autoterminal  config.json  .git  .gitignore  pyproject.toml  .python-version  README.md  uv.lock
```

## 支持的LLM

- OpenAI GPT系列
- 兼容OpenAI API的其他模型（如阿里云、腾讯云等）

## 项目结构

```
autoterminal/
├── __init__.py             # 包初始化文件
├── main.py                 # 主程序入口
├── config/                 # 配置管理模块
│   ├── __init__.py         # 包初始化文件
│   ├── loader.py           # 配置加载器
│   └── manager.py          # 配置管理器
├── llm/                    # LLM相关模块
│   ├── __init__.py         # 包初始化文件
│   └── client.py           # LLM客户端
├── utils/                  # 工具函数
│   ├── __init__.py         # 包初始化文件
│   └── helpers.py          # 辅助函数
├── pyproject.toml          # 项目配置
├── config.json             # 用户配置文件
├── .gitignore
└── README.md
