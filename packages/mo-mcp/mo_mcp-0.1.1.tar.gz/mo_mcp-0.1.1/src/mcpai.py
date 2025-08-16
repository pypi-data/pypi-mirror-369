import os
import sys
import json
import argparse
import asyncio
import platform
from typing import Any, Dict, List, Tuple
from contextlib import AsyncExitStack
from getpass import getpass
import re
import time
import httpx
import pandas as pd
from bs4 import BeautifulSoup
import glob
import html

try:
    import qrcode
except ImportError:
    qrcode = None

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

try:
	from openai import OpenAI
except ImportError:
	print("Please install dependencies with: pip install -r requirements.txt", file=sys.stderr)
	raise


class ConnectedServer:
	def __init__(self, name: str, session: ClientSession, tools: List[Any]):
		self.name = name
		self.session = session
		self.tools = tools


async def open_all_servers(servers_cfg: List[Dict[str, Any]]) -> Tuple[List[ConnectedServer], AsyncExitStack]:
	stack = AsyncExitStack()
	await stack.__aenter__()
	connected: List[ConnectedServer] = []
	for server_cfg in servers_cfg:
		name = server_cfg["name"]
		params = StdioServerParameters(
			command=server_cfg["command"],
			args=server_cfg.get("args", []),
			env=server_cfg.get("env", None),
		)
		read, write = await stack.enter_async_context(stdio_client(params))
		session: ClientSession = await stack.enter_async_context(ClientSession(read, write))
		await session.initialize()
		tools_resp = await session.list_tools()
		tools = tools_resp.tools if hasattr(tools_resp, 'tools') else tools_resp
		connected.append(ConnectedServer(name=name, session=session, tools=tools))
	return connected, stack


def extract_tool_fields(raw_tool: Any) -> Tuple[str, str, Dict[str, Any]]:
	name: str | None = None
	description: str | None = None
	parameters: Dict[str, Any] | None = None
	
	# dict-form
	if isinstance(raw_tool, dict):
		name = raw_tool.get("name") or raw_tool.get("tool")
		description = raw_tool.get("description")
		parameters = (
			raw_tool.get("input_schema")
			or raw_tool.get("inputSchema")
			or raw_tool.get("parameters")
		)
	# object-form (包括 mcp.types.Tool)
	else:
		if hasattr(raw_tool, "name") and isinstance(getattr(raw_tool, "name"), str):
			name = getattr(raw_tool, "name")
		elif hasattr(raw_tool, "tool") and isinstance(getattr(raw_tool, "tool"), str):
			name = getattr(raw_tool, "tool")
		if hasattr(raw_tool, "description"):
			description = getattr(raw_tool, "description")
		# 检查 inputSchema 属性
		if hasattr(raw_tool, "inputSchema"):
			parameters = getattr(raw_tool, "inputSchema")
		else:
			for attr in ("input_schema", "inputSchema", "parameters", "schema"):
				if hasattr(raw_tool, attr):
					candidate = getattr(raw_tool, attr)
					if isinstance(candidate, dict):
						parameters = candidate
	# tuple/list-form best-effort
	if name is None and isinstance(raw_tool, (list, tuple)):
		if len(raw_tool) >= 1 and isinstance(raw_tool[0], str):
			name = raw_tool[0]
		if len(raw_tool) >= 2 and isinstance(raw_tool[1], dict) and parameters is None:
			parameters = raw_tool[1]
		if len(raw_tool) >= 3 and isinstance(raw_tool[2], str) and description is None:
			description = raw_tool[2]
	
	if parameters is None:
		parameters = {"type": "object", "properties": {}}
	
	final_name = name or "tool"
	return final_name, (description or f"MCP tool {final_name}"), parameters


def builtin_tools() -> List[Dict[str, Any]]:
	return [
		{
			"type": "function",
			"function": {
				"name": "fsx.list_dir",
				"description": "列出目录下的文件（自动解析 ~ 相对路径等，受安全白名单限制）",
				"parameters": {
					"type": "object",
					"properties": {
						"path": {"type": "string", "description": "目录路径，可用 ~、相对路径或绝对路径"}
					},
					"required": ["path"],
					"additionalProperties": False
				}
			}
		},
		{
			"type": "function",
			"function": {
				"name": "fsx.glob",
				"description": "按 glob 模式匹配文件，返回匹配列表（受安全白名单限制）",
				"parameters": {
					"type": "object",
					"properties": {
						"pattern": {"type": "string", "description": "如 ~/Desktop/*.txt 或 相对路径模式"},
						"limit": {"type": "number", "description": "最多返回条目数，默认200"}
					},
					"required": ["pattern"],
					"additionalProperties": False
				}
			}
		},
		{
			"type": "function",
			"function": {
				"name": "fsx.read_text",
				"description": "读取文本文件（受安全白名单限制）",
				"parameters": {
					"type": "object",
					"properties": {
						"path": {"type": "string"},
						"maxBytes": {"type": "number", "description": "最大读取字节数，默认1048576"},
						"encoding": {"type": "string", "description": "指定编码，默认自动"}
					},
					"required": ["path"],
					"additionalProperties": False
				}
			}
		},
		{
			"type": "function",
			"function": {
				"name": "fsx.search",
				"description": "在目录中搜索文本，返回匹配文件与行（受安全白名单限制）",
				"parameters": {
					"type": "object",
					"properties": {
						"root": {"type": "string", "description": "搜索根目录"},
						"query": {"type": "string"},
						"regex": {"type": "boolean", "description": "是否按正则匹配，默认false"},
						"limit": {"type": "number", "description": "最多返回多少条匹配，默认200"}
					},
					"required": ["root", "query"],
					"additionalProperties": False
				}
			}
		},
		{
			"type": "function",
			"function": {
				"name": "web.search",
				"description": "基础网页搜索（备用方案，建议优先使用websearch.search）",
				"parameters": {
					"type": "object",
					"properties": {
						"query": {"type": "string", "description": "搜索关键词"},
						"engine": {"type": "string", "description": "搜索引擎：duckduckgo/google", "default": "duckduckgo"},
						"count": {"type": "number", "description": "结果数量，默认5", "default": 5}
					},
					"required": ["query"],
					"additionalProperties": False
				}
			}
		},
		{
			"type": "function",
			"function": {
				"name": "web.search_serper",
				"description": "使用Serper API进行Google搜索（需要API Key）",
				"parameters": {
					"type": "object",
					"properties": {
						"query": {"type": "string"},
						"api_key": {"type": "string", "description": "Serper API Key"}
					},
					"required": ["query", "api_key"],
					"additionalProperties": False
				}
			}
		},
		{
			"type": "function",
			"function": {
				"name": "web.scrape_images",
				"description": "下载网页中的所有图片到指定目录，并按日期重命名",
				"parameters": {
					"type": "object",
					"properties": {
						"url": {"type": "string"},
						"dest": {"type": "string", "description": "保存目录"}
					},
					"required": ["url", "dest"],
					"additionalProperties": False
				}
			}
		},
		{
			"type": "function",
			"function": {
				"name": "fsx.organize_by_type",
				"description": "将目录下文件按扩展名整理到子文件夹",
				"parameters": {
					"type": "object",
					"properties": {"path": {"type": "string"}},
					"required": ["path"],
					"additionalProperties": False
				}
			}
		},
		{
			"type": "function",
			"function": {
				"name": "data.csv_merge",
				"description": "合并多个 CSV 中的指定列为一个表格",
				"parameters": {
					"type": "object",
					"properties": {
						"pattern": {"type": "string", "description": "glob 模式，如 ~/data/*.csv"},
						"columns": {"type": "array", "items": {"type": "string"}}
					},
					"required": ["pattern"],
					"additionalProperties": False
				}
			}
		},
		{
			"type": "function",
			"function": {
				"name": "data.excel_summary",
				"description": "分析 Excel 销售数据，输出关键汇总",
				"parameters": {
					"type": "object",
					"properties": {"path": {"type": "string"}, "sheet": {"type": "string"}},
					"required": ["path"],
					"additionalProperties": False
				}
			}
		},
		{
			"type": "function",
			"function": {
				"name": "code.quick_inspect",
				"description": "快速扫描目录中的代码文件，给出语言、模块与依赖初步报告",
				"parameters": {
					"type": "object",
					"properties": {"path": {"type": "string"}},
					"required": ["path"],
					"additionalProperties": False
				}
			}
		}
	]


def build_openai_tools(servers: List[ConnectedServer]) -> List[Dict[str, Any]]:
	openai_tools: List[Dict[str, Any]] = []
	for s in servers:
		for raw in s.tools:
			tool_name, description, parameters = extract_tool_fields(raw)
			openai_tools.append(
				{
					"type": "function",
					"function": {
						"name": f"{s.name}.{tool_name}",
						"description": description,
						"parameters": parameters,
					},
				}
			)
	# Append builtin synthetic tools
	openai_tools.extend(builtin_tools())
	return openai_tools


def make_invoker(servers: List[ConnectedServer]):
	index: Dict[str, Tuple[ClientSession, str]] = {}
	for s in servers:
		for raw in s.tools:
			tool_name, _, _ = extract_tool_fields(raw)
			full_name = f"{s.name}.{tool_name}"
			index[full_name] = (s.session, tool_name)
	
	async def invoke(full_name: str, args: Dict[str, Any]) -> Any:
		if full_name not in index:
			raise RuntimeError(f"Tool not found: {full_name}")
		session, tool = index[full_name]
		try:
			result = await session.call_tool(tool, arguments=args or {})
			return result
		except Exception as e:
			# 如果第一次调用失败，尝试使用 input 格式
			try:
				result = await session.call_tool(tool, arguments={"input": args or {}})
				return result
			except Exception as e2:
				# 如果两种格式都失败，返回错误信息
				return {"error": f"工具调用失败: {str(e2)}", "tool": full_name, "args": args}

	return invoke


def to_json_safe(obj: Any) -> Any:
	# Already serializable primitives
	if obj is None or isinstance(obj, (bool, int, float, str)):
		return obj
	# MCP CallToolResult objects
	if hasattr(obj, "content"):
		content = obj.content
		if hasattr(content, "text"):
			return content.text
		else:
			return str(content)
	# Pydantic v2 models
	if hasattr(obj, "model_dump_json"):
		try:
			return json.loads(obj.model_dump_json())
		except Exception:
			pass
	if hasattr(obj, "model_dump"):
		try:
			return to_json_safe(obj.model_dump())
		except Exception:
			pass
	# Common dict/list
	if isinstance(obj, dict):
		return {k: to_json_safe(v) for k, v in obj.items()}
	if isinstance(obj, (list, tuple)):
		return [to_json_safe(v) for v in obj]
	# Fallbacks
	if hasattr(obj, "dict"):
		try:
			return to_json_safe(obj.dict())
		except Exception:
			pass
	if hasattr(obj, "__dict__"):
		try:
			return to_json_safe(vars(obj))
		except Exception:
			pass
	return repr(obj)


def safe_parse_json(s: str) -> Dict[str, Any]:
	if not s:
		return {}
	try:
		return json.loads(s)
	except Exception:
		return {}


def render_markdown(text: str) -> str:
	"""渲染 Markdown 格式文本为带颜色的终端输出"""
	if not text:
		return ""
	
	# 颜色代码
	colors = {
		'bold': '\033[1m',
		'red': '\033[91m',
		'green': '\033[92m',
		'yellow': '\033[93m',
		'blue': '\033[94m',
		'magenta': '\033[95m',
		'cyan': '\033[96m',
		'gray': '\033[90m',
		'reset': '\033[0m',
		'bg_blue': '\033[44m',
		'bg_green': '\033[42m',
		'bg_yellow': '\033[43m',
		'bg_red': '\033[41m'
	}
	
	# 处理标题
	text = re.sub(r'^### (.*?)$', rf'{colors["bold"]}{colors["cyan"]}### \1{colors["reset"]}', text, flags=re.MULTILINE)
	text = re.sub(r'^## (.*?)$', rf'{colors["bold"]}{colors["blue"]}## \1{colors["reset"]}', text, flags=re.MULTILINE)
	text = re.sub(r'^# (.*?)$', rf'{colors["bold"]}{colors["magenta"]}# \1{colors["reset"]}', text, flags=re.MULTILINE)
	
	# 处理粗体
	text = re.sub(r'\*\*(.*?)\*\*', rf'{colors["bold"]}\1{colors["reset"]}', text)
	text = re.sub(r'__(.*?)__', rf'{colors["bold"]}\1{colors["reset"]}', text)
	
	# 处理斜体
	text = re.sub(r'\*(.*?)\*', rf'{colors["cyan"]}\1{colors["reset"]}', text)
	text = re.sub(r'_(.*?)_', rf'{colors["cyan"]}\1{colors["reset"]}', text)
	
	# 处理代码块
	text = re.sub(r'```(\w+)?\n(.*?)```', rf'{colors["bg_blue"]}\2{colors["reset"]}', text, flags=re.DOTALL)
	text = re.sub(r'`([^`]+)`', rf'{colors["bg_green"]}\1{colors["reset"]}', text)
	
	# 处理链接
	text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', rf'{colors["blue"]}\1{colors["reset"]} ({colors["cyan"]}\2{colors["reset"]})', text)
	
	# 处理列表
	text = re.sub(r'^(\s*)[-*+] (.*?)$', rf'\1{colors["yellow"]}•{colors["reset"]} \2', text, flags=re.MULTILINE)
	text = re.sub(r'^(\s*)(\d+)\. (.*?)$', rf'\1{colors["yellow"]}\2.{colors["reset"]} \3', text, flags=re.MULTILINE)
	
	# 处理引用
	text = re.sub(r'^> (.*?)$', rf'{colors["gray"]}> \1{colors["reset"]}', text, flags=re.MULTILINE)
	
	# 处理表格分隔线
	text = re.sub(r'^\|[-|:]+\|$', rf'{colors["gray"]}\0{colors["reset"]}', text, flags=re.MULTILINE)
	
	# 处理表格行
	text = re.sub(r'^\|(.*?)\|$', rf'{colors["gray"]}|\1|{colors["reset"]}', text, flags=re.MULTILINE)
	
	# 处理水平线
	text = re.sub(r'^---$', rf'{colors["gray"]}{"─" * 50}{colors["reset"]}', text, flags=re.MULTILINE)
	text = re.sub(r'^___$', rf'{colors["gray"]}{"─" * 50}{colors["reset"]}', text, flags=re.MULTILINE)
	
	return text


def format_table(data: List[Dict[str, Any]], title: str = "") -> str:
	"""格式化数据为 Markdown 表格"""
	if not data:
		return ""
	
	# 获取所有列
	columns = list(data[0].keys()) if data else []
	
	# 构建表格
	table = []
	if title:
		table.append(f"## {title}")
		table.append("")
	
	# 表头
	header = "| " + " | ".join(columns) + " |"
	table.append(header)
	
	# 分隔线
	separator = "| " + " | ".join(["---"] * len(columns)) + " |"
	table.append(separator)
	
	# 数据行
	for row in data:
		row_str = "| " + " | ".join(str(row.get(col, "")) for col in columns) + " |"
		table.append(row_str)
	
	return "\n".join(table)


def format_list(items: List[str], title: str = "", style: str = "bullet") -> str:
	"""格式化列表"""
	if not items:
		return ""
	
	result = []
	if title:
		result.append(f"## {title}")
		result.append("")
	
	if style == "bullet":
		for item in items:
			result.append(f"- {item}")
	elif style == "number":
		for i, item in enumerate(items, 1):
			result.append(f"{i}. {item}")
	
	return "\n".join(result)


def format_code_block(code: str, language: str = "") -> str:
	"""格式化代码块"""
	if language:
		return f"```{language}\n{code}\n```"
	else:
		return f"```\n{code}\n```"


def show_logo() -> None:
	"""显示 Mo MCP 的 ASCII 艺术 LOGO"""
	colors = {
		'bold': '\033[1m',
		'red': '\033[91m',
		'green': '\033[92m',
		'yellow': '\033[93m',
		'blue': '\033[94m',
		'magenta': '\033[95m',
		'cyan': '\033[96m',
		'white': '\033[97m',
		'reset': '\033[0m'
	}
	
	# 获取系统信息
	system_info = get_system_info()
	
	logo = f"""
{colors['bold']}{colors['cyan']}
 __       __                  __       __   ______   _______  
/  \     /  |                /  \     /  | /      \ /       \ 
$$  \   /$$ |  ______        $$  \   /$$ |/$$$$$$  |$$$$$$$  |
$$$  \ /$$$ | /      \       $$$  \ /$$$ |$$ |  $$/ $$ |__$$ |
$$$$  /$$$$ |/$$$$$$  |      $$$$  /$$$$ |$$ |      $$    $$/ 
$$ $$ $$/$$ |$$ |  $$ |      $$ $$ $$/$$ |$$ |   __ $$$$$$$/  
$$ |$$$/ $$ |$$ \__$$ |      $$ |$$$/ $$ |$$ \__/  |$$ |      
$$ | $/  $$ |$$    $$/       $$ | $/  $$ |$$    $$/ $$ |      
$$/      $$/  $$$$$$/        $$/      $$/  $$$$$$/  $$/       
{colors['reset']}
{colors['bold']}{colors['blue']}╔══════════════════════════════════════════════════════════════════════════╗{colors['reset']}
{colors['bold']}{colors['blue']}║                    🚀 智能命令行助手 - 基于通义千问                      ║{colors['reset']}
{colors['bold']}{colors['blue']}║                    🔧 支持 MCP 协议的多工具集成平台                      ║{colors['reset']}
{colors['bold']}{colors['blue']}╚══════════════════════════════════════════════════════════════════════════╝{colors['reset']}

{colors['yellow']}✨ 特性：{colors['reset']} 自然语言交互 | 多工具支持 | 连续对话 | Markdown 渲染
{colors['green']}🔧 工具：{colors['reset']} 文件系统 | 网络搜索 | 数据分析 | 代码检查
{colors['magenta']}💡 提示：{colors['reset']} 输入 /help 查看所有可用命令

{colors['cyan']}{'─' * 70}{colors['reset']}
{colors['bold']}{colors['blue']}🖥️  系统：{colors['reset']} {system_info['icon']} {system_info['name']} {system_info['release']} ({system_info['machine']})
{colors['cyan']}{'─' * 70}{colors['reset']}
"""
	
	print(logo)


def get_system_info() -> Dict[str, str]:
	"""获取系统信息"""
	system = platform.system().lower()
	release = platform.release()
	machine = platform.machine()
	
	# 系统图标映射
	system_icons = {
		'darwin': '🍎',      # macOS
		'windows': '🪟',     # Windows
		'linux': '🐧',       # Linux
	}
	
	# 系统名称映射
	system_names = {
		'darwin': 'macOS',
		'windows': 'Windows',
		'linux': 'Linux',
	}
	
	return {
		'icon': system_icons.get(system, '💻'),
		'name': system_names.get(system, system.title()),
		'release': release,
		'machine': machine,
		'raw_system': system
	}


def expand_path(p: str) -> str:
	if os.name == 'nt' and p.startswith('~'):
		user_profile = os.environ.get('USERPROFILE', '')
		if user_profile:
			p = p.replace('~', user_profile, 1)
		else:
			username = os.environ.get('USERNAME', '')
			if username:
				p = p.replace('~', f'C:\\Users\\{username}', 1)
	else:
		p = os.path.expanduser(p)
	
	if not os.path.isabs(p):
		p = os.path.abspath(os.path.join(os.getcwd(), p))
	return os.path.realpath(p)


def get_allowed_roots_from_config(config: Dict[str, Any]) -> List[str]:
	roots: List[str] = []
	for srv in config.get("servers", []):
		args = srv.get("args", [])
		for a in args:
			if isinstance(a, str) and (a.startswith("/") or a.startswith("~") or a.startswith("C:\\")):
				expanded_path = expand_path(a)
				roots.append(expanded_path)
	
	# 如果没有配置路径，使用当前工作目录
	if not roots:
		roots.append(os.getcwd())
	
	return sorted(set(roots))


def is_path_allowed(path: str, allowed_roots: List[str]) -> bool:
	rp = os.path.realpath(path)
	for root in allowed_roots:
		try:
			if os.path.commonpath([rp, root]) == root:
				return True
		except Exception:
			continue
	return False

def resolve_under_roots(path: str, allowed_roots: List[str]) -> Tuple[str, bool, str | None]:
	rp = expand_path(path)
	if is_path_allowed(rp, allowed_roots):
		return rp, True, None
	if not os.path.isabs(path) and allowed_roots:
		candidate = os.path.realpath(os.path.join(allowed_roots[0], path))
		return candidate, is_path_allowed(candidate, allowed_roots), None if is_path_allowed(candidate, allowed_roots) else allowed_roots[0]
	if os.path.isabs(path) and allowed_roots:
		suggestion = os.path.realpath(os.path.join(allowed_roots[0], os.path.basename(path)))
		return rp, False, suggestion
	return rp, False, None


def write_api_key_to_config(config_path: str, api_key: str) -> None:
	# 确保目录存在
	dir_path = os.path.dirname(config_path)
	if dir_path and not os.path.exists(dir_path):
		os.makedirs(dir_path, exist_ok=True)
	# 读取或创建配置
	try:
		with open(config_path, "r", encoding="utf-8") as f:
			data = json.load(f)
	except FileNotFoundError:
		data = {}
	model = data.get("model") or {}
	model["apiKey"] = api_key
	data["model"] = model
	with open(config_path, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=1)


def create_qr_code_ascii(text: str, size: int = 1) -> str:
	"""创建ASCII字符二维码"""
	if qrcode is None:
		return "❌ 二维码功能未安装，请运行: pip install qrcode[pil]"
	
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=size,
		border=2,
	)
	qr.add_data(text)
	qr.make(fit=True)
	
	# 获取二维码矩阵
	matrix = qr.get_matrix()
	
	# 转换为ASCII字符
	ascii_qr = ""
	for row in matrix:
		for cell in row:
			ascii_qr += "██" if cell else "  "
		ascii_qr += "\n"
	
	return ascii_qr


def show_recharge_qr() -> None:
	"""显示通义千问充值二维码"""
	recharge_url = "https://billing-cost.console.aliyun.com/fortune/fund-management/recharge"
	
	colors = {
		'bold': '\033[1m',
		'blue': '\033[94m',
		'cyan': '\033[96m',
		'green': '\033[92m',
		'yellow': '\033[93m',
		'red': '\033[91m',
		'magenta': '\033[95m',
		'reset': '\033[0m'
	}
	
	print(f"\n{colors['bold']}{colors['blue']}=== 通义千问余额充值 ==={colors['reset']}")
	print(f"{colors['yellow']}📱 请使用手机扫描下方二维码进行充值{colors['reset']}")
	print(f"{colors['cyan']}💳 充值地址: {recharge_url}{colors['reset']}")
	print()
	
	# 生成并显示二维码
	qr_code = create_qr_code_ascii(recharge_url, size=1)
	print(qr_code)
	
	print(f"{colors['green']}✅ 扫描二维码后，请在浏览器中完成充值操作{colors['reset']}")
	print(f"{colors['yellow']}💡 充值完成后，您就可以正常使用通义千问API了{colors['reset']}")


def show_customer_service_qr() -> None:
	"""显示客服联系二维码"""
	cs_url = "https://cs.andyjin.website"
	
	colors = {
		'bold': '\033[1m',
		'blue': '\033[94m',
		'cyan': '\033[96m',
		'green': '\033[92m',
		'yellow': '\033[93m',
		'red': '\033[91m',
		'magenta': '\033[95m',
		'reset': '\033[0m'
	}
	
	print(f"\n{colors['bold']}{colors['blue']}=== 客服支持 ==={colors['reset']}")
	print(f"{colors['yellow']}📱 请使用手机扫描下方二维码联系客服{colors['reset']}")
	print(f"{colors['cyan']}💬 客服地址: {cs_url}{colors['reset']}")
	print()
	
	# 生成并显示二维码
	qr_code = create_qr_code_ascii(cs_url, size=1)
	print(qr_code)
	
	print(f"{colors['green']}✅ 扫描二维码后，您可以通过客服获得技术支持{colors['reset']}")
	print(f"{colors['yellow']}💡 遇到问题？客服会为您提供专业帮助{colors['reset']}")
	print(f"{colors['magenta']}📧 支持问题反馈、功能建议、使用指导等{colors['reset']}")


def write_model_to_config(config_path: str, model_name: str) -> None:
	try:
		with open(config_path, "r", encoding="utf-8") as f:
			data = json.load(f)
	except FileNotFoundError:
		data = {}
	model = data.get("model") or {}
	model["model"] = model_name
	data["model"] = model
	with open(config_path, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=1)


def interactive_api_key_setup(config_path: str, current_key: str | None) -> str:
	print("API 密钥配置选项：")
	print("1) 仅本次使用（不保存到文件）")
	print(f"2) 保存到配置文件：{config_path}")
	print("3) 取消")
	while True:
		choice = input("请选择 [1/2/3]: ").strip()
		if choice not in {"1", "2", "3"}:
			continue
		if choice == "3":
			print("已取消。")
			sys.exit(1)
		api_key = getpass("请输入 DashScope API Key（输入不可见）：").strip()
		if not api_key:
			print("密钥不能为空。")
			continue
		if choice == "2":
			write_api_key_to_config(config_path, api_key)
			print("已写入配置文件。")
		return api_key

async def handle_builtin_tool(name: str, args: Dict[str, Any], allowed_roots: List[str]) -> Any:
	if name == "fsx.list_dir":
		raw = args.get("path", "")
		path, allowed, suggestion = resolve_under_roots(raw, allowed_roots)
		if not allowed:
			return {"error": f"越过允许目录: {path}", "suggestion": suggestion, "allowedRoots": allowed_roots}
		if not os.path.isdir(path):
			return {"error": f"路径不是目录: {path}"}
		items = []
		try:
			for entry in os.scandir(path):
				items.append({
					"name": entry.name,
					"type": "dir" if entry.is_dir() else "file",
					"size": entry.stat().st_size if entry.is_file() else None
				})
			return {"path": path, "items": items}
		except Exception as e:
			return {"error": str(e), "path": path}
	elif name == "fsx.glob":
		pattern = args.get("pattern", "")
		limit = int(args.get("limit", 200))
		# 支持相对或绝对模式
		# 若模式未含路径分隔，默认基于第一个 root
		paths: List[str] = []
		if os.path.isabs(os.path.expanduser(pattern)):
			paths = glob.glob(expand_path(pattern))
		elif allowed_roots:
			paths = []
			for root in allowed_roots:
				paths.extend(glob.glob(os.path.join(root, pattern)))
		else:
			paths = glob.glob(expand_path(pattern))
		# 过滤越权
		paths = [os.path.realpath(p) for p in paths if is_path_allowed(p, allowed_roots)]
		paths = sorted(set(paths))[:limit]
		return {"matches": paths}
	elif name == "fsx.read_text":
		raw = args.get("path", "")
		max_bytes = int(args.get("maxBytes", 1048576))
		encoding = args.get("encoding")
		path, allowed, suggestion = resolve_under_roots(raw, allowed_roots)
		if not allowed:
			return {"error": f"越过允许目录: {path}", "suggestion": suggestion, "allowedRoots": allowed_roots}
		if not os.path.isfile(path):
			return {"error": f"不是文件: {path}"}
		try:
			with open(path, "rb") as f:
				data = f.read(max_bytes)
			try:
				text = data.decode(encoding or "utf-8", errors="replace")
			except Exception:
				text = data.decode("latin-1", errors="replace")
			return {"path": path, "text": text, "truncated": os.path.getsize(path) > len(data)}
		except Exception as e:
			return {"error": str(e), "path": path}
	elif name == "fsx.search":
		root_raw = args.get("root", "")
		query = args.get("query", "")
		use_regex = bool(args.get("regex", False))
		limit = int(args.get("limit", 200))
		root, allowed, suggestion = resolve_under_roots(root_raw, allowed_roots)
		if not allowed:
			return {"error": f"越过允许目录: {root}", "suggestion": suggestion, "allowedRoots": allowed_roots}
		if not os.path.isdir(root):
			return {"error": f"路径不是目录: {root}"}
		matches = []
		pattern = re.compile(query) if use_regex else None
		for dirpath, _, filenames in os.walk(root):
			for fn in filenames:
				fp = os.path.join(dirpath, fn)
				if not is_path_allowed(fp, allowed_roots):
					continue
				try:
					# 跳过过大文件
					if os.path.getsize(fp) > 2 * 1024 * 1024:
						continue
					with open(fp, "rb") as f:
						data = f.read()
					text = data.decode("utf-8", errors="ignore")
					for i, line in enumerate(text.splitlines(), 1):
						ok = bool(pattern.search(line)) if pattern else (query in line)
						if ok:
							matches.append({"path": fp, "line": i, "text": line.strip()})
							if len(matches) >= limit:
								return {"matches": matches, "truncated": True}
				except Exception:
					continue
		return {"matches": matches, "truncated": False}
	elif name == "fsx.organize_by_type":
		root_raw = args.get("path", "")
		root, allowed, suggestion = resolve_under_roots(root_raw, allowed_roots)
		if not allowed:
			return {"error": f"越过允许目录: {root}", "suggestion": suggestion, "allowedRoots": allowed_roots}
		if not os.path.isdir(root):
			return {"error": f"路径不是目录: {root}"}
		moved = []
		for entry in os.scandir(root):
			if entry.is_file():
				ext = os.path.splitext(entry.name)[1].lstrip(".") or "unknown"
				dst_dir = os.path.join(root, ext)
				os.makedirs(dst_dir, exist_ok=True)
				src = os.path.join(root, entry.name)
				dst = os.path.join(dst_dir, entry.name)
				os.replace(src, dst)
				moved.append({"from": src, "to": dst})
		return {"moved": moved}
	elif name == "web.search":
		q = args.get("query", "").strip()
		engine = args.get("engine", "duckduckgo").lower()
		count = min(int(args.get("count", 5)), 10)
		
		if not q:
			return {"error": "query 为空"}
		
		try:
			if engine == "duckduckgo":
				# DuckDuckGo 搜索
				url = f"https://duckduckgo.com/html/?q={httpx.QueryParams({'q': q})['q']}"
				async with httpx.AsyncClient(timeout=15) as client:
					resp = await client.get(url, headers={
						"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
					})
					soup = BeautifulSoup(resp.text, "lxml")
					results = []
					for a in soup.select("a.result__a")[:count]:
						title = a.get_text(strip=True)
						url = a.get("href")
						if title and url:
							results.append({"title": title, "url": url})
					return {"results": results, "engine": "duckduckgo", "query": q}
			
			elif engine == "google":
				# 使用 Serper API 进行 Google 搜索（免费额度）
				serper_key = os.getenv("SERPER_API_KEY")
				if not serper_key:
					return {"error": "Google搜索需要SERPER_API_KEY环境变量", "suggestion": "请设置SERPER_API_KEY或使用duckduckgo引擎"}
				
				url = "https://google.serper.dev/search"
				async with httpx.AsyncClient(timeout=15) as client:
					resp = await client.post(url, json={"q": q, "num": count}, headers={"X-API-KEY": serper_key})
					data = resp.json()
					results = []
					for item in data.get("organic", [])[:count]:
						results.append({
							"title": item.get("title", ""),
							"url": item.get("link", ""),
							"snippet": item.get("snippet", "")
						})
					return {"results": results, "engine": "google", "query": q}
			
			else:
				return {"error": f"不支持的搜索引擎: {engine}", "supported": ["duckduckgo", "google"]}
				
		except Exception as e:
			return {"error": f"搜索失败: {str(e)}", "suggestion": "请检查网络连接或稍后重试"}
	
	elif name == "web.search_serper":
		q = args.get("query", "").strip()
		api_key = args.get("api_key", "").strip()
		
		if not q:
			return {"error": "query 为空"}
		if not api_key:
			return {"error": "api_key 为空"}
		
		try:
			url = "https://google.serper.dev/search"
			async with httpx.AsyncClient(timeout=15) as client:
				resp = await client.post(url, json={"q": q, "num": 5}, headers={"X-API-KEY": api_key})
				if resp.status_code != 200:
					return {"error": f"API请求失败: {resp.status_code}", "response": resp.text}
				
				data = resp.json()
				results = []
				for item in data.get("organic", []):
					results.append({
						"title": item.get("title", ""),
						"url": item.get("link", ""),
						"snippet": item.get("snippet", "")
					})
				return {"results": results, "engine": "google", "query": q}
				
		except Exception as e:
			return {"error": f"Serper搜索失败: {str(e)}", "suggestion": "请检查API Key和网络连接"}
	elif name == "web.scrape_images":
		url = args.get("url", "")
		dest_raw = args.get("dest", "")
		dest, allowed, suggestion = resolve_under_roots(dest_raw, allowed_roots)
		if not allowed:
			return {"error": f"越过允许目录: {dest}", "suggestion": suggestion, "allowedRoots": allowed_roots}
		if not url or not dest:
			return {"error": "url/dest 不能为空"}
		os.makedirs(dest, exist_ok=True)
		async with httpx.AsyncClient(timeout=20) as client:
			resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
			soup = BeautifulSoup(resp.text, "lxml")
			imgs = [img.get("src") for img in soup.find_all("img") if img.get("src")]
			downloaded = []
			for i, src in enumerate(imgs, 1):
				try:
					abs_url = src if src.startswith("http") else httpx.URL(url).join(src)
					fn = time.strftime("%Y%m%d_%H%M%S") + f"_{i:03d}.jpg"
					fp = os.path.join(dest, fn)
					binr = await client.get(str(abs_url))
					with open(fp, "wb") as f:
						f.write(binr.content)
					downloaded.append({"url": str(abs_url), "path": fp})
				except Exception as e:
					pass
			return {"downloaded": downloaded}
	elif name == "data.csv_merge":
		pattern_raw = args.get("pattern", "")
		# 支持相对模式，映射到所有允许根
		files: List[str] = []
		if os.path.isabs(os.path.expanduser(pattern_raw)):
			for p in glob.glob(expand_path(pattern_raw)):
				if is_path_allowed(p, allowed_roots):
					files.append(p)
		else:
			for root in allowed_roots:
				files.extend(glob.glob(os.path.join(root, pattern_raw)))
		files = [os.path.realpath(p) for p in files if is_path_allowed(p, allowed_roots)]
		columns = args.get("columns")
		frames = []
		for fp in files:
			try:
				df = pd.read_csv(fp)
				if columns:
					df = df[[c for c in columns if c in df.columns]]
				frames.append(df)
			except Exception:
				pass
		if not frames:
			return {"error": "未找到可读的 CSV"}
		out = pd.concat(frames, ignore_index=True)
		return {"columns": list(out.columns), "rows": min(len(out), 10), "preview": out.head(10).to_dict(orient="records")}
	elif name == "data.excel_summary":
		raw = args.get("path", "")
		path, allowed, suggestion = resolve_under_roots(raw, allowed_roots)
		if not allowed:
			return {"error": f"越过允许目录: {path}", "suggestion": suggestion, "allowedRoots": allowed_roots}
		sheet = args.get("sheet")
		if not os.path.exists(path):
			return {"error": "文件不存在"}
		df = pd.read_excel(path, sheet_name=sheet) if sheet else pd.read_excel(path)
		summary = {"shape": df.shape, "columns": list(df.columns)}
		num_cols = df.select_dtypes(include=["number"]).columns.tolist()
		if num_cols:
			stats = df[num_cols].describe().to_dict()
			summary["describe"] = stats
		return summary
	elif name == "code.quick_inspect":
		raw = args.get("path", "")
		root, allowed, suggestion = resolve_under_roots(raw, allowed_roots)
		if not allowed:
			return {"error": f"越过允许目录: {root}", "suggestion": suggestion, "allowedRoots": allowed_roots}
		if not os.path.isdir(root):
			return {"error": f"路径不是目录: {root}"}
		report = {"languages": {}, "files": 0, "modules": []}
		for dirpath, _, filenames in os.walk(root):
			for fn in filenames:
				ext = os.path.splitext(fn)[1].lower()
				report["languages"][ext] = report["languages"].get(ext, 0) + 1
				report["files"] += 1
				if ext in {".py", ".js", ".ts", ".java", ".go"}:
					report["modules"].append(os.path.join(dirpath, fn))
		return report
	return {"error": f"Unknown builtin tool: {name}"}


async def run_once(user_query: str, config: Dict[str, Any], api_key: str, verbose: bool = False, conversation_history: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
	servers_cfg = config.get("servers", [])
	if not servers_cfg:
		raise RuntimeError("No MCP servers configured. See README for config format.")

	connected = []
	stack: AsyncExitStack
	connected, stack = await open_all_servers(servers_cfg)
	try:
		openai_tools = build_openai_tools(connected)
		invoke = make_invoker(connected)
		allowed_roots = get_allowed_roots_from_config(config)

		client = OpenAI(
			api_key=api_key,
			base_url=(config.get("model", {}).get("baseURL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"),
		)
		model_name = config.get("model", {}).get("model", "qwen-plus")
		max_steps = int(config.get("limits", {}).get("maxSteps", 6))

		# 构建对话历史
		messages: List[Dict[str, Any]] = [
			{
				"role": "system",
				"content": "你是一个可以调用工具的智能体。需要外部能力（文件/命令/搜索等）时再调用工具；根据工具结果输出简洁中文答案。\n\n可用的工具包括：\n- websearch.search: 多引擎搜索（推荐），参数：query（必需）、limit（可选）、engines（可选，数组）\n- web.search: 基础搜索（备用）\n- fsx.list_dir: 列出目录文件\n- fsx.glob: 文件模式匹配\n- fsx.read_text: 读取文本文件\n- fsx.search: 搜索文件内容\n- data.csv_merge: 合并CSV文件\n- data.excel_summary: Excel数据分析\n- code.quick_inspect: 代码检查\n\n搜索优化建议：\n1. 快速搜索：使用 websearch.search 并指定 engines=['bing']（最快）\n2. 全面搜索：使用 websearch.search 并指定 engines=['bing', 'duckduckgo']（平衡速度和结果）\n3. 中文搜索：使用 websearch.search 并指定 engines=['baidu', 'csdn']（中文内容更丰富）",
			}
		]
		
		# 添加对话历史
		if conversation_history:
			messages.extend(conversation_history)
		
		# 添加当前用户问题
		messages.append({"role": "user", "content": user_query})

		for step in range(max_steps):
			resp = client.chat.completions.create(
				model=model_name,
				messages=messages,
				tools=openai_tools,
			)
			choice = resp.choices[0]
			msg = choice.message

			if getattr(msg, "tool_calls", None):
				# Echo assistant tool_calls into the transcript as required by spec
				messages.append({
					"role": "assistant",
					"content": msg.content,
					"tool_calls": [
						{
							"id": tc.id,
							"type": tc.type,
							"function": {"name": tc.function.name, "arguments": tc.function.arguments},
						}
						for tc in msg.tool_calls
					],
				})

				for tc in msg.tool_calls:
					name = tc.function.name
					args = safe_parse_json(tc.function.arguments)
					if verbose:
						print(f"[tool] calling {name} with {args}")
					try:
						if name.startswith("fsx.") or name.startswith("web.") or name.startswith("data.") or name.startswith("code."):
							result = await handle_builtin_tool(name, args, allowed_roots)
						else:
							result = await invoke(name, args)
					except RuntimeError as e:
						if "Tool not found" in str(e):
							result = {"error": f"工具未找到: {name}", "available_tools": [t["function"]["name"] for t in openai_tools]}
						else:
							raise
					except Exception as e:
						if verbose:
							print(f"[error] 工具调用失败: {name} - {e}")
						result = {"error": f"工具调用失败: {str(e)}", "tool": name, "args": args}
					serializable = to_json_safe(result)
					messages.append(
						{
							"role": "tool",
							"tool_call_id": tc.id,
							"name": name,
							"content": json.dumps(serializable, ensure_ascii=False),
						}
					)
				continue

			# Final answer
			if msg.content:
				# 渲染 Markdown 格式
				rendered_content = render_markdown(msg.content)
				print(rendered_content)
				# 添加助手回复到对话历史
				messages.append({
					"role": "assistant",
					"content": msg.content
				})
				break
	finally:
		await stack.aclose()
	
	# 返回更新后的对话历史（排除系统消息）
	return [msg for msg in messages if msg["role"] != "system"]


async def conversation_loop(config_path: str, config: Dict[str, Any], api_key: str, verbose: bool = False) -> None:
	conversation_history: List[Dict[str, Any]] = []
	
	# 显示 LOGO
	show_logo()
	print()  # 空行
	
	# 使用颜色美化界面
	colors = {
		'bold': '\033[1m',
		'blue': '\033[94m',
		'cyan': '\033[96m',
		'green': '\033[92m',
		'yellow': '\033[93m',
		'magenta': '\033[95m',
		'reset': '\033[0m'
	}
	
	print(f"{colors['bold']}{colors['blue']}=== MCP AI CLI 连续对话模式 ==={colors['reset']}")
	print(f"{colors['cyan']}直接输入问题开始对话，支持以下特殊命令：{colors['reset']}")
	print(f"  {colors['yellow']}/help{colors['reset']}     - 显示帮助信息")
	print(f"  {colors['yellow']}/config{colors['reset']}   - 配置选项")
	print(f"  {colors['yellow']}/clear{colors['reset']}    - 清空对话历史")
	print(f"  {colors['yellow']}/cs{colors['reset']}       - 联系客服支持")
	print(f"  {colors['yellow']}/quit{colors['reset']}     - 退出程序")
	print(f"  {colors['yellow']}Ctrl+C{colors['reset']}    - 退出程序")
	print()
	
	while True:
		try:
			# 显示对话提示
			user_input = input("> ").strip()
			
			if not user_input:
				continue
			
			# 处理特殊命令
			if user_input.startswith("/"):
				command = user_input.lower()
				if command == "/help":
					help_text = """
## 特殊命令说明

### 基础命令
- **/help**     - 显示此帮助信息
- **/config**   - 进入配置菜单
- **/clear**    - 清空对话历史
- **/cs**       - 联系客服获得支持
- **/quit**     - 退出程序

### 使用技巧
- 直接输入问题即可开始对话
- 支持 **Markdown** 格式输出
- 支持连续对话，AI 会记住上下文
- 使用 `Ctrl+C` 可随时退出
- 遇到问题？使用 `/cs` 联系客服
"""
					print(render_markdown(help_text))
					continue
				elif command == "/config":
					await config_menu(config_path, config, api_key)
					continue
				elif command == "/clear":
					conversation_history.clear()
					print(f"{colors['green']}✓ 对话历史已清空！{colors['reset']}")
					continue
				elif command == "/cs":
					show_customer_service_qr()
					continue
				elif command == "/quit":
					print(f"{colors['cyan']}👋 再见！{colors['reset']}")
					return
				else:
					print(f"未知命令: {user_input}，输入 /help 查看帮助")
					continue
			
			# 正常对话
			print("AI: ", end="", flush=True)
			conversation_history = await run_once(user_input, config, api_key=api_key, verbose=verbose, conversation_history=conversation_history)
			print()  # 换行
			
		except (EOFError, KeyboardInterrupt):
			print("\n\n再见！")
			return


async def config_menu(config_path: str, config: Dict[str, Any], api_key: str) -> None:
	"""配置菜单，从对话模式中调用"""
	colors = {
		'bold': '\033[1m',
		'blue': '\033[94m',
		'cyan': '\033[96m',
		'green': '\033[92m',
		'yellow': '\033[93m',
		'magenta': '\033[95m',
		'reset': '\033[0m'
	}
	
	while True:
		print(f"\n{colors['bold']}{colors['blue']}=== 配置菜单 ==={colors['reset']}")
		print(f"1) {colors['cyan']}配置通义千问 API Key{colors['reset']}")
		print(f"2) {colors['cyan']}切换模型（model）{colors['reset']}")
		print(f"3) {colors['cyan']}查看当前配置概览{colors['reset']}")
		print(f"4) {colors['cyan']}配置文件系统路径{colors['reset']}")
		print(f"5) {colors['magenta']}💳 通义千问余额充值{colors['reset']}")
		print(f"6) {colors['yellow']}返回对话模式{colors['reset']}")
		choice = input(f"{colors['green']}请选择 [1-6]: {colors['reset']}").strip()
		
		if choice == "1":
			api_key = interactive_api_key_setup(config_path, api_key)
		elif choice == "2":
			new_model = input("请输入模型名（如 qwen-plus 或 qwen2.5-72b-instruct）：").strip()
			if not new_model:
				continue
			print("是否保存到配置文件？ y/N")
			if input().strip().lower() == "y":
				write_model_to_config(config_path, new_model)
				config = load_config(config_path)
				print("已保存。")
			else:
				config.setdefault("model", {})["model"] = new_model
		elif choice == "3":
			model = (config.get("model") or {}).get("model", "qwen-plus")
			base_url = (config.get("model") or {}).get("baseURL", "(默认)")
			servers = config.get("servers", [])
			print(f"模型: {model}")
			print(f"BaseURL: {base_url}")
			print(f"API Key: {'已配置' if api_key else '未配置'}")
			print(f"MCP 服务器数: {len(servers)} -> {[s.get('name') for s in servers]}")
		elif choice == "4":
			print("当前允许的文件系统路径:")
			allowed_roots = get_allowed_roots_from_config(config)
			for i, root in enumerate(allowed_roots):
				print(f"  {i+1}. {root}")
			
			# 根据系统显示不同的路径选项
			system_info = get_system_info()
			if system_info['raw_system'] == 'windows':
				print("\n路径配置选项 (Windows):")
				print("1) 使用用户主目录 (%USERPROFILE%)")
				print("2) 使用当前工作目录")
				print("3) 自定义路径")
				print("4) 返回")
				
				path_choice = input("请选择 [1-4]: ").strip()
				if path_choice == "1":
					new_path = "~"  # 在 Windows 上 ~ 会被自动转换为 %USERPROFILE%
				elif path_choice == "2":
					new_path = os.getcwd()
				elif path_choice == "3":
					new_path = input("请输入路径（支持 ~、%USERPROFILE% 和相对路径）: ").strip()
					if not new_path:
						continue
				else:
					continue
			else:
				print("\n路径配置选项:")
				print("1) 使用用户主目录 (~)")
				print("2) 使用当前工作目录")
				print("3) 自定义路径")
				print("4) 返回")
				
				path_choice = input("请选择 [1-4]: ").strip()
				if path_choice == "1":
					new_path = "~"
				elif path_choice == "2":
					new_path = os.getcwd()
				elif path_choice == "3":
					new_path = input("请输入路径（支持 ~ 和相对路径）: ").strip()
					if not new_path:
						continue
				else:
					continue
			
			# 更新配置文件
			for server in config.get("servers", []):
				if server.get("name") == "fs":
					server["args"] = ["@modelcontextprotocol/server-filesystem", new_path]
					break
			
			# 保存到配置文件
			config_path = os.path.expanduser("~/.mcp/config.json")
			with open(config_path, "w", encoding="utf-8") as f:
				json.dump(config, f, ensure_ascii=False, indent=2)
			
			print(f"文件系统路径已更新为: {new_path}")
			print("重启程序后生效")
			
		elif choice == "5":
			show_recharge_qr()
		elif choice == "6":
			print("返回对话模式...")
			break
		else:
			continue


async def repl(config: Dict[str, Any], api_key: str, verbose: bool = False) -> None:
	print("MCP AI CLI (Qwen). Type Ctrl+C to exit.")
	while True:
		try:
			query = input("> ").strip()
			if not query:
				continue
			await run_once(query, config, api_key=api_key, verbose=verbose)
		except (EOFError, KeyboardInterrupt):
			print()
			return


def load_config(path: str) -> Dict[str, Any]:
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)


def main():
	parser = argparse.ArgumentParser(description="Natural language to MCP tool caller (Qwen)")
	parser.add_argument("query", nargs=argparse.REMAINDER, help="Single-turn query to run. If empty, enter interactive menu.")
	parser.add_argument("--config", dest="config", default=os.getenv("MCP_CONFIG_PATH") or os.path.expanduser("~/.mcp/config.json"), help="Path to config JSON")
	parser.add_argument("--api-key", dest="api_key", default=None, help="DashScope API key for Qwen (overrides env/config)")
	parser.add_argument("--setup", dest="setup", action="store_true", help="Interactive API key setup before running")
	parser.add_argument("--verbose", dest="verbose", action="store_true", help="Verbose tool call logs")
	args = parser.parse_args()

	config = load_config(args.config)
	query_text = " ".join(args.query).strip()

	api_key = (
		args.api_key
		or config.get("model", {}).get("apiKey")
		or os.getenv("DASHSCOPE_API_KEY")
	)

	if args.setup or (not api_key and not query_text):
		api_key = interactive_api_key_setup(args.config, api_key)

	if query_text:
		if not api_key:
			print("Error: DashScope API key not provided.", file=sys.stderr)
			sys.exit(1)
		# 显示 LOGO
		show_logo()
		print()  # 空行
		asyncio.run(run_once(query_text, config, api_key=api_key, verbose=args.verbose))
	else:
		asyncio.run(conversation_loop(args.config, config, api_key=api_key or "", verbose=args.verbose))


if __name__ == "__main__":
	main() 