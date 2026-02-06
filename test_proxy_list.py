import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import time
from dotenv import load_dotenv
import os
import config

# 加载环境变量
load_dotenv()

async def test_telegram_proxy(proxy_tuple):
    """测试代理与Telegram的连接
    proxy_tuple format: (type, ip, port, rdns, username, password)
    """
    try:
        # 提取代理信息用于显示
        # config.PROXY_LIST 格式: ("socks5", ip, port, rdns, username, password)
        proxy_type, addr, port, rdns, username, password = proxy_tuple

        # 创建客户端 - Telethon 直接支持元组格式的代理配置
        client = TelegramClient(
            StringSession(),
            config.API_ID,
            config.API_HASH,
            proxy=proxy_tuple
        )

        # 测试连接
        start_time = time.time()
        print(f"   正在连接到 {addr}:{port}...")
        await client.connect()
        
        if not await client.is_user_authorized():
            print("   连接成功，但未授权")
            status = "未授权但可连接"
        else:
            me = await client.get_me()
            print(f"   连接成功，已授权 (@{me.username})")
            status = f"已授权 (@{me.username})"
            
        elapsed = time.time() - start_time
        await client.disconnect()
        return True, elapsed, status
        
    except Exception as e:
        return False, str(e), "连接失败"

async def test_proxy(proxy_tuple):
    """测试单个代理"""
    proxy_type, addr, port, rdns, username, password = proxy_tuple
    print(f"\n测试代理: {addr}:{port}")
    
    # 测试Telegram连接
    tg_success, tg_result, status = await test_telegram_proxy(proxy_tuple)
    
    if isinstance(tg_result, float):
        print(f"   ✅ 连接成功 (延迟: {tg_result:.2f}秒)")
        print(f"   状态: {status}")
    else:
        print(f"   ❌ 连接失败: {tg_result}")
    
    return {
        'proxy': f"{addr}:{port}",
        'success': tg_success,
        'result': tg_result,
        'status': status
    }

async def main():
    """主函数"""
    print("开始测试代理列表 (from config.py)...")
    results = []
    
    if not config.PROXY_LIST:
        print("config.py 中没有配置代理")
        return

    for proxy in config.PROXY_LIST:
        result = await test_proxy(proxy)
        results.append(result)
    
    # 打印总结报告
    print("\n=== 测试报告 ===")
    print(f"总共测试: {len(results)} 个代理")
    
    # 统计成功的代理
    success_count = sum(1 for r in results if r['success'])
    print(f"成功连接: {success_count}")
    print(f"连接失败: {len(results) - success_count}")
    
    # 打印可用的代理
    if success_count > 0:
        print("\n可用代理列表:")
        for result in results:
            if result['success']:
                print(f"{result['proxy']} - {result['status']}")
                print(f"延迟: {result['result']:.2f}秒")

if __name__ == "__main__":
    asyncio.run(main())
