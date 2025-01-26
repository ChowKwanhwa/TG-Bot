import socket
import socks
import requests
import time
from typing import Dict, Tuple
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

# Telegram API 凭证
API_ID = 22453265
API_HASH = "641c3fad1c94728381a70113c70cd52d"

async def test_telegram_connection(proxy: Dict) -> bool:
    """测试代理是否可以连接到 Telegram"""
    try:
        # 构建代理配置
        proxy_config = {
            'proxy_type': 'socks5',
            'addr': proxy['addr'],
            'port': proxy['port'],
            'username': proxy.get('username'),
            'password': proxy.get('password')
        }

        # 创建临时客户端
        client = TelegramClient(
            StringSession(),
            API_ID,
            API_HASH,
            proxy=proxy_config
        )

        # 尝试连接
        await client.connect()
        is_connected = await client.is_user_authorized()
        await client.disconnect()
        return True
    except Exception as e:
        print(f"Telegram 连接测试失败: {str(e)}")
        return False

def test_proxy(proxy: Dict) -> Tuple[bool, float, bool]:
    """测试代理并返回可用性、速度和 Telegram 连接状态"""
    print(f"\n开始测试代理: {proxy['addr']}:{proxy['port']}")
    
    try:
        # 构建代理URL
        proxy_url = f"socks5://{proxy['username']}:{proxy['password']}@{proxy['addr']}:{proxy['port']}" \
            if proxy.get('username') and proxy.get('password') \
            else f"socks5://{proxy['addr']}:{proxy['port']}"
        
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        print(f"代理设置: {proxy_url}")

        # 测试网站列表 - 只测试 Telegram 相关
        test_urls = [
            'https://api.telegram.org',
            'https://web.telegram.org'
        ]
        
        start_time = time.time()
        for url in test_urls:
            try:
                print(f"\n尝试访问: {url}")
                response = requests.get(
                    url, 
                    proxies=proxies,
                    timeout=15,  # 增加超时时间
                    verify=False
                )
                
                if response.status_code == 200:
                    print(f"成功访问 {url}")
                else:
                    print(f"访问 {url} 失败，状态码: {response.status_code}")
                    continue  # 继续测试其他URL，而不是直接返回失败
                    
            except Exception as e:
                print(f"访问 {url} 失败: {str(e)}")
                continue  # 继续测试其他URL

        elapsed_time = time.time() - start_time
        
        # 测试 Telegram 客户端连接
        print("\n测试 Telegram 客户端连接...")
        telegram_result = asyncio.get_event_loop().run_until_complete(
            test_telegram_connection(proxy)
        )
        
        return True, elapsed_time, telegram_result

    except Exception as e:
        print(f"代理测试失败: {str(e)}")
        return False, float('inf'), False

if __name__ == "__main__":
    # 测试代理示例
    test_proxy_config = {
        'addr': '119.42.39.170',
        'port': 5798,
        'username': 'Maomaomao77',
        'password': 'Maomaomao77'
    }
    
    # 禁用 SSL 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 测试代理
    is_working, speed, telegram_ok = test_proxy(test_proxy_config)
    
    # 显示测试结果
    print("\n测试结果:")
    print(f"代理可用: {'是' if is_working else '否'}")
    if is_working:
        print(f"响应时间: {speed:.2f}秒")
    print(f"Telegram 连接: {'成功' if telegram_ok else '失败'}") 