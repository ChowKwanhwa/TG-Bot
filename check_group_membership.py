import os
import asyncio
from telethon import TelegramClient, functions
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import GetDiscussionMessageRequest
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

# 配置
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
TARGET_GROUP = "https://t.me/hopper_global"  # 主群组链接
TOPIC_ID = 1  # topic ID
SESSIONS_DIR = "hecai"

# 代理配置
PROXY_CONFIG = {
    'proxy_type': 'socks5',
    'addr': '45.252.58.93',
    'port': 6722,
    'username': 'Maomaomao77',
    'password': 'Maomaomao77'
}

async def check_membership(session_file):
    """检查单个账号的群组成员身份，如果未加入则尝试加入"""
    session_path = os.path.join(SESSIONS_DIR, session_file.replace('.session', ''))
    client = TelegramClient(session_path, API_ID, API_HASH, proxy=PROXY_CONFIG)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"[未授权] {session_file}")
            return False
            
        me = await client.get_me()
        print(f"\n检查账号: {me.first_name} (@{me.username})")
        
        try:
            # 先获取主群组
            channel = await client.get_entity(TARGET_GROUP)
            
            try:
                # 检查是否在群组中
                participant = await client.get_participants(channel, limit=1)
                print(f"[✓] {session_file} - 已在主群组中")
                
                # 尝试访问指定的topic
                try:
                    # 获取topic消息
                    message = await client.get_messages(channel, ids=TOPIC_ID)
                    if message:
                        print(f"[✓] {session_file} - 可以访问Topic {TOPIC_ID}")
                        return True
                    else:
                        print(f"[!] {session_file} - 无法访问Topic {TOPIC_ID}")
                        return False
                except Exception as topic_error:
                    print(f"[✗] {session_file} - 访问Topic失败: {str(topic_error)}")
                    return False
                    
            except Exception:
                print(f"[!] {session_file} - 未加入群组，正在尝试加入...")
                try:
                    await client(JoinChannelRequest(channel))
                    print(f"[✓] {session_file} - 成功加入群组")
                    # 等待一下再检查topic访问权限
                    await asyncio.sleep(2)
                    try:
                        message = await client.get_messages(channel, ids=TOPIC_ID)
                        if message:
                            print(f"[✓] {session_file} - 可以访问Topic {TOPIC_ID}")
                            return True
                        else:
                            print(f"[!] {session_file} - 无法访问Topic {TOPIC_ID}")
                            return False
                    except Exception as topic_error:
                        print(f"[✗] {session_file} - 访问Topic失败: {str(topic_error)}")
                        return False
                except Exception as join_error:
                    print(f"[✗] {session_file} - 加入群组失败: {str(join_error)}")
                    return False
                    
        except Exception as e:
            print(f"[错误] {session_file} - 获取群组信息失败: {str(e)}")
            return False
            
    except Exception as e:
        print(f"[错误] {session_file} - 连接失败: {str(e)}")
        return False
    finally:
        try:
            await client.disconnect()
        except:
            pass

async def main():
    # 获取所有session文件
    session_files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]
    
    if not session_files:
        print(f"在 {SESSIONS_DIR} 目录中没有找到session文件")
        return
        
    print(f"找到 {len(session_files)} 个session文件")
    print("-" * 50)
    
    # 检查结果统计
    total = len(session_files)
    success = 0
    failed = 0
    
    # 检查每个session
    for session_file in session_files:
        if await check_membership(session_file):
            success += 1
        else:
            failed += 1
        print("-" * 50)
    
    # 打印统计结果
    print("\n检查完成!")
    print(f"总计: {total} 个账号")
    print(f"已加入群组并可以访问Topic: {success} 个")
    print(f"未加入群组或无法访问Topic: {failed} 个")

if __name__ == "__main__":
    asyncio.run(main())
