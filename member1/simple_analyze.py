import pandas as pd
import os

years = [2022, 2023, 2024, 2025]
all_data = []

# 加载 raw_base 数据
for y in years:
    file = f'raw_base_{y}.csv'
    if os.path.exists(file):
        df = pd.read_csv(file)
        df['year'] = y
        all_data.append(df)

full_raw = pd.concat(all_data)

# 1. 定义识别规则：必须包含修复关键字
keywords = ['fix', 'bug', 'error', 'crash', 'leak', 'overflow', 'assert']
full_raw['is_fix'] = full_raw['msg'].str.lower().apply(lambda x: any(k in str(x) for k in keywords))

# 2. 筛选：只看 Bug 修复，且按 msg 长度降序排序（描述越长通常逻辑越典型）
top_10_fixes = full_raw[full_raw['is_fix']].copy()
top_10_fixes['msg_len'] = top_10_fixes['msg'].str.len()
top_10_list = top_10_fixes.sort_values(by='msg_len', ascending=False).head(10)

# 3. 整理输出格式
top_10_final = top_10_list[['year', 'hash', 'author', 'msg']]
print("--- 2022-2025 PostgreSQL 典型 Bug 修复 Top 10 ---")
print(top_10_final)

# 导出给唐明迪
top_10_final.to_csv('top_10_bug_fixes.csv', index=False)