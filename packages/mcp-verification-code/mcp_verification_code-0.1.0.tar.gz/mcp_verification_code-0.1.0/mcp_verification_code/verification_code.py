# -*- coding: utf-8 -*-  
"""
FastMCP 验证码生成工具。
"""
from mcp.server.fastmcp import FastMCP 
import random
import string

# 创建一个 MCP 服务器实例
mcp = FastMCP("VerificationCode")  

# 直接导出的函数，可以被其他模块导入
def generate_numeric_verification_code(digits: int = 6) -> str:
    """
    生成一个数字验证码。
    如果未指定位数，默认生成6位数字验证码。
    """
    return ''.join(random.choices(string.digits, k=digits))

def generate_alphabetic_verification_code(length: int = 6) -> str:
    """
    生成一个纯字母验证码（包含大小写）。
    如果未指定长度，默认生成6位字母验证码。
    """
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_mixed_verification_code(length: int = 6) -> str:
    """
    生成一个字母和数字混合的验证码。
    如果未指定长度，默认生成6位混合验证码。
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# 注册为MCP工具
mcp.tool()(generate_numeric_verification_code)
mcp.tool()(generate_alphabetic_verification_code)
mcp.tool()(generate_mixed_verification_code)

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    根据提供的名称，获取一句个性化的问候语。
    """
    return f"Hello, {name}!"

@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """
    根据给定的名字和风格，生成一句问候语的提示词。
    """
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

def run_server():
    """启动MCP服务器"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()