---
slug: 基于通义千问的 MCP 协议多工具集成平台，支持自然语言交互。
title: MoMCP - 智能命令行助手
authors: [AndyJin]
tags: [Python,MCP]
---

基于通义千问的 MCP 协议多工具集成平台，支持自然语言交互。

<!-- truncate -->

## 🖥️ 跨平台支持

### 系统要求
- **macOS**: 10.14+ (Mojave)
- **Windows**: 10/11
- **Linux**: Ubuntu 18.04+, CentOS 7+, 等主流发行版

## 🚀 快速开始

### 1. 安装
```bash
# 从 PyPI 安装（推荐）
pip install mo-mcp
```

### 2. 配置 API Key
```bash
# 使用 PyPI 安装的版本
momcp --setup

# 或者源码版本
python src/mcpai.py --setup
```

### 3. 运行程序
```bash
# 使用 PyPI 安装的版本
momcp "你好，帮我搜索一下Python教程"
momcp  # 进入交互模式

# 或者源码版本
python src/mcpai.py "你好，帮我搜索一下Python教程"
python src/mcpai.py  # 进入交互模式
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

### 基础命令
- 输入 `/help` 查看帮助
- 输入 `/config` 进入配置菜单
- 输入 `/clear` 清空对话历史
- 使用 `Ctrl+C` 退出程序

### 实际使用场景
```bash
# 文件管理
momcp "帮我整理 ~/Downloads 目录，按文件类型分类"
momcp "查找 ~/Documents 中包含 'TODO' 的所有文件"
momcp "列出 ~/Desktop 目录下的所有文件"
momcp "在项目中搜索所有包含 'bug' 的代码文件"

# 网络搜索
momcp "用 Bing 搜索 'Python 异步编程最佳实践'"
momcp "用百度搜索 'React 18 新特性' 的相关信息"

# 数据分析
momcp "分析 ~/Desktop/data.xlsx 文件，生成销售数据摘要"
momcp "合并 ~/data 目录下所有的用户数据 CSV 文件"

# 代码检查
momcp "检查当前目录的代码项目结构"
momcp "分析 ~/projects/webapp 目录下的代码文件类型分布"
```

## 🔍 支持的工具

### 文件系统工具
- **`fsx.list_dir`**: 列出目录内容
  ```bash
  momcp "列出 ~/Desktop 目录下的所有文件"
  momcp "查看当前工作目录下有什么文件"
  ```
- **`fsx.glob`**: 按模式匹配文件
  ```bash
  momcp "查找 ~/Documents 目录下所有的 .pdf 文件"
  momcp "搜索当前目录中所有以 'test' 开头的文件"
  ```
- **`fsx.read_text`**: 读取文本文件
  ```bash
  momcp "读取 ~/Desktop/notes.txt 文件内容"
  momcp "查看 README.md 文件的前1000个字符"
  ```
- **`fsx.search`**: 在文件中搜索文本
  ```bash
  momcp "在 ~/Documents 目录中搜索包含 'TODO' 的所有文件"
  momcp "查找当前项目中所有包含 'bug' 或 'fix' 的代码文件"
  ```
- **`fsx.organize_by_type`**: 按文件类型整理目录
  ```bash
  momcp "整理 ~/Downloads 目录，按文件扩展名分类到子文件夹"
  momcp "将当前目录下的文件按类型整理，图片、文档、代码分别放不同文件夹"
  ```

### 网络搜索工具
- **`websearch.search`**: 多引擎搜索（推荐）
  ```bash
  momcp "搜索 'Python 机器学习教程'"
  momcp "用 Bing 搜索 '如何学习 Rust 编程'"
  momcp "用百度搜索 '最新的人工智能发展'"
  ```

- **`web.search`**: 基础网页搜索（备用方案）
  ```bash
  momcp "用 DuckDuckGo 搜索 'Docker 容器化最佳实践'"
  momcp "搜索 'React 18 新特性'"
  ```

### 数据分析工具
- **`data.csv_merge`**: 合并 CSV 文件
  ```bash
  momcp "合并 ~/data 目录下所有的 sales_*.csv 文件"
  momcp "将多个用户数据 CSV 文件合并，只保留 name 和 email 列"
  ```
- **`data.excel_summary`**: Excel 数据分析
  ```bash
  momcp "分析 ~/Desktop/sales.xlsx 文件，生成数据摘要"
  momcp "查看财务数据表格的统计信息，包括平均值和标准差"
  ```

### 代码检查工具
- **`code.quick_inspect`**: 代码项目检查
  ```bash
  momcp "检查 ~/projects/myapp 目录下的代码文件类型和数量"
  momcp "分析当前目录的代码项目，统计各种编程语言文件数量"
  ```

## �� 许可证

MIT License 