import pandas as pd
import subprocess
import os

# --- 配置区 ---
CSV_FILE = 'task_for_quxiangming.csv'
REPO_PATH = './postgres' 
OUTPUT_DIR = 'static_analysis_diffs'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

df = pd.read_csv(CSV_FILE)
print(f"🚀 开始提取 {len(df)} 条提交的代码差异（已开启 UTF-8 兼容模式）...")

success_count = 0
fail_count = 0

for index, row in df.iterrows():
    commit_hash = row['hash']
    year = row['year']
    filename = f"{year}_{commit_hash[:8]}.diff"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        # 核心修复 1: 增加 encoding='utf-8' 和 errors='ignore'
        # 核心修复 2: 显式设置 shell=True 在某些环境下更稳定
        result = subprocess.run(
            ['git', '-C', REPO_PATH, 'show', commit_hash, '-U5'],
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore'  # 忽略无法解码的字符，保证流程不中断
        )
        
        if result.stdout:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            success_count += 1
        else:
            print(f"⚠️ Hash {commit_hash[:8]} 输出为空，可能是由于之前的读取错误。")
            fail_count += 1
            
    except Exception as e:
        print(f"❌ 提取 {commit_hash[:8]} 失败: {str(e)}")
        fail_count += 1

    if (index + 1) % 50 == 0:
        print(f"进度：已处理 {index + 1} / {len(df)}")

print(f"\n✨ 提取结束！")
print(f"✅ 成功: {success_count} 条")
print(f"❌ 失败: {fail_count} 条")