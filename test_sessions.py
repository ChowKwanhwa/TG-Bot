import os
import asyncio
import argparse
from telethon import TelegramClient
from dotenv import load_dotenv
import config

# 加载环境变量
load_dotenv()

# 控制并发数量
MAX_CONCURRENT_SESSIONS = 5
semaphore = asyncio.Semaphore(MAX_CONCURRENT_SESSIONS)

async def try_connect_with_proxy(session_file, proxy_config, sessions_dir):
    """尝试使用代理连接并测试会话
    proxy_config format: (type, ip, port, rdns, username, password)
    """
    session_path = os.path.join(sessions_dir, session_file.replace('.session', ''))
    
    try:
        # 提取代理信息用于显示
        proxy_type, addr, port, rdns, username, password = proxy_config
        # print(f"正在使用代理 {addr}:{port} 测试 {session_file}...")
        
        # 创建客户端
        client = TelegramClient(
            session_path,
            config.API_ID,
            config.API_HASH,
            proxy=proxy_config
        )
        
        # 尝试连接
        await client.connect()
        
        if await client.is_user_authorized():
            me = await client.get_me()
            # print(f"[成功] {session_file} 已连接: {me.first_name} (@{me.username})")
            return True, client, f"已授权 (@{me.username})"
        else:
            # print(f"[失败] {session_file} 未授权")
            await client.disconnect()
            return False, None, "未授权"
            
    except Exception as e:
        # print(f"[错误] 测试 {session_file} 时出错: {str(e)}")
        return False, None, f"错误: {str(e)}"

async def test_session(session_file, sessions_dir):
    """使用所有代理尝试测试会话文件"""
    async with semaphore:
        if not config.PROXY_LIST:
            return session_file, None, "无代理可用"

        print(f"开始测试: {session_file}")
        for proxy in config.PROXY_LIST:
            success, client, status = await try_connect_with_proxy(session_file, proxy, sessions_dir)
            if success:
                if client:
                    await client.disconnect()
                return session_file, True, status
        
        return session_file, False, "所有代理均失败/未授权"

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Test Telegram sessions.')
    parser.add_argument('--folder', type=str, help='Specific folder within sessions directory to test (e.g., "SuperExCN")')
    args = parser.parse_args()

    # 确定会话目录
    target_dir = config.SESSIONS_DIR
    if args.folder:
        target_dir = os.path.join(config.SESSIONS_DIR, args.folder)

    if not os.path.exists(target_dir):
        print(f"错误: 会话目录 {target_dir} 不存在!")
        return
    
    # 获取所有.session文件
    session_files = [f for f in os.listdir(target_dir) if f.endswith('.session')]
    if not session_files:
        print(f"错误: 在 {target_dir} 目录中没有找到.session文件!")
        return
    
    print(f"目标目录: {target_dir}")
    print(f"找到 {len(session_files)} 个会话文件，准备并发测试 (并发数: {MAX_CONCURRENT_SESSIONS})...")
    
    # 并发测试所有会话文件
    tasks = [test_session(f, target_dir) for f in session_files]
    results = await asyncio.gather(*tasks)
    
    # 打印总结报告
    print("\n=== 测试报告 ===")
    print(f"总共测试: {len(results)} 个会话文件")
    valid_count = sum(1 for _, success, _ in results if success)
    print(f"有效会话: {valid_count}")
    print(f"无效会话: {len(results) - valid_count}")
    
    # 打印详细状态 (仅打印成功的，或者是显示具体错误)
    print("\n详细结果:")
    for session_file, success, status in results:
        mark = "✅" if success else "❌"
        print(f"{mark} {session_file}: {status}")

if __name__ == "__main__":
    asyncio.run(main())