import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 从环境变量获取API凭据
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置文件路径
GROUP_CONFIG_FILE = "group_config.json"
SESSIONS_DIR = "sessions"

# 表情符号列表用于reactions
REACTION_EMOJIS = ['👍', '🔥', '🎉', '😂']

# 代理列表（Telethon 支持的元组格式: type, ip, port, rdns, username, password）
PROXY_LIST = [
    ("socks5", "50.3.54.17", 443, True, "VYHMOLXmzmCy", "X9FgH374SH"),
    ("socks5", "66.93.164.245", 50101, True, "zhouyunhua0628", "pzBLnbDWjs"),
]


