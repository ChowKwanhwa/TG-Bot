import os
import pandas as pd
from telethon import TelegramClient
import asyncio
import random
import argparse
from telethon.tl.types import InputPeerChannel, ReactionEmoji
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.functions.channels import JoinChannelRequest
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 配置
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
TARGET_GROUP = "https://t.me/qiangshengjituan101"  # 目标群组
SESSIONS_DIR = "huahua"  # session文件目录
MESSAGES_FILE = "话术/latest_messages.csv"  # 消息文件
REACTION_EMOJIS = ['👍', '🔥', '🎉', '❤️']  # 表情反应列表

# 代理配置
PROXY_CONFIG = {
    'proxy_type': 'socks5',
    'addr': '119.42.39.170',
    'port': 5798,
    'username': 'Maomaomao77',
    'password': 'Maomaomao77'
}

async def try_join_group(client, group_url):
    """尝试加入目标群组"""
    try:
        channel = await client.get_entity(group_url)
        try:
            participant = await client.get_participants(channel, limit=1)
            print(f"账号已在目标群组中")
            return True
        except Exception:
            print(f"账号未在目标群组中，正在尝试加入...")
            try:
                await client(JoinChannelRequest(channel))
                print(f"成功加入目标群组")
                return True
            except Exception as join_error:
                print(f"加入群组失败: {str(join_error)}")
                return False
    except Exception as e:
        print(f"获取群组信息失败: {str(e)}")
        return False

async def init_client(session_file):
    """初始化客户端"""
    session_path = os.path.join(SESSIONS_DIR, session_file.replace('.session', ''))
    client = TelegramClient(session_path, API_ID, API_HASH, proxy=PROXY_CONFIG)
    
    try:
        await client.connect()
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"[成功] 账号连接成功: {me.first_name} (@{me.username})")
            if await try_join_group(client, TARGET_GROUP):
                return client
        await client.disconnect()
        return None
    except Exception as e:
        print(f"[失败] 连接失败: {str(e)}")
        try:
            await client.disconnect()
        except:
            pass
        return None

async def get_recent_messages(client, limit=5):
    """获取最近的消息"""
    channel = await client.get_entity(TARGET_GROUP)
    messages = []
    async for message in client.iter_messages(channel, limit=limit):
        messages.append(message)
    return messages[::-1]

async def process_message(client, message_data, recent_messages):
    """处理单条消息"""
    try:
        channel = await client.get_entity(TARGET_GROUP)
        random_value = random.random()
        
        if random_value < 0.15:  # 15% 概率发送表情反应
            if recent_messages:
                target_message = random.choice(recent_messages)
                chosen_emoji = random.choice(REACTION_EMOJIS)
                reaction = [ReactionEmoji(emoticon=chosen_emoji)]
                await client(SendReactionRequest(
                    peer=channel,
                    msg_id=target_message.id,
                    reaction=reaction
                ))
                me = await client.get_me()
                print(f"@{me.username} 对消息ID {target_message.id} 进行了表情反应: {chosen_emoji}")
                
        elif random_value < 0.40:  # 25% 概率回复消息
            if recent_messages:
                target_message = random.choice(recent_messages)
                if message_data['message_type'] == 'text':
                    await client.send_message(channel, message_data['message_content'], 
                                           reply_to=target_message.id)
                else:
                    media_path = os.path.join("话术", message_data['media_path'].replace('话术\\', ''))
                    await client.send_file(channel, media_path, reply_to=target_message.id)
                    
        else:  # 60% 概率直接发送消息
            if message_data['message_type'] == 'text':
                await client.send_message(channel, message_data['message_content'])
            else:
                media_path = os.path.join("话术", message_data['media_path'].replace('话术\\', ''))
                await client.send_file(channel, media_path)
                
    except Exception as e:
        print(f"发送消息失败: {str(e)}")

async def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='发送消息到Telegram群组')
    parser.add_argument('--loop', action='store_true', help='循环发送消息')
    args = parser.parse_args()

    # 读取消息数据
    df = pd.read_csv(MESSAGES_FILE)
    messages = df.to_dict('records')
    messages.reverse()  # 反转消息列表，确保从最后一条（最老的）消息开始发送
    
    # 初始化客户端
    session_files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]
    clients = []
    for session_file in session_files:
        client = await init_client(session_file)
        if client:
            clients.append(client)
    
    if not clients:
        print("错误: 没有成功连接的客户端!")
        return
    
    print(f"成功初始化 {len(clients)} 个客户端")
    num_clients = len(clients)
    total_messages = len(messages)
    
    while True:  # 主循环
        print("\n开始新一轮消息发送...")
        # 按组处理消息
        for i in range(0, total_messages, num_clients):
            # 获取当前批次的消息
            batch_messages = messages[i:i + num_clients]
            if not batch_messages:
                break
                
            # 获取最近的消息
            recent_messages = await get_recent_messages(clients[0], limit=5)
            
            print(f"正在发送第 {i + 1} 到 {min(i + num_clients, total_messages)} 条消息 (共 {total_messages} 条)...")
            
            # 随机打乱客户端顺序
            available_clients = clients.copy()
            random.shuffle(available_clients)
            
            # 发送消息
            for msg, client in zip(batch_messages, available_clients):
                await process_message(client, msg, recent_messages)
                await asyncio.sleep(random.uniform(5, 15))  # 随机延迟5-15秒
        
        if not args.loop:  # 如果不是循环模式，跳出循环
            break
        
        print("本轮消息发送完成，等待开始下一轮...")
        await asyncio.sleep(30)  # 每轮之间等待30秒
    
    print("所有消息发送完成！")
    
    # 关闭所有客户端
    for client in clients:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
