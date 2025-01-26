import pandas as pd

# 读取原始CSV文件
df = pd.read_csv('Hopper/Hopper_messages.csv')

# 删除id列
if 'id' in df.columns:
    df = df.drop('id', axis=1)

# 重命名列
df = df.rename(columns={
    'date': 'timestamp',
    'type': 'message_type',
    'content': 'message_content',
    'media_file': 'media_path'
})

# 添加新列
df['group_name'] = '@LSMM8'
df['username'] = 'BTC1357900'

# 重排列顺序
df = df[['timestamp', 'group_name', 'username', 'message_type', 'message_content', 'media_path']]

# 保存处理后的CSV文件
df.to_csv('Hopper/Hopper_messages.csv', index=False)

print("CSV文件处理完成！")
