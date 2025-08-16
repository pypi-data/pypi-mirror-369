# -*- coding: utf-8 -*-  
"""
FastMCP 快速入门示例。  
首先，请切换到 `examples/snippets/clients` 目录，然后运行以下命令来启动服务器：
    uv run server fastmcp_quickstart stdio
"""
# 从 mcp.server.fastmcp 模块中导入 FastMCP 类，这是构建 MCP 服务器的核心。
from mcp.server.fastmcp import FastMCP 
# 导入必要的模块用于颜色转换
import webcolors

# 创建一个 MCP 服务器实例，并将其命名为 "Demo"。
# 这个名字会向连接到此服务器的 AI 客户端展示。
mcp = FastMCP("Demo")  
# 使用 @mcp.tool() 装饰器来定义一个"工具"。
# 工具是 AI 可以调用的具体函数，用于执行特定的操作。
@mcp.tool()
def color_to_rgb(color: str) -> str:
    """
    这个工具的功能是将颜色名称或16进制颜色码转换为RGB格式。
    参数:
    - color: 颜色名称（如'red'）或16进制颜色码（如'#FF0000'）
    返回:
    - RGB格式的颜色字符串（如'rgb(255, 0, 0)'）
    """
    try:
        # 尝试将颜色名称转换为RGB
        rgb = webcolors.name_to_rgb(color)
        return f'rgb({rgb.red}, {rgb.green}, {rgb.blue})'
    except ValueError:
        try:
            # 尝试将16进制颜色码转换为RGB
            rgb = webcolors.hex_to_rgb(color)
            return f'rgb({rgb.red}, {rgb.green}, {rgb.blue})'
        except ValueError:
            return f'无效的颜色输入: {color}。请使用有效的颜色名称或16进制颜色码（如#FF0000）。'

# 使用 @mcp.resource() 装饰器来定义一个"资源"。
# 资源代表 AI 可以访问的数据或信息。这里的路径 "greeting://{name}" 是动态的，
# {name} 部分可以被实际的名称替换，例如 "greeting://World"。
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    根据提供的名称，获取一句个性化的问候语。
    """
    # 使用 f-string 格式化字符串，返回包含名字的问候语。
    return f"Hello, {name}!"
# 使用 @mcp.prompt() 装饰器来定义一个"提示词模板"。
# 这个功能可以根据输入动态生成更复杂的、用于指导大语言模型（LLM）的指令（Prompt）。
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """
    根据给定的名字和风格，生成一句问候语的提示词。
    """
    # 定义一个字典，存储不同风格对应的提示词文本。
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    # 根据传入的 style 参数，从字典中获取对应的提示词。
    # 如果 style 参数无效或未提供，则默认使用 "friendly" 风格。
    # 最后，将选择的风格提示词与用户名组合，形成一个完整的指令。
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

if __name__ == "__main__":
    mcp.run(transport="stdio")