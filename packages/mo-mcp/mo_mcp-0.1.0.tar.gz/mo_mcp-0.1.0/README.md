# Mo MCP - 智能命令行助手

基于通义千问的 MCP 协议多工具集成平台，支持自然语言交互。

## 🖥️ 跨平台支持

### 系统要求
- **macOS**: 10.14+ (Mojave)
- **Windows**: 10/11
- **Linux**: Ubuntu 18.04+, CentOS 7+, 等主流发行版

## 🚀 快速开始

### 1. 配置 API Key
```bash
python src/mcpai.py --setup
```

### 2. 运行程序
```bash
# 单次查询
python src/mcpai.py "你好，帮我搜索一下Python教程"

# 连续对话模式
python src/mcpai.py
```

## 🔧 功能特性

- **自然语言交互**: 支持中文对话
- **多工具集成**: 文件系统、网络搜索、数据分析等
- **跨平台兼容**: 自动识别操作系统
- **Markdown 渲染**: 美观的输出格式
- **连续对话**: 支持上下文记忆

## 📁 配置文件

配置文件位置：
- **macOS/Linux**: `~/.mcp/config.json`
- **Windows**: `%USERPROFILE%\.mcp\config.json`

## 🎯 使用技巧

- 输入 `/help` 查看帮助
- 输入 `/config` 进入配置菜单
- 输入 `/clear` 清空对话历史
- 使用 `Ctrl+C` 退出程序

## 🔍 支持的工具

- **文件系统**: `fsx.list_dir`, `fsx.glob`, `fsx.read_text`
- **网络搜索**: `web.search`, `web.search_serper`
- **数据分析**: `data.csv_merge`, `data.excel_summary`
- **代码检查**: `code.quick_inspect`

## �� 许可证

MIT License 