import pandas as pd
import random
import time
from datetime import datetime, timedelta

csv_file = '/Users/ericc/Desktop/TG-Repeat-Bot/messages/SuperExCN/1111.csv'
output_file = csv_file # Overwrite

# Load existing
try:
    df = pd.read_csv(csv_file)
except Exception as e:
    print(f"Error reading CSV: {e}")
    exit(1)

# Dialogue Block
# 1. 你听说superex最近新推出那个全币种合约吗
# 2. media/ff8e... (photo)
# 3. 那个是真牛逼
# 4. 炒完meme之后剩下的钱还能拿来直接开单
# 5. 梭他妈的
# 6. 拿meme炒大饼真牛逼
# 7. 我看到了 (photo: media/screenshot_new.png)
# 8. 哥们又要迟到了

insert_rows_data = [
    {"type": "text", "content": "你听说superex最近新推出那个全币种合约吗", "media_file": ""},
    {"type": "photo", "content": "", "media_file": "media/ff8e7c77a2c34b7eb9c98baca05f2c0a.jpg"},
    {"type": "text", "content": "那个是真牛逼", "media_file": ""},
    {"type": "text", "content": "炒完meme之后剩下的钱还能拿来直接开单", "media_file": ""},
    {"type": "text", "content": "梭他妈的", "media_file": ""},
    {"type": "text", "content": "拿meme炒大饼真牛逼", "media_file": ""},
    {"type": "photo", "content": "我看到了", "media_file": "media/screenshot_new.png"},
    {"type": "text", "content": "哥们又要迟到了", "media_file": ""}
]

new_rows = []
base_id = 90000000 # Start with high ID

def generate_row(data):
    global base_id
    base_id += 1
    # Generate a random recent timestamp
    now = datetime.utcnow()
    # Random format: 2026-01-26T00:42:50+00:00
    ts = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    
    return {
        "id": base_id,
        "date": ts,
        "type": data["type"],
        "content": data["content"],
        "media_file": data["media_file"]
    }

original_records = df.to_dict('records')
final_records = []

insert_interval = 90
count = 0

for row in original_records:
    final_records.append(row)
    count += 1
    
    if count % insert_interval == 0:
        # Insert block
        for item in insert_rows_data:
            final_records.append(generate_row(item))

# Convert back to DF
new_df = pd.DataFrame(final_records)

# Ensure columns order
cols = ["id", "date", "type", "content", "media_file"]
# Add missing cols if any
for c in cols:
    if c not in new_df.columns:
        new_df[c] = ""
        
new_df = new_df[cols]

new_df.to_csv(output_file, index=False)
print(f"Processed {len(original_records)} rows. New total: {len(new_df)} rows.")
