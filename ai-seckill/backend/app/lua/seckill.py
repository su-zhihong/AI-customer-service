"""
文件路径: backend/app/lua/seckill.py
秒杀 Lua 脚本加载模块。
从 .lua 文件中读取 Redis Lua 脚本内容。
"""

import os

# 获取当前文件所在目录
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_seckill_lua_script() -> str:
    """
    获取秒杀原子操作的 Lua 脚本内容。
    
    返回:
        Lua 脚本字符串
    """
    lua_file_path = os.path.join(_CURRENT_DIR, "seckill.lua")
    with open(lua_file_path, "r", encoding="utf-8") as f:
        # 跳过文件开头的 Python 风格注释（如果有）
        content = f.read()
    return content